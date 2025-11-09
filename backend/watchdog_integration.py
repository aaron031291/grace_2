"""
Watchdog Integration with Unified Logic
Maps anomalies to playbooks and captures outcomes for learning
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def setup_watchdog_integration():
    """
    Hook anomaly watchdog to:
    1. Metrics snapshots/forecasts
    2. Logic update tracking
    3. Playbook execution
    4. Knowledge capture
    """
    
    try:
        from backend.trigger_mesh import trigger_mesh
        from backend.anomaly_watchdog import anomaly_watchdog
        from backend.capa_system import capa_system, CAPAType, CAPASeverity
        
        # Track playbook execution outcomes
        playbook_failures = {}
        
        async def on_anomaly_detected(event):
            """Handle detected anomalies"""
            anomaly = event.payload
            anomaly_id = anomaly.get("anomaly_id")
            severity = anomaly.get("severity", "medium")
            component = anomaly.get("component")
            metric = anomaly.get("metric")
            
            logger.info(f"[WATCHDOG_INTEGRATION] Anomaly detected: {anomaly_id}")
            
            # Map to playbook
            playbook_id = await map_anomaly_to_playbook(anomaly)
            
            if playbook_id:
                logger.info(f"[WATCHDOG_INTEGRATION] Mapped to playbook: {playbook_id}")
                
                # Track execution
                execution_id = f"exec_{anomaly_id}"
                
                # Wait for playbook outcome
                # (In production, subscribe to playbook.execution_complete)
                
            # Auto-create CAPA for critical anomalies
            if severity == "critical":
                capa_id = await capa_system.create_capa(
                    title=f"Critical anomaly: {metric}",
                    description=f"Anomaly detected in {component}: {anomaly.get('description')}",
                    capa_type=CAPAType.CORRECTIVE,
                    severity=CAPASeverity.CRITICAL,
                    source="anomaly_watchdog",
                    detected_by="watchdog_integration",
                    evidence=anomaly
                )
                
                logger.info(f"[WATCHDOG_INTEGRATION] Auto-created CAPA: {capa_id}")
        
        async def on_playbook_outcome(event):
            """Capture playbook execution outcomes"""
            playbook_id = event.payload.get("playbook_id")
            outcome = event.payload.get("outcome")
            anomaly_id = event.payload.get("anomaly_id")
            
            # Store in knowledge for next boot pre-check
            knowledge_entry = {
                "anomaly_id": anomaly_id,
                "playbook_id": playbook_id,
                "outcome": outcome,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "effective": outcome == "success"
            }
            
            await store_playbook_outcome_knowledge(knowledge_entry)
            
            # Check for repeated failures
            if outcome == "failure":
                playbook_failures[playbook_id] = playbook_failures.get(playbook_id, 0) + 1
                
                if playbook_failures[playbook_id] >= 2:
                    # Same playbook failed twice - escalate
                    await escalate_to_human(
                        reason=f"Playbook {playbook_id} failed {playbook_failures[playbook_id]} times",
                        anomaly_id=anomaly_id,
                        playbook_id=playbook_id
                    )
        
        # Subscribe to events
        trigger_mesh.subscribe("anomaly.detected", on_anomaly_detected)
        trigger_mesh.subscribe("playbook.execution_complete", on_playbook_outcome)
        
        logger.info("[WATCHDOG_INTEGRATION] Subscribed to anomaly and playbook events")
        
    except Exception as e:
        logger.error(f"[WATCHDOG_INTEGRATION] Failed to setup: {e}")


async def map_anomaly_to_playbook(anomaly: Dict[str, Any]) -> Optional[str]:
    """Map anomaly to appropriate playbook"""
    
    metric = anomaly.get("metric")
    component = anomaly.get("component")
    severity = anomaly.get("severity")
    
    # Logic update rollback
    if "logic_hub" in metric and "rollback" in metric:
        return "logic_update_rollback"
    
    # Database issues
    if "database" in component or "db_" in metric:
        return "database_connection_fix"
    
    # Memory issues
    if "memory" in component:
        return "memory_optimization"
    
    # API issues
    if "api" in metric or "latency" in metric:
        return "api_performance_optimization"
    
    return None


async def store_playbook_outcome_knowledge(entry: Dict[str, Any]):
    """Store playbook outcome in knowledge base for boot pre-checks"""
    
    try:
        from backend.knowledge import knowledge_service
        
        await knowledge_service.store(
            domain="playbook_outcomes",
            content=f"Playbook {entry['playbook_id']} outcome: {entry['outcome']}",
            metadata=entry,
            source="watchdog_integration"
        )
        
        logger.info(f"[WATCHDOG_INTEGRATION] Stored outcome knowledge: {entry['playbook_id']}")
        
    except Exception as e:
        logger.debug(f"Could not store knowledge: {e}")


async def escalate_to_human(
    reason: str,
    anomaly_id: str,
    playbook_id: str
):
    """Escalate repeated failures to human review"""
    
    logger.error(f"[WATCHDOG_INTEGRATION] ESCALATION: {reason}")
    
    try:
        # Create high-priority CAPA
        from backend.capa_system import capa_system, CAPAType, CAPASeverity
        
        capa_id = await capa_system.create_capa(
            title=f"Repeated playbook failure: {playbook_id}",
            description=reason,
            capa_type=CAPAType.PREVENTIVE,
            severity=CAPASeverity.HIGH,
            source="escalation",
            detected_by="watchdog_integration",
            evidence={
                "anomaly_id": anomaly_id,
                "playbook_id": playbook_id,
                "failure_count": 2
            }
        )
        
        logger.info(f"[WATCHDOG_INTEGRATION] Created escalation CAPA: {capa_id}")
        
        # Notify (AMP integration or alert system)
        try:
            from backend.alert_system import alert_system
            
            await alert_system.send_alert(
                severity="high",
                title=f"Playbook Failure Escalation",
                message=reason,
                metadata={"capa_id": capa_id}
            )
        except Exception as e:
            logger.debug(f"Could not send alert: {e}")
        
    except Exception as e:
        logger.error(f"[WATCHDOG_INTEGRATION] Escalation failed: {e}")


# Initialize on module import
watchdog_integration_ready = False
