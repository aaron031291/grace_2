"""Constitutional AI Framework - Grace's Bill of Rights

Defines foundational principles, operational tenets, safety constraints,
and clarification protocols that govern ALL Grace behavior.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .models import Base

class ConstitutionalPrinciple(Base):
    """Foundational principles that are always true"""
    __tablename__ = "constitutional_principles"
    
    id = Column(Integer, primary_key=True)
    principle_name = Column(String(128), unique=True, nullable=False)
    principle_level = Column(String(32), nullable=False)  # foundational, operational, safety
    
    # Principle definition
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    
    # Enforcement
    enforcement_type = Column(String(64), nullable=False)  # governance, hunter, verification, clarification
    severity = Column(String(32), default="critical")  # critical, high, medium, low
    
    # Related policies/rules
    governance_policy_ids = Column(JSON, default=list)
    hunter_rule_ids = Column(JSON, default=list)
    
    # Metadata
    category = Column(String(64), nullable=True)  # transparency, safety, ethics, performance
    applies_to = Column(JSON, default=list)  # ["code_generation", "knowledge_ingest", "all"]
    
    # Status
    active = Column(Boolean, default=True)
    immutable = Column(Boolean, default=True)  # Foundational principles cannot be changed
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(64), default="system")
    
    # Relationships
    violations = relationship("ConstitutionalViolation", back_populates="principle")

class ConstitutionalViolation(Base):
    """Log of constitutional violations"""
    __tablename__ = "constitutional_violations"
    
    id = Column(Integer, primary_key=True)
    principle_id = Column(Integer, ForeignKey("constitutional_principles.id"), nullable=False)
    
    # Violation details
    violation_type = Column(String(64), nullable=False)  # attempt, accidental, bypassed
    actor = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    resource = Column(String(256), nullable=True)
    
    # Detection
    detected_by = Column(String(64), nullable=False)  # governance, hunter, verification, human
    severity = Column(String(32), nullable=False)
    
    # Context
    details = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)
    
    # Response
    blocked = Column(Boolean, default=False)
    remediation_action = Column(Text, nullable=True)
    escalated = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    
    # Relationships
    principle = relationship("ConstitutionalPrinciple", back_populates="violations")

class ClarificationRequest(Base):
    """Questions Grace asks when uncertain"""
    __tablename__ = "clarification_requests"
    
    id = Column(Integer, primary_key=True)
    request_id = Column(String(64), unique=True, nullable=False)
    
    # Context
    user = Column(String(64), nullable=False)
    session_id = Column(String(128), nullable=True)
    
    # Uncertainty
    original_input = Column(Text, nullable=False)
    uncertainty_type = Column(String(64), nullable=False)  # ambiguous, low_confidence, conflict, policy
    confidence_score = Column(Float, nullable=False)  # How uncertain (0.0 = very uncertain, 1.0 = certain)
    
    # Clarification
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # List of possible interpretations
    context_provided = Column(Text, nullable=True)  # Additional context Grace provides
    
    # Response
    status = Column(String(32), default="pending")  # pending, answered, timeout, bypassed
    user_response = Column(Text, nullable=True)
    selected_option = Column(String(128), nullable=True)
    
    # Resolution
    resolved_action = Column(Text, nullable=True)  # What Grace did after clarification
    success = Column(Boolean, nullable=True)  # Was the action successful
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    audit_log_id = Column(Integer, nullable=True)

class ConstitutionalCompliance(Base):
    """Track constitutional compliance per action"""
    __tablename__ = "constitutional_compliance"
    
    id = Column(Integer, primary_key=True)
    action_id = Column(String(128), nullable=False)
    
    # Action details
    actor = Column(String(64), nullable=False)
    action_type = Column(String(128), nullable=False)
    resource = Column(String(256), nullable=True)
    
    # Compliance checks
    principles_checked = Column(JSON, default=list)  # List of principle IDs checked
    principles_passed = Column(JSON, default=list)
    principles_failed = Column(JSON, default=list)
    
    # Overall compliance
    compliant = Column(Boolean, nullable=False)
    compliance_score = Column(Float, default=1.0)  # 0.0-1.0
    
    # Evidence
    explanation_provided = Column(Boolean, default=False)
    reasoning_logged = Column(Boolean, default=False)
    approval_obtained = Column(Boolean, default=False)
    verification_signed = Column(Boolean, default=False)
    
    # Violations
    violation_ids = Column(JSON, default=list)  # ConstitutionalViolation IDs
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    audit_log_id = Column(Integer, nullable=True)

class OperationalTenet(Base):
    """Day-to-day operational rules derived from principles"""
    __tablename__ = "operational_tenets"
    
    id = Column(Integer, primary_key=True)
    tenet_name = Column(String(128), unique=True, nullable=False)
    
    # Content
    description = Column(Text, nullable=False)
    rule_example = Column(Text, nullable=True)
    
    # Derived from
    principle_id = Column(Integer, ForeignKey("constitutional_principles.id"), nullable=True)
    
    # Implementation
    integration_point = Column(String(64), nullable=False)  # governance, hunter, clarifier, memory
    enforcement_method = Column(Text, nullable=False)
    
    # Metadata
    category = Column(String(64), nullable=True)
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest
    
    # Status
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
