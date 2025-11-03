from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
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
