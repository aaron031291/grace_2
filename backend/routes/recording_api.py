"""
Recording API
Screen sharing, video calls, and voice notes with consent management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.services.recording_service import recording_service


router = APIRouter(prefix="/api/recordings", tags=["recordings"])


class StartRecordingRequest(BaseModel):
    """Start recording session"""
    session_type: str
    title: str
    purpose: str
    participants: Optional[List[Dict]] = None
    consent_given: bool = False


class ConsentRequest(BaseModel):
    """Consent decision"""
    consent_given: bool
    consent_types: List[str]  # ["recording", "transcription", "learning"]


@router.post("/start")
async def start_recording(
    request: StartRecordingRequest,
    created_by: str = "ui_user"
) -> Dict[str, Any]:
    """
    Start new recording session
    
    SECURITY: Consent must be obtained before processing!
    """
    session_id = await recording_service.start_recording(
        session_type=request.session_type,
        title=request.title,
        purpose=request.purpose,
        created_by=created_by,
        participants=request.participants,
        consent_given=request.consent_given
    )
    
    # If no consent yet, request it
    if not request.consent_given:
        await recording_service.request_consent(
            session_id=session_id,
            user_id=created_by,
            consent_types=["recording", "transcription", "learning"],
            purpose=request.purpose
        )
    
    return {
        "session_id": session_id,
        "status": "started",
        "consent_required": not request.consent_given,
        "storage_ready": True
    }


@router.post("/{session_id}/upload")
async def upload_recording_file(
    session_id: str,
    file: UploadFile = File(...),
    uploaded_by: str = "ui_user"
) -> Dict[str, Any]:
    """
    Upload recording file (audio/video/screen capture)
    
    File is encrypted and stored in storage/recordings/<session_id>/
    """
    file_content = await file.read()
    
    success = await recording_service.upload_recording(
        session_id=session_id,
        file_content=file_content,
        filename=file.filename,
        uploaded_by=uploaded_by
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "filename": file.filename,
        "size_bytes": len(file_content),
        "status": "uploaded",
        "next_step": "consent_check"
    }


@router.post("/{session_id}/consent")
async def grant_consent(
    session_id: str,
    request: ConsentRequest,
    user_id: str = "ui_user"
) -> Dict[str, Any]:
    """
    Grant or deny consent for recording processing
    
    REQUIRED before transcription/ingestion/learning
    """
    success = await recording_service.grant_consent(
        session_id=session_id,
        user_id=user_id,
        consent_given=request.consent_given,
        consent_types=request.consent_types
    )
    
    next_action = "processing" if request.consent_given else "no_action"
    
    return {
        "session_id": session_id,
        "consent_granted": request.consent_given,
        "consent_types": request.consent_types,
        "next_action": next_action,
        "success": success
    }


@router.post("/{session_id}/transcribe")
async def transcribe_recording(
    session_id: str
) -> Dict[str, Any]:
    """
    Trigger transcription for recording
    
    Requires consent to have been granted
    """
    success = await recording_service.transcribe_recording(session_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Transcription failed or no consent")
    
    return {
        "session_id": session_id,
        "transcription_started": True,
        "status": "transcribing"
    }


@router.post("/{session_id}/ingest")
async def ingest_to_knowledge(
    session_id: str
) -> Dict[str, Any]:
    """
    Ingest transcript into knowledge base
    
    Requires transcription to be complete
    """
    artifact_ids = await recording_service.ingest_to_knowledge_base(session_id)
    
    return {
        "session_id": session_id,
        "artifacts_created": len(artifact_ids),
        "artifact_ids": artifact_ids,
        "status": "ingested"
    }


# Export router
__all__ = ['router']
