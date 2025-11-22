"""
Secrets Consent Flow - User Approval Before Credential Redemption

Features:
- UI prompt before Grace uses stored credentials
- Governance-enforced consent requirements
- Audit trail for all credential access
- Revocable consent per secret/action
- Risk-based approval workflows

Integration:
- Hooks into secrets_vault.retrieve_secret()
- Message bus events for UI prompts
- Governance checks before access
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from backend.core.message_bus import message_bus, MessagePriority
from backend.logging_system_utils import log_event
from backend.models.base_models import async_session, Base
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON, Integer, select, update
from sqlalchemy.sql import func


class ConsentStatus(Enum):
    """Consent request statuses"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SecretConsentRecord(Base):
    """Track consent for secret access"""
    __tablename__ = "secret_consent_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Consent identification
    consent_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Secret details
    secret_key = Column(String(128), nullable=False, index=True)
    secret_type = Column(String(64), nullable=False)
    service = Column(String(128), nullable=True)
    
    # Request details
    requested_by = Column(String(128), nullable=False)  # Which component/agent
    requested_for = Column(String(256), nullable=False)  # Purpose
    requested_action = Column(String(128), nullable=False)  # e.g., "send_email", "git_push"
    
    # User approval
    user_id = Column(String(128), nullable=False, index=True)
    consent_status = Column(String(32), nullable=False, default="pending")
    
    # Timing
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    denied_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Decision details
    approval_method = Column(String(64), nullable=True)  # ui_click, cli_command, auto_approved
    denial_reason = Column(Text, nullable=True)
    revocation_reason = Column(Text, nullable=True)
    
    # Scope
    single_use = Column(Boolean, default=False)  # One-time consent vs persistent
    consent_duration_hours = Column(Integer, nullable=True)  # How long consent valid
    allowed_actions = Column(JSON, nullable=True)  # Specific actions allowed
    
    # Usage tracking
    used_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Risk assessment
    risk_level = Column(String(32), default="medium")
    governance_approval_required = Column(Boolean, default=False)
    governance_approved = Column(Boolean, nullable=True)
    
    # Metadata
    context = Column(JSON, nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)


@dataclass
class ConsentRequest:
    """Consent request for secret access"""
    consent_id: str
    secret_key: str
    secret_type: str
    service: str
    requested_by: str
    requested_for: str
    requested_action: str
    user_id: str
    risk_level: str
    context: Dict[str, Any]
    expires_in_seconds: int = 300  # Default 5 min


class SecretsConsentFlow:
    """
    Manages consent flow for secret access
    
    Flow:
    1. Component requests secret access
    2. Check if consent already granted
    3. If not, send UI prompt to user
    4. Wait for user approval/denial
    5. Check governance if required
    6. Log access attempt
    7. Return access decision
    """
    
    def __init__(self):
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.auto_approve_patterns: List[str] = []  # Patterns for auto-approval
        
    async def start(self):
        """Start consent flow service"""
        # Subscribe to consent responses from UI
        message_bus.subscribe("secrets.consent.response", self._handle_consent_response)
        message_bus.subscribe("secrets.consent.revoke", self._handle_consent_revoke)
        
        print("[SECRETS CONSENT] Flow service started")
    
    async def request_consent(
        self,
        secret_key: str,
        secret_type: str,
        service: str,
        requested_by: str,
        requested_for: str,
        requested_action: str,
        user_id: str,
        context: Optional[Dict] = None,
        risk_level: str = "medium",
        timeout_seconds: int = 300
    ) -> bool:
        """
        Request user consent to access secret
        
        Args:
            secret_key: Key of secret being accessed
            secret_type: Type (api_key, password, token)
            service: Service name (github, email, slack)
            requested_by: Component requesting access
            requested_for: Purpose description
            requested_action: Specific action (e.g., "send_email")
            user_id: User to request consent from
            context: Additional context
            risk_level: low/medium/high/critical
            timeout_seconds: How long to wait for response
            
        Returns:
            True if consent granted, False if denied/timeout
        """
        # Check for existing valid consent
        existing_consent = await self._check_existing_consent(
            secret_key=secret_key,
            requested_action=requested_action,
            user_id=user_id
        )
        
        if existing_consent:
            print(f"[SECRETS CONSENT] Using existing consent for {secret_key}")
            await self._record_consent_usage(existing_consent)
            return True
        
        # Check if auto-approval applies
        if await self._should_auto_approve(secret_key, service, requested_action):
            return await self._auto_approve_consent(
                secret_key, secret_type, service, requested_by,
                requested_for, requested_action, user_id, context
            )
        
        # Create consent request
        consent_id = f"consent_{secret_key}_{requested_action}_{datetime.now(timezone.utc).timestamp()}"
        
        consent_request = ConsentRequest(
            consent_id=consent_id,
            secret_key=secret_key,
            secret_type=secret_type,
            service=service,
            requested_by=requested_by,
            requested_for=requested_for,
            requested_action=requested_action,
            user_id=user_id,
            risk_level=risk_level,
            context=context or {},
            expires_in_seconds=timeout_seconds
        )
        
        # Store in database
        async with async_session() as session:
            record = SecretConsentRecord(
                consent_id=consent_id,
                secret_key=secret_key,
                secret_type=secret_type,
                service=service,
                requested_by=requested_by,
                requested_for=requested_for,
                requested_action=requested_action,
                user_id=user_id,
                consent_status="pending",
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds),
                risk_level=risk_level,
                governance_approval_required=(risk_level in ["high", "critical"]),
                context=context,
                single_use=(risk_level == "critical")  # Critical actions require re-approval
            )
            session.add(record)
            await session.commit()
        
        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[consent_id] = response_future
        
        # Send UI prompt
        await self._send_consent_prompt(consent_request)
        
        # Wait for response with timeout
        try:
            approved = await asyncio.wait_for(response_future, timeout=timeout_seconds)
            
            # If high/critical risk, check governance
            if risk_level in ["high", "critical"]:
                governance_approved = await self._check_governance_approval(
                    secret_key, requested_action, user_id, context
                )
                
                if not governance_approved:
                    print(f"[SECRETS CONSENT] Governance denied {secret_key} for {requested_action}")
                    await self._update_consent_status(consent_id, "denied", denial_reason="Governance denied")
                    return False
                
                # Update governance approval
                async with async_session() as session:
                    await session.execute(
                        update(SecretConsentRecord)
                        .where(SecretConsentRecord.consent_id == consent_id)
                        .values(governance_approved=True)
                    )
                    await session.commit()
            
            return approved
            
        except asyncio.TimeoutError:
            print(f"[SECRETS CONSENT] Timeout waiting for consent {consent_id}")
            await self._update_consent_status(consent_id, "expired")
            return False
            
        finally:
            # Cleanup
            if consent_id in self.pending_requests:
                del self.pending_requests[consent_id]
    
    async def _send_consent_prompt(self, request: ConsentRequest):
        """Send consent prompt to UI via message bus"""
        
        # Publish to message bus for UI to display prompt
        await message_bus.publish(
            source="secrets_consent_flow",
            topic="secrets.consent.request",
            payload={
                "consent_id": request.consent_id,
                "secret_key": request.secret_key,
                "secret_type": request.secret_type,
                "service": request.service,
                "requested_by": request.requested_by,
                "requested_for": request.requested_for,
                "requested_action": request.requested_action,
                "user_id": request.user_id,
                "risk_level": request.risk_level,
                "context": request.context,
                "expires_in_seconds": request.expires_in_seconds,
                "prompt_message": f"Grace wants to use your {request.service} credentials to {request.requested_for}. Allow?"
            },
            priority=MessagePriority.HIGH if request.risk_level == "critical" else MessagePriority.NORMAL
        )
        
        log_event(
            action="secrets.consent.requested",
            actor=request.requested_by,
            resource=request.secret_key,
            outcome="prompt_sent",
            payload={
                "consent_id": request.consent_id,
                "action": request.requested_action,
                "risk_level": request.risk_level
            }
        )
        
        print(f"[SECRETS CONSENT] Prompt sent: {request.consent_id}")
    
    async def _handle_consent_response(self, event: Dict[str, Any]):
        """Handle user response to consent request"""
        consent_id = event.get("consent_id")
        approved = event.get("approved", False)
        denial_reason = event.get("denial_reason")
        
        if not consent_id or consent_id not in self.pending_requests:
            return
        
        # Update database
        status = "approved" if approved else "denied"
        await self._update_consent_status(
            consent_id, status,
            approval_method=event.get("approval_method", "ui_click"),
            denial_reason=denial_reason
        )
        
        # Resolve future
        future = self.pending_requests[consent_id]
        if not future.done():
            future.set_result(approved)
        
        log_event(
            action=f"secrets.consent.{status}",
            actor=event.get("user_id", "user"),
            resource=consent_id,
            outcome=status,
            payload={
                "approved": approved,
                "denial_reason": denial_reason
            }
        )
        
        print(f"[SECRETS CONSENT] User response: {consent_id} → {status}")
    
    async def _handle_consent_revoke(self, event: Dict[str, Any]):
        """Handle consent revocation"""
        consent_id = event.get("consent_id")
        secret_key = event.get("secret_key")
        revocation_reason = event.get("reason")
        
        # Revoke specific consent or all for secret
        if consent_id:
            await self._update_consent_status(
                consent_id, "revoked",
                revocation_reason=revocation_reason
            )
        elif secret_key:
            # Revoke all active consents for this secret
            async with async_session() as session:
                await session.execute(
                    update(SecretConsentRecord)
                    .where(SecretConsentRecord.secret_key == secret_key)
                    .where(SecretConsentRecord.consent_status == "approved")
                    .values(
                        consent_status="revoked",
                        revoked_at=datetime.now(timezone.utc),
                        revocation_reason=revocation_reason
                    )
                )
                await session.commit()
        
        print(f"[SECRETS CONSENT] Revoked: {consent_id or secret_key}")
    
    async def _check_existing_consent(
        self,
        secret_key: str,
        requested_action: str,
        user_id: str
    ) -> Optional[SecretConsentRecord]:
        """Check if valid consent already exists"""
        now = datetime.now(timezone.utc)
        
        async with async_session() as session:
            result = await session.execute(
                select(SecretConsentRecord)
                .where(SecretConsentRecord.secret_key == secret_key)
                .where(SecretConsentRecord.user_id == user_id)
                .where(SecretConsentRecord.consent_status == "approved")
                .where(SecretConsentRecord.single_use == False)
                .where(
                    (SecretConsentRecord.expires_at.is_(None)) |
                    (SecretConsentRecord.expires_at > now)
                )
                .order_by(SecretConsentRecord.approved_at.desc())
            )
            consent = result.scalar_one_or_none()
            
            if consent:
                # Check if action is allowed
                if consent.allowed_actions:
                    if requested_action not in consent.allowed_actions:
                        return None
            
            return consent
    
    async def _record_consent_usage(self, consent: SecretConsentRecord):
        """Record that consent was used"""
        async with async_session() as session:
            await session.execute(
                update(SecretConsentRecord)
                .where(SecretConsentRecord.id == consent.id)
                .values(
                    used_count=consent.used_count + 1,
                    last_used_at=datetime.now(timezone.utc)
                )
            )
            await session.commit()
    
    async def _should_auto_approve(
        self,
        secret_key: str,
        service: str,
        requested_action: str
    ) -> bool:
        """Check if this request should be auto-approved"""
        # Check patterns (e.g., "read_only" actions auto-approved)
        for pattern in self.auto_approve_patterns:
            if pattern in requested_action.lower() or pattern in service.lower():
                return True
        
        return False
    
    async def _auto_approve_consent(
        self,
        secret_key: str,
        secret_type: str,
        service: str,
        requested_by: str,
        requested_for: str,
        requested_action: str,
        user_id: str,
        context: Dict
    ) -> bool:
        """Auto-approve low-risk requests"""
        consent_id = f"auto_{secret_key}_{datetime.now(timezone.utc).timestamp()}"
        
        async with async_session() as session:
            record = SecretConsentRecord(
                consent_id=consent_id,
                secret_key=secret_key,
                secret_type=secret_type,
                service=service,
                requested_by=requested_by,
                requested_for=requested_for,
                requested_action=requested_action,
                user_id=user_id,
                consent_status="approved",
                approved_at=datetime.now(timezone.utc),
                approval_method="auto_approved",
                risk_level="low",
                context=context
            )
            session.add(record)
            await session.commit()
        
        print(f"[SECRETS CONSENT] Auto-approved: {secret_key} for {requested_action}")
        return True
    
    async def _check_governance_approval(
        self,
        secret_key: str,
        requested_action: str,
        user_id: str,
        context: Dict
    ) -> bool:
        """Check governance approval for high-risk operations"""
        try:
            from backend.governance_system.governance import governance_engine
            
            check_result = await governance_engine.check(
                actor=user_id,
                action=f"secrets.{requested_action}",
                resource=secret_key,
                payload=context
            )
            
            return check_result.get("approved", False)
            
        except Exception as e:
            print(f"[SECRETS CONSENT] Governance check error: {e}")
            return False  # Fail-safe: deny on error
    
    async def _update_consent_status(
        self,
        consent_id: str,
        status: str,
        approval_method: Optional[str] = None,
        denial_reason: Optional[str] = None,
        revocation_reason: Optional[str] = None
    ):
        """Update consent record status"""
        now = datetime.now(timezone.utc)
        
        values = {"consent_status": status}
        
        if status == "approved":
            values["approved_at"] = now
            if approval_method:
                values["approval_method"] = approval_method
        elif status == "denied":
            values["denied_at"] = now
            if denial_reason:
                values["denial_reason"] = denial_reason
        elif status == "revoked":
            values["revoked_at"] = now
            if revocation_reason:
                values["revocation_reason"] = revocation_reason
        
        async with async_session() as session:
            await session.execute(
                update(SecretConsentRecord)
                .where(SecretConsentRecord.consent_id == consent_id)
                .values(**values)
            )
            await session.commit()
    
    async def get_consent_history(
        self,
        secret_key: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get consent history"""
        async with async_session() as session:
            query = select(SecretConsentRecord)
            
            if secret_key:
                query = query.where(SecretConsentRecord.secret_key == secret_key)
            if user_id:
                query = query.where(SecretConsentRecord.user_id == user_id)
            
            query = query.order_by(SecretConsentRecord.requested_at.desc()).limit(limit)
            
            result = await session.execute(query)
            records = result.scalars().all()
        
        return [
            {
                "consent_id": r.consent_id,
                "secret_key": r.secret_key,
                "service": r.service,
                "requested_for": r.requested_for,
                "requested_action": r.requested_action,
                "consent_status": r.consent_status,
                "risk_level": r.risk_level,
                "requested_at": r.requested_at.isoformat() if r.requested_at else None,
                "approved_at": r.approved_at.isoformat() if r.approved_at else None,
                "used_count": r.used_count
            }
            for r in records
        ]


# Global instance
secrets_consent_flow = SecretsConsentFlow()
