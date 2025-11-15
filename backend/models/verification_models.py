"""Verification and cryptographic signature models"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .base_models import Base

class VerificationArtifact(Base):
    """Placeholder for verification artifacts"""
    __tablename__ = "verification_artifacts"
    id = Column(Integer, primary_key=True)
    artifact_type = Column(String(64))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VerificationEnvelope(Base):
    """Signed envelopes for actions"""
    __tablename__ = "verification_envelopes"
    id = Column(Integer, primary_key=True)
    action_id = Column(String(64), unique=True, nullable=False)
    actor = Column(String(64), nullable=False)
    action_type = Column(String(128), nullable=False)
    resource = Column(String(256))
    input_hash = Column(String(64), nullable=False)
    output_hash = Column(String(64))
    signature = Column(String(256), nullable=False)
    verified = Column(Boolean, default=False)
    criteria_met = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())