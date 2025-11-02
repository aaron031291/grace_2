"""Database models for Memory Scoring System"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from models import Base

class MemoryArtifact(Base):
    """Memory artifact with trust and decay scoring"""
    __tablename__ = "cognition_memory_artifacts"
    
    id = Column(Integer, primary_key=True)
    memory_ref = Column(String(128), unique=True, nullable=False)
    loop_id = Column(String(128), nullable=False)
    component = Column(String(64), nullable=False)
    output_type = Column(String(32), nullable=False)
    
    # Content
    result_data = Column(Text, nullable=False)
    reasoning_chain_id = Column(String(128))
    
    # Trust scoring fields
    trust_score = Column(Float, default=0.5)
    provenance_score = Column(Float, default=0.5)
    consensus_score = Column(Float, default=0.5)
    governance_score = Column(Float, default=1.0)
    usage_score = Column(Float, default=0.0)
    
    # Decay configuration
    decay_curve = Column(String(32), default="hyperbolic")
    half_life_hours = Column(Float, default=168.0)
    
    # Usage tracking
    access_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Quality & confidence
    confidence = Column(Float, default=1.0)
    quality_score = Column(Float)
    importance = Column(Float, default=0.5)
    
    # Governance
    constitutional_compliance = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Metadata
    domain = Column(String(64))
    category = Column(String(64))
    policy_tags = Column(Text)
    meta_data = Column(Text)
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Verification
    verification_envelope_id = Column(String(128))
    audit_log_id = Column(Integer)


class TrustEvent(Base):
    """Tracks trust score changes over time"""
    __tablename__ = "cognition_trust_events"
    
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cognition_memory_artifacts.id'), nullable=False)
    
    event_type = Column(String(32), nullable=False)
    reason = Column(String(64), nullable=False)
    
    old_trust_score = Column(Float, nullable=False)
    new_trust_score = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)
    
    # Specific signal changes
    provenance_delta = Column(Float, default=0.0)
    consensus_delta = Column(Float, default=0.0)
    governance_delta = Column(Float, default=0.0)
    usage_delta = Column(Float, default=0.0)
    
    actor = Column(String(64))
    meta_data = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MemoryIndex(Base):
    """Symbolic indexing for fast memory retrieval"""
    __tablename__ = "cognition_memory_index"
    
    id = Column(Integer, primary_key=True)
    artifact_id = Column(Integer, ForeignKey('cognition_memory_artifacts.id'), nullable=False)
    
    index_type = Column(String(32), nullable=False)
    index_value = Column(String(256), nullable=False)
    weight = Column(Float, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GarbageCollectionLog(Base):
    """Tracks garbage collection operations"""
    __tablename__ = "cognition_gc_log"
    
    id = Column(Integer, primary_key=True)
    
    policy_name = Column(String(64), nullable=False)
    artifacts_scanned = Column(Integer, default=0)
    artifacts_archived = Column(Integer, default=0)
    artifacts_deleted = Column(Integer, default=0)
    
    threshold_trust = Column(Float)
    threshold_age_hours = Column(Float)
    
    duration_ms = Column(Integer)
    meta_data = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
