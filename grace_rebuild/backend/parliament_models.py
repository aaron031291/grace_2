"""Parliament & Quorum Governance Models

Multi-agent voting system for distributed decision-making.
Supports quorum-based consensus with signatures and verification.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .models import Base

class GovernanceMember(Base):
    """Parliament members (humans, agents, or Grace herself)"""
    __tablename__ = "governance_members"
    
    id = Column(Integer, primary_key=True)
    member_id = Column(String(64), unique=True, nullable=False)
    member_type = Column(String(32), nullable=False)  # human, agent, grace_reflection, grace_hunter, etc.
    display_name = Column(String(128), nullable=False)
    
    # Permissions
    role = Column(String(64), default="member")  # member, admin, observer
    committees = Column(JSON, default=list)  # List of committee names
    
    # Voting power
    vote_weight = Column(Float, default=1.0)  # Some members may have weighted votes
    
    # Status
    active = Column(Boolean, default=True)
    suspended = Column(Boolean, default=False)
    suspension_reason = Column(Text, nullable=True)
    
    # Metadata
    public_key = Column(String(256), nullable=True)  # For vote signature verification
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_vote_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_votes = Column(Integer, default=0)
    votes_approved = Column(Integer, default=0)
    votes_rejected = Column(Integer, default=0)
    votes_abstained = Column(Integer, default=0)
    
    # Relationships
    votes = relationship("GovernanceVote", back_populates="member")

class GovernanceSession(Base):
    """Voting session for a governance decision"""
    __tablename__ = "governance_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(64), unique=True, nullable=False)
    
    # What's being voted on
    policy_name = Column(String(128), nullable=False)
    action_type = Column(String(64), nullable=False)  # execute, approve, modify, reject
    action_payload = Column(JSON, nullable=False)  # Full details of the action
    
    # Context
    category = Column(String(64), nullable=True)  # file_access, execution, network, etc.
    resource = Column(String(256), nullable=True)
    actor = Column(String(64), nullable=True)  # Who initiated the action
    
    # Quorum requirements
    committee = Column(String(64), default="general")  # Which committee should vote
    quorum_required = Column(Integer, default=3)  # Minimum votes needed
    approval_threshold = Column(Float, default=0.5)  # % of votes needed to approve (0.5 = majority)
    
    # Current status
    status = Column(String(32), default="pending")  # pending, voting, approved, rejected, expired
    
    # Vote tallies
    votes_approve = Column(Integer, default=0)
    votes_reject = Column(Integer, default=0)
    votes_abstain = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Weighted tallies (if members have vote_weight)
    weighted_approve = Column(Float, default=0.0)
    weighted_reject = Column(Float, default=0.0)
    weighted_abstain = Column(Float, default=0.0)
    total_weighted = Column(Float, default=0.0)
    
    # Outcome
    outcome = Column(String(32), nullable=True)  # approved, rejected, tie, expired
    decision_reason = Column(Text, nullable=True)
    
    # Security & verification
    hunter_alerts = Column(JSON, default=list)  # Attached security alerts
    verification_envelope_id = Column(Integer, nullable=True)
    risk_level = Column(String(32), default="medium")  # low, medium, high, critical
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    voting_started_at = Column(DateTime(timezone=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    audit_log_id = Column(Integer, nullable=True)
    
    # Relationships
    votes = relationship("GovernanceVote", back_populates="session", cascade="all, delete-orphan")
    
class GovernanceVote(Base):
    """Individual vote in a session"""
    __tablename__ = "governance_votes"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("governance_sessions.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("governance_members.id"), nullable=False)
    
    # Vote
    vote = Column(String(16), nullable=False)  # approve, reject, abstain
    vote_weight = Column(Float, default=1.0)  # Captured at vote time
    
    # Reasoning
    reason = Column(Text, nullable=True)
    automated = Column(Boolean, default=False)  # True if cast by an agent/Grace
    
    # Confidence (for agent votes)
    confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Signature & verification
    vote_signature = Column(String(256), nullable=True)
    verification_status = Column(String(32), default="pending")  # pending, verified, failed
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Audit
    audit_log_id = Column(Integer, nullable=True)
    
    # Relationships
    session = relationship("GovernanceSession", back_populates="votes")
    member = relationship("GovernanceMember", back_populates="votes")

class CommitteeDefinition(Base):
    """Define committees and their responsibilities"""
    __tablename__ = "committees"
    
    id = Column(Integer, primary_key=True)
    committee_name = Column(String(64), unique=True, nullable=False)
    display_name = Column(String(128), nullable=False)
    
    # Purpose
    description = Column(Text, nullable=True)
    responsibilities = Column(JSON, default=list)  # List of action types this committee handles
    
    # Membership
    member_ids = Column(JSON, default=list)  # List of member_ids
    min_members = Column(Integer, default=3)
    max_members = Column(Integer, default=10)
    
    # Quorum settings
    default_quorum = Column(Integer, default=3)
    default_threshold = Column(Float, default=0.5)
    
    # Auto-assignment rules
    auto_assign_categories = Column(JSON, default=list)  # Categories to auto-assign
    auto_assign_risk_levels = Column(JSON, default=list)  # Risk levels to auto-assign
    
    # Status
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ParliamentConfig(Base):
    """Global parliament configuration"""
    __tablename__ = "parliament_config"
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(64), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
