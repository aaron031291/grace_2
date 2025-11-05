import json
from datetime import datetime, timedelta
from .governance_models import SecurityRule, SecurityEvent
from .models import async_session
from sqlalchemy import select

class Hunter:
    """Security monitoring and threat detection"""
    
    def __init__(self):
        self.use_ml_prediction = True
        self.ml_confidence_threshold = 0.9
    
    async def inspect(self, actor: str, action: str, resource: str, payload: dict):
        """Check for security threats"""
        async with async_session() as session:
            result = await session.execute(select(SecurityRule))
            rules = result.scalars().all()

            triggered = []
            for rule in rules:
                if self._matches(rule, action, resource, payload):
                    rule_severity = rule.severity
                    predicted_severity = rule_severity
                    ml_confidence = 0.0
                    ml_used = False
                    
                    if self.use_ml_prediction:
                        from .ml_classifiers import alert_severity_predictor
                        
                        try:
                            alert_data = {
                                'actor': actor,
                                'action': action,
                                'resource': resource,
                                'timestamp': datetime.utcnow()
                            }
                            
                            predicted_severity, ml_confidence = await alert_severity_predictor.predict_severity(alert_data)
                            
                            if ml_confidence >= self.ml_confidence_threshold:
                                ml_used = True
                                print(f"🤖 ML override: {rule_severity} → {predicted_severity} (confidence: {ml_confidence:.2%})")
                            else:
                                predicted_severity = rule_severity
                                print(f"📊 ML prediction: {predicted_severity} (confidence: {ml_confidence:.2%}, using rule severity)")
                        except Exception as e:
                            print(f"⚠️ ML prediction failed: {e}, using rule severity")
                            predicted_severity = rule_severity
                    
                    details_dict = payload.copy()
                    details_dict['ml_prediction'] = {
                        'predicted_severity': predicted_severity if ml_used else None,
                        'confidence': ml_confidence,
                        'rule_severity': rule_severity,
                        'ml_used': ml_used
                    }
                    
                    event = SecurityEvent(
                        actor=actor,
                        action=action,
                        resource=resource,
                        severity=predicted_severity,
                        details=json.dumps(details_dict),
                    )
                    session.add(event)
                    await session.flush()
                    triggered.append((rule.name, event.id))
                    print(f"⚠️ Security alert: {rule.name} triggered by {actor} [severity: {predicted_severity}]")
            
            if triggered:
                await session.commit()
                
                from .hunter_integration import handle_security_alert
                for rule_name, event_id in triggered:
                    await handle_security_alert(actor, rule_name, event_id, resource)
                
                from .causal_graph import CausalGraph
                try:
                    graph = CausalGraph()
                    end = datetime.utcnow()
                    start = end - timedelta(hours=24)
                    await graph.build_from_events(start, end)
                    for rule_name, event_id in triggered[:1]:
                        causes = graph.find_causes(event_id, "security_event", max_depth=2)
                        if causes:
                            print(f"🔍 Hunter traced security event {event_id} to {len(causes)} causal events")
                except Exception as e:
                    print(f"⚠ Causal trace failed: {e}")
            
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
  
# Global instance  
hunter_service = Hunter()  
hunter_engine = hunter_service 


# Backwards compatibility alias for legacy imports
class HunterEngine(Hunter):
    """Alias class to maintain compatibility with legacy imports.
    Inherit from Hunter to expose the same interface.
    """
    pass
