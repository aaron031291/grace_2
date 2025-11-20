"""
Base database models and session management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./grace.db")

# Create async engine with SQLite-specific configuration
engine_kwargs = {
    "echo": False,
    "future": True
}

# For SQLite, ensure compatibility with RETURNING clause
if DATABASE_URL.startswith("sqlite"):
    # aiosqlite handles async properly, no need for check_same_thread
    # SQLAlchemy 2.0+ with SQLite 3.35+ supports RETURNING
    pass

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Export async_session for backward compatibility
async_session = async_session_maker

# Context manager for database sessions
async def get_db_session():
    """Get database session context manager"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


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


class CAPARecord(Base):
    """Corrective and Preventive Action records (ISO 9001)"""
    __tablename__ = "capa_records"
    
    id = Column(Integer, primary_key=True)
    capa_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    capa_type = Column(String(16), nullable=False)  # corrective, preventive
    severity = Column(String(16), nullable=False)  # critical, high, medium, low
    source = Column(String(64), nullable=False)  # anomaly, customer, audit, internal
    
    # Linkage
    related_update_id = Column(String(64), nullable=True)
    detected_by = Column(String(64), nullable=False)
    
    # Status
    status = Column(String(32), default="open", index=True)
    
    # Analysis
    root_cause = Column(Text, nullable=True)
    root_cause_analysis = Column(Text, nullable=True)  # JSON
    
    # Actions
    corrective_actions = Column(Text, nullable=True)  # JSON
    preventive_actions = Column(Text, nullable=True)  # JSON
    implementation_plan = Column(Text, nullable=True)  # JSON
    
    # Implementation
    implemented_at = Column(DateTime(timezone=True), nullable=True)
    implemented_by = Column(String(64), nullable=True)
    
    # Verification
    verification_results = Column(Text, nullable=True)  # JSON
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(64), nullable=True)
    effective = Column(Boolean, nullable=True)
    
    # Closure
    closed_at = Column(DateTime(timezone=True), nullable=True)
    closed_by = Column(String(64), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ComponentRegistration(Base):
    """Component handshake and registry"""
    __tablename__ = "component_registry"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(String(128), unique=True, nullable=False, index=True)
    component_type = Column(String(64), nullable=False)
    version = Column(String(32), nullable=False)
    
    # Capabilities
    capabilities = Column(Text, nullable=False)  # JSON
    expected_metrics = Column(Text, nullable=False)  # JSON
    
    # Handshake
    handshake_id = Column(String(64), nullable=True)
    crypto_signature = Column(String(128), nullable=True)
    
    # Status
    status = Column(String(32), default="pending")
    
    # Timestamps
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    integrated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy and metadata
    sensitive_data_redacted = Column(Boolean, default=False)
    meta_data = Column(Text)

