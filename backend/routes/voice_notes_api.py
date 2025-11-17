"""
Voice Notes API - Simplified Interface for Voice Note Pipeline

Provides user-friendly endpoints for:
- Recording voice notes
- Granting consent
- Searching notes
- Viewing transcripts
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.services.voice_notes_pipeline import voice_notes_pipeline


router = APIRouter(prefix="/api/voice-notes", tags=["voice_notes"])


class StartVoiceNoteRequest(BaseModel):
    """Request to start voice note"""
    title: str
    user_id: str
    purpose: str = "learning"


class GrantConsentRequest(BaseModel):
    """Grant consent for voice note processing"""
    session_id: str
    user_id: str


@router.post("/start")
async def start_voice_note(request: StartVoiceNoteRequest):
    """
    Start new voice note recording
    
    Returns session_id for upload
    """
    try:
        session_id = await voice_notes_pipeline.start_voice_note(
            title=request.title,
            user_id=request.user_id,
            purpose=request.purpose
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "next_step": "upload_audio"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/upload")
async def upload_voice_note(
    session_id: str,
    user_id: str,
    file: UploadFile = File(...)
):
    """
    Upload audio file for voice note
    
    Accepts: .mp3, .wav, .m4a, .ogg
    """
    try:
        # Read file
        audio_bytes = await file.read()
        
        # Upload
        success = await voice_notes_pipeline.upload_audio(
            session_id=session_id,
            audio_bytes=audio_bytes,
            filename=file.filename or "voice_note.mp3",
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Upload failed")
        
        # Request consent
        consent_id = await voice_notes_pipeline.request_consent(
            session_id=session_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "consent_id": consent_id,
            "next_step": "approve_consent",
            "message": "Audio uploaded. Please approve consent to process."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/consent")
async def grant_consent(request: GrantConsentRequest):
    """
    Grant consent for voice note processing
    
    Triggers automatic: transcribe → embed → ingest → learn
    """
    try:
        # Grant consent
        success = await recording_service.grant_consent(
            session_id=request.session_id,
            user_id=request.user_id,
            consent_given=True,
            consent_types=["recording", "transcription", "learning"]
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Consent grant failed")
        
        # Trigger processing
        processing_result = await voice_notes_pipeline.process_voice_note(
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "session_id": request.session_id,
            "processing": processing_result,
            "message": "Consent granted. Processing voice note..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/status")
async def get_voice_note_status(session_id: str):
    """
    Get processing status of voice note
    
    Returns current step and completion status
    """
    status = await voice_notes_pipeline.get_pipeline_status(session_id)
    return status


@router.get("/{session_id}/transcript")
async def get_voice_note_transcript(session_id: str, user_id: str):
    """
    Get transcript text for voice note
    
    Returns full transcript
    """
    transcript = await voice_notes_pipeline.get_voice_note_transcript(
        session_id=session_id,
        user_id=user_id
    )
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found or not ready")
    
    return {
        "session_id": session_id,
        "transcript": transcript,
        "length": len(transcript)
    }


@router.post("/search")
async def search_voice_notes(
    query: str,
    user_id: str,
    top_k: int = 10
):
    """
    Search across all voice notes
    
    Semantic search through transcripts
    """
    try:
        results = await voice_notes_pipeline.search_voice_notes(
            query=query,
            user_id=user_id,
            top_k=top_k
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_voice_notes(user_id: str, limit: int = 50):
    """
    List user's voice notes
    
    Returns recent voice notes with status
    """
    from backend.models.recording_models import RecordingSession
    from backend.models.base_models import async_session
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(RecordingSession)
            .where(RecordingSession.created_by == user_id)
            .where(RecordingSession.session_type == RecordingType.VOICE_NOTE)
            .order_by(RecordingSession.created_at.desc())
            .limit(limit)
        )
        recordings = result.scalars().all()
    
    return {
        "total": len(recordings),
        "voice_notes": [
            {
                "session_id": r.session_id,
                "title": r.title,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "duration_seconds": r.duration_seconds,
                "status": r.status,
                "consent_given": r.consent_given,
                "transcript_length": len(r.transcript_text or ""),
                "searchable": r.ingestion_status == "completed"
            }
            for r in recordings
        ]
    }


@router.get("/health")
async def voice_notes_health():
    """Voice notes pipeline health check"""
    return {
        "status": "operational",
        "pipeline": "voice_notes",
        "features": [
            "consent_required",
            "whisper_transcription",
            "vector_embedding",
            "semantic_search",
            "learning_integration"
        ]
    }
