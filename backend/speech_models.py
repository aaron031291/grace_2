"""Database models for speech/audio interactions"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from .models import Base

class SpeechMessage(Base):
    """Voice messages with transcripts and audio storage"""
    __tablename__ = "speech_messages"
    
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    session_id = Column(String(128), nullable=True)
    
    # Audio file storage
    audio_path = Column(String(512), nullable=False)
    audio_format = Column(String(32), default="webm")
    audio_duration_ms = Column(Integer, nullable=True)
    audio_size_bytes = Column(Integer, nullable=True)
    audio_hash = Column(String(64), nullable=True)
    
    # Transcription
    transcript = Column(Text, nullable=True)
    language = Column(String(16), default="en")
    confidence = Column(Float, default=0.0)
    transcription_service = Column(String(64), default="whisper")
    transcription_model = Column(String(64), nullable=True)
    
    # Speaker identification
    speaker_id = Column(String(64), nullable=True)
    speaker_confidence = Column(Float, nullable=True)
    
    # Processing status
    status = Column(String(32), default="uploaded")  # uploaded, transcribing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Review and approval
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(String(64), nullable=True)
    review_status = Column(String(32), nullable=True)  # pending, approved, rejected, quarantined
    
    # Verification and audit
    verification_envelope_id = Column(Integer, nullable=True)
    audit_log_id = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transcribed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

class TextToSpeechMessage(Base):
    """Grace's spoken responses"""
    __tablename__ = "tts_messages"
    
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    session_id = Column(String(128), nullable=True)
    
    # Text content
    text_content = Column(Text, nullable=False)
    
    # Audio output
    audio_path = Column(String(512), nullable=False)
    audio_format = Column(String(32), default="mp3")
    audio_duration_ms = Column(Integer, nullable=True)
    audio_size_bytes = Column(Integer, nullable=True)
    
    # TTS configuration
    tts_service = Column(String(64), default="coqui")
    voice_model = Column(String(128), nullable=True)
    voice_speed = Column(Float, default=1.0)
    voice_pitch = Column(Float, default=1.0)
    
    # Status
    status = Column(String(32), default="pending")  # pending, generating, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Related to original message
    reply_to_speech_id = Column(Integer, ForeignKey("speech_messages.id"), nullable=True)
    reply_to_chat_id = Column(Integer, nullable=True)
    
    # Verification
    verification_envelope_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_at = Column(DateTime(timezone=True), nullable=True)

class SpeechSession(Base):
    """Voice conversation sessions"""
    __tablename__ = "speech_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), unique=True, nullable=False)
    user = Column(String(64), nullable=False)
    
    # Session metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_messages = Column(Integer, default=0)
    total_duration_ms = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    
    # Session context
    context_summary = Column(Text, nullable=True)
    primary_language = Column(String(16), default="en")
    
    status = Column(String(32), default="active")  # active, completed, abandoned

class AudioQuality(Base):
    """Audio quality metrics for monitoring"""
    __tablename__ = "audio_quality"
    
    id = Column(Integer, primary_key=True)
    speech_message_id = Column(Integer, ForeignKey("speech_messages.id"), nullable=False)
    
    # Quality metrics
    sample_rate = Column(Integer, nullable=True)
    bit_rate = Column(Integer, nullable=True)
    channels = Column(Integer, default=1)
    
    # Noise detection
    noise_level = Column(Float, nullable=True)
    signal_to_noise_ratio = Column(Float, nullable=True)
    
    # Clipping and distortion
    clipping_detected = Column(Boolean, default=False)
    distortion_level = Column(Float, nullable=True)
    
    # Overall quality score (0-100)
    quality_score = Column(Float, nullable=True)
    quality_issues = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
