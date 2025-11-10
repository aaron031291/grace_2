import json
from typing import Optional
from .governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from .models import async_session
from sqlalchemy import select

class GovernanceEngine:
    def __init__(self):
        self.parliament_enabled = True  # Enable parliament integration
    
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
