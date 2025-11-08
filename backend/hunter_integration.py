"""Integration layer connecting Hunter alerts to tasks/reflections"""

from .hunter import hunter
from .models import async_session, Task
from .memory import PersistentMemory
from .governance_models import SecurityEvent

memory = PersistentMemory()


class HunterIntegration:
    """Integration layer for Hunter security monitoring"""
    
    async def flag_verification_failure(self, action_id: str, actor: str, action_type: str, reason: str):
        """Flag a verification failure as a security event"""
        async with async_session() as session:
            event = SecurityEvent(
                actor=actor,
                action=action_type,
                resource=action_id,
                severity="critical",
                details=f"Verification failed: {reason}",
                status="open"
            )
            session.add(event)
            await session.commit()
            
            print(f"[WARN] Verification failure flagged: {action_type} by {actor}")


hunter_integration = HunterIntegration()


async def handle_security_alert(actor: str, rule_name: str, event_id: int, resource: str):
    """React to Hunter security alerts"""
    
    async with async_session() as session:
        task = Task(
            user=actor,
            title=f"Security Alert: {rule_name}",
            description=f"Hunter detected: {rule_name} in {resource}. Review event #{event_id}",
            status="pending",
            priority="high",
            auto_generated=True
        )
        session.add(task)
        await session.commit()
        
        print(f"[OK] Created security task for alert: {rule_name}")
    
    await memory.store(
        "system",
        "hunter_alert",
        f"Security event: {rule_name} triggered by {actor} on {resource}"
    )
    
    from .trigger_mesh import trigger_mesh, TriggerEvent
    from datetime import datetime
    
    await trigger_mesh.publish(TriggerEvent(
        event_type="hunter.alert_created",
        source="hunter",
        actor=actor,
        resource=resource,
        payload={"rule": rule_name, "event_id": event_id},
        timestamp=datetime.utcnow()
    ))
