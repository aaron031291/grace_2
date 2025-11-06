from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .models import Base

class KnowledgeArtifact(Base):
    """Ingested knowledge items"""
    __tablename__ = "knowledge_artifacts"
    id = Column(Integer, primary_key=True)
    path = Column(String(512), unique=True, nullable=False)
    title = Column(String(512))
    artifact_type = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))
    artifact_metadata = Column(Text)
    source = Column(String(256))
    ingested_by = Column(String(64), nullable=False)
    domain = Column(String(64))
    tags = Column(Text)
    size_bytes = Column(Integer)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KnowledgeRevision(Base):
    """Revision history for knowledge artifacts"""
    __tablename__ = "knowledge_revisions"
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey("knowledge_artifacts.id"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    edited_by = Column(String(64), nullable=False)
    change_summary = Column(Text, nullable=True)
    diff = Column(Text, nullable=True)  # JSON string of field changes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('artifact_id', 'revision_number', name='uq_artifact_revision'),
    )

class KnowledgeTombstone(Base):
    """Soft-delete marker for knowledge artifacts"""
    __tablename__ = "knowledge_tombstones"
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey("knowledge_artifacts.id"), nullable=False, unique=True, index=True)
    deleted_by = Column(String(64), nullable=False)
    reason = Column(Text, nullable=True)
    deleted_at = Column(DateTime(timezone=True), server_default=func.now())
