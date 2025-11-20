"""
Vision API - Screen sharing and camera feeds for Grace

Allows Grace to see what you see with proper governance controls.
"""

import base64
import io
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field

from backend.auth.auth_service import get_current_user, verify_session_token, create_session_token
from backend.action_gateway import action_gateway
from backend.event_bus import event_bus, Event, EventType
from backend.core.unified_event_publisher import publish_event_obj

router = APIRouter()

# Active vision sessions
vision_sessions: Dict[str, Dict[str, Any]] = {}
active_vision_streams: Dict[str, WebSocket] = {}


class VisionStartRequest(BaseModel):
    """Request to start vision session"""
    user_id: str = Field(default="user")
    source_type: str = Field(..., description="screen, camera, or window")
    quality: str = Field(default="medium", description="low, medium, high")
    governance_level: str = Field(default="approval_required", description="Governance tier for vision access")


@router.post("/vision/start")
async def start_vision_session(
    request: VisionStartRequest,
    user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Start a vision session (screen share or camera)
    
    Governance:
    - Requires approval through Action Gateway
    - All frames logged to audit trail
    - User must explicitly grant vision access
    """
    try:
        # Request approval through Action Gateway
        governance_result = await action_gateway.request_action(
            action_type="vision_access",
            agent="grace_vision",
            params={
                "user_id": user["user_id"],
                "source_type": request.source_type,
                "quality": request.quality
            },
            trace_id=f"vision_{uuid4().hex[:12]}"
        )
        
        if not governance_result.get("approved"):
            return {
                "success": False,
                "message": "Vision access requires approval",
                "governance": governance_result,
                "requires_approval": True
            }
        
        # Create vision session
        session_token = create_session_token(
            user_id=user["user_id"],
            session_type="vision",
            metadata={
                "source_type": request.source_type,
                "quality": request.quality,
                "governance_level": request.governance_level
            }
        )
        
        session_data = {
            "session_token": session_token,
            "user_id": user["user_id"],
            "source_type": request.source_type,
            "quality": request.quality,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "frame_count": 0,
            "governance_approved": True
        }
        
        vision_sessions[session_token] = session_data
        
        # Log session start
        await publish_event_obj(
            event_type=EventType.AGENT_ACTION,
            source="vision_api",
            data={
                "action": "vision_started",
                "session_token": session_token,
                "user_id": user["user_id"],
                "source_type": request.source_type,
                "governance": governance_result
            },
            trace_id=session_token
        )
        
        return {
            "success": True,
            "message": "Vision session started",
            "session": session_data,
            "websocket_url": f"/api/vision/stream?session_token={session_token}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start vision session: {str(e)}"
        )


@router.post("/vision/stop")
async def stop_vision_session(
    session_token: str,
    user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Stop a vision session"""
    try:
        if session_token not in vision_sessions:
            raise HTTPException(status_code=404, detail="Vision session not found")
        
        session = vision_sessions[session_token]
        
        # Verify user owns this session
        if session["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        session["status"] = "stopped"
        session["stopped_at"] = datetime.now().isoformat()
        
        # Close WebSocket if active
        if session_token in active_vision_streams:
            ws = active_vision_streams[session_token]
            await ws.close()
            del active_vision_streams[session_token]
        
        # Log session stop
        await publish_event_obj(
            event_type=EventType.AGENT_ACTION,
            source="vision_api",
            data={
                "action": "vision_stopped",
                "session_token": session_token,
                "user_id": user["user_id"],
                "frame_count": session.get("frame_count", 0)
            },
            trace_id=session_token
        )
        
        return {
            "success": True,
            "message": "Vision session stopped",
            "session": session
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop vision session: {str(e)}"
        )


@router.websocket("/vision/stream")
async def vision_stream(
    websocket: WebSocket,
    session_token: Optional[str] = None
):
    """
    WebSocket endpoint for streaming screen/camera frames
    
    Protocol:
    1. Client connects with session_token (from POST /api/vision/start)
    2. Client sends frames: {"type": "frame", "data": base64_image, "timestamp": ...}
    3. Server processes frames (OCR, object detection, etc.)
    4. Server sends analysis: {"type": "analysis", "text": "...", "objects": [...]}
    5. Client sends control: {"type": "pause"} or {"type": "resume"}
    
    Governance:
    - All frames logged to audit
    - Processing governed by Action Gateway
    - User can pause/resume at any time
    """
    
    await websocket.accept()
    
    try:
        # Verify session token
        if not session_token:
            await websocket.send_json({
                "type": "error",
                "message": "Missing session_token parameter"
            })
            await websocket.close(code=4001)
            return
        
        try:
            session = verify_session_token(session_token)
        except HTTPException as e:
            await websocket.send_json({
                "type": "error",
                "message": e.detail
            })
            await websocket.close(code=4001)
            return
        
        if session_token not in vision_sessions:
            await websocket.send_json({
                "type": "error",
                "message": "Vision session not found"
            })
            await websocket.close(code=4001)
            return
        
        vision_session = vision_sessions[session_token]
        user_id = vision_session["user_id"]
        
        # Store active connection
        active_vision_streams[session_token] = websocket
        
        # Send connection acknowledgment
        await websocket.send_json({
            "type": "connected",
            "session_token": session_token,
            "user_id": user_id,
            "message": "Vision stream connected. Send frames for analysis."
        })
        
        is_paused = False
        
        # Main message loop
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "frame":
                if not is_paused:
                    # Receive frame
                    frame_data = message.get("data")  # base64 encoded image
                    timestamp = message.get("timestamp", datetime.now().isoformat())
                    
                    vision_session["frame_count"] += 1
                    
                    # Process frame (placeholder - integrate with vision model)
                    analysis = await process_frame(
                        frame_data=frame_data,
                        session_token=session_token,
                        user_id=user_id
                    )
                    
                    # Send analysis back
                    if analysis:
                        await websocket.send_json({
                            "type": "analysis",
                            "timestamp": timestamp,
                            "frame_number": vision_session["frame_count"],
                            **analysis
                        })
                    
                    # Log frame to audit (governance requirement)
                    await publish_event_obj(
                        event_type=EventType.AGENT_ACTION,
                        source="vision_stream",
                        data={
                            "action": "frame_processed",
                            "session_token": session_token,
                            "user_id": user_id,
                            "frame_number": vision_session["frame_count"],
                            "analysis": analysis
                        },
                        trace_id=session_token
                    )
            
            elif msg_type == "pause":
                is_paused = True
                await websocket.send_json({
                    "type": "status",
                    "paused": True,
                    "message": "Vision stream paused"
                })
            
            elif msg_type == "resume":
                is_paused = False
                await websocket.send_json({
                    "type": "status",
                    "paused": False,
                    "message": "Vision stream resumed"
                })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
    
    except WebSocketDisconnect:
        if session_token in active_vision_streams:
            del active_vision_streams[session_token]
        
        await publish_event_obj(
            event_type=EventType.AGENT_ACTION,
            source="vision_stream",
            data={
                "action": "vision_stream_disconnected",
                "session_token": session_token
            },
            trace_id=session_token
        )
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Stream error: {str(e)}"
        })
        await websocket.close(code=1011)
        
        if session_token in active_vision_streams:
            del active_vision_streams[session_token]


async def process_frame(
    frame_data: str,
    session_token: str,
    user_id: str
) -> Optional[Dict[str, Any]]:
    """
    Process vision frame with OCR/object detection
    
    TODO: Integrate with:
    - GPT-4 Vision API for image analysis
    - Tesseract/EasyOCR for text extraction
    - YOLO/other models for object detection
    
    Args:
        frame_data: Base64-encoded image
        session_token: Vision session token
        user_id: User identifier
    
    Returns:
        Analysis results
    """
    # Placeholder - integrate with actual vision processing
    # In production, decode base64, send to vision model
    
    return {
        "text_detected": "[OCR would extract text here]",
        "objects": ["screen", "window", "code"],
        "confidence": 0.85,
        "message": "Frame analysis complete (mock)"
    }


@router.get("/vision/sessions")
async def list_vision_sessions(
    user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all vision sessions for current user"""
    user_sessions = [
        session for session in vision_sessions.values()
        if session["user_id"] == user["user_id"]
    ]
    
    return {
        "sessions": user_sessions,
        "total": len(user_sessions),
        "active_streams": len(active_vision_streams)
    }
