from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .base_models import Base, async_session
import hashlib
import json

class MemoryArtifact(Base):
    __tablename__ = "memory_artifacts"
    id = Column(Integer, primary_key=True)
    path = Column(String(512), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    artifact_metadata = Column(Text)
    domain = Column(String(64))
    category = Column(String(64))
    status = Column(String(32), default="draft")
    version = Column(Integer, default=1)
    created_by = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

class MemoryOperation(Base):
    """Immutable audit trail with hash chaining"""
    __tablename__ = "memory_operations"
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, nullable=False)
    operation = Column(String(32), nullable=False)
    actor = Column(String(64), nullable=False)
    previous_content_hash = Column(String(64))
    new_content_hash = Column(String(64), nullable=False)
    operation_hash = Column(String(64), nullable=False)
    previous_operation_hash = Column(String(64))
    reason = Column(Text)
    operation_metadata = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    @staticmethod
    def compute_hash(artifact_id: int, operation: str, actor: str, content_hash: str, previous_hash: str) -> str:
        """Compute hash for immutable chain"""
        data = f"{artifact_id}:{operation}:{actor}:{content_hash}:{previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class MemoryEvent(Base):
    """Trigger mesh events for memory operations"""
    __tablename__ = "memory_events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=False)
    artifact_id = Column(Integer, nullable=False)
    artifact_path = Column(String(512))
    actor = Column(String(64))
    payload = Column(Text)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
