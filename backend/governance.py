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
                        # Use Parliament voting instead of single approval
                        if self.parliament_enabled:
                            parliament_session = await self._create_parliament_session(
                                policy=policy,
                                actor=actor,
                                action=action,
                                resource=resource,
                                payload=payload,
                                audit_id=audit.id
                            )
                            
                            await session.commit()
                            print(f"🏛️ Parliament: Session created for {policy.name}")
                            return {
                                "decision": "parliament_pending",
                                "policy": policy.name,
                                "audit_id": audit.id,
                                "parliament_session_id": parliament_session["session_id"]
                            }
                        else:
                            # Fallback to traditional approval request
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
    
    async def _create_parliament_session(
        self,
        policy: GovernancePolicy,
        actor: str,
        action: str,
        resource: str,
        payload: dict,
        audit_id: int
    ) -> dict:
        """Create a Parliament voting session for governance review"""
        
        from .parliament_engine import parliament_engine
        from .hunter import hunter_engine
        
        # Determine category and committee
        category = self._categorize_action(action, resource, payload)
        committee = self._route_to_committee(category, policy)
        
        # Get risk level from policy or payload
        risk_level = payload.get("risk_level", "medium")
        
        # Check for Hunter alerts related to this action
        hunter_alerts = []
        try:
            recent_alerts = await hunter_engine.get_recent_alerts(resource=resource, limit=5)
            hunter_alerts = [
                {
                    "severity": alert.get("severity"),
                    "rule_name": alert.get("rule_name"),
                    "created_at": alert.get("created_at")
                }
                for alert in recent_alerts
            ]
        except:
            pass
        
        # Create session
        session = await parliament_engine.create_session(
            policy_name=policy.name,
            action_type=action,
            action_payload=payload,
            actor=actor,
            category=category,
            resource=resource,
            committee=committee,
            quorum_required=self._get_quorum_for_risk(risk_level),
            approval_threshold=0.5,
            expires_in_hours=24,
            hunter_alerts=hunter_alerts,
            risk_level=risk_level
        )
        
        # Trigger Grace auto-voting
        try:
            from .grace_parliament_agent import grace_voting_agent
            await grace_voting_agent.cast_automated_vote(session["session_id"])
        except Exception as e:
            print(f"⚠️  Grace auto-vote failed: {e}")
        
        return session
    
    def _categorize_action(self, action: str, resource: str, payload: dict) -> str:
        """Categorize action for committee routing"""
        
        if "execute" in action.lower() or "run" in action.lower():
            return "execution"
        elif "security" in action.lower() or "access" in action.lower():
            return "security"
        elif "knowledge" in action.lower() or "learn" in action.lower():
            return "knowledge"
        elif "meta" in action.lower() or "optimize" in action.lower():
            return "meta"
        else:
            return "general"
    
    def _route_to_committee(self, category: str, policy: GovernancePolicy) -> str:
        """Route to appropriate committee based on category"""
        
        committee_map = {
            "execution": "execution",
            "security": "security",
            "knowledge": "knowledge",
            "meta": "meta"
        }
        
        return committee_map.get(category, "general")
    
    def _get_quorum_for_risk(self, risk_level: str) -> int:
        """Determine quorum requirement based on risk level"""
        
        quorum_map = {
            "low": 2,
            "medium": 3,
            "high": 4,
            "critical": 5
        }
        
        return quorum_map.get(risk_level, 3)

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
