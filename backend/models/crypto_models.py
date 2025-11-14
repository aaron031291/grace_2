"""
Crypto Models - Persistent Storage for Cryptographic Keys
Stores encrypted private keys and public key registry
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.sql import func
from .base_models import Base


class CryptoKeyStore(Base):
    """
    Persistent storage for cryptographic keys
    
    Security:
    - Private keys stored encrypted with master key
    - Public keys stored in PEM format
    - Key rotation tracked
    - Audit trail maintained
    """
    __tablename__ = "crypto_key_store"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Key identification
    key_id = Column(String(128), unique=True, nullable=False, index=True)
    component_id = Column(String(128), nullable=False, index=True)
    key_type = Column(String(32), default="ed25519", nullable=False)
    
    # Key material (encrypted)
    private_key_encrypted = Column(Text, nullable=False)  # Encrypted PEM
    public_key_pem = Column(Text, nullable=False)  # Public key (not encrypted)
    
    # Encryption metadata
    encryption_algorithm = Column(String(64), default="fernet")
    key_derivation = Column(String(64), default="pbkdf2")
    
    # Lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    rotated_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_rotated = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    purpose = Column(String(128), nullable=True)  # signing, encryption, etc.
    key_metadata = Column(Text, nullable=True)  # JSON blob (renamed to avoid SQLAlchemy conflict)
    
    # Audit
    created_by = Column(String(128), default="crypto_key_manager")
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    use_count = Column(Integer, default=0)


class ComponentCryptoIdentity(Base):
    """
    Registry of component crypto identities and public keys
    Allows signature verification without accessing private keys
    """
    __tablename__ = "component_crypto_identities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    component_id = Column(String(128), unique=True, nullable=False, index=True)
    current_key_id = Column(String(128), nullable=False)
    public_key_pem = Column(Text, nullable=False)
    
    # Identity verification
    identity_hash = Column(String(64), nullable=False)  # Hash of public key
    verified = Column(Boolean, default=False)
    
    # Metadata
    component_type = Column(String(64), nullable=True)  # kernel, service, agent
    capabilities = Column(Text, nullable=True)  # JSON list
    
    # Lifecycle
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_rotation_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Audit
    total_signatures = Column(Integer, default=0)
    last_signature_at = Column(DateTime(timezone=True), nullable=True)
