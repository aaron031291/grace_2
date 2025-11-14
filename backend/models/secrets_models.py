"""
Secrets Vault Models
Secure storage for API keys, passwords, tokens, and credentials

NEVER store secrets in general memory - use dedicated encrypted storage
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, Float, JSON
from sqlalchemy.sql import func
from .base_models import Base


class SecretVault(Base):
    """
    Encrypted secrets storage
    
    Security:
    - Value stored encrypted with Fernet
    - Only hash stored for change detection
    - Metadata tracked for governance
    - Access logged to audit trail
    - Never logged in plaintext
    """
    __tablename__ = "secret_vault"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Secret identification
    secret_id = Column(String(128), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=False)  # User-provided label
    secret_type = Column(String(64), nullable=False, index=True)
    # Types: api_key, password, token, oauth_token, ssh_key, certificate
    
    # Encrypted value
    encrypted_value = Column(Text, nullable=False)  # Fernet encrypted
    value_hash = Column(String(64), nullable=False, index=True)  # SHA256 for change detection
    
    # Encryption metadata
    encryption_algorithm = Column(String(64), default="fernet")
    key_derivation = Column(String(64), default="master_key")
    salt = Column(String(128), nullable=True)  # For additional key derivation
    
    # Scope and permissions
    scope = Column(String(256), nullable=False)  # What this secret is for
    environment = Column(String(32), default="production")  # prod, staging, dev
    service_name = Column(String(128), nullable=True)  # External service name
    allowed_agents = Column(JSON, default=list)  # Which agents can access
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), nullable=False)  # User or agent
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_rotated_at = Column(DateTime(timezone=True), nullable=True)
    rotation_interval_days = Column(Integer, default=90)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_validated = Column(Boolean, default=False)  # Tested and working
    validation_status = Column(String(32), nullable=True)  # passed, failed, pending
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_by = Column(String(128), nullable=True)
    
    # Governance
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    governance_policy_id = Column(String(128), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    source = Column(String(128), default="ui_capture")  # ui_capture, api, import, discovered
    
    # Security flags
    high_privilege = Column(Boolean, default=False)  # Write access, admin, etc.
    production_only = Column(Boolean, default=True)  # Restrict to prod environment
    audit_all_access = Column(Boolean, default=True)  # Log every access


class SecretAccessLog(Base):
    """
    Audit log for secret access
    Every secret redemption/access is logged
    """
    __tablename__ = "secret_access_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # What was accessed
    secret_id = Column(String(128), nullable=False, index=True)
    secret_name = Column(String(256), nullable=False)
    
    # Who accessed
    accessed_by = Column(String(128), nullable=False, index=True)
    agent_type = Column(String(64), nullable=True)  # librarian, remote_access, ingestion
    
    # When and why
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    purpose = Column(String(256), nullable=False)  # "ingestion_task_123", "remote_login"
    task_id = Column(String(128), nullable=True, index=True)  # HTM task ID
    intent_id = Column(String(128), nullable=True, index=True)  # Layer 3 intent ID
    
    # Result
    access_granted = Column(Boolean, nullable=False)
    denial_reason = Column(String(256), nullable=True)
    
    # Usage details
    duration_seconds = Column(Float, nullable=True)  # How long secret was in memory
    operations_performed = Column(JSON, nullable=True)  # What was done with it
    success = Column(Boolean, nullable=True)  # Did the operation succeed
    
    # Security
    source_ip = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)
    governance_check_id = Column(String(128), nullable=True)


class ContactRegistry(Base):
    """
    Contact information storage (emails, phone numbers)
    Separate from secrets - requires explicit opt-in
    """
    __tablename__ = "contact_registry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Contact info
    contact_id = Column(String(128), unique=True, nullable=False, index=True)
    contact_type = Column(String(32), nullable=False)  # email, phone, slack, etc.
    contact_value = Column(String(256), nullable=False)  # The actual email/phone
    
    # Purpose
    purpose = Column(String(128), nullable=False)  # login, notification, support, billing
    service_name = Column(String(128), nullable=True)  # Which service uses this
    
    # Consent
    opted_in = Column(Boolean, default=False, nullable=False)
    consent_given_at = Column(DateTime(timezone=True), nullable=True)
    consent_source = Column(String(64), default="ui_prompt")  # ui_prompt, import, manual
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), nullable=False)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary contact for user
    
    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)


class SecretValidation(Base):
    """
    Secret validation results
    Tracks whether secrets work when tested
    """
    __tablename__ = "secret_validations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    secret_id = Column(String(128), nullable=False, index=True)
    
    # Validation details
    validated_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_by = Column(String(128), default="librarian")
    validation_method = Column(String(64), nullable=False)  # sandbox_api_call, test_login
    
    # Result
    validation_passed = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    http_status = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    
    # Details
    endpoint_tested = Column(String(512), nullable=True)
    test_payload = Column(JSON, nullable=True)  # Sanitized test data
    validation_context = Column(JSON, nullable=True)
