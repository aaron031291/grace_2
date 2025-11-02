import json
from .governance_models import SecurityRule, SecurityEvent
from .models import async_session
from sqlalchemy import select

class Hunter:
    """Security monitoring and threat detection"""
    
    async def inspect(self, actor: str, action: str, resource: str, payload: dict):
        """Check for security threats"""
        async with async_session() as session:
            result = await session.execute(select(SecurityRule))
            rules = result.scalars().all()

            triggered = []
            for rule in rules:
                if self._matches(rule, action, resource, payload):
                    event = SecurityEvent(
                        actor=actor,
                        action=action,
                        resource=resource,
                        severity=rule.severity,
                        details=json.dumps(payload),
                    )
                    session.add(event)
                    await session.flush()
                    triggered.append((rule.name, event.id))
                    print(f"⚠️ Security alert: {rule.name} triggered by {actor}")
            
            if triggered:
                await session.commit()
                
                from .hunter_integration import handle_security_alert
                for rule_name, event_id in triggered:
                    await handle_security_alert(actor, rule_name, event_id, resource)
            
            return triggered

    def _matches(self, rule: SecurityRule, action: str, resource: str, payload: dict) -> bool:
        try:
            condition = json.loads(rule.condition)
        except:
            return False
        
        if condition.get("action") and condition["action"] != action:
            return False
        
        keywords = condition.get("keywords", [])
        if keywords:
            data = json.dumps(payload).lower()
            if any(k.lower() in data for k in keywords):
                return True
        
        forbidden = condition.get("forbidden_paths", [])
        if forbidden and any(path in resource for path in forbidden):
            return True
        
        return False

hunter = Hunter()
