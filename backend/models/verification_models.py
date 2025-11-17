from datetime import datetime
from backend.models.base_models import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
import uuid

class RegisteredDevice(Base):
    """Device registration model"""
    __tablename__ = "registered_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, default=lambda: f"dev_{uuid.uuid4().hex}")
    device_name = Column(String)
    device_type = Column(String)
    user_identity = Column(String)
    device_fingerprint = Column(String, unique=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending_approval")  # pending_approval, allowlisted, blocked


class DeviceAllowlist(Base):
    """Device allowlist model"""
    __tablename__ = "device_allowlist"
    
    device_id = Column(String, ForeignKey("registered_devices.device_id"), primary_key=True)
    approved_by = Column(String)
    approval_date = Column(DateTime, default=datetime.utcnow)
    
class DeviceRole(Base):
    """Device role model"""
    __tablename__ = "device_roles"
    
    device_id = Column(String, ForeignKey("registered_devices.device_id"), primary_key=True)
    role = Column(String, default="developer")
    assigned_by = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

class RemoteAccessPolicy(Base):
    """Remote access policy configuration"""
    __tablename__ = "remote_access_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String, unique=True, nullable=False)
    description = Column(String)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationArtifact(Base):
    """Verification artifact model for tracking verification requests"""
    __tablename__ = "verification_artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(String, unique=True, index=True, default=lambda: f"artifact_{uuid.uuid4().hex}")
    artifact_type = Column(String, nullable=False)  # code, data, config, etc.
    content_hash = Column(String, nullable=False)  # SHA-256 hash
    created_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime, nullable=True)
    verified_by = Column(String, nullable=True)

class VerificationEnvelope(Base):
    """Verification envelope model for complete verification packages"""
    __tablename__ = "verification_envelopes"
    
    id = Column(Integer, primary_key=True, index=True)
    envelope_id = Column(String, unique=True, index=True, default=lambda: f"envelope_{uuid.uuid4().hex}")
    artifact_id = Column(String, ForeignKey("verification_artifacts.artifact_id"))
    envelope_type = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    envelope_metadata = Column(String)  # JSON metadata (renamed from 'metadata' - reserved word)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)