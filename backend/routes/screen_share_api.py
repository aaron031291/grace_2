"""
Screen Share API - WebRTC signaling and screen capture

Endpoints:
- Start/stop screen sharing
- Toggle learning/observation modes
- Get stream link
- Screen capture events
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.event_bus import event_bus, Event, EventType
from backend.memory.memory_catalog import AssetSource, AssetType
from backend.learning.memory_ingestion_hook import memory_ingestion_hook
from backend.core.unified_event_publisher import publish_event_obj

router = APIRouter()

# Active screen share sessions
active_sessions: Dict[str, Dict[str, Any]] = {}


class ScreenShareSession(BaseModel):
    """Screen share session info"""
    session_id: str
    user_id: str
    status: str
    stream_url: Optional[str] = None
    learning_enabled: bool = False
    observe_enabled: bool = True
    started_at: str
    frames_captured: int = 0


class StartScreenShareRequest(BaseModel):
    """Start screen share request"""
    user_id: str = "user"
    learning_enabled: bool = False
    observe_enabled: bool = True


@router.post("/screen_share/start")
async def start_screen_share(req: StartScreenShareRequest) -> Dict[str, Any]:
    """
    Start screen sharing session
    
    Returns:
        - session_id: Unique session identifier
        - stream_url: WebRTC stream URL or signaling endpoint
        - status: Session status
    """
    session_id = f"screen_{uuid4().hex[:12]}"
    
    # Create WebRTC signaling endpoint
    stream_url = f"/api/screen_share/stream/{session_id}"
    
    session = {
        "session_id": session_id,
        "user_id": req.user_id,
        "status": "active",
        "stream_url": stream_url,
        "learning_enabled": req.learning_enabled,
        "observe_enabled": req.observe_enabled,
        "started_at": datetime.utcnow().isoformat(),
        "frames_captured": 0,
    }
    
    active_sessions[session_id] = session
    
    # Publish event
    await publish_event_obj(Event(
        event_type=EventType.AGENT_ACTION,
        source="screen_share_api",
        data={
            "action": "screen_share_started",
            "session_id": session_id,
            "user_id": req.user_id,
            "learning_enabled": req.learning_enabled,
        }
    ))
    
    return {
        "success": True,
        "session_id": session_id,
        "stream_url": stream_url,
        "status": "active",
        "message": "Screen sharing started"
    }


@router.post("/screen_share/stop/{session_id}")
async def stop_screen_share(session_id: str) -> Dict[str, Any]:
    """
    Stop screen sharing session
    
    Args:
        session_id: Session to stop
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    session["status"] = "stopped"
    session["stopped_at"] = datetime.utcnow().isoformat()
    
    # Publish event
    await publish_event_obj(Event(
        event_type=EventType.AGENT_ACTION,
        source="screen_share_api",
        data={
            "action": "screen_share_stopped",
            "session_id": session_id,
            "frames_captured": session["frames_captured"],
        }
    ))
    
    # Remove from active sessions
    del active_sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "status": "stopped",
        "frames_captured": session["frames_captured"],
        "message": "Screen sharing stopped"
    }


@router.post("/screen_share/{session_id}/toggle_learning")
async def toggle_learning(session_id: str, enabled: bool) -> Dict[str, Any]:
    """Toggle learning mode for screen share session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    active_sessions[session_id]["learning_enabled"] = enabled
    
    return {
        "success": True,
        "session_id": session_id,
        "learning_enabled": enabled,
        "message": f"Learning {'enabled' if enabled else 'disabled'}"
    }


@router.post("/screen_share/{session_id}/toggle_observe")
async def toggle_observe(session_id: str, enabled: bool) -> Dict[str, Any]:
    """Toggle observation mode for screen share session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    active_sessions[session_id]["observe_enabled"] = enabled
    
    return {
        "success": True,
        "session_id": session_id,
        "observe_enabled": enabled,
        "message": f"Observation {'enabled' if enabled else 'disabled'}"
    }


@router.post("/screen_share/{session_id}/capture")
async def capture_frame(
    session_id: str,
    image_data: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Capture and process screen frame
    
    Args:
        session_id: Screen share session
        image_data: Base64 encoded image or image path
        metadata: Frame metadata (window title, timestamp, etc.)
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    session["frames_captured"] += 1
    
    # Save frame if learning enabled
    if session["learning_enabled"]:
        from pathlib import Path
        import base64
        
        # Save to storage
        frame_path = Path(f"storage/memory/raw/screen_share/frame_{session_id}_{session['frames_captured']}.png")
        frame_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Decode and save (simplified - real impl would handle base64)
        # with open(frame_path, "wb") as f:
        #     f.write(base64.b64decode(image_data))
        
        # Ingest into memory catalog
        frame_metadata = metadata or {}
        frame_metadata.update({
            "session_id": session_id,
            "frame_number": session["frames_captured"],
            "window_title": frame_metadata.get("window_title", "Unknown"),
        })
        
        # Trigger ingestion
        await publish_event_obj(Event(
            event_type=EventType.MEMORY_UPDATE,
            source="screen_share_api",
            data={
                "action": "screen_share_captured",
                "image_path": str(frame_path),
                "metadata": frame_metadata,
            }
        ))
    
    return {
        "success": True,
        "session_id": session_id,
        "frame_number": session["frames_captured"],
        "learned": session["learning_enabled"]
    }


@router.get("/screen_share/sessions")
async def list_sessions() -> Dict[str, Any]:
    """List all active screen share sessions"""
    return {
        "sessions": [
            ScreenShareSession(**session).dict()
            for session in active_sessions.values()
        ],
        "total": len(active_sessions)
    }


@router.get("/screen_share/{session_id}")
async def get_session(session_id: str) -> ScreenShareSession:
    """Get screen share session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return ScreenShareSession(**active_sessions[session_id])
