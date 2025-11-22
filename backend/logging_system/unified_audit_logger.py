"""
Unified Audit Logger

Consolidates all audit logging through a single interface to:
- Reduce 261+ duplicate ImmutableLog instances
- Standardize audit trail format
- Enable centralized compliance and governance
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UnifiedAuditLogger:
    """
    Central audit logging service that routes audit events to immutable log.
    Replaces direct ImmutableLog() instantiation in components.
    """
    
    def __init__(self):
        self._immutable_log = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize connection to immutable log"""
        if self._initialized:
            return
            
        try:
            from backend.logging_system.immutable_log import immutable_log
            self._immutable_log = immutable_log
            self._initialized = True
            logger.info("Unified audit logger initialized")
        except ImportError:
            logger.warning("Immutable log not available")
            self._initialized = True
    
    async def log_event(
        self,
        category: str,
        action: str,
        actor: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log audit event to immutable log.
        
        Args:
            category: Event category (e.g., 'security', 'governance', 'healing')
            action: Action performed (e.g., 'secret_accessed', 'policy_checked')
            actor: Who/what performed the action
            resource: Resource affected (optional)
            details: Additional context (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Audit log ID
        """
        if not self._initialized:
            await self.initialize()
            
        if self._immutable_log:
            try:
                audit_id = await self._immutable_log.log_event(
                    category=category,
                    action=action,
                    actor=actor,
                    resource=resource,
                    details=details or {},
                    metadata=metadata or {}
                )
                logger.debug(f"Audit logged: {category}.{action} by {actor}")
                return audit_id
            except Exception as e:
                logger.error(f"Failed to log audit event: {e}")
                return -1
        else:
            logger.warning(f"Audit log unavailable, event dropped: {category}.{action}")
            return -1
    
    async def log_security_event(
        self,
        action: str,
        actor: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log security-related audit event"""
        return await self.log_event(
            category="security",
            action=action,
            actor=actor,
            resource=resource,
            details=details
        )
    
    async def log_governance_event(
        self,
        action: str,
        actor: str,
        policy: Optional[str] = None,
        result: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log governance/policy audit event"""
        audit_details = details or {}
        if policy:
            audit_details['policy'] = policy
        if result:
            audit_details['result'] = result
            
        return await self.log_event(
            category="governance",
            action=action,
            actor=actor,
            details=audit_details
        )
    
    async def log_healing_event(
        self,
        action: str,
        component: str,
        playbook: Optional[str] = None,
        result: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log self-healing audit event"""
        audit_details = details or {}
        if playbook:
            audit_details['playbook'] = playbook
        if result:
            audit_details['result'] = result
            
        return await self.log_event(
            category="healing",
            action=action,
            actor="self_healing_kernel",
            resource=component,
            details=audit_details
        )
    
    async def log_ml_event(
        self,
        action: str,
        model_id: str,
        deployment_stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log ML model lifecycle audit event"""
        audit_details = details or {}
        if deployment_stage:
            audit_details['deployment_stage'] = deployment_stage
            
        return await self.log_event(
            category="ml_lifecycle",
            action=action,
            actor="model_registry",
            resource=model_id,
            details=audit_details
        )
    
    async def log_business_event(
        self,
        action: str,
        actor: str,
        resource: Optional[str] = None,
        transaction_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> int:
        """Log business operation audit event"""
        audit_details = details or {}
        if transaction_id:
            audit_details['transaction_id'] = transaction_id
            
        return await self.log_event(
            category="business",
            action=action,
            actor=actor,
            resource=resource,
            details=audit_details
        )


# Global singleton
_unified_audit_logger: Optional[UnifiedAuditLogger] = None


def get_audit_logger() -> UnifiedAuditLogger:
    """Get or create the global unified audit logger"""
    global _unified_audit_logger
    
    if _unified_audit_logger is None:
        _unified_audit_logger = UnifiedAuditLogger()
    
    return _unified_audit_logger


# Convenience functions for common patterns
async def log_audit(category: str, action: str, actor: str, **kwargs) -> int:
    """Log audit event (convenience function)"""
    audit_logger = get_audit_logger()
    return await audit_logger.log_event(category, action, actor, **kwargs)


async def log_security(action: str, actor: str, **kwargs) -> int:
    """Log security event (convenience function)"""
    audit_logger = get_audit_logger()
    return await audit_logger.log_security_event(action, actor, **kwargs)


async def log_governance(action: str, actor: str, **kwargs) -> int:
    """Log governance event (convenience function)"""
    audit_logger = get_audit_logger()
    return await audit_logger.log_governance_event(action, actor, **kwargs)


# Alias for compatibility
async def audit_log(action: str, actor: str = "system", resource: str = None, outcome: str = "success", details: Optional[Dict[str, Any]] = None, source: str = None, **kwargs) -> int:
    """
    Audit log function (compatibility alias)
    
    This is an alias for log_audit with a more flexible signature.
    """
    audit_logger = get_audit_logger()
    await audit_logger.initialize()
    
    # Merge details with kwargs
    all_details = details or {}
    all_details.update(kwargs)
    if source:
        all_details['source'] = source
    if outcome:
        all_details['outcome'] = outcome
    
    return await audit_logger.log_event(
        category="audit",
        action=action,
        actor=actor,
        resource=resource,
        details=all_details
    )
