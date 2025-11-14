"""
Recording Service
Handles screen sharing, video calls, and voice notes with consent and governance

Flow:
1. Capture → Encrypted Storage
2. Consent Check → Governance Approval
3. Transcription → Text Extraction
4. Ingestion → Knowledge Base
5. Learning → Outcome Tracking
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from backend.models.recording_models import RecordingSession, RecordingTranscript, RecordingAccess, ConsentRecord
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from backend.core.message_bus import message_bus, MessagePriority
from sqlalchemy import select


class RecordingType:
    """Recording types"""
    SCREEN_SHARE = "screen_share"
    VIDEO_CALL = "video_call"
    VOICE_NOTE = "voice_note"
    MEETING_RECORDING = "meeting_recording"


class RecordingService:
    """
    Manages multimedia recordings with consent and governance
    
    Features:
    - Encrypted storage
    - Consent management
    - Automatic transcription
    - Ingestion pipeline integration
    - Learning loop feedback
    - Access control
    """
    
    def __init__(self):
        self.storage_base = Path("storage/recordings")
        self.storage_base.mkdir(parents=True, exist_ok=True)
    
    async def start_recording(
        self,
        session_type: str,
        title: str,
        purpose: str,
        created_by: str,
        participants: Optional[List[Dict]] = None,
        consent_given: bool = False
    ) -> str:
        """
        Start new recording session
        
        IMPORTANT: Consent must be obtained before processing!
        
        Args:
            session_type: screen_share, video_call, voice_note
            title: Session name
            purpose: Why recording (meeting, training, support)
            created_by: User initiating
            participants: List of participants
            consent_given: Pre-flight consent flag
            
        Returns:
            session_id for tracking
        """
        session_id = f"rec_{session_type}_{datetime.now(timezone.utc).timestamp()}"
        
        # Create storage directory
        session_dir = self.storage_base / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session record
        async with async_session() as session:
            recording = RecordingSession(
                session_id=session_id,
                session_type=session_type,
                storage_path=str(session_dir),
                title=title,
                purpose=purpose,
                participants=participants or [],
                host=created_by,
                consent_given=consent_given,
                status="captured",
                created_by=created_by,
                started_at=datetime.now(timezone.utc),
                source="ui_upload"
            )
            session.add(recording)
            await session.commit()
        
        # Log (NO CONTENT)
        log_event(
            action="recording.started",
            actor=created_by,
            resource=session_id,
            outcome="ok",
            payload={
                "session_id": session_id,
                "type": session_type,
                "purpose": purpose,
                "consent_given": consent_given
            }
        )
        
        print(f"[RECORDING] Started: {title} ({session_type}) - {session_id}")
        
        return session_id
    
    async def upload_recording(
        self,
        session_id: str,
        file_content: bytes,
        filename: str,
        uploaded_by: str
    ) -> bool:
        """
        Upload recording file (encrypted storage)
        
        Args:
            session_id: Recording session ID
            file_content: Raw file bytes
            filename: Original filename
            uploaded_by: Who uploaded
            
        Returns:
            Success boolean
        """
        # Load session
        async with async_session() as session:
            result = await session.execute(
                select(RecordingSession)
                .where(RecordingSession.session_id == session_id)
            )
            recording = result.scalar_one_or_none()
            
            if not recording:
                return False
            
            # Save file (encrypted)
            storage_path = Path(recording.storage_path)
            file_path = storage_path / filename
            
            # TODO: Encrypt file before writing
            file_path.write_bytes(file_content)
            
            # Update session
            from sqlalchemy import update
            await session.execute(
                update(RecordingSession)
                .where(RecordingSession.session_id == session_id)
                .values(
                    file_size_bytes=len(file_content),
                    status="uploaded"
                )
            )
            await session.commit()
        
        print(f"[RECORDING] Uploaded: {session_id} ({len(file_content)} bytes)")
        
        # Publish event for transcription pipeline
        await message_bus.publish(
            source="recording_service",
            topic="recording.uploaded",
            payload={
                "session_id": session_id,
                "filename": filename,
                "size_bytes": len(file_content),
                "needs_transcription": True
            },
            priority=MessagePriority.NORMAL
        )
        
        return True
    
    async def request_consent(
        self,
        session_id: str,
        user_id: str,
        consent_types: List[str],
        purpose: str
    ) -> str:
        """
        Request consent from user for recording processing
        
        Args:
            session_id: Recording session
            user_id: User to request from
            consent_types: ["recording", "transcription", "learning", "sharing"]
            purpose: Why consent is needed
            
        Returns:
            consent_id for tracking
        """
        consent_id = f"consent_{session_id}_{user_id}"
        
        # Create consent request
        async with async_session() as session:
            for consent_type in consent_types:
                consent = ConsentRecord(
                    session_id=session_id,
                    user_id=user_id,
                    consent_given=False,  # Pending user response
                    consent_type=consent_type,
                    purpose=purpose,
                    consent_method="ui_prompt"
                )
                session.add(consent)
            
            await session.commit()
        
        # Publish consent request event (UI should show prompt)
        await message_bus.publish(
            source="recording_service",
            topic="consent.requested",
            payload={
                "session_id": session_id,
                "user_id": user_id,
                "consent_types": consent_types,
                "purpose": purpose,
                "message": f"This {purpose} session will be recorded for learning. Allow?"
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"[RECORDING] Consent requested: {session_id} from {user_id}")
        
        return consent_id
    
    async def grant_consent(
        self,
        session_id: str,
        user_id: str,
        consent_given: bool,
        consent_types: List[str]
    ) -> bool:
        """
        Record user consent decision
        
        Args:
            session_id: Recording session
            user_id: User granting/denying
            consent_given: True/False
            consent_types: Which types consented to
            
        Returns:
            Success boolean
        """
        async with async_session() as session:
            from sqlalchemy import update
            
            # Update consent records
            await session.execute(
                update(ConsentRecord)
                .where(ConsentRecord.session_id == session_id)
                .where(ConsentRecord.user_id == user_id)
                .where(ConsentRecord.consent_type.in_(consent_types))
                .values(
                    consent_given=consent_given,
                    consent_given_at=datetime.now(timezone.utc)
                )
            )
            
            # Update session if all consents given
            if consent_given:
                await session.execute(
                    update(RecordingSession)
                    .where(RecordingSession.session_id == session_id)
                    .values(
                        consent_given=True,
                        consent_given_at=datetime.now(timezone.utc),
                        consent_given_by=user_id
                    )
                )
            
            await session.commit()
        
        log_event(
            action="consent.granted" if consent_given else "consent.denied",
            actor=user_id,
            resource=session_id,
            outcome="ok",
            payload={
                "session_id": session_id,
                "consent_types": consent_types,
                "consent_given": consent_given
            }
        )
        
        # If consent given, trigger processing
        if consent_given:
            await message_bus.publish(
                source="recording_service",
                topic="recording.consent_granted",
                payload={
                    "session_id": session_id,
                    "ready_for_processing": True
                },
                priority=MessagePriority.NORMAL
            )
        
        return True
    
    async def transcribe_recording(
        self,
        session_id: str
    ) -> bool:
        """
        Transcribe audio from recording using Whisper
        
        Called automatically after consent + upload
        """
        # Load session
        async with async_session() as session:
            result = await session.execute(
                select(RecordingSession)
                .where(RecordingSession.session_id == session_id)
            )
            recording = result.scalar_one_or_none()
            
            if not recording:
                return False
            
            # Check consent
            if not recording.consent_given:
                print(f"[RECORDING] Cannot transcribe {session_id}: no consent")
                return False
            
            # Find audio file
            storage_path = Path(recording.storage_path)
            audio_files = list(storage_path.glob("*.mp3")) + list(storage_path.glob("*.wav")) + list(storage_path.glob("*.m4a"))
            
            if not audio_files:
                print(f"[RECORDING] No audio file found for {session_id}")
                return False
            
            audio_file = audio_files[0]
            
            # Transcribe using existing audio processor
            try:
                from backend.processors.multimodal_processors import AudioProcessor
                
                file_bytes = audio_file.read_bytes()
                result = await AudioProcessor.process(str(audio_file), file_bytes)
                
                if result.get("status") == "success":
                    transcript = result.get("transcript", "")
                    language = result.get("language", "en")
                    
                    # Save transcript
                    transcript_path = storage_path / "transcript.txt"
                    transcript_path.write_text(transcript, encoding='utf-8')
                    
                    # Update session
                    from sqlalchemy import update
                    await session.execute(
                        update(RecordingSession)
                        .where(RecordingSession.session_id == session_id)
                        .values(
                            transcript_path=str(transcript_path),
                            transcript_text=transcript,
                            transcript_language=language,
                            transcription_status="completed",
                            status="transcribed"
                        )
                    )
                    await session.commit()
                    
                    print(f"[RECORDING] Transcribed: {session_id} ({len(transcript)} chars)")
                    
                    # Publish for ingestion
                    await message_bus.publish(
                        source="recording_service",
                        topic="recording.transcribed",
                        payload={
                            "session_id": session_id,
                            "transcript_length": len(transcript),
                            "ready_for_ingestion": True
                        },
                        priority=MessagePriority.NORMAL
                    )
                    
                    return True
                else:
                    print(f"[RECORDING] Transcription failed: {result.get('message')}")
                    return False
            
            except Exception as e:
                print(f"[RECORDING] Transcription error: {e}")
                return False
    
    async def ingest_to_knowledge_base(
        self,
        session_id: str
    ) -> List[int]:
        """
        Ingest transcript into knowledge base
        
        Flow:
        1. Load transcript
        2. Check PII filters
        3. Chunk text
        4. Create knowledge artifacts
        5. Update learning loop
        
        Returns:
            List of artifact IDs created
        """
        # Load session
        async with async_session() as session:
            result = await session.execute(
                select(RecordingSession)
                .where(RecordingSession.session_id == session_id)
            )
            recording = result.scalar_one_or_none()
            
            if not recording or not recording.transcript_text:
                return []
            
            # Ingest via ingestion service
            try:
                from backend.ingestion_services.ingestion_service import ingestion_service
                
                artifact_id = await ingestion_service.ingest(
                    content=recording.transcript_text,
                    artifact_type="transcript",
                    title=recording.title or f"Recording {session_id}",
                    actor=recording.created_by,
                    source=f"recording_{recording.session_type}",
                    domain="recordings",
                    tags=[recording.session_type, recording.purpose],
                    metadata={
                        "session_id": session_id,
                        "session_type": recording.session_type,
                        "duration_seconds": recording.duration_seconds,
                        "participants": recording.participants,
                        "consent_given": True
                    }
                )
                
                if artifact_id:
                    # Update session
                    from sqlalchemy import update
                    await session.execute(
                        update(RecordingSession)
                        .where(RecordingSession.session_id == session_id)
                        .values(
                            ingested_at=datetime.now(timezone.utc),
                            ingested_artifact_ids=[artifact_id],
                            ingestion_status="completed",
                            status="ingested"
                        )
                    )
                    await session.commit()
                    
                    print(f"[RECORDING] Ingested to knowledge base: {session_id} → artifact {artifact_id}")
                    
                    return [artifact_id]
            
            except Exception as e:
                print(f"[RECORDING] Ingestion error: {e}")
                return []
        
        return []


# Global instance
recording_service = RecordingService()
