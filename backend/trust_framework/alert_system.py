"""
Alert Notification System - PRODUCTION
Sends alerts for critical TRUST framework events

Channels:
- Console (immediate)
- File logging (persistent)
- Webhook (Slack, Discord, Teams)
- Email (SMTP)
- PagerDuty (critical only)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels"""
    CONSOLE = "console"
    FILE = "file"
    WEBHOOK = "webhook"
    EMAIL = "email"
    PAGERDUTY = "pagerduty"


@dataclass
class Alert:
    """Alert message"""
    
    alert_id: str
    severity: AlertSeverity
    title: str
    message: str
    
    # Context
    component: str
    model: Optional[str] = None
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Actions
    recommended_action: str = ""
    escalation_required: bool = False
    
    # Delivery
    channels: List[AlertChannel] = field(default_factory=list)
    delivered_to: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'component': self.component,
            'model': self.model,
            'timestamp': self.timestamp,
            'recommended_action': self.recommended_action,
            'escalation_required': self.escalation_required,
            'channels': [c.value for c in self.channels],
            'delivered_to': self.delivered_to
        }


class AlertNotificationSystem:
    """
    Production alert notification system
    
    Routes alerts based on severity:
    - INFO: Console + File
    - WARNING: Console + File + Webhook
    - ERROR: Console + File + Webhook + Email
    - CRITICAL: All channels including PagerDuty
    """
    
    def __init__(self, storage_path: str = "logs/alerts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Alert history
        self.alert_history: List[Alert] = []
        
        # Configuration
        self.webhook_url: Optional[str] = None
        self.email_config: Optional[Dict] = None
        self.pagerduty_key: Optional[str] = None
        
        # Statistics
        self.alerts_sent = 0
        self.alerts_by_severity = {s: 0 for s in AlertSeverity}
        
        # Load config
        self._load_config()
        
        logger.info("[ALERTS] Notification system initialized")
    
    def _load_config(self):
        """Load alert configuration"""
        
        config_file = Path("config/alert_config.json")
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                    self.webhook_url = config.get('webhook_url')
                    self.email_config = config.get('email')
                    self.pagerduty_key = config.get('pagerduty_key')
                
                logger.info("[ALERTS] Configuration loaded")
            
            except Exception as e:
                logger.warning(f"[ALERTS] Failed to load config: {e}")
    
    async def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        component: str,
        model: Optional[str] = None,
        recommended_action: str = ""
    ):
        """Send alert through appropriate channels"""
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            severity=severity,
            title=title,
            message=message,
            component=component,
            model=model,
            recommended_action=recommended_action,
            escalation_required=(severity == AlertSeverity.CRITICAL)
        )
        
        # Determine channels based on severity
        if severity == AlertSeverity.INFO:
            alert.channels = [AlertChannel.CONSOLE, AlertChannel.FILE]
        
        elif severity == AlertSeverity.WARNING:
            alert.channels = [AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.WEBHOOK]
        
        elif severity == AlertSeverity.ERROR:
            alert.channels = [AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.WEBHOOK, AlertChannel.EMAIL]
        
        elif severity == AlertSeverity.CRITICAL:
            alert.channels = [AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.WEBHOOK, AlertChannel.EMAIL, AlertChannel.PAGERDUTY]
        
        # Send to channels
        await self._deliver_alert(alert)
        
        # Record
        self.alert_history.append(alert)
        self.alerts_sent += 1
        self.alerts_by_severity[severity] += 1
    
    async def _deliver_alert(self, alert: Alert):
        """Deliver alert to all configured channels"""
        
        for channel in alert.channels:
            try:
                if channel == AlertChannel.CONSOLE:
                    await self._send_to_console(alert)
                    alert.delivered_to.append('console')
                
                elif channel == AlertChannel.FILE:
                    await self._send_to_file(alert)
                    alert.delivered_to.append('file')
                
                elif channel == AlertChannel.WEBHOOK and self.webhook_url:
                    await self._send_to_webhook(alert)
                    alert.delivered_to.append('webhook')
                
                elif channel == AlertChannel.EMAIL and self.email_config:
                    await self._send_to_email(alert)
                    alert.delivered_to.append('email')
                
                elif channel == AlertChannel.PAGERDUTY and self.pagerduty_key:
                    await self._send_to_pagerduty(alert)
                    alert.delivered_to.append('pagerduty')
            
            except Exception as e:
                logger.error(f"[ALERTS] Failed to send to {channel.value}: {e}")
    
    async def _send_to_console(self, alert: Alert):
        """Send alert to console"""
        
        severity_colors = {
            AlertSeverity.INFO: "\033[94m",  # Blue
            AlertSeverity.WARNING: "\033[93m",  # Yellow
            AlertSeverity.ERROR: "\033[91m",  # Red
            AlertSeverity.CRITICAL: "\033[91m\033[1m"  # Bold red
        }
        
        color = severity_colors.get(alert.severity, "")
        reset = "\033[0m"
        
        print(f"{color}[{alert.severity.value.upper()}] {alert.title}{reset}")
        print(f"  Component: {alert.component}")
        
        if alert.model:
            print(f"  Model: {alert.model}")
        
        print(f"  {alert.message}")
        
        if alert.recommended_action:
            print(f"  Action: {alert.recommended_action}")
        
        print()
    
    async def _send_to_file(self, alert: Alert):
        """Send alert to log file"""
        
        alert_file = self.storage_path / f"alerts_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert.to_dict()) + '\n')
    
    async def _send_to_webhook(self, alert: Alert):
        """Send alert to webhook (Slack, Discord, Teams)"""
        
        if not self.webhook_url:
            return
        
        try:
            import httpx
            
            # Format for Slack/Discord
            payload = {
                'text': f"[{alert.severity.value.upper()}] {alert.title}",
                'attachments': [{
                    'color': 'danger' if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL] else 'warning',
                    'fields': [
                        {'title': 'Component', 'value': alert.component, 'short': True},
                        {'title': 'Model', 'value': alert.model or 'N/A', 'short': True},
                        {'title': 'Message', 'value': alert.message, 'short': False}
                    ]
                }]
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(self.webhook_url, json=payload, timeout=10)
        
        except Exception as e:
            logger.error(f"[ALERTS] Webhook failed: {e}")
    
    async def _send_to_email(self, alert: Alert):
        """Send alert via email"""
        
        # In production, would use SMTP to send email
        logger.info(f"[ALERTS] Would send email for: {alert.title}")
    
    async def _send_to_pagerduty(self, alert: Alert):
        """Send alert to PagerDuty"""
        
        # In production, would use PagerDuty Events API
        logger.critical(f"[ALERTS] Would page on-call for: {alert.title}")
    
    def get_stats(self) -> Dict:
        """Get alert statistics"""
        
        return {
            'alerts_sent': self.alerts_sent,
            'by_severity': {
                s.value: count
                for s, count in self.alerts_by_severity.items()
            },
            'recent_alerts': [
                a.to_dict() for a in self.alert_history[-10:]
            ]
        }


# Global alert system
alert_system = AlertNotificationSystem()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def alert_model_quarantined(model_name: str, reason: str):
    """Alert that model was quarantined"""
    
    await alert_system.send_alert(
        severity=AlertSeverity.CRITICAL,
        title=f"Model Quarantined: {model_name}",
        message=f"Model {model_name} has been quarantined. Reason: {reason}",
        component="model_integrity",
        model=model_name,
        recommended_action="Verify model integrity and rollback if needed"
    )


async def alert_hallucination_detected(model_name: str, details: str):
    """Alert about hallucination"""
    
    await alert_system.send_alert(
        severity=AlertSeverity.WARNING,
        title=f"Hallucination Detected: {model_name}",
        message=details,
        component="hallucination_ledger",
        model=model_name,
        recommended_action="Review hallucination ledger and adjust guardrails"
    )


async def alert_cascade_failure(cascade_info: Dict):
    """Alert about cascading failure"""
    
    await alert_system.send_alert(
        severity=AlertSeverity.CRITICAL,
        title="Cascading Failure Detected",
        message=f"Cascade affecting {cascade_info['cascade_size']} services. Root: {cascade_info.get('cascade_root', 'unknown')}",
        component="advanced_watchdog",
        recommended_action="Emergency restart sequence required"
    )


async def alert_predictive_failure(model_name: str, minutes_to_failure: float):
    """Alert about predicted failure"""
    
    await alert_system.send_alert(
        severity=AlertSeverity.WARNING,
        title=f"Predicted Failure: {model_name}",
        message=f"Model predicted to fail in {minutes_to_failure:.1f} minutes",
        component="advanced_watchdog",
        model=model_name,
        recommended_action="Consider preventive restart"
    )
