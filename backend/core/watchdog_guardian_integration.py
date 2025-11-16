"""
Watchdog → Guardian Integration - PRODUCTION
Forwards structured telemetry from watchdog to Guardian for auto-remediation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from .guardian_playbooks import RemediationResult

logger = logging.getLogger(__name__)


@dataclass
class WatchdogAlert:
    """Structured alert from watchdog to Guardian"""
    
    # Identity
    alert_id: str
    timestamp: str
    
    # Source
    subsystem: str  # "port_watchdog", "network_monitor", etc.
    component: str  # "port_8000", "message_bus", etc.
    
    # Issue
    failure_type: str  # "port_not_responding", "module_missing", etc.
    severity: str  # "info", "warning", "error", "critical"
    description: str
    
    # Context
    last_successful_check: Optional[str] = None
    failure_count: int = 1
    context: Dict[str, Any] = None
    
    # Recommendations
    recommended_action: str = ""
    priority: int = 5  # 1-10
    
    # Response
    handled_by: Optional[str] = None
    remediation_attempted: bool = False
    remediation_result: Optional[str] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict:
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp,
            'source': {
                'subsystem': self.subsystem,
                'component': self.component
            },
            'issue': {
                'type': self.failure_type,
                'severity': self.severity,
                'description': self.description
            },
            'tracking': {
                'last_successful': self.last_successful_check,
                'failure_count': self.failure_count
            },
            'context': self.context,
            'recommended_action': self.recommended_action,
            'priority': self.priority,
            'response': {
                'handled_by': self.handled_by,
                'remediation_attempted': self.remediation_attempted,
                'remediation_result': self.remediation_result
            }
        }


class WatchdogGuardianBridge:
    """
    Bridge between watchdog and Guardian
    
    Responsibilities:
    1. Receive raw watchdog events
    2. Structure into actionable alerts
    3. Forward to Guardian with priority
    4. Track response and outcomes
    """
    
    def __init__(self):
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        self.alert_history: List[WatchdogAlert] = []
        
        # Guardian reference
        self.guardian_playbook_registry = None
        
        # Statistics
        self.alerts_received = 0
        self.alerts_handled = 0
        self.alerts_escalated = 0
        
        # Running state
        self.running = False
        
        logger.info("[WATCHDOG-GUARDIAN] Bridge initialized")
    
    async def start(self):
        """Start processing alerts"""
        
        if self.running:
            return
        
        # Load Guardian playbook registry
        try:
            from backend.core.guardian_playbooks import guardian_playbook_registry
            self.guardian_playbook_registry = guardian_playbook_registry
            logger.info("[WATCHDOG-GUARDIAN] Connected to Guardian playbook registry")
        except Exception as e:
            logger.error(f"[WATCHDOG-GUARDIAN] Failed to load Guardian playbooks: {e}")
        
        self.running = True
        
        # Start alert processing loop
        asyncio.create_task(self._process_alerts_loop())
        
        logger.info("[WATCHDOG-GUARDIAN] Bridge started - processing alerts")
    
    async def submit_alert(self, alert: WatchdogAlert):
        """
        Submit alert from watchdog
        
        Called by watchdog when it detects an issue
        """
        
        self.alerts_received += 1
        await self.alert_queue.put(alert)
        
        logger.info(
            f"[WATCHDOG-GUARDIAN] Alert submitted: {alert.failure_type} "
            f"on {alert.component} (priority: {alert.priority})"
        )
    
    async def _process_alerts_loop(self):
        """Continuous alert processing loop"""
        
        logger.info("[WATCHDOG-GUARDIAN] Alert processing loop started")
        
        while self.running:
            try:
                # Get next alert (wait up to 10 seconds)
                alert = await asyncio.wait_for(
                    self.alert_queue.get(),
                    timeout=10.0
                )
                
                # Process alert
                await self._process_alert(alert)
                
            except asyncio.TimeoutError:
                # No alerts - continue waiting
                continue
            
            except Exception as e:
                logger.error(f"[WATCHDOG-GUARDIAN] Error processing alert: {e}")
    
    async def _process_alert(self, alert: WatchdogAlert):
        """
        Process a single alert
        
        1. Attempt auto-remediation via Guardian playbooks
        2. Log result
        3. Escalate if needed
        """
        
        logger.info(f"[WATCHDOG-GUARDIAN] Processing: {alert.description}")
        
        # Try to remediate
        if self.guardian_playbook_registry:
            result = await self.guardian_playbook_registry.remediate(
                alert.description,
                alert.context
            )
            
            if result:
                alert.remediation_attempted = True
                alert.remediation_result = result.status.value
                
                if result.success:
                    alert.handled_by = "guardian_auto_remediation"
                    self.alerts_handled += 1
                    
                    logger.info(
                        f"[WATCHDOG-GUARDIAN] ✓ Auto-remediated: {alert.failure_type} "
                        f"(actions: {', '.join(result.actions_taken)})"
                    )
                
                elif result.status == RemediationStatus.ESCALATED:
                    alert.handled_by = "escalated_to_human"
                    self.alerts_escalated += 1
                    
                    logger.warning(
                        f"[WATCHDOG-GUARDIAN] ⚠ Escalated: {alert.failure_type} "
                        f"(reason: {result.escalation_reason})"
                    )
                    
                    # Send to human escalation system
                    await self._escalate_to_human(alert, result)
                
                else:
                    logger.error(
                        f"[WATCHDOG-GUARDIAN] ✗ Remediation failed: {alert.failure_type} "
                        f"(error: {result.error})"
                    )
            else:
                logger.debug(f"[WATCHDOG-GUARDIAN] No playbook found for: {alert.failure_type}")
        
        # Save alert to history
        self.alert_history.append(alert)
        
        # Limit history size
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-5000:]
    
    async def _escalate_to_human(self, alert: WatchdogAlert, result: RemediationResult):
        """
        Escalate to human operator
        
        In production, would:
        - Send Slack/email notification
        - Create ticket
        - Update dashboard
        - Log to incident system
        """
        
        logger.critical(
            f"[WATCHDOG-GUARDIAN] HUMAN ESCALATION REQUIRED\n"
            f"  Issue: {alert.description}\n"
            f"  Component: {alert.component}\n"
            f"  Reason: {result.escalation_reason}\n"
            f"  Priority: {alert.priority}\n"
            f"  Actions attempted: {', '.join(result.actions_taken)}"
        )
        
        # TODO: Send to actual escalation systems
        # - Slack webhook
        # - PagerDuty
        # - Email
        # - Ticket system
    
    def get_stats(self) -> Dict:
        """Get bridge statistics"""
        
        handle_rate = self.alerts_handled / max(1, self.alerts_received)
        
        return {
            'alerts_received': self.alerts_received,
            'alerts_handled': self.alerts_handled,
            'alerts_escalated': self.alerts_escalated,
            'handle_rate': handle_rate,
            'queue_size': self.alert_queue.qsize(),
            'history_size': len(self.alert_history),
            'running': self.running
        }


# Global bridge
watchdog_guardian_bridge = WatchdogGuardianBridge()
