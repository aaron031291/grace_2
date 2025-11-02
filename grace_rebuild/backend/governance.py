import json
from typing import Optional
from .governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from .models import async_session
from sqlalchemy import select

class GovernanceEngine:
    async def check(self, *, actor: str, action: str, resource: str, payload: dict) -> dict:
        async with async_session() as session:
            result = await session.execute(select(GovernancePolicy))
            policies = result.scalars().all()

            for policy in policies:
                if self._matches(policy, action, resource, payload):
                    audit = AuditLog(
                        actor=actor,
                        action=action,
                        resource=resource,
                        policy_checked=policy.name,
                        result="pending" if policy.action == "review" else policy.action,
                        details=json.dumps(payload),
                    )
                    session.add(audit)
                    await session.flush()

                    if policy.action == "review":
                        req = ApprovalRequest(
                            event_id=audit.id,
                            requested_by=actor,
                            reason=f"Policy {policy.name} requires review",
                        )
                        session.add(req)

                    await session.commit()
                    print(f"✓ Governance: {policy.action} - {actor} {action} {resource}")
                    return {"decision": policy.action, "policy": policy.name, "audit_id": audit.id}

            audit = AuditLog(
                actor=actor,
                action=action,
                resource=resource,
                policy_checked=None,
                result="allow",
                details=json.dumps(payload),
            )
            session.add(audit)
            await session.commit()
            return {"decision": "allow", "policy": None, "audit_id": audit.id}

    def _matches(self, policy: GovernancePolicy, action: str, resource: str, payload: dict) -> bool:
        try:
            condition = json.loads(policy.condition)
        except:
            return False
        
        match_action = condition.get("action")
        match_resource = condition.get("resource")
        keywords = condition.get("keywords", [])

        if match_action and match_action != action:
            return False
        if match_resource and match_resource not in resource:
            return False
        if keywords:
            data = json.dumps(payload).lower()
            if not any(keyword.lower() in data for keyword in keywords):
                return False
        return True

governance_engine = GovernanceEngine()
