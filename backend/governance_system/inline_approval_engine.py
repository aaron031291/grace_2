"""
Inline Approval Engine
Governance decisions before any mission modifies production resources/models

Features:
- Risk scoring (0-1) for auto-approval
- Low risk = auto-approved
- High risk = blocked or requires manual approval
- All decisions logged to immutable log
- Guardian escalation on denials
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk levels for approval decisions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalDecision(str, Enum):
    """Approval decision outcomes"""
    AUTO_APPROVED = "auto_approved"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    ESCALATED = "escalated"


@dataclass
class ResourceAccess:
    """Resource access request"""
    
    resource_type: str  # 'production_db', 'model', 'vector_store', 'file_system', etc.
    resource_id: str
    action: str  # 'read', 'write', 'delete', 'modify', 'execute'
    requester: str  # Service account or agent ID
    mission_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'requester': self.requester,
            'mission_id': self.mission_id,
            'context': self.context
        }


@dataclass
class ApprovalResult:
    """Result of approval decision"""
    
    request_id: str
    decision: ApprovalDecision
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    reason: str
    auto_approved: bool
    approved_by: Optional[str] = None
    escalated_to: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'request_id': self.request_id,
            'decision': self.decision.value,
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'reason': self.reason,
            'auto_approved': self.auto_approved,
            'approved_by': self.approved_by,
            'escalated_to': self.escalated_to,
            'timestamp': self.timestamp.isoformat()
        }


class InlineApprovalEngine:
    """
    Governance decision engine for missions and operations
    
    Features:
    - Risk-based auto-approval
    - RBAC integration
    - Guardian escalation
    - Immutable log integration
    """
    
    def __init__(self):
        self.running = False
        
        # Configuration
        self.auto_approval_threshold = 0.3  # Auto-approve if risk < 0.3
        self.escalation_threshold = 0.7  # Escalate to Guardian if risk > 0.7
        
        # Risk weights by resource type
        self.resource_risk_weights = {
            'production_db': 0.9,
            'production_model': 0.8,
            'staging_db': 0.4,
            'staging_model': 0.3,
            'vector_store': 0.5,
            'file_system': 0.2,
            'test_environment': 0.1,
            'read_only_resource': 0.05
        }
        
        # Risk weights by action
        self.action_risk_weights = {
            'read': 0.1,
            'write': 0.5,
            'modify': 0.6,
            'delete': 0.9,
            'execute': 0.7,
            'deploy': 0.8,
            'scale': 0.6
        }
        
        # Statistics
        self.stats = {
            'requests_processed': 0,
            'auto_approved': 0,
            'manually_approved': 0,
            'denied': 0,
            'escalated': 0
        }
        
        # Pending approvals (for manual review)
        self.pending_approvals: Dict[str, ResourceAccess] = {}
        
        # Dependencies
        self.immutable_log = None
        self.guardian = None
        self.rbac_system = None
        self.message_bus = None
    
    async def start(self):
        """Start the approval engine"""
        if self.running:
            return
        
        logger.info("[APPROVAL-ENGINE] Starting inline approval engine...")
        
        # Initialize dependencies
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[APPROVAL-ENGINE] Immutable log not available")
        
        try:
            from backend.core.guardian import guardian
            self.guardian = guardian
        except ImportError:
            logger.warning("[APPROVAL-ENGINE] Guardian not available")
        
        try:
            from backend.governance_system.rbac_system import rbac_system
            self.rbac_system = rbac_system
        except ImportError:
            logger.warning("[APPROVAL-ENGINE] RBAC system not available")
        
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
        except ImportError:
            logger.warning("[APPROVAL-ENGINE] Message bus not available")
        
        self.running = True
        
        logger.info("[APPROVAL-ENGINE] ✅ Started")
        logger.info(f"[APPROVAL-ENGINE] Auto-approval threshold: {self.auto_approval_threshold}")
        logger.info(f"[APPROVAL-ENGINE] Escalation threshold: {self.escalation_threshold}")
    
    async def stop(self):
        """Stop the approval engine"""
        self.running = False
        logger.info("[APPROVAL-ENGINE] Stopped")
    
    async def request_approval(
        self,
        resource_access: ResourceAccess
    ) -> ApprovalResult:
        """
        Request approval for resource access
        
        Args:
            resource_access: Resource access request
            
        Returns:
            Approval result
        """
        request_id = f"approval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        logger.info(f"[APPROVAL-ENGINE] Processing request: {request_id}")
        logger.info(f"[APPROVAL-ENGINE]   Resource: {resource_access.resource_type}:{resource_access.resource_id}")
        logger.info(f"[APPROVAL-ENGINE]   Action: {resource_access.action}")
        logger.info(f"[APPROVAL-ENGINE]   Requester: {resource_access.requester}")
        
        self.stats['requests_processed'] += 1
        
        # Step 1: Check RBAC permissions
        rbac_allowed = await self._check_rbac_permission(resource_access)
        
        if not rbac_allowed:
            return await self._deny_request(
                request_id,
                resource_access,
                "RBAC permission denied",
                escalate=True
            )
        
        # Step 2: Calculate risk score
        risk_score = self._calculate_risk_score(resource_access)
        risk_level = self._classify_risk_level(risk_score)
        
        logger.info(f"[APPROVAL-ENGINE]   Risk score: {risk_score:.2f} ({risk_level.value})")
        
        # Step 3: Make decision based on risk
        if risk_score < self.auto_approval_threshold:
            # Low risk = auto-approve
            result = ApprovalResult(
                request_id=request_id,
                decision=ApprovalDecision.AUTO_APPROVED,
                risk_level=risk_level,
                risk_score=risk_score,
                reason=f"Low risk ({risk_score:.2f}) - auto-approved",
                auto_approved=True
            )
            
            self.stats['auto_approved'] += 1
            logger.info(f"[APPROVAL-ENGINE] ✅ Auto-approved: {request_id}")
        
        elif risk_score > self.escalation_threshold:
            # High risk = escalate to Guardian
            result = await self._escalate_to_guardian(
                request_id,
                resource_access,
                risk_score,
                risk_level
            )
        
        else:
            # Medium risk = pending manual approval
            result = await self._request_manual_approval(
                request_id,
                resource_access,
                risk_score,
                risk_level
            )
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='governance',
                subcategory='approval_decision',
                data={
                    'request_id': request_id,
                    'resource_access': resource_access.to_dict(),
                    'result': result.to_dict()
                },
                actor=resource_access.requester,
                action='request_approval',
                resource=f"{resource_access.resource_type}:{resource_access.resource_id}"
            )
        
        # Publish event
        if self.message_bus:
            await self.message_bus.publish('governance.approval_decision', {
                'request_id': request_id,
                'decision': result.decision.value,
                'risk_score': result.risk_score
            })
        
        return result
    
    async def _check_rbac_permission(
        self,
        resource_access: ResourceAccess
    ) -> bool:
        """Check RBAC permissions"""
        
        if not self.rbac_system:
            # No RBAC system = allow (fail open for now)
            logger.warning("[APPROVAL-ENGINE] RBAC system not available - allowing by default")
            return True
        
        # Check permission
        allowed = await self.rbac_system.check_permission(
            principal=resource_access.requester,
            resource_type=resource_access.resource_type,
            resource_id=resource_access.resource_id,
            action=resource_access.action
        )
        
        logger.info(f"[APPROVAL-ENGINE] RBAC check: {allowed}")
        
        return allowed
    
    def _calculate_risk_score(
        self,
        resource_access: ResourceAccess
    ) -> float:
        """
        Calculate risk score (0.0 - 1.0)
        
        Factors:
        - Resource type (production vs staging vs test)
        - Action type (read vs write vs delete)
        - Context (mission type, previous failures)
        """
        
        # Base risk from resource type
        resource_risk = self.resource_risk_weights.get(
            resource_access.resource_type,
            0.5  # Default medium risk
        )
        
        # Risk from action type
        action_risk = self.action_risk_weights.get(
            resource_access.action,
            0.5  # Default medium risk
        )
        
        # Combine (weighted average)
        base_risk = (resource_risk * 0.6) + (action_risk * 0.4)
        
        # Context modifiers
        context = resource_access.context
        
        # Increase risk for production
        if 'production' in resource_access.resource_type:
            base_risk *= 1.2
        
        # Decrease risk for test/dev
        if 'test' in resource_access.resource_type or 'dev' in resource_access.resource_type:
            base_risk *= 0.5
        
        # Increase risk if mission has failed before
        if context.get('previous_failures', 0) > 0:
            base_risk *= (1 + context.get('previous_failures', 0) * 0.1)
        
        # Decrease risk if requester has good track record
        if context.get('success_rate', 0) > 0.9:
            base_risk *= 0.8
        
        # Clamp to [0, 1]
        risk_score = max(0.0, min(1.0, base_risk))
        
        return risk_score
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level from score"""
        
        if risk_score < 0.3:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.85:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    async def _deny_request(
        self,
        request_id: str,
        resource_access: ResourceAccess,
        reason: str,
        escalate: bool = False
    ) -> ApprovalResult:
        """Deny request"""
        
        risk_score = self._calculate_risk_score(resource_access)
        risk_level = self._classify_risk_level(risk_score)
        
        result = ApprovalResult(
            request_id=request_id,
            decision=ApprovalDecision.DENIED,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=reason,
            auto_approved=False
        )
        
        self.stats['denied'] += 1
        logger.warning(f"[APPROVAL-ENGINE] ❌ Denied: {request_id} - {reason}")
        
        # Escalate to Guardian if requested
        if escalate and self.guardian:
            await self._notify_guardian_denial(request_id, resource_access, reason)
        
        return result
    
    async def _escalate_to_guardian(
        self,
        request_id: str,
        resource_access: ResourceAccess,
        risk_score: float,
        risk_level: RiskLevel
    ) -> ApprovalResult:
        """Escalate high-risk request to Guardian"""
        
        logger.warning(f"[APPROVAL-ENGINE] ⚠️ Escalating to Guardian: {request_id}")
        
        result = ApprovalResult(
            request_id=request_id,
            decision=ApprovalDecision.ESCALATED,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=f"High risk ({risk_score:.2f}) - escalated to Guardian",
            auto_approved=False,
            escalated_to='guardian'
        )
        
        self.stats['escalated'] += 1
        
        # Notify Guardian
        if self.guardian:
            await self._notify_guardian_escalation(request_id, resource_access, risk_score)
        
        return result
    
    async def _request_manual_approval(
        self,
        request_id: str,
        resource_access: ResourceAccess,
        risk_score: float,
        risk_level: RiskLevel
    ) -> ApprovalResult:
        """Request manual approval for medium-risk action"""
        
        logger.info(f"[APPROVAL-ENGINE] 🔔 Pending manual approval: {request_id}")
        
        # Store for manual review
        self.pending_approvals[request_id] = resource_access
        
        result = ApprovalResult(
            request_id=request_id,
            decision=ApprovalDecision.PENDING,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=f"Medium risk ({risk_score:.2f}) - awaiting manual approval",
            auto_approved=False
        )
        
        # Publish event for manual review
        if self.message_bus:
            await self.message_bus.publish('governance.approval_required', {
                'request_id': request_id,
                'resource_access': resource_access.to_dict(),
                'risk_score': risk_score
            })
        
        return result
    
    async def _notify_guardian_denial(
        self,
        request_id: str,
        resource_access: ResourceAccess,
        reason: str
    ):
        """Notify Guardian of denial"""
        
        if self.message_bus:
            await self.message_bus.publish('guardian.approval_denied', {
                'request_id': request_id,
                'resource_access': resource_access.to_dict(),
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        logger.info(f"[APPROVAL-ENGINE] Guardian notified of denial: {request_id}")
    
    async def _notify_guardian_escalation(
        self,
        request_id: str,
        resource_access: ResourceAccess,
        risk_score: float
    ):
        """Notify Guardian of escalation"""
        
        if self.message_bus:
            await self.message_bus.publish('guardian.approval_escalated', {
                'request_id': request_id,
                'resource_access': resource_access.to_dict(),
                'risk_score': risk_score,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        logger.warning(f"[APPROVAL-ENGINE] Guardian notified of escalation: {request_id}")
    
    async def approve_pending(
        self,
        request_id: str,
        approved_by: str
    ) -> ApprovalResult:
        """Manually approve pending request"""
        
        if request_id not in self.pending_approvals:
            raise ValueError(f"No pending approval: {request_id}")
        
        resource_access = self.pending_approvals.pop(request_id)
        risk_score = self._calculate_risk_score(resource_access)
        risk_level = self._classify_risk_level(risk_score)
        
        result = ApprovalResult(
            request_id=request_id,
            decision=ApprovalDecision.APPROVED,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=f"Manually approved by {approved_by}",
            auto_approved=False,
            approved_by=approved_by
        )
        
        self.stats['manually_approved'] += 1
        logger.info(f"[APPROVAL-ENGINE] ✅ Manually approved: {request_id} by {approved_by}")
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='governance',
                subcategory='manual_approval',
                data={
                    'request_id': request_id,
                    'approved_by': approved_by,
                    'result': result.to_dict()
                },
                actor=approved_by,
                action='approve_request',
                resource=request_id
            )
        
        return result
    
    async def deny_pending(
        self,
        request_id: str,
        denied_by: str,
        reason: str
    ) -> ApprovalResult:
        """Manually deny pending request"""
        
        if request_id not in self.pending_approvals:
            raise ValueError(f"No pending approval: {request_id}")
        
        resource_access = self.pending_approvals.pop(request_id)
        risk_score = self._calculate_risk_score(resource_access)
        risk_level = self._classify_risk_level(risk_score)
        
        result = ApprovalResult(
            request_id=request_id,
            decision=ApprovalDecision.DENIED,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=f"Manually denied by {denied_by}: {reason}",
            auto_approved=False,
            approved_by=denied_by
        )
        
        self.stats['denied'] += 1
        logger.warning(f"[APPROVAL-ENGINE] ❌ Manually denied: {request_id} by {denied_by}")
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='governance',
                subcategory='manual_denial',
                data={
                    'request_id': request_id,
                    'denied_by': denied_by,
                    'reason': reason,
                    'result': result.to_dict()
                },
                actor=denied_by,
                action='deny_request',
                resource=request_id
            )
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval engine statistics"""
        
        total = self.stats['requests_processed']
        
        return {
            **self.stats,
            'running': self.running,
            'pending_approvals': len(self.pending_approvals),
            'auto_approval_rate': (
                self.stats['auto_approved'] / max(1, total) * 100
            )
        }
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending approval requests"""
        
        return [
            {
                'request_id': request_id,
                'resource_access': access.to_dict()
            }
            for request_id, access in self.pending_approvals.items()
        ]


# Global instance
inline_approval_engine = InlineApprovalEngine()
