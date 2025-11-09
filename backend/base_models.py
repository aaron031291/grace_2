"""
Base Models - Foundation Layer

Core database models that all agentic systems build upon.
No circular dependencies - this is the bottom of the stack.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .settings import settings

# Database setup
DATABASE_URL = settings.DATABASE_URL or "sqlite+aiosqlite:///./databases/grace.db"
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "timeout": 30,
        "check_same_thread": False
    },
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for all models
Base = declarative_base()


class ImmutableLogEntry(Base):
    """Tamper-proof append-only audit log - Foundation for all agentic systems"""
    __tablename__ = "immutable_log"
    
    id = Column(Integer, primary_key=True)
    sequence = Column(Integer, unique=True, nullable=False)
    actor = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    resource = Column(String(256))
    subsystem = Column(String(64))
    payload = Column(Text)
    result = Column(String(64))
    entry_hash = Column(String(64), nullable=False, unique=True)
    previous_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    @staticmethod
    def compute_hash(sequence: int, actor: str, action: str, resource: str, payload: str, result: str, previous_hash: str) -> str:
        """Cryptographic hash for tamper detection"""
        import hashlib
        data = f"{sequence}:{actor}:{action}:{resource}:{payload}:{result}:{previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()


class AgenticInsight(Base):
    """Compact agentic decision ledger - Transparency layer"""
    __tablename__ = "agentic_insights"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), nullable=False, index=True)
    phase = Column(String(32), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # What the agent perceived
    signal_type = Column(String(64))
    signal_summary = Column(String(256))
    
    # What the agent diagnosed
    diagnosis = Column(String(256))
    root_cause = Column(String(256))
    
    # What the agent planned
    plan_type = Column(String(64))
    plan_summary = Column(String(512))
    
    # Guardrails and trust
    guardrails_checked = Column(Text)
    guardrails_passed = Column(Boolean)
    risk_score = Column(Float)
    confidence = Column(Float)
    
    # Decision rationale
    rationale = Column(Text)
    options_considered = Column(Text)
    chosen_option = Column(String(256))
    
    # Approval and execution
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String(64))
    approved_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    
    # Outcome
    outcome = Column(String(64))
    outcome_detail = Column(Text)
    verified = Column(Boolean)


class LogicUpdateRecord(Base):
    """Persistent registry for Unified Logic Hub updates"""
    __tablename__ = "logic_updates"
    
    id = Column(Integer, primary_key=True)
    update_id = Column(String(64), unique=True, nullable=False, index=True)
    update_type = Column(String(32), nullable=False)  # schema, code_module, playbook, config, metric_definition
    version = Column(String(32), nullable=False)
    
    # Targets
    component_targets = Column(Text, nullable=False)  # JSON array of component IDs
    
    # Content checksums
    checksum = Column(String(64), nullable=True)
    
    # Governance & Crypto
    governance_approval_id = Column(String(128), nullable=True)
    crypto_id = Column(String(128), nullable=True)
    crypto_signature = Column(String(128), nullable=True)
    
    # Status
    status = Column(String(32), default="proposed")  # proposed, validated, approved, distributed, failed, rolled_back
    
    # Validation
    validation_results = Column(Text, nullable=True)  # JSON
    diagnostics = Column(Text, nullable=True)  # JSON array
    
    # Rollback
    previous_version = Column(String(32), nullable=True)
    rollback_instructions = Column(Text, nullable=True)  # JSON
    
    # Metadata
    created_by = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    risk_level = Column(String(16), default="medium")
    
    # Observability
    immutable_log_sequence = Column(Integer, nullable=True)
    trigger_mesh_event_id = Column(String(64), nullable=True)
    
    # Outcome tracking
    distributed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy and metadata
    sensitive_data_redacted = Column(Boolean, default=False)
    meta_data = Column(Text)
