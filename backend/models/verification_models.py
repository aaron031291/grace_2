from datetime import datetime
from backend.models.base_models import Base
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
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
    __tablename__ = "remote_access_policies"