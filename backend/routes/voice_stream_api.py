"""
Voice Stream API - WebSocket endpoint for real-time voice streaming

Allows persistent voice connection with Grace where audio streams continuously
until the user mutes or disconnects.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from backend.auth.auth_service import verify_session_token, create_session_token
from backend.event_bus import event_bus, Event, EventType
from backend.routes.chat_api import chat_with_grace, ChatMessage

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/voice/stream")
async def voice_stream(
    websocket: WebSocket,
    session_token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time voice streaming
    
    Protocol:
    1. Client connects with session_token (from POST /api/voice/start)
    2. Client sends audio chunks: {"type": "audio", "data": base64_audio}
    3. Server sends transcripts: {"type": "transcript", "text": "...", "final": bool}
    4. Client sends control: {"type": "mute"} or {"type": "unmute"}
    5. Server sends responses: {"type": "response", "message": {...}}
    
    Auth:
    - Requires session_token from POST /api/voice/start
    - Token verified on connect
    - Session logged in audit trail
    """
    
    # Accept connection first
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
        
        user_id = session.get("user_id", "unknown")
        
        # Store active connection
        active_connections[session_token] = websocket
        
        # Log session start
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="voice_stream_api",
            data={
                "action": "voice_stream_connected",
                "session_token": session_token,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            },
            trace_id=session_token
        ))
        
        # Send connection acknowledgment
        await websocket.send_json({
            "type": "connected",
            "session_token": session_token,
            "user_id": user_id,
            "message": "Voice stream connected. Send audio chunks or control messages."
        })
        
        # State
        is_muted = False
        audio_buffer = []
        
        # Main message loop
        while True:
            # Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "audio":
                # Receive audio chunk
                if not is_muted:
                    audio_data = message.get("data")  # base64 encoded audio
                    audio_buffer.append(audio_data)
                    
                    # Optionally: Send to transcription service (Whisper API)
                    # For now, simulate transcript
                    if len(audio_buffer) >= 10:  # Process every 10 chunks
                        transcript = await process_audio_buffer(audio_buffer, user_id)
                        audio_buffer = []
                        
                        if transcript:
                            # Send transcript to client
                            await websocket.send_json({
                                "type": "transcript",
                                "text": transcript,
                                "final": True,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Forward transcript to chat endpoint
                            try:
                                chat_msg = ChatMessage(
                                    message=transcript,
                                    user_id=user_id,
                                    session_id=session_token
                                )
                                response = await chat_with_grace(chat_msg)
                                
                                # Send Grace's response back over WebSocket
                                await websocket.send_json({
                                    "type": "response",
                                    "message": response.dict(),
                                    "timestamp": datetime.now().isoformat()
                                })
                            except Exception as e:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"Chat processing failed: {str(e)}"
                                })
            
            elif msg_type == "mute":
                is_muted = True
                await websocket.send_json({
                    "type": "status",
                    "muted": True,
                    "message": "Voice input muted"
                })
                
                # Log mute event
                await event_bus.publish(Event(
                    event_type=EventType.AGENT_ACTION,
                    source="voice_stream_api",
                    data={
                        "action": "voice_muted",
                        "session_token": session_token,
                        "user_id": user_id
                    },
                    trace_id=session_token
                ))
            
            elif msg_type == "unmute":
                is_muted = False
                await websocket.send_json({
                    "type": "status",
                    "muted": False,
                    "message": "Voice input unmuted"
                })
                
                # Log unmute event
                await event_bus.publish(Event(
                    event_type=EventType.AGENT_ACTION,
                    source="voice_stream_api",
                    data={
                        "action": "voice_unmuted",
                        "session_token": session_token,
                        "user_id": user_id
                    },
                    trace_id=session_token
                ))
            
            elif msg_type == "ping":
                # Keepalive
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })
    
    except WebSocketDisconnect:
        # Client disconnected
        if session_token in active_connections:
            del active_connections[session_token]
        
        # Log disconnect
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="voice_stream_api",
            data={
                "action": "voice_stream_disconnected",
                "session_token": session_token,
                "timestamp": datetime.now().isoformat()
            },
            trace_id=session_token
        ))
    
    except Exception as e:
        # Error occurred
        await websocket.send_json({
            "type": "error",
            "message": f"Stream error: {str(e)}"
        })
        await websocket.close(code=1011)
        
        if session_token in active_connections:
            del active_connections[session_token]


async def process_audio_buffer(audio_buffer: list, user_id: str) -> Optional[str]:
    """
    Process audio buffer and return transcript
    
    TODO: Integrate with Whisper API or other transcription service
    
    Args:
        audio_buffer: List of base64-encoded audio chunks
        user_id: User identifier
    
    Returns:
        Transcript text or None
    """
    # Placeholder: In production, send to Whisper API
    # For now, simulate transcription
    await asyncio.sleep(0.1)  # Simulate processing
    
    # Mock transcript (replace with actual Whisper API call)
    if len(audio_buffer) > 0:
        return f"[Mock transcript from {len(audio_buffer)} audio chunks]"
    
    return None


@router.get("/voice/stream/status")
async def get_stream_status() -> Dict[str, Any]:
    """
    Get status of active voice streams
    
    Returns count and list of active connections.
    """
    return {
        "active_streams": len(active_connections),
        "sessions": list(active_connections.keys())
    }
