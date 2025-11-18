"""
Voice API - Voice control endpoints for Grace

Persistent voice sessions with start/stop/toggle
"""

from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.world_model.world_model_service import world_model_service
from backend.event_bus import event_bus, Event, EventType

router = APIRouter()

# In-memory voice session storage
voice_sessions: Dict[str, Dict[str, Any]] = {}


class VoiceStartRequest(BaseModel):
    """Request to start voice session"""
    user_id: str = Field(default="user", description="User identifier")
    language: str = Field(default="en-US", description="Language code")
    continuous: bool = Field(default=True, description="Continuous listening mode")


class VoiceSession(BaseModel):
    """Voice session response"""
    session_id: str
    user_id: str
    status: str
    language: str
    continuous: bool
    started_at: str
    stopped_at: Optional[str] = None


@router.post("/voice/start")
async def start_voice(request: VoiceStartRequest) -> Dict[str, Any]:
    """
    Start a persistent voice session
    
    Returns a session token that the frontend can reuse for each turn.
    Voice remains active until explicitly stopped or toggled off.
    """
    try:
        # Check if user already has an active session
        active_session = None
        for session_id, session in voice_sessions.items():
            if session["user_id"] == request.user_id and session["status"] == "active":
                active_session = session_id
                break
        
        if active_session:
            # Return existing session
            return {
                "success": True,
                "message": "Voice session already active",
                "session": voice_sessions[active_session]
            }
        
        # Create new session
        session_id = f"voice_{uuid4().hex[:12]}"
        
        session_data = {
            "session_id": session_id,
            "user_id": request.user_id,
            "status": "active",
            "language": request.language,
            "continuous": request.continuous,
            "started_at": datetime.now().isoformat(),
            "stopped_at": None,
            "message_count": 0
        }
        
        voice_sessions[session_id] = session_data
        
        # Enable voice in world model service
        await world_model_service.toggle_voice(request.user_id, True)
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="voice_api",
            data={
                "action": "voice_started",
                "session_id": session_id,
                "user_id": request.user_id,
                "language": request.language
            },
            trace_id=session_id
        ))
        
        return {
            "success": True,
            "message": "Voice session started",
            "session": session_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start voice session: {str(e)}"
        )


@router.post("/voice/stop")
async def stop_voice(
    session_id: Optional[str] = None,
    user_id: str = "user"
) -> Dict[str, Any]:
    """
    Stop a voice session
    
    Can stop by session_id or stop all sessions for a user_id.
    """
    try:
        stopped_sessions = []
        
        if session_id:
            # Stop specific session
            if session_id in voice_sessions:
                voice_sessions[session_id]["status"] = "stopped"
                voice_sessions[session_id]["stopped_at"] = datetime.now().isoformat()
                stopped_sessions.append(session_id)
        else:
            # Stop all active sessions for user
            for sid, session in voice_sessions.items():
                if session["user_id"] == user_id and session["status"] == "active":
                    session["status"] = "stopped"
                    session["stopped_at"] = datetime.now().isoformat()
                    stopped_sessions.append(sid)
        
        if not stopped_sessions:
            return {
                "success": False,
                "message": "No active voice sessions found"
            }
        
        # Disable voice in world model service
        await world_model_service.toggle_voice(user_id, False)
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.AGENT_ACTION,
            source="voice_api",
            data={
                "action": "voice_stopped",
                "session_ids": stopped_sessions,
                "user_id": user_id
            },
            trace_id=stopped_sessions[0] if stopped_sessions else "unknown"
        ))
        
        return {
            "success": True,
            "message": f"Stopped {len(stopped_sessions)} voice session(s)",
            "stopped_sessions": stopped_sessions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop voice session: {str(e)}"
        )


@router.post("/voice/toggle")
async def toggle_voice(user_id: str = "user") -> Dict[str, Any]:
    """
    Toggle voice on/off for a user
    
    If voice is active, stops it. If inactive, starts it.
    """
    try:
        # Check if user has active session
        active_session = None
        for session_id, session in voice_sessions.items():
            if session["user_id"] == user_id and session["status"] == "active":
                active_session = session_id
                break
        
        if active_session:
            # Stop voice
            result = await stop_voice(session_id=active_session, user_id=user_id)
            return {
                **result,
                "voice_enabled": False
            }
        else:
            # Start voice
            result = await start_voice(VoiceStartRequest(user_id=user_id))
            return {
                **result,
                "voice_enabled": True
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to toggle voice: {str(e)}"
        )


@router.get("/voice/status")
async def get_voice_status(user_id: str = "user") -> Dict[str, Any]:
    """
    Get voice session status for a user
    """
    try:
        # Find active sessions for user
        active_sessions = [
            session for session in voice_sessions.values()
            if session["user_id"] == user_id and session["status"] == "active"
        ]
        
        return {
            "success": True,
            "voice_enabled": len(active_sessions) > 0,
            "active_sessions": len(active_sessions),
            "sessions": active_sessions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get voice status: {str(e)}"
        )


@router.get("/voice/sessions")
async def list_voice_sessions(
    user_id: Optional[str] = None,
    include_stopped: bool = False
) -> Dict[str, Any]:
    """
    List all voice sessions
    
    Optionally filter by user_id and include stopped sessions.
    """
    try:
        sessions = list(voice_sessions.values())
        
        # Filter by user_id if provided
        if user_id:
            sessions = [s for s in sessions if s["user_id"] == user_id]
        
        # Filter out stopped sessions if requested
        if not include_stopped:
            sessions = [s for s in sessions if s["status"] == "active"]
        
        return {
            "success": True,
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list voice sessions: {str(e)}"
        )


@router.post("/voice/process")
async def process_voice_input(
    session_id: str,
    transcript: str,
    confidence: float = 1.0
) -> Dict[str, Any]:
    """
    Process voice input transcript
    
    Links to the voice session and forwards to chat endpoint.
    """
    try:
        if session_id not in voice_sessions:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        session = voice_sessions[session_id]
        
        if session["status"] != "active":
            raise HTTPException(status_code=400, detail="Voice session not active")
        
        # Increment message count
        session["message_count"] += 1
        session["last_input_at"] = datetime.now().isoformat()
        
        # Forward to chat API
        from backend.routes.chat_api import chat_with_grace, ChatMessage
        
        chat_msg = ChatMessage(
            message=transcript,
            user_id=session["user_id"],
            session_id=session_id
        )
        
        response = await chat_with_grace(chat_msg)
        
        # Add voice metadata
        return {
            "success": True,
            "voice_session_id": session_id,
            "transcript": transcript,
            "transcript_confidence": confidence,
            "chat_response": response.dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process voice input: {str(e)}"
        )
