"""
Alert Notification System
Grace sends alerts for critical events and system changes
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

from .trigger_mesh import trigger_mesh, TriggerEvent
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSystem:
    """
    Send alerts for important events
    """
    
    def __init__(self):
        self.alerts_sent = []
        self.running = False
        self.alert_handlers = []
    
    async def start(self):
        """Start alert system"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to critical events
        trigger_mesh.subscribe("error.detected", self._on_error_detected)
        trigger_mesh.subscribe("code.fixed", self._on_fix_applied)
        trigger_mesh.subscribe("startup.error", self._on_startup_error)
        trigger_mesh.subscribe("meta.systemic_issue", self._on_systemic_issue)
        
        logger.info("[ALERTS] 🔔 Alert system started")
    
    async def stop(self):
        """Stop alert system"""
        self.running = False
        logger.info("[ALERTS] Alert system stopped")
    
    async def send_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        context: Optional[Dict] = None
    ):
        """Send an alert"""
        
        alert = {
            'level': level.value,
            'title': title,
            'message': message,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.alerts_sent.append(alert)
        
        # Log alert
        await unified_logger.log_agentic_spine_decision(
            decision_type='alert_sent',
            decision_context=context or {},
            chosen_action='send_alert',
            rationale=message,
            actor='alert_system',
            confidence=1.0,
            risk_score=0.0,
            status='completed',
            outcome='alert_sent'
        )
        
        logger.info(f"[ALERTS] {level.value.upper()}: {title}")
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def register_handler(self, handler):
        """Register alert handler"""
        self.alert_handlers.append(handler)
    
    async def _on_error_detected(self, event: TriggerEvent):
        """Handle error detection events"""
        error_data = event.payload
        severity = error_data.get('severity', 'medium')
        
        if severity in ['high', 'critical']:
            await self.send_alert(
                level=AlertLevel.ERROR if severity == 'high' else AlertLevel.CRITICAL,
                title=f"Error Detected: {error_data.get('error_type')}",
                message=f"Error in {error_data.get('file_path', 'unknown')}: {error_data.get('error_message', '')}",
                context=error_data
            )
    
    async def _on_fix_applied(self, event: TriggerEvent):
        """Handle fix applied events"""
        await self.send_alert(
            level=AlertLevel.INFO,
            title="Fix Applied Successfully",
            message=f"Fixed {event.payload.get('description', 'unknown')} in {event.resource}",
            context=event.payload
        )
    
    async def _on_startup_error(self, event: TriggerEvent):
        """Handle startup errors"""
        await self.send_alert(
            level=AlertLevel.CRITICAL,
            title=f"Startup Error: {event.resource}",
            message=f"Component {event.resource} failed to start",
            context=event.payload
        )
    
    async def _on_systemic_issue(self, event: TriggerEvent):
        """Handle systemic issues"""
        await self.send_alert(
            level=AlertLevel.WARNING,
            title="Systemic Issue Detected",
            message=f"Meta-loop detected systemic issue: {event.payload.get('issue_type')}",
            context=event.payload
        )
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts_sent[-limit:] if self.alerts_sent else []


# Global instance
alert_system = AlertSystem()
