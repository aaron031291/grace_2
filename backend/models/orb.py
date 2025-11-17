"""
Orb Models - Pydantic schemas for the unified World Model / Orb interface
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class OrbSession(BaseModel):
    """Orb session with topic extraction and duration tracking"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    message_count: int = 0
    topics: Dict[str, int] = Field(default_factory=dict)  # topic -> mention count
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active, closed


class SessionCreateRequest(BaseModel):
    """Request to create a new Orb session"""
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class SessionInfoResponse(BaseModel):
    """Session information response"""
    session_id: str
    user_id: str
    start_time: datetime
    duration_seconds: float
    duration_formatted: str
    message_count: int
    key_topics: List[Dict[str, Any]]  # [{topic, count, score}]
    status: str


class ScreenShareRequest(BaseModel):
    """Request to start screen sharing"""
    user_id: str
    quality_settings: Dict[str, Any] = Field(default_factory=dict)


class ScreenShareResponse(BaseModel):
    """Screen share session response"""
    session_id: str
    status: str
    message: str


class RecordingRequest(BaseModel):
    """Request to start recording"""
    user_id: str
    media_type: str  # screen_recording, video_recording, audio_recording
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecordingResponse(BaseModel):
    """Recording session response"""
    session_id: str
    status: str
    message: str


class VoiceToggleResponse(BaseModel):
    """Voice control toggle response"""
    voice_enabled: bool
    user_id: str
    message: str


class TaskCreateRequest(BaseModel):
    """Request to create a background task"""
    task_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Task creation response"""
    task_id: str
    status: str
    message: str


class BackgroundTask(BaseModel):
    """Background task model"""
    task_id: str
    task_type: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MediaSession(BaseModel):
    """Media session (screen-share, recording, etc.)"""
    session_id: str
    user_id: str
    media_type: str
    status: str  # active, completed, failed
    start_time: datetime
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SandboxExperiment(BaseModel):
    """Sandbox experiment model"""
    experiment_id: str
    status: str  # validating, ready, rejected
    title: str
    description: str
    metrics: Dict[str, Any]
    progress: float


class ConsensusPersona(BaseModel):
    """Cross-persona consensus vote"""
    role: str
    avatar: str
    vote: str  # approve, caution, reject
    confidence: float


class FeedbackItem(BaseModel):
    """Human feedback queue item"""
    id: str
    title: str
    description: str
    priority: str  # normal, high, critical
    created_at: str


class SovereigntyMetrics(BaseModel):
    """Grace's sovereignty metrics"""
    autonomy_level: float
    autonomous_decisions_30d: int
    success_rate: float
    learning_velocity: float
    trust_calibration: float
    active_sandboxes: int
    trust_score: float
    pending_reviews: int


class OrbStats(BaseModel):
    """Comprehensive Orb statistics"""
    sessions: Dict[str, int]  # active, total
    memory: Dict[str, Any]  # total_fragments, average_trust_score, total_size
    intelligence: Dict[str, Any]  # version, domain_pods, models_available
    governance: Dict[str, int]  # total_tasks, pending_tasks
    notifications: Dict[str, int]  # total, unread
    multimodal: Dict[str, Any]  # active_sessions, background_tasks, voice_enabled_users
