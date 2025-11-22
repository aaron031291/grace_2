"""
Database models for Immutable Audit Logs
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ImmutableAuditLog(Base):
    """
    Immutable Audit Log table - stores all auditable events with cryptographic integrity

    This table provides the persistent storage for Grace's audit trail.
    Once written, entries cannot be modified or deleted.
    """
    __tablename__ = "immutable_audit_logs"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core audit fields
    entry_id = Column(String(255), unique=True, nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False, index=True)

    # Cryptographic chain
    prev_hash = Column(String(64), nullable=False, index=True)
    hash = Column(String(64), nullable=False, index=True)

    # Event metadata
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    actor = Column(String(255), nullable=False, index=True)
    resource = Column(String(500), nullable=False)

    # Event data
    payload = Column(Text, nullable=False)  # JSON string

    # Trust and governance
    trust_score = Column(Float, nullable=True)
    governance_tier = Column(String(50), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified = Column(Boolean, default=True, nullable=False)  # Hash verification status

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_audit_timestamp_actor', 'timestamp', 'actor'),
        Index('idx_audit_event_resource', 'event_type', 'resource'),
        Index('idx_audit_sequence', 'sequence_number'),
        Index('idx_audit_governance', 'governance_tier', 'trust_score'),
    )


class AuditChainVerification(Base):
    """
    Chain verification results - tracks integrity checks
    """
    __tablename__ = "audit_chain_verifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_entries = Column(Integer, nullable=False)
    verified_entries = Column(Integer, nullable=False)
    chain_integrity = Column(Boolean, nullable=False)
    issues_found = Column(Text, nullable=True)  # JSON array of issues
    verification_duration_ms = Column(Float, nullable=False)


class AuditRetentionPolicy(Base):
    """
    Audit retention policies and archival status
    """
    __tablename__ = "audit_retention_policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_name = Column(String(100), nullable=False)
    retention_days = Column(Integer, nullable=False)
    archival_required = Column(Boolean, default=False, nullable=False)
    last_cleanup = Column(DateTime, nullable=True)
    entries_cleaned = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)</code></edit_file>
