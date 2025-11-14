import json
from typing import Optional
from .governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from .models import async_session
from sqlalchemy import select

class GovernanceEngine:
    def __init__(self):
        self.parliament_enabled = True  # Enable parliament integration
    
    async def check(self, update_type: str = None, content: dict = None, risk_level: str = "medium", **kwargs) -> dict:
        """
        Primary check method for unified logic hub integration.
        
        Args:
            update_type: Type of update
            content: Update content
            risk_level: Risk level (low/medium/high/critical)
            **kwargs: Legacy parameters (actor, action, resource, payload)
        
        Returns:
            Check result with requires_approval flag
        """
        # Handle legacy calls
        if 'actor' in kwargs or 'action' in kwargs:
            return await self.check_policy(**kwargs)
        
        # High/critical risk requires approval
        if risk_level in ['high', 'critical']:
            return {
                'requires_approval': True,
                'reason': f'Risk level {risk_level} requires approval',
                'approved': False
            }
        
        # Schema changes require approval
        if update_type in ['memory_table_schema_create', 'memory_table_schema_modify']:
            return {
                'requires_approval': True,
                'reason': 'Schema changes require approval',
                'approved': False
            }
        
        # Low/medium risk auto-approved for data operations
        return {
            'requires_approval': False,
            'approved': True,
            'reason': 'Low risk auto-approved'
        }
    
    # Backward-compatible API aliases
    async def check_policy(self, *, actor: str, action: str, resource: str, payload: dict | None = None) -> dict:
        """Alias for legacy callers expecting `check_policy`.
        Delegates to `check()` and accepts optional payload.
        """
        return await self.check(actor=actor, action=action, resource=resource, payload=payload or {})

    async def check_action(self, actor: str, action: str, resource: str, context: dict | None = None) -> dict:
        """Alias for legacy callers expecting `check_action` with `context` instead of `payload`."""
        return await self.check(actor=actor, action=action, resource=resource, payload=context or {})


governance_engine = GovernanceEngine()
