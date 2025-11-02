from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GovernancePolicy(Base):
    __tablename__ = "governance_policies"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    severity = Column(String(32), default="low")
    condition = Column(Text, nullable=False)
    action = Column(String(32), default="allow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    actor = Column(String(64))
    action = Column(String(128))
    resource = Column(String(128))
    policy_checked = Column(String(128), nullable=True)
    result = Column(String(32))
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    hash = Column(String(64), nullable=True)
    previous_hash = Column(String(64), nullable=True)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    status = Column(String(32), default="pending")
    requested_by = Column(String(64))
    reason = Column(Text)
    decision_by = Column(String(64), nullable=True)
    decision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    id = Column(Integer, primary_key=True)
    actor = Column(String(64))
    action = Column(String(128))
    resource = Column(String(128))
    severity = Column(String(32))
    details = Column(Text)
    status = Column(String(32), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)

class SecurityRule(Base):
    __tablename__ = "security_rules"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    description = Column(Text)
    condition = Column(Text)
    severity = Column(String(32))
    action = Column(String(32))

class HealthCheck(Base):
    __tablename__ = "health_checks"
    id = Column(Integer, primary_key=True)
    component = Column(String(64))
    status = Column(String(32))
    latency_ms = Column(Integer)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HealingAction(Base):
    __tablename__ = "healing_actions"
    id = Column(Integer, primary_key=True)
    component = Column(String(64))
    action = Column(String(128))
    result = Column(String(32))
    detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
