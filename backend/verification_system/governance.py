"""
Governance Engine for Verification System
Checks actions against governance policies
"""

from typing import Dict, Any, Optional
from backend.logging.unified_audit_logger import audit_log

class GovernanceEngine:
    """Governance policy checker"""
    
    def __init__(self):
        self.policies = {}
    
    async def check(
        self,
        action_type: str,
        actor: str,
        resource: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if action complies with governance policies
        
        Returns:
            {
                'allowed': bool,
                'reason': str,
                'policy': str or None
            }
        """
        # Default: allow all actions (permissive mode for development)
        # In production, implement actual policy checks
        return {
            'allowed': True,
            'reason': 'Default policy: allow',
            'policy': None
        }
    
    async def check_action(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Alias for check() to match UnifiedLogicHub expectations.
        Adapts parameters and return format.
        """
        # Map parameters to check()
        result = await self.check(
            action_type=action,
            actor=actor,
            resource=resource,
            input_data=context or {}
        )
        
        # Adapt return format
        return {
            "approved": result.get("allowed", False),
            "reason": result.get("reason", "No reason provided"),
            "approval_id": f"auto_approved_{action}_{resource}",
            "checks": result
        }

    async def log_decision(
        self,
        action_id: str,
        decision: Dict[str, Any]
    ):
        """Log governance decision for audit"""
        await audit_log(
            action="governance.decision",
            actor=decision.get("actor", "unknown"),
            resource=decision.get("resource", action_id),
            outcome="allowed" if decision.get("allowed") else "denied",
            details={
                "action_id": action_id,
                "decision": decision,
                "policy": decision.get("policy"),
                "reason": decision.get("reason")
            },
            source="governance_engine"
        )

    
    def __getattr__(self, name):
        """Fail-safe for missing methods (API regression)"""
        if name == "check_action":
            # Log the regression trigger
            import logging
            logging.getLogger(__name__).error(f"Governance API Regression: object has no attribute '{name}'")
            
            # Return a fail-safe async stub
            async def fail_safe_check(*args, **kwargs):
                return {
                    "approved": False,
                    "reason": "Governance API Regression: Method missing. Fail-safe block.",
                    "approval_id": "failsafe_block"
                }
            return fail_safe_check
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

# Singleton instance
governance_engine = GovernanceEngine()
