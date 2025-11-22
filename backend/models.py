"""
Grace 3.0 - Database Models
SQLAlchemy ORM models for Fusion layer
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class FusionArtifact(Base):
    """Main artifacts table"""
    __tablename__ = 'fusion_artifacts'
    
    artifact_id = Column(String(255), primary_key=True)
    name = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)
    layer = Column(String(20), default='fusion', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dna = relationship("MemoryDNA", back_populates="artifact", cascade="all, delete-orphan")
    lifecycle = relationship("LifecycleEvent", back_populates="artifact", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("layer IN ('lightning', 'fusion')", name='check_layer'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.artifact_id,
            'name': self.name,
            'type': self.type,
            'layer': self.layer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MemoryDNA(Base):
    """Memory DNA table (versioning information)"""
    __tablename__ = 'memory_dna'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(String(255), ForeignKey('fusion_artifacts.artifact_id', ondelete='CASCADE'), nullable=False)
    version_id = Column(String(255), unique=True, nullable=False)
    origin = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    intent = Column(String(500), nullable=False)
    checksum = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artifact = relationship("FusionArtifact", back_populates="dna")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'artifactId': self.artifact_id,
            'versionId': self.version_id,
            'origin': self.origin,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'intent': self.intent,
            'checksum': self.checksum
        }


class LifecycleEvent(Base):
    """Lifecycle events table (audit log)"""
    __tablename__ = 'lifecycle_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(String(255), ForeignKey('fusion_artifacts.artifact_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    action = Column(String(100), nullable=False)
    actor = Column(String(255), nullable=False)
    description = Column(Text)
    previous_version_id = Column(String(255))
    snapshot = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artifact = relationship("FusionArtifact", back_populates="lifecycle")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action': self.action,
            'actor': self.actor,
            'description': self.description,
            'previousVersionId': self.previous_version_id,
            'snapshot': self.snapshot
        }
