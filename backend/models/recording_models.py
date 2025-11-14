"""
Recording Models - Screen Sharing, Video Calls, Voice Notes

Handles multimedia ingestion with:
- Consent management
- Encrypted storage
- Transcription tracking
- Learning integration
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON
from sqlalchemy.sql import func
from .base_models import Base


class RecordingSession(Base):
    """
    Recording session (screen share, video call, voice note)
    
    Security:
    - Consent required before ingestion
    - Files encrypted at rest
    - Access controlled per user
    - PII filters applied
    """
    __tablename__ = "recording_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Session identification
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    session_type = Column(String(64), nullable=False, index=True)
    # Types: screen_share, video_call, voice_note, meeting_recording
    
    # Storage
    storage_path = Column(String(512), nullable=False)  # storage/recordings/<session_id>/
    file_size_bytes = Column(Integer, nullable=True)
    encrypted = Column(Boolean, default=True)
    encryption_key_id = Column(String(128), nullable=True)
    
    # Metadata
    title = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    purpose = Column(String(256), nullable=False)  # meeting, training, support, etc.
    
    # Participants (for video calls/screen shares)
    participants = Column(JSON, default=list)  # [{user_id, name, role}]
    host = Column(String(128), nullable=True)
    
    # Consent & Governance
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_given_at = Column(DateTime(timezone=True), nullable=True)
    consent_given_by = Column(String(128), nullable=True)
    all_participants_consented = Column(Boolean, default=False)
    consent_metadata = Column(JSON, nullable=True)  # Detailed consent records
    
    # Processing status
    status = Column(String(32), default="captured", nullable=False)
    # States: captured, transcribing, processing, ingested, failed
    transcription_status = Column(String(32), nullable=True)
    ingestion_status = Column(String(32), nullable=True)
    
    # Transcription
    transcript_path = Column(String(512), nullable=True)
    transcript_text = Column(Text, nullable=True)  # Full transcript
    transcript_language = Column(String(16), nullable=True)
    transcript_confidence = Column(Float, nullable=True)
    
    # Processing metadata
    duration_seconds = Column(Float, nullable=True)
    frame_count = Column(Integer, nullable=True)  # For screen/video
    audio_extracted = Column(Boolean, default=False)
    
    # Ingestion
    ingested_at = Column(DateTime(timezone=True), nullable=True)
    ingested_artifact_ids = Column(JSON, default=list)  # Knowledge artifact IDs
    chunks_created = Column(Integer, default=0)
    embeddings_created = Column(Integer, default=0)
    
    # Learning
    learned_from = Column(Boolean, default=False)
    learning_outcome_id = Column(String(128), nullable=True)
    usefulness_score = Column(Float, nullable=True)  # User feedback on value
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False)
    allowed_users = Column(JSON, default=list)  # Who can access
    requires_approval = Column(Boolean, default=True)
    
    # Retention
    retention_days = Column(Integer, default=90)
    auto_delete_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    source = Column(String(64), default="ui_upload")  # ui_upload, conferencing_hook, mobile
    quality = Column(String(32), nullable=True)  # audio/video quality


class RecordingTranscript(Base):
    """
    Timed transcript segments
    Enables precise timestamp-based retrieval
    """
    __tablename__ = "recording_transcripts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    session_id = Column(String(128), nullable=False, index=True)
    
    # Segment
    segment_number = Column(Integer, nullable=False)
    start_time_seconds = Column(Float, nullable=False)
    end_time_seconds = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    
    # Content
    text = Column(Text, nullable=False)
    speaker = Column(String(128), nullable=True)  # Who spoke (if detected)
    confidence = Column(Float, nullable=True)
    language = Column(String(16), nullable=True)
    
    # Processing
    contains_pii = Column(Boolean, default=False)
    redacted = Column(Boolean, default=False)
    redacted_text = Column(Text, nullable=True)
    
    # Embedding
    embedded = Column(Boolean, default=False)
    embedding_id = Column(String(128), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RecordingAccess(Base):
    """
    Audit log for recording access
    Track who accessed raw recordings
    """
    __tablename__ = "recording_access"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    session_id = Column(String(128), nullable=False, index=True)
    
    # Who accessed
    accessed_by = Column(String(128), nullable=False, index=True)
    access_type = Column(String(64), nullable=False)
    # Types: playback, download, transcription_view, deletion
    
    # When and why
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    purpose = Column(String(256), nullable=False)
    
    # Result
    access_granted = Column(Boolean, nullable=False)
    denial_reason = Column(String(256), nullable=True)
    
    # Details
    duration_seconds = Column(Float, nullable=True)  # How long accessed
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)


class ConsentRecord(Base):
    """
    Explicit consent tracking for recordings
    Required before any processing or learning
    """
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    session_id = Column(String(128), nullable=False, index=True)
    
    # Who gave consent
    user_id = Column(String(128), nullable=False)
    user_name = Column(String(256), nullable=True)
    user_role = Column(String(64), nullable=True)  # host, participant, observer
    
    # Consent details
    consent_given = Column(Boolean, nullable=False)
    consent_type = Column(String(64), nullable=False)
    # Types: recording, transcription, learning, sharing
    
    # When
    consent_given_at = Column(DateTime(timezone=True), server_default=func.now())
    consent_method = Column(String(64), default="ui_prompt")
    # Methods: ui_prompt, api_call, implicit_meeting_start, terms_accepted
    
    # Scope
    purpose = Column(String(256), nullable=False)
    retention_agreed_days = Column(Integer, default=90)
    
    # Revocation
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(Text, nullable=True)
    
    # Metadata
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)
    consent_metadata = Column(JSON, nullable=True)
