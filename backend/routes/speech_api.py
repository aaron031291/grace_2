"""Speech and audio API endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

from ..speech_service import speech_service
from ..tts_service import tts_service
from ..auth import get_current_user
from ..governance import governance_engine
from ..hunter import hunter_engine
from ..websocket_manager import websocket_manager
=======
from ..schemas_extended import (
    SpeechUploadResponse,
    SpeechMessageResponse,
    SpeechListResponse,
    SpeechReviewResponse,
    SpeechDeleteResponse,
    TTSGenerateResponse
)

>>>>>>> origin/main

router = APIRouter(prefix="/api/audio", tags=["speech"])

class ReviewRequest(BaseModel):
    approved: bool
    notes: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    voice_model: Optional[str] = "default"
    speed: float = 1.0
    pitch: float = 1.0
    reply_to_speech_id: Optional[int] = None
    reply_to_chat_id: Optional[int] = None

<<<<<<< HEAD
@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
    current_user: str = None
):
    """
    Upload audio file for transcription
    
    Accepts: multipart/form-data with audio file
    Returns: speech_id, status, verification_id
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate file type
    allowed_formats = ["audio/webm", "audio/wav", "audio/mp3", "audio/ogg", "audio/m4a"]
    if file.content_type not in allowed_formats:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid audio format. Allowed: {allowed_formats}"
        )
    
    # Read audio data
    audio_data = await file.read()
    
    # Check file size (max 50MB)
    if len(audio_data) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file too large (max 50MB)")
    
    # Determine format from content type
    format_map = {
        "audio/webm": "webm",
        "audio/wav": "wav",
        "audio/mp3": "mp3",
        "audio/ogg": "ogg",
        "audio/m4a": "m4a"
    }
    audio_format = format_map.get(file.content_type, "webm")
    
    # Upload and process
    result = await speech_service.upload_audio(
        user=current_user,
        audio_data=audio_data,
        audio_format=audio_format,
        session_id=session_id
    )
    
    return result

@router.get("/{speech_id}")
async def get_speech_message(speech_id: int, current_user: str = None):
    """
    Get speech message details including transcript
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    if not speech_msg:
        raise HTTPException(status_code=404, detail="Speech message not found")
    
    # Check authorization
    if speech_msg["user"] != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return speech_msg

@router.get("/{speech_id}/file")
async def get_audio_file(speech_id: int, current_user: str = None):
    """
    Stream audio file for playback
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    if not speech_msg:
        raise HTTPException(status_code=404, detail="Speech message not found")
    
    # Check authorization
    if speech_msg["user"] != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if file exists
    audio_path = Path(speech_msg["audio_path"])
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Determine media type
    format_to_media = {
        "webm": "audio/webm",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "m4a": "audio/mp4"
    }
    media_type = format_to_media.get(speech_msg["audio_format"], "audio/webm")
    
    # Stream file
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=f"speech_{speech_id}.{speech_msg['audio_format']}"
    )

@router.get("/list")
async def list_speech_messages(
    session_id: Optional[str] = None,
    limit: int = 50,
    current_user: str = None
):
    """
    List user's speech messages
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    messages = await speech_service.list_speech_messages(
        user=current_user,
        session_id=session_id,
        limit=limit
    )
    
    return {"messages": messages}

@router.post("/{speech_id}/review")
async def review_transcript(
    speech_id: int,
    review: ReviewRequest,
    current_user: str = None
):
    """
    Approve or reject speech transcript
    Updates review status and triggers governance if needed
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await speech_service.review_transcript(
        speech_id=speech_id,
        approved=review.approved,
        reviewed_by=current_user,
        notes=review.notes
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Speech message not found")
    
    return result

@router.delete("/{speech_id}")
async def delete_speech_message(speech_id: int, current_user: str = None):
    """
    Delete speech message with governance approval
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    speech_msg = await speech_service.get_speech_message(speech_id)
    
    if not speech_msg:
        raise HTTPException(status_code=404, detail="Speech message not found")
    
    # Check authorization
    if speech_msg["user"] != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create governance approval request for deletion
    approval_result = await governance_engine.create_approval_request(
        event_type="speech_deletion",
        resource=f"speech_message_{speech_id}",
        requested_by=current_user,
        reason="User requested deletion"
    )
    
    # Execute deletion
    result = await speech_service.delete_speech_message(speech_id, current_user)
    
    return {
        "deleted": True,
        "speech_id": speech_id,
        "approval_id": approval_result.get("approval_id")
    }

@router.post("/tts/generate")
async def generate_tts(request: TTSRequest, current_user: str = None):
    """
    Generate text-to-speech audio from text
    
    Returns: tts_id, audio_path, status
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate text length (max 5000 chars)
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    # Generate TTS
    result = await tts_service.generate_speech(
        user=current_user,
        text=request.text,
        voice_model=request.voice_model,
        speed=request.speed,
        pitch=request.pitch,
        reply_to_speech_id=request.reply_to_speech_id,
        reply_to_chat_id=request.reply_to_chat_id
    )
    
    return result

@router.get("/tts/{tts_id}/file")
async def get_tts_file(tts_id: int, current_user: str = None):
    """
    Get TTS audio file for playback
    """
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    tts_msg = await tts_service.get_tts_message(tts_id)
    
    if not tts_msg:
        raise HTTPException(status_code=404, detail="TTS message not found")
    
    # Check authorization
    if tts_msg["user"] != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if file exists
    audio_path = Path(tts_msg["audio_path"])
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    # Stream file
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=f"tts_{tts_id}.mp3"
    )

@router.websocket("/ws")
async def websocket_audio_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time audio streaming and transcription updates
    
    Client sends: {"type": "audio_chunk", "data": base64_audio, "format": "webm"}
    Server sends: {"type": "transcript_update", "speech_id": 123, "transcript": "...", "confidence": 0.95}
    """
    
    await websocket.accept()
    
    # Get user from token (if provided in query params)
    user = websocket.query_params.get("user", "anonymous")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "audio_chunk":
                # Handle streaming audio chunk
                import base64
                audio_data = base64.b64decode(data.get("data", ""))
                audio_format = data.get("format", "webm")
                
                # For streaming, we could buffer chunks or process incrementally
                # For now, send acknowledgment
                await websocket.send_json({
                    "type": "ack",
                    "received_bytes": len(audio_data)
                })
            
            elif msg_type == "finalize_audio":
                # Client signals end of audio stream
                # Process accumulated audio
                await websocket.send_json({
                    "type": "processing",
                    "status": "transcribing"
                })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
