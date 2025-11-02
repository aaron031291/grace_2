"""Secure Secrets Vault for External API Credentials

Stores API keys, tokens, and credentials with encryption and governance.
Integrates with system keyring and supports multiple backend stores.
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from .models import Base, async_session
from .verification import VerificationEngine
from .immutable_log import ImmutableLogger
from .governance import GovernanceEngine

class SecretEntry(Base):
    """Encrypted secret storage"""
    __tablename__ = "secrets"
    
    id = Column(Integer, primary_key=True)
    secret_key = Column(String(128), unique=True, nullable=False)
    secret_type = Column(String(64), nullable=False)  # api_key, token, password, certificate
    
    # Encrypted data
    encrypted_value = Column(Text, nullable=False)
    encryption_method = Column(String(32), default="fernet")
    
    # Metadata
    description = Column(Text, nullable=True)
    owner = Column(String(64), nullable=False)
    service = Column(String(128), nullable=True)  # github, slack, aws, etc.
    
    # Access control
    allowed_users = Column(JSON, default=list)
    allowed_services = Column(JSON, default=list)
    
    # Rotation
    expires_at = Column(DateTime(timezone=True), nullable=True)
    rotation_days = Column(Integer, nullable=True)  # Auto-rotate every N days
    last_rotated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    accessed_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_by = Column(String(64), nullable=True)
    
    # Status
    active = Column(Boolean, default=True)
    revoked = Column(Boolean, default=False)
    revoked_reason = Column(Text, nullable=True)
    
    # Audit
    verification_envelope_id = Column(Integer, nullable=True)
    audit_log_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SecretAccessLog(Base):
    """Log of secret access attempts"""
    __tablename__ = "secret_access_log"
    
    id = Column(Integer, primary_key=True)
    secret_key = Column(String(128), nullable=False)
    accessor = Column(String(64), nullable=False)
    access_type = Column(String(32), nullable=False)  # read, create, update, delete, rotate
    
    # Result
    success = Column(Boolean, nullable=False)
    denied_reason = Column(Text, nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(256), nullable=True)
    service = Column(String(64), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SecretsVault:
    """Secure vault for API credentials and secrets"""
    
    def __init__(self, master_password: Optional[str] = None):
        """
        Initialize secrets vault
        
        Args:
            master_password: Optional master password for encryption.
                            If not provided, uses environment variable GRACE_VAULT_KEY
        """
        
        # Get or generate encryption key
        if master_password:
            self.encryption_key = self._derive_key(master_password)
        else:
            env_key = os.getenv("GRACE_VAULT_KEY")
            if env_key:
                self.encryption_key = env_key.encode()
            else:
                # Generate new key (should be saved securely in production)
                self.encryption_key = Fernet.generate_key()
                print("⚠ Warning: Generated new vault key. Set GRACE_VAULT_KEY environment variable.")
        
        self.cipher = Fernet(self.encryption_key)
        self.verification = VerificationEngine()
        self.audit = ImmutableLogger()
        self.governance = GovernanceEngine()
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        
        if salt is None:
            salt = b'grace_vault_salt_2025'  # Fixed salt (use random in production with storage)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _encrypt(self, value: str) -> str:
        """Encrypt a value"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt a value"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    async def store_secret(
        self,
        secret_key: str,
        secret_value: str,
        secret_type: str,
        owner: str,
        service: Optional[str] = None,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        rotation_days: Optional[int] = None,
        allowed_users: List[str] = None,
        allowed_services: List[str] = None
    ) -> Dict[str, Any]:
        """
        Store a secret in the vault
        
        Args:
            secret_key: Unique identifier for the secret
            secret_value: The actual secret (API key, token, etc.)
            secret_type: Type (api_key, token, password, certificate)
            owner: Who owns this secret
            service: Which service (github, slack, aws, etc.)
            description: Human-readable description
            expires_in_days: Optional expiration in days
            rotation_days: Auto-rotate every N days
            allowed_users: List of users allowed to access
            allowed_services: List of services allowed to access
        
        Returns:
            Storage confirmation
        """
        
        # Check governance
        gov_result = await self.governance.check_policy(
            actor=owner,
            action="secret_create",
            resource=f"secret_{secret_key}",
            context={"secret_type": secret_type, "service": service}
        )
        
        if gov_result["decision"] == "deny":
            raise PermissionError(f"Governance denied secret creation: {gov_result['reason']}")
        
        # Encrypt the secret
        encrypted_value = self._encrypt(secret_value)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create verification envelope
        secret_hash = hashlib.sha256(secret_value.encode()).hexdigest()
        verification_id = self.verification.create_envelope(
            action_id=f"secret_{secret_key}",
            actor=owner,
            action_type="secret_store",
            resource=secret_key,
            input_data={"secret_hash": secret_hash, "service": service}
        )
        
        # Store in database
        async with async_session() as session:
            # Check if exists
            from sqlalchemy import select
            result = await session.execute(
                select(SecretEntry).where(SecretEntry.secret_key == secret_key)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing
                existing.encrypted_value = encrypted_value
                existing.secret_type = secret_type
                existing.description = description
                existing.service = service
                existing.expires_at = expires_at
                existing.rotation_days = rotation_days
                existing.allowed_users = allowed_users or []
                existing.allowed_services = allowed_services or []
                existing.last_rotated_at = datetime.utcnow()
                existing.verification_envelope_id = verification_id
                existing.updated_at = datetime.utcnow()
                
                action = "updated"
            else:
                # Create new
                secret_entry = SecretEntry(
                    secret_key=secret_key,
                    secret_type=secret_type,
                    encrypted_value=encrypted_value,
                    description=description,
                    owner=owner,
                    service=service,
                    expires_at=expires_at,
                    rotation_days=rotation_days,
                    allowed_users=allowed_users or [],
                    allowed_services=allowed_services or [],
                    last_rotated_at=datetime.utcnow(),
                    verification_envelope_id=verification_id,
                    active=True
                )
                session.add(secret_entry)
                action = "created"
            
            await session.commit()
        
        # Log to audit
        audit_id = await self.audit.log_event(
            actor=owner,
            action=f"secret_{action}",
            resource=secret_key,
            result="success",
            details={"service": service, "type": secret_type}
        )
        
        # Log access
        await self._log_access(secret_key, owner, "create", True)
        
        return {
            "secret_key": secret_key,
            "action": action,
            "service": service,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "verification_id": verification_id,
            "message": f"Secret {action} successfully"
        }
    
    async def retrieve_secret(
        self,
        secret_key: str,
        accessor: str,
        service: Optional[str] = None
    ) -> str:
        """
        Retrieve a secret from the vault
        
        Args:
            secret_key: Secret identifier
            accessor: Who is accessing
            service: Which service is accessing (optional)
        
        Returns:
            Decrypted secret value
        
        Raises:
            PermissionError: If access denied
            ValueError: If secret not found or expired
        """
        
        # Get secret
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SecretEntry).where(SecretEntry.secret_key == secret_key)
            )
            secret_entry = result.scalar_one_or_none()
            
            if not secret_entry:
                await self._log_access(secret_key, accessor, "read", False, "Secret not found")
                raise ValueError(f"Secret not found: {secret_key}")
            
            # Check if active
            if not secret_entry.active or secret_entry.revoked:
                await self._log_access(secret_key, accessor, "read", False, "Secret revoked")
                raise PermissionError(f"Secret is revoked or inactive")
            
            # Check expiration
            if secret_entry.expires_at and datetime.utcnow() > secret_entry.expires_at:
                await self._log_access(secret_key, accessor, "read", False, "Secret expired")
                raise ValueError(f"Secret has expired")
            
            # Check access permissions
            if secret_entry.allowed_users and accessor not in secret_entry.allowed_users:
                await self._log_access(secret_key, accessor, "read", False, "User not allowed")
                raise PermissionError(f"Access denied for user: {accessor}")
            
            if service and secret_entry.allowed_services and service not in secret_entry.allowed_services:
                await self._log_access(secret_key, accessor, "read", False, "Service not allowed")
                raise PermissionError(f"Access denied for service: {service}")
            
            # Check governance
            gov_result = await self.governance.check_policy(
                actor=accessor,
                action="secret_read",
                resource=f"secret_{secret_key}",
                context={"service": secret_entry.service}
            )
            
            if gov_result["decision"] == "deny":
                await self._log_access(secret_key, accessor, "read", False, "Governance denied")
                raise PermissionError(f"Governance denied access: {gov_result['reason']}")
            
            # Update access tracking
            secret_entry.accessed_count += 1
            secret_entry.last_accessed_at = datetime.utcnow()
            secret_entry.last_accessed_by = accessor
            
            await session.commit()
            
            encrypted_value = secret_entry.encrypted_value
        
        # Decrypt
        decrypted_value = self._decrypt(encrypted_value)
        
        # Log access
        await self._log_access(secret_key, accessor, "read", True)
        
        # Audit
        await self.audit.log_event(
            actor=accessor,
            action="secret_accessed",
            resource=secret_key,
            result="success",
            details={"service": service}
        )
        
        return decrypted_value
    
    async def _log_access(
        self,
        secret_key: str,
        accessor: str,
        access_type: str,
        success: bool,
        denied_reason: Optional[str] = None
    ):
        """Log secret access attempt"""
        
        async with async_session() as session:
            log_entry = SecretAccessLog(
                secret_key=secret_key,
                accessor=accessor,
                access_type=access_type,
                success=success,
                denied_reason=denied_reason
            )
            session.add(log_entry)
            await session.commit()
    
    async def list_secrets(
        self,
        owner: Optional[str] = None,
        service: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """List secrets (metadata only, not values)"""
        
        async with async_session() as session:
            from sqlalchemy import select
            query = select(SecretEntry)
            
            if owner:
                query = query.where(SecretEntry.owner == owner)
            if service:
                query = query.where(SecretEntry.service == service)
            if not include_inactive:
                query = query.where(SecretEntry.active == True, SecretEntry.revoked == False)
            
            result = await session.execute(query)
            secrets = result.scalars().all()
            
            return [
                {
                    "secret_key": s.secret_key,
                    "secret_type": s.secret_type,
                    "service": s.service,
                    "description": s.description,
                    "owner": s.owner,
                    "active": s.active,
                    "revoked": s.revoked,
                    "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                    "accessed_count": s.accessed_count,
                    "last_accessed_at": s.last_accessed_at.isoformat() if s.last_accessed_at else None,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in secrets
            ]
    
    async def revoke_secret(
        self,
        secret_key: str,
        actor: str,
        reason: str
    ) -> Dict[str, Any]:
        """Revoke a secret"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SecretEntry).where(SecretEntry.secret_key == secret_key)
            )
            secret_entry = result.scalar_one_or_none()
            
            if not secret_entry:
                raise ValueError(f"Secret not found: {secret_key}")
            
            secret_entry.revoked = True
            secret_entry.active = False
            secret_entry.revoked_reason = reason
            
            await session.commit()
        
        # Audit
        await self.audit.log_event(
            actor=actor,
            action="secret_revoked",
            resource=secret_key,
            result="success",
            details={"reason": reason}
        )
        
        return {"secret_key": secret_key, "status": "revoked", "reason": reason}

secrets_vault = SecretsVault()
