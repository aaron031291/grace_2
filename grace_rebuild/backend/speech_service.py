"""Speech-to-text and text-to-speech service"""

import asyncio
import hashlib
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import aiofiles

from sqlalchemy import select, update
from .models import async_session
from .speech_models import SpeechMessage, TextToSpeechMessage, SpeechSession, AudioQuality
from .verification import VerificationEngine
from .governance import GovernanceEngine
from .hunter import HunterEngine
from .immutable_log import ImmutableLogger

class SpeechService:
    """Manages speech-to-text transcription and audio storage"""
    
    def __init__(self):
        self.audio_storage_path = Path("./audio_messages")
        self.audio_storage_path.mkdir(exist_ok=True)
        
        self.verification = VerificationEngine()
        self.governance = GovernanceEngine()
        self.hunter = HunterEngine()
        self.audit = ImmutableLogger()
        
        self.whisper_model = None  # Lazy load
    
    async def upload_audio(
        self,
        user: str,
        audio_data: bytes,
        audio_format: str = "webm",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload audio file, store it, and queue for transcription
        
        Returns:
            {
                "speech_id": int,
                "audio_path": str,
                "status": str,
                "verification_id": str
            }
        """
        
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        filename = f"{user}_{audio_id}.{audio_format}"
        audio_path = self.audio_storage_path / filename
        
        # Calculate hash for verification
        audio_hash = hashlib.sha256(audio_data).hexdigest()
        
        # Save audio file
        async with aiofiles.open(audio_path, 'wb') as f:
            await f.write(audio_data)
        
        audio_size = len(audio_data)
        
        # Create verification envelope
        verification_id = self.verification.create_envelope(
            action_id=audio_id,
            actor=user,
            action_type="audio_upload",
            resource=str(audio_path),
            input_data={"audio_hash": audio_hash, "size": audio_size}
        )
        
        # Create speech message record
        async with async_session() as session:
            speech_msg = SpeechMessage(
                user=user,
                session_id=session_id or audio_id,
                audio_path=str(audio_path),
                audio_format=audio_format,
                audio_size_bytes=audio_size,
                audio_hash=audio_hash,
                status="uploaded",
                verification_envelope_id=verification_id
            )
            session.add(speech_msg)
            await session.commit()
            await session.refresh(speech_msg)
            
            speech_id = speech_msg.id
        
        # Log to audit trail
        audit_id = await self.audit.log_event(
            actor=user,
            action="audio_upload",
            resource=f"speech_message_{speech_id}",
            result="uploaded",
            details={"audio_hash": audio_hash, "size": audio_size}
        )
        
        # Update with audit log ID
        async with async_session() as session:
            await session.execute(
                update(SpeechMessage)
                .where(SpeechMessage.id == speech_id)
                .values(audit_log_id=audit_id)
            )
            await session.commit()
        
        # Queue for transcription (async task)
        asyncio.create_task(self._transcribe_audio(speech_id))
        
        return {
            "speech_id": speech_id,
            "audio_path": str(audio_path),
            "status": "uploaded",
            "verification_id": verification_id,
            "queued_for_transcription": True
        }
    
    async def _transcribe_audio(self, speech_id: int):
        """
        Background task to transcribe audio using Whisper
        """
        try:
            # Update status to transcribing
            async with async_session() as session:
                await session.execute(
                    update(SpeechMessage)
                    .where(SpeechMessage.id == speech_id)
                    .values(status="transcribing")
                )
                await session.commit()
            
            # Get speech message
            async with async_session() as session:
                result = await session.execute(
                    select(SpeechMessage).where(SpeechMessage.id == speech_id)
                )
                speech_msg = result.scalar_one_or_none()
                
                if not speech_msg:
                    return
                
                audio_path = speech_msg.audio_path
                user = speech_msg.user
            
            # Load Whisper model (lazy loading)
            if self.whisper_model is None:
                try:
                    import whisper
                    self.whisper_model = whisper.load_model("base")
                    print("✓ Whisper model loaded: base")
                except ImportError:
                    # Fallback: use mock transcription for testing
                    print("⚠ Whisper not installed, using mock transcription")
                    transcript = "[Mock transcription - install openai-whisper]"
                    confidence = 0.5
                    language = "en"
                    
                    await self._save_transcription(
                        speech_id, transcript, confidence, language,
                        "mock", "base"
                    )
                    return
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_path)
            
            transcript = result["text"].strip()
            language = result["language"]
            
            # Calculate average confidence from segments
            segments = result.get("segments", [])
            if segments:
                confidences = [
                    seg.get("no_speech_prob", 0.5) 
                    for seg in segments
                ]
                confidence = 1.0 - (sum(confidences) / len(confidences))
            else:
                confidence = 0.8
            
            # Save transcription
            await self._save_transcription(
                speech_id, transcript, confidence, language,
                "whisper", "base"
            )
            
            # Run governance and security checks
            await self._check_transcript_security(speech_id, transcript, user)
            
        except Exception as e:
            # Update status to failed
            async with async_session() as session:
                await session.execute(
                    update(SpeechMessage)
                    .where(SpeechMessage.id == speech_id)
                    .values(
                        status="failed",
                        error_message=str(e)
                    )
                )
                await session.commit()
            
            print(f"✗ Transcription failed for speech {speech_id}: {e}")
    
    async def _save_transcription(
        self,
        speech_id: int,
        transcript: str,
        confidence: float,
        language: str,
        service: str,
        model: str
    ):
        """Save transcription result"""
        
        async with async_session() as session:
            await session.execute(
                update(SpeechMessage)
                .where(SpeechMessage.id == speech_id)
                .values(
                    transcript=transcript,
                    confidence=confidence,
                    language=language,
                    transcription_service=service,
                    transcription_model=model,
                    status="completed",
                    transcribed_at=datetime.utcnow()
                )
            )
            await session.commit()
        
        print(f"✓ Transcription completed for speech {speech_id}: {transcript[:50]}...")
    
    async def _check_transcript_security(
        self,
        speech_id: int,
        transcript: str,
        user: str
    ):
        """
        Run Hunter security checks on transcript
        Flag sensitive content, trigger governance if needed
        """
        
        # Run Hunter scan on transcript
        hunter_result = await self.hunter.scan_content(
            content=transcript,
            content_type="speech_transcript",
            actor=user
        )
        
        needs_review = False
        review_status = None
        
        if hunter_result["alerts"]:
            # Check severity
            critical_alerts = [
                a for a in hunter_result["alerts"]
                if a["severity"] == "critical"
            ]
            
            if critical_alerts:
                # Auto-quarantine critical issues
                needs_review = True
                review_status = "quarantined"
                
                # Create governance approval request
                await self.governance.create_approval_request(
                    event_type="speech_quarantine",
                    resource=f"speech_message_{speech_id}",
                    requested_by=user,
                    reason=f"Critical security alert: {critical_alerts[0]['rule_name']}"
                )
            else:
                # Flag for review
                needs_review = True
                review_status = "pending"
        
        # Check confidence threshold
        async with async_session() as session:
            result = await session.execute(
                select(SpeechMessage).where(SpeechMessage.id == speech_id)
            )
            speech_msg = result.scalar_one()
            
            if speech_msg.confidence < 0.7:
                needs_review = True
                if not review_status:
                    review_status = "low_confidence"
        
        # Update review status
        if needs_review:
            async with async_session() as session:
                await session.execute(
                    update(SpeechMessage)
                    .where(SpeechMessage.id == speech_id)
                    .values(
                        needs_review=True,
                        review_status=review_status
                    )
                )
                await session.commit()
    
    async def get_speech_message(self, speech_id: int) -> Optional[Dict[str, Any]]:
        """Get speech message by ID"""
        
        async with async_session() as session:
            result = await session.execute(
                select(SpeechMessage).where(SpeechMessage.id == speech_id)
            )
            speech_msg = result.scalar_one_or_none()
            
            if not speech_msg:
                return None
            
            return {
                "id": speech_msg.id,
                "user": speech_msg.user,
                "session_id": speech_msg.session_id,
                "audio_path": speech_msg.audio_path,
                "audio_format": speech_msg.audio_format,
                "audio_size_bytes": speech_msg.audio_size_bytes,
                "transcript": speech_msg.transcript,
                "confidence": speech_msg.confidence,
                "language": speech_msg.language,
                "status": speech_msg.status,
                "needs_review": speech_msg.needs_review,
                "review_status": speech_msg.review_status,
                "created_at": speech_msg.created_at.isoformat() if speech_msg.created_at else None,
                "transcribed_at": speech_msg.transcribed_at.isoformat() if speech_msg.transcribed_at else None
            }
    
    async def list_speech_messages(
        self,
        user: str,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """List speech messages for user"""
        
        async with async_session() as session:
            query = select(SpeechMessage).where(SpeechMessage.user == user)
            
            if session_id:
                query = query.where(SpeechMessage.session_id == session_id)
            
            query = query.order_by(SpeechMessage.created_at.desc()).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            return [
                {
                    "id": msg.id,
                    "session_id": msg.session_id,
                    "transcript": msg.transcript,
                    "confidence": msg.confidence,
                    "status": msg.status,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in messages
            ]
    
    async def review_transcript(
        self,
        speech_id: int,
        approved: bool,
        reviewed_by: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Review and approve/reject transcript
        """
        
        async with async_session() as session:
            result = await session.execute(
                select(SpeechMessage).where(SpeechMessage.id == speech_id)
            )
            speech_msg = result.scalar_one_or_none()
            
            if not speech_msg:
                return None
            
            review_status = "approved" if approved else "rejected"
            
            await session.execute(
                update(SpeechMessage)
                .where(SpeechMessage.id == speech_id)
                .values(
                    needs_review=False,
                    review_status=review_status,
                    reviewed_by=reviewed_by,
                    reviewed_at=datetime.utcnow()
                )
            )
            await session.commit()
        
        # Log review action
        await self.audit.log_event(
            actor=reviewed_by,
            action="speech_review",
            resource=f"speech_message_{speech_id}",
            result=review_status,
            details={"notes": notes} if notes else {}
        )
        
        return {
            "speech_id": speech_id,
            "review_status": review_status,
            "reviewed_by": reviewed_by
        }
    
    async def delete_speech_message(
        self,
        speech_id: int,
        user: str
    ) -> bool:
        """
        Delete speech message and audio file
        """
        
        async with async_session() as session:
            result = await session.execute(
                select(SpeechMessage).where(SpeechMessage.id == speech_id)
            )
            speech_msg = result.scalar_one_or_none()
            
            if not speech_msg:
                return False
            
            # Delete audio file if exists
            audio_path = Path(speech_msg.audio_path)
            if audio_path.exists():
                audio_path.unlink()
            
            # Delete database record
            await session.delete(speech_msg)
            await session.commit()
        
        # Log deletion
        await self.audit.log_event(
            actor=user,
            action="speech_deletion",
            resource=f"speech_message_{speech_id}",
            result="deleted",
            details={}
        )
        
        return True

speech_service = SpeechService()
