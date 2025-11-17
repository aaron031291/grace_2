"""
Secrets Service - Secure Credential Management

NEVER store secrets in general memory!
Use this dedicated encrypted vault with governance.

Features:
- Fernet encryption for all secret values
- Change detection via hashing
- Access logging (who/when/why)
- Governance integration
- Validation workflow
- Automatic redaction
"""

import hashlib
import base64
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet

from backend.models.secrets_models import SecretVault, SecretAccessLog, ContactRegistry, SecretValidation
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from backend.core.message_bus import message_bus, MessagePriority
from sqlalchemy import select, update, desc


class SecretType:
    """Common secret types"""
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    OAUTH_TOKEN = "oauth_token"
    SSH_KEY = "ssh_key"
    CERTIFICATE = "certificate"
    DATABASE_URL = "database_url"


class SecretsService:
    """
    Dedicated secrets vault service
    
    Usage:
        # Store secret
        secret_id = await secrets_service.store_secret(
            name="Stripe API Key",
            value="sk_live_...",
            secret_type=SecretType.API_KEY,
            scope="payment_processing",
            created_by="user_123"
        )
        
        # Retrieve secret (logged)
        value = await secrets_service.get_secret(
            secret_id=secret_id,
            requested_by="librarian",
            purpose="salesforce_ingestion"
        )
        
        # Automatic redaction
        redacted = secrets_service.redact("My key is sk_live_123456")
        # Returns: "My key is sk_***REDACTED***"
    """
    
    def __init__(self):
        self._master_key = None
        self._fernet = None
        
        # Secret detection patterns
        self.secret_patterns = {
            "openai_key": re.compile(r'sk-[A-Za-z0-9]{48}'),
            "stripe_key": re.compile(r'sk_(live|test)_[A-Za-z0-9]{24,}'),
            "aws_key": re.compile(r'AKIA[0-9A-Z]{16}'),
            "github_token": re.compile(r'ghp_[A-Za-z0-9]{36}'),
            "generic_key": re.compile(r'[A-Za-z0-9_-]{32,}')
        }
        
        # Email pattern
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    def _get_master_key(self) -> bytes:
        """Get or create master encryption key"""
        if self._master_key:
            return self._master_key
        
        import os
        
        # Check environment variable
        env_key = os.getenv("GRACE_SECRETS_MASTER_KEY")
        if env_key:
            self._master_key = base64.b64decode(env_key)
            return self._master_key
        
        # Check file
        key_file = os.path.join(os.path.expanduser("~"), ".grace", "secrets_master.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self._master_key = f.read()
                return self._master_key
        
        # Generate new master key
        self._master_key = Fernet.generate_key()
        
        # Save to file
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(self._master_key)
        
        print(f"[SECRETS] Generated new secrets master key: {key_file}")
        
        return self._master_key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet cipher"""
        if not self._fernet:
            self._fernet = Fernet(self._get_master_key())
        return self._fernet
    
    def _encrypt(self, value: str) -> str:
        """Encrypt secret value"""
        f = self._get_fernet()
        encrypted = f.encrypt(value.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt secret value"""
        f = self._get_fernet()
        encrypted_bytes = base64.b64decode(encrypted_value)
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def _hash_value(self, value: str) -> str:
        """Hash value for change detection"""
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    async def store_secret(
        self,
        name: str,
        value: str,
        secret_type: str,
        scope: str,
        created_by: str,
        environment: str = "production",
        service_name: Optional[str] = None,
        description: Optional[str] = None,
        expires_days: Optional[int] = None,
        high_privilege: bool = False,
        allowed_agents: Optional[List[str]] = None,
        requires_approval: bool = True
    ) -> str:
        """
        Store secret in encrypted vault
        
        Args:
            name: User-friendly label ("Stripe API Key")
            value: The actual secret (will be encrypted)
            secret_type: Type of secret (api_key, password, etc.)
            scope: What it's used for ("payment_processing")
            created_by: Who created it
            
        Returns:
            secret_id for retrieval
        """
        # Generate secret ID
        secret_id = f"secret_{secret_type}_{datetime.now(timezone.utc).timestamp()}"
        
        # Encrypt value
        encrypted_value = self._encrypt(value)
        value_hash = self._hash_value(value)
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
        
        # Store in database
        async with async_session() as session:
            secret_record = SecretVault(
                secret_id=secret_id,
                name=name,
                secret_type=secret_type,
                encrypted_value=encrypted_value,
                value_hash=value_hash,
                scope=scope,
                environment=environment,
                service_name=service_name,
                allowed_agents=allowed_agents or [],
                created_by=created_by,
                expires_at=expires_at,
                is_active=True,
                is_validated=False,
                requires_approval=requires_approval,
                description=description,
                high_privilege=high_privilege,
                source="ui_capture"
            )
            session.add(secret_record)
            await session.commit()
        
        # Log to audit (NO SECRET VALUE)
        log_event(
            action="secret.stored",
            actor=created_by,
            resource=secret_id,
            outcome="ok",
            payload={
                "secret_id": secret_id,
                "name": name,
                "type": secret_type,
                "scope": scope,
                "environment": environment,
                "requires_approval": requires_approval
            }
        )
        
        # Publish event for Librarian workflow
        await message_bus.publish(
            source="secrets_service",
            topic="secrets.stored",
            payload={
                "secret_id": secret_id,
                "name": name,
                "type": secret_type,
                "scope": scope,
                "requires_validation": True,
                "requires_approval": requires_approval
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"[SECRETS] Stored: {name} ({secret_type}) - {secret_id}")
        
        return secret_id
    
    async def get_secret(
        self,
        secret_id: str,
        requested_by: str,
        purpose: str,
        task_id: Optional[str] = None,
        intent_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Retrieve and decrypt secret
        
        IMPORTANT: Access is logged and governed!
        
        Args:
            secret_id: Secret identifier
            requested_by: Agent/user requesting access
            purpose: Why the secret is needed
            task_id: HTM task ID (if applicable)
            intent_id: Layer 3 intent ID (if applicable)
            
        Returns:
            Decrypted secret value or None if denied
        """
        start_time = datetime.now(timezone.utc)
        
        # Load secret from database
        async with async_session() as session:
            result = await session.execute(
                select(SecretVault)
                .where(SecretVault.secret_id == secret_id)
                .where(SecretVault.is_active == True)
            )
            secret_record = result.scalar_one_or_none()
            
            if not secret_record:
                await self._log_access_denied(secret_id, requested_by, purpose, "secret_not_found")
                return None
            
            # Check if agent is allowed
            if secret_record.allowed_agents and requested_by not in secret_record.allowed_agents:
                await self._log_access_denied(secret_id, requested_by, purpose, "agent_not_authorized")
                print(f"[SECRETS] Access denied: {requested_by} not in allowed_agents for {secret_record.name}")
                return None
            
            # Check if expired
            if secret_record.expires_at and secret_record.expires_at < datetime.now(timezone.utc):
                await self._log_access_denied(secret_id, requested_by, purpose, "secret_expired")
                print(f"[SECRETS] Access denied: {secret_record.name} has expired")
                return None
            
            # Decrypt value
            try:
                decrypted_value = self._decrypt(secret_record.encrypted_value)
            except Exception as e:
                await self._log_access_denied(secret_id, requested_by, purpose, f"decryption_failed: {e}")
                return None
            
            # Update usage stats
            await session.execute(
                update(SecretVault)
                .where(SecretVault.secret_id == secret_id)
                .values(
                    access_count=SecretVault.access_count + 1,
                    last_accessed_at=datetime.now(timezone.utc),
                    last_accessed_by=requested_by
                )
            )
            await session.commit()
            
            # Log access (NO SECRET VALUE)
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            await self._log_access_granted(
                secret_id=secret_id,
                secret_name=secret_record.name,
                requested_by=requested_by,
                purpose=purpose,
                task_id=task_id,
                intent_id=intent_id,
                duration_seconds=duration
            )
            
            print(f"[SECRETS] Retrieved: {secret_record.name} by {requested_by} (purpose: {purpose})")
            
            return decrypted_value
    
    async def _log_access_granted(
        self,
        secret_id: str,
        secret_name: str,
        requested_by: str,
        purpose: str,
        task_id: Optional[str],
        intent_id: Optional[str],
        duration_seconds: float
    ):
        """Log successful secret access"""
        async with async_session() as session:
            access_log = SecretAccessLog(
                secret_id=secret_id,
                secret_name=secret_name,
                accessed_by=requested_by,
                purpose=purpose,
                task_id=task_id,
                intent_id=intent_id,
                access_granted=True,
                duration_seconds=duration_seconds
            )
            session.add(access_log)
            await session.commit()
        
        # Log to structured logging (NO SECRET)
        log_event(
            action="secret.accessed",
            actor=requested_by,
            resource=secret_id,
            outcome="ok",
            payload={
                "secret_name": secret_name,
                "purpose": purpose,
                "task_id": task_id,
                "intent_id": intent_id
            }
        )
    
    async def _log_access_denied(
        self,
        secret_id: str,
        requested_by: str,
        purpose: str,
        denial_reason: str
    ):
        """Log denied secret access"""
        async with async_session() as session:
            access_log = SecretAccessLog(
                secret_id=secret_id,
                secret_name="unknown",
                accessed_by=requested_by,
                purpose=purpose,
                access_granted=False,
                denial_reason=denial_reason
            )
            session.add(access_log)
            await session.commit()
        
        log_event(
            action="secret.access_denied",
            actor=requested_by,
            resource=secret_id,
            outcome="denied",
            payload={
                "reason": denial_reason,
                "purpose": purpose
            }
        )
    
    def detect_secrets(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential secrets in text
        
        Returns list of detected secrets with type and position
        """
        detected = []
        
        for pattern_name, pattern in self.secret_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                detected.append({
                    "type": pattern_name,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "masked": self._mask_value(match.group())
                })
        
        return detected
    
    def detect_emails(self, text: str) -> List[str]:
        """Detect email addresses in text"""
        matches = self.email_pattern.findall(text)
        return matches
    
    def redact(self, text: str) -> str:
        """
        Redact all secrets from text
        
        Returns text with secrets replaced by ***REDACTED***
        """
        redacted = text
        
        for pattern_name, pattern in self.secret_patterns.items():
            redacted = pattern.sub("***REDACTED***", redacted)
        
        return redacted
    
    def _mask_value(self, value: str) -> str:
        """Mask secret value for display"""
        if len(value) <= 8:
            return "***"
        return value[:4] + "***" + value[-4:]
    
    async def validate_secret(
        self,
        secret_id: str,
        validation_method: str = "test_api_call",
        test_endpoint: Optional[str] = None
    ) -> bool:
        """
        Validate that secret works
        
        Called by Librarian workflow after secret is stored
        """
        # Get secret
        secret_value = await self.get_secret(
            secret_id=secret_id,
            requested_by="librarian_validator",
            purpose="validation_test"
        )
        
        if not secret_value:
            return False
        
        validation_passed = False
        error_message = None
        http_status = None
        response_time = None
        
        try:
            if validation_method == "test_api_call" and test_endpoint:
                # Make sandbox API call
                import httpx
                start = datetime.now(timezone.utc)
                
                headers = {"Authorization": f"Bearer {secret_value}"}
                async with httpx.AsyncClient() as client:
                    response = await client.get(test_endpoint, headers=headers, timeout=10.0)
                    http_status = response.status_code
                    response_time = (datetime.now(timezone.utc) - start).total_seconds() * 1000
                
                validation_passed = http_status in [200, 201, 204]
            
            else:
                # Basic validation: secret exists and is non-empty
                validation_passed = len(secret_value) > 0
        
        except Exception as e:
            error_message = str(e)
            validation_passed = False
        
        # Store validation result
        async with async_session() as session:
            validation = SecretValidation(
                secret_id=secret_id,
                validated_by="librarian_validator",
                validation_method=validation_method,
                validation_passed=validation_passed,
                error_message=error_message,
                http_status=http_status,
                response_time_ms=response_time,
                endpoint_tested=test_endpoint
            )
            session.add(validation)
            
            # Update secret validation status
            await session.execute(
                update(SecretVault)
                .where(SecretVault.secret_id == secret_id)
                .values(
                    is_validated=validation_passed,
                    validation_status="passed" if validation_passed else "failed",
                    last_validated_at=datetime.now(timezone.utc)
                )
            )
            
            await session.commit()
        
        print(f"[SECRETS] Validation {'PASSED' if validation_passed else 'FAILED'}: {secret_id}")
        
        return validation_passed
    
    async def store_contact(
        self,
        contact_value: str,
        contact_type: str,
        purpose: str,
        created_by: str,
        service_name: Optional[str] = None,
        consent_given: bool = False
    ) -> str:
        """
        Store contact information (email, phone) with opt-in consent
        
        Separate from secrets - requires explicit consent
        """
        contact_id = f"contact_{contact_type}_{datetime.now(timezone.utc).timestamp()}"
        
        async with async_session() as session:
            contact = ContactRegistry(
                contact_id=contact_id,
                contact_type=contact_type,
                contact_value=contact_value,
                purpose=purpose,
                service_name=service_name,
                opted_in=consent_given,
                consent_given_at=datetime.now(timezone.utc) if consent_given else None,
                created_by=created_by,
                is_active=True
            )
            session.add(contact)
            await session.commit()
        
        log_event(
            action="contact.stored",
            actor=created_by,
            resource=contact_id,
            outcome="ok",
            payload={
                "contact_type": contact_type,
                "purpose": purpose,
                "consent_given": consent_given
            }
        )
        
        print(f"[SECRETS] Contact stored: {self._mask_value(contact_value)} ({contact_type})")
        
        return contact_id
    
    async def list_secrets(
        self,
        requested_by: str,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all secrets (metadata only, no values)
        """
        async with async_session() as session:
            query = select(SecretVault)
            if not include_inactive:
                query = query.where(SecretVault.is_active == True)
            
            result = await session.execute(query.order_by(desc(SecretVault.created_at)))
            secrets = result.scalars().all()
            
            return [
                {
                    "secret_id": s.secret_id,
                    "name": s.name,
                    "type": s.secret_type,
                    "scope": s.scope,
                    "environment": s.environment,
                    "service_name": s.service_name,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "is_validated": s.is_validated,
                    "validation_status": s.validation_status,
                    "access_count": s.access_count,
                    "last_accessed_at": s.last_accessed_at.isoformat() if s.last_accessed_at else None,
                    "requires_approval": s.requires_approval,
                    "approved": s.approved_by is not None
                }
                for s in secrets
            ]


# Global instance
secrets_service = SecretsService()
