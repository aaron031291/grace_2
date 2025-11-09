"""
Lightning and Fusion Memory Database Models
Integrates with existing memory stack
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from .base_models import Base


class CryptoIdentity(Base):
    """Universal cryptographic identities for all Grace entities"""
    __tablename__ = "crypto_identities"
    
    id = Column(Integer, primary_key=True)
    crypto_id = Column(String(128), unique=True, nullable=False, index=True)
    entity_id = Column(String(256), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)  # grace_components, messages, files, bots, users, decisions
    crypto_standard = Column(String(128), nullable=False)
    signature = Column(Text, nullable=False)
    constitutional_validated = Column(Boolean, default=False)
    trust_score = Column(Float, nullable=True)
    immutable_log_sequence = Column(Integer, nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved word)


class FusionMemoryFragment(Base):
    """Fusion memory fragments with full verification"""
    __tablename__ = "fusion_memory_fragments"
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(String(64), unique=True, nullable=False, index=True)
    crypto_id = Column(String(128), ForeignKey("crypto_identities.crypto_id"), nullable=False)
    
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    
    # Verification metadata
    verification_status = Column(String(32), nullable=False, default="validated")  # validated, pending, rejected
    verification_confidence = Column(Float, nullable=False)
    verification_method = Column(String(64), nullable=True)
    verification_details = Column(JSON, nullable=True)
    
    # Constitutional compliance
    constitutional_approved = Column(Boolean, default=False)
    constitutional_check_details = Column(JSON, nullable=True)
    
    # Source tracking
    source_type = Column(String(64), nullable=False)  # web_scraping, api_call, github, reddit, etc.
    source_url = Column(Text, nullable=True)
    source_metadata = Column(JSON, nullable=True)
    
    # Memory properties
    importance = Column(Float, default=0.5)
    memory_type = Column(String(32), default="semantic")
    
    # Linking to existing memory systems
    persistent_memory_id = Column(Integer, ForeignKey("memory_artifacts.id"), nullable=True)
    
    # Timestamps
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)
    
    # Retention
    expiry_at = Column(DateTime(timezone=True), nullable=True)


class LightningMemoryCache(Base):
    """Lightning-fast memory cache for sub-millisecond access"""
    __tablename__ = "lightning_memory_cache"
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(128), unique=True, nullable=False, index=True)
    cache_value = Column(JSON, nullable=False)
    
    crypto_id = Column(String(128), ForeignKey("crypto_identities.crypto_id"), nullable=True)
    
    # Performance tracking
    access_count = Column(Integer, default=0)
    avg_access_time_ms = Column(Float, nullable=True)
    last_access_ms = Column(Float, nullable=True)
    
    # Cache management
    cache_type = Column(String(64), nullable=False)  # pattern, constitutional, decision
    priority = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class ComponentCryptoRegistration(Base):
    """Registry of all Grace component cryptographic identities"""
    __tablename__ = "component_crypto_registry"
    
    id = Column(Integer, primary_key=True)
    component_id = Column(String(128), unique=True, nullable=False, index=True)
    component_type = Column(String(128), nullable=False)
    crypto_id = Column(String(128), ForeignKey("crypto_identities.crypto_id"), nullable=False)
    
    # Component metadata
    layer = Column(String(64), nullable=True)  # governance, event_mesh, memory, immutable, ai_ml, self_heal, external, ui
    component_name = Column(String(256), nullable=True)
    
    # Registration status
    initialized = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Performance tracking
    operations_signed = Column(Integer, default=0)
    signatures_validated = Column(Integer, default=0)
    validation_failures = Column(Integer, default=0)
    
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_operation_at = Column(DateTime(timezone=True), nullable=True)


class DiagnosticTrace(Base):
    """Lightning diagnostic traces for instant problem resolution"""
    __tablename__ = "diagnostic_traces"
    
    id = Column(Integer, primary_key=True)
    trace_id = Column(String(64), unique=True, nullable=False, index=True)
    
    # Problem details
    problem_type = Column(String(128), nullable=False)
    problem_indicators = Column(JSON, nullable=False)
    affected_components = Column(JSON, nullable=True)
    symptoms = Column(JSON, nullable=True)
    
    # Diagnosis
    diagnosis = Column(Text, nullable=False)
    root_cause = Column(String(256), nullable=True)
    resolution_confidence = Column(Float, nullable=False)
    
    # Resolution
    recommended_playbooks = Column(JSON, nullable=True)
    playbooks_executed = Column(JSON, nullable=True)
    resolution_status = Column(String(32), default="diagnosed")  # diagnosed, healing, resolved, escalated
    
    # Crypto trace
    crypto_trace_data = Column(JSON, nullable=True)
    cross_component_correlation = Column(JSON, nullable=True)
    
    # Performance
    diagnosis_duration_ms = Column(Float, nullable=False)
    sub_millisecond = Column(Boolean, default=False)
    
    # Immutable audit
    immutable_log_sequence = Column(Integer, nullable=True)
    
    diagnosed_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class VerificationAuditLog(Base):
    """Audit log for all Fusion Memory verification operations"""
    __tablename__ = "verification_audit_log"
    
    id = Column(Integer, primary_key=True)
    verification_id = Column(String(64), unique=True, nullable=False, index=True)
    
    # Content being verified
    content_hash = Column(String(64), nullable=False, index=True)
    source_type = Column(String(64), nullable=False)
    crypto_id = Column(String(128), ForeignKey("crypto_identities.crypto_id"), nullable=True)
    
    # Verification result
    verified = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    verification_method = Column(String(64), nullable=True)
    verification_details = Column(JSON, nullable=True)
    
    # Constitutional check
    constitutional_approved = Column(Boolean, default=False)
    constitutional_check_details = Column(JSON, nullable=True)
    
    # Storage result
    stored = Column(Boolean, default=False)
    memory_id = Column(String(64), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Immutable audit
    immutable_log_sequence = Column(Integer, nullable=True)
    
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
