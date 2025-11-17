"""
Security Models - Database models for security features
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.models.base_models import Base

class SecurityEvent(Base):
    """Security event logging"""
    __tablename__ = "security_event_logs"
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), default="info")  # info, warning, error, critical
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    event_metadata = Column(Text, nullable=True)  # JSON metadata (renamed to avoid SQLAlchemy conflict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "source": self.source,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AccessLog(Base):
    """Access logging for audit trails"""
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(200), nullable=False)
    method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "method": self.method,
            "status_code": self.status_code,
            "ip_address": self.ip_address,
            "response_time_ms": self.response_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SecurityPolicy(Base):
    """Security policies and rules"""
    __tablename__ = "security_policies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    policy_type = Column(String(50), nullable=False)  # rate_limit, ip_block, content_filter, etc.
    rules = Column(Text, nullable=False)  # JSON rules
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=100)  # Lower number = higher priority
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type,
            "rules": self.rules,
            "enabled": self.enabled,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Export all models
__all__ = [
    "SecurityEvent",
    "AccessLog", 
    "SecurityPolicy"
]