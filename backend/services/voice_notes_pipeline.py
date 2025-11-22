"""
Voice Notes to Learning Pipeline - End-to-End

Complete pipeline for voice notes:
1. Capture → Upload audio file
2. Consent → User approves recording/transcription/learning
3. Transcribe → Whisper speech-to-text
4. Embed → Vector embeddings
5. Index → Searchable via semantic query
6. Ingest → Knowledge base
7. Learn → Feed to learning loop

This is the pilot for expanding to screen/video recordings.
"""

import asyncio
from typing import Dict, Any, Optional

from backend.services.recording_service import recording_service, RecordingType
from backend.core.message_bus import message_bus
from backend.logging_system_utils import log_event


class VoiceNotesPipeline:
    """
    End-to-end voice notes processing pipeline
    
    Usage:
        pipeline = VoiceNotesPipeline()
        
        # Start voice note
        session_id = await pipeline.start_voice_note(
            title="Meeting Notes",
            user_id="aaron"
        )
        
        # Upload audio
        await pipeline.upload_audio(session_id, audio_bytes, "note.mp3")
        
        # Request consent
        await pipeline.request_consent(session_id, "aaron")
        
        # User approves via UI
        # ... automatic processing continues ...
        
        # Search voice notes
        results = await pipeline.search_voice_notes(
            query="what did I say about the deadline?"
        )
    """
    
    def __init__(self):
        self.processing_status: Dict[str, str] = {}  # session_id -> status
        
        # Subscribe to events
        message_bus.subscribe("secrets.consent.response", self._handle_consent_response)
        message_bus.subscribe("recording.transcribed", self._handle_transcription_complete)
        
        print("[VOICE NOTES] Pipeline initialized")
    
    async def start_voice_note(
        self,
        title: str,
        user_id: str,
        purpose: str = "learning"
    ) -> str:
        """
        Start voice note recording session
        
        Args:
            title: Note title
            user_id: User recording
            purpose: Purpose (learning, meeting, memo)
            
        Returns:
            session_id for tracking
        """
        session_id = await recording_service.start_recording(
            session_type=RecordingType.VOICE_NOTE,
            title=title,
            purpose=purpose,
            created_by=user_id,
            participants=[{
                "user_id": user_id,
                "name": user_id,
                "role": "host"
            }],
            consent_given=False  # Require explicit consent
        )
        
        self.processing_status[session_id] = "created"
        
        log_event(
            action="voice_note.started",
            actor=user_id,
            resource=session_id,
            outcome="created",
            payload={"title": title, "purpose": purpose}
        )
        
        print(f"[VOICE NOTES] Started session {session_id}: {title}")
        
        return session_id
    
    async def upload_audio(
        self,
        session_id: str,
        audio_bytes: bytes,
        filename: str,
        user_id: str
    ) -> bool:
        """
        Upload audio file for voice note
        
        Args:
            session_id: Recording session ID
            audio_bytes: Audio file content
            filename: Original filename
            user_id: User uploading
            
        Returns:
            Success boolean
        """
        success = await recording_service.upload_recording(
            session_id=session_id,
            file_content=audio_bytes,
            filename=filename,
            uploaded_by=user_id
        )
        
        if success:
            self.processing_status[session_id] = "uploaded"
            print(f"[VOICE NOTES] Uploaded {len(audio_bytes)} bytes for {session_id}")
        
        return success
    
    async def request_consent(
        self,
        session_id: str,
        user_id: str
    ) -> str:
        """
        Request user consent for processing
        
        Args:
            session_id: Recording session
            user_id: User to request from
            
        Returns:
            consent_id for tracking
        """
        consent_id = await recording_service.request_consent(
            session_id=session_id,
            user_id=user_id,
            consent_types=["recording", "transcription", "learning"],
            purpose="voice note learning and knowledge base"
        )
        
        self.processing_status[session_id] = "awaiting_consent"
        
        print(f"[VOICE NOTES] Consent requested for {session_id}")
        
        return consent_id
    
    async def _handle_consent_response(self, event: Dict[str, Any]):
        """Handle consent approval from user"""
        # Consent responses are handled by recording_service
        # This just monitors for voice note sessions
        pass
    
    async def process_voice_note(
        self,
        session_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process voice note through complete pipeline
        
        This is called after consent is granted.
        Performs: transcribe → embed → index → ingest → learn
        
        Args:
            session_id: Recording session
            user_id: User who owns the note
            
        Returns:
            Processing results
        """
        results = {
            "session_id": session_id,
            "steps_completed": [],
            "errors": []
        }
        
        # Step 1: Transcribe
        try:
            transcribe_success = await recording_service.transcribe_recording(
                session_id=session_id,
                user_id=user_id
            )
            
            if not transcribe_success:
                results["errors"].append("Transcription failed")
                return results
            
            results["steps_completed"].append("transcribed")
            self.processing_status[session_id] = "transcribed"
            
        except Exception as e:
            results["errors"].append(f"Transcription error: {e}")
            return results
        
        # Step 2: Wait for embedding (handled by vector_integration automatically)
        # The recording.transcribed event triggers auto-embedding
        
        # Give it a moment to complete
        await asyncio.sleep(2)
        
        results["steps_completed"].append("embedded")
        self.processing_status[session_id] = "embedded"
        
        # Step 3: Ingest to knowledge base
        try:
            artifact_ids = await recording_service.ingest_to_knowledge_base(
                session_id=session_id,
                user_id=user_id
            )
            
            if artifact_ids:
                results["steps_completed"].append("ingested")
                results["artifact_ids"] = artifact_ids
                self.processing_status[session_id] = "ingested"
            else:
                results["errors"].append("Ingestion failed")
                
        except Exception as e:
            results["errors"].append(f"Ingestion error: {e}")
        
        # Step 4: Feed to learning loop
        try:
            learning_success = await recording_service.feed_to_learning_loop(
                session_id=session_id,
                usefulness_score=0.8  # Default, user can update
            )
            
            if learning_success:
                results["steps_completed"].append("learned")
                self.processing_status[session_id] = "completed"
            
        except Exception as e:
            results["errors"].append(f"Learning loop error: {e}")
        
        # Log completion
        log_event(
            action="voice_note.processed",
            actor=user_id,
            resource=session_id,
            outcome="completed" if len(results["errors"]) == 0 else "partial",
            payload={
                "steps_completed": results["steps_completed"],
                "errors": results["errors"]
            }
        )
        
        print(f"[VOICE NOTES] Processing complete for {session_id}: {len(results['steps_completed'])} steps")
        
        return results
    
    async def search_voice_notes(
        self,
        query: str,
        user_id: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search across all user's voice notes
        
        Args:
            query: Search query
            user_id: User whose notes to search
            top_k: Number of results
            
        Returns:
            Search results with timestamps
        """
        from backend.services.rag_service import rag_service
        
        # Search with filters
        results = await rag_service.retrieve(
            query=query,
            top_k=top_k,
            source_types=["recording"],
            filters={
                "session_type": RecordingType.VOICE_NOTE
            },
            requested_by=user_id
        )
        
        return results
    
    async def get_voice_note_transcript(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[str]:
        """
        Get full transcript for voice note
        
        Args:
            session_id: Recording session
            user_id: User requesting
            
        Returns:
            Transcript text or None
        """
        from backend.models.recording_models import RecordingSession
        from backend.models.base_models import async_session as db_session
        from sqlalchemy import select
        
        async with db_session() as session:
            result = await session.execute(
                select(RecordingSession)
                .where(RecordingSession.session_id == session_id)
                .where(RecordingSession.created_by == user_id)
            )
            recording = result.scalar_one_or_none()
            
            if recording and recording.transcript_text:
                return recording.transcript_text
        
        return None
    
    async def get_pipeline_status(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get current status of voice note processing
        
        Args:
            session_id: Recording session
            
        Returns:
            Current status and completed steps
        """
        from backend.models.recording_models import RecordingSession
        from backend.models.base_models import async_session as db_session
        from sqlalchemy import select
        
        async with db_session() as session:
            result = await session.execute(
                select(RecordingSession)
                .where(RecordingSession.session_id == session_id)
            )
            recording = result.scalar_one_or_none()
            
            if not recording:
                return {"error": "Recording not found"}
            
            steps_completed = []
            
            if recording.consent_given:
                steps_completed.append("consent_granted")
            if recording.transcription_status == "completed":
                steps_completed.append("transcribed")
            if recording.ingestion_status == "completed":
                steps_completed.append("ingested")
            if recording.learned_from:
                steps_completed.append("learned")
            
            return {
                "session_id": session_id,
                "status": self.processing_status.get(session_id, recording.status),
                "steps_completed": steps_completed,
                "consent_given": recording.consent_given,
                "transcript_length": len(recording.transcript_text or ""),
                "searchable": recording.ingestion_status == "completed"
            }


# Global instance
voice_notes_pipeline = VoiceNotesPipeline()
