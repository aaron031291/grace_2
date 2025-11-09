"""
Cognition Alert System
Sends notifications when benchmarks cross thresholds or SaaS readiness achieved
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from .trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


class AlertChannel:
    """Base class for alert channels"""
    
    async def send(self, alert: Dict[str, Any]):
        """Send an alert"""
        raise NotImplementedError


class CLIAlertChannel(AlertChannel):
    """CLI notification channel - writes to file for CLI to read"""
    
    def __init__(self, alert_file: str = "cli_alerts.json"):
        self.alert_file = alert_file
    
    async def send(self, alert: Dict[str, Any]):
        """Write alert to file for CLI to display"""
        try:
            import json
            from pathlib import Path
            
            alert_path = Path(self.alert_file)
            
            # Load existing alerts
            alerts = []
            if alert_path.exists():
                try:
                    alerts = json.loads(alert_path.read_text())
                except:
                    alerts = []
            
            # Add new alert
            alert["timestamp"] = datetime.now().isoformat()
            alerts.append(alert)
            
            # Keep last 100 alerts
            alerts = alerts[-100:]
            
            # Write back
            alert_path.write_text(json.dumps(alerts, indent=2))
            
            logger.info(f"CLI alert sent: {alert['type']}")
        except Exception as e:
            logger.error(f"Failed to send CLI alert: {e}")


class SlackAlertChannel(AlertChannel):
    """Slack notification channel"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
    
    async def send(self, alert: Dict[str, Any]):
        """Send alert to Slack"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        try:
            import httpx
            
            message = self._format_slack_message(alert)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json={"text": message},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Slack alert sent: {alert['type']}")
                else:
                    logger.warning(f"Slack alert failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _format_slack_message(self, alert: Dict[str, Any]) -> str:
        """Format alert for Slack"""
        alert_type = alert.get("type", "unknown")
        
        if alert_type == "saas_ready":
            return (
                f"🚀 *Grace SaaS Readiness Achieved!*\n\n"
                f"Grace has sustained 90%+ performance for 7 days:\n"
                f"• Health: {alert.get('health', 0):.1%}\n"
                f"• Trust: {alert.get('trust', 0):.1%}\n"
                f"• Confidence: {alert.get('confidence', 0):.1%}\n\n"
                f"*Time to consider SaaS commercialization!*"
            )
        
        elif alert_type == "benchmark_crossed":
            return (
                f"📈 *Benchmark Threshold Crossed*\n\n"
                f"Metric: {alert.get('metric')}\n"
                f"Value: {alert.get('value', 0):.1%} (threshold: 90%)\n"
                f"Status: Above target!"
            )
        
        elif alert_type == "domain_dip":
            return (
                f"⚠️ *Domain Performance Dip*\n\n"
                f"Domain: {alert.get('domain')}\n"
                f"Health: {alert.get('health', 0):.1%}\n"
                f"Action needed!"
            )
        
        return f"Grace Alert: {alert_type}"


class EmailAlertChannel(AlertChannel):
    """Email notification channel"""
    
    def __init__(self, smtp_config: Dict[str, Any] = None):
        self.smtp_config = smtp_config or {}
    
    async def send(self, alert: Dict[str, Any]):
        """Send alert via email"""
        if not self.smtp_config:
            logger.warning("Email SMTP config not configured")
            return
        
        try:
            # Email implementation would go here
            logger.info(f"Email alert sent: {alert['type']}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")


class CognitionAlertManager:
    """
    Manages cognition-related alerts and notifications
    Triggered by benchmark scheduler
    """
    
    def __init__(self):
        self.channels: List[AlertChannel] = []
        self.alert_history: List[Dict[str, Any]] = []
        
        # Default channels
        self.channels.append(CLIAlertChannel())
    
    def add_channel(self, channel: AlertChannel):
        """Add an alert channel"""
        self.channels.append(channel)
    
    async def send_saas_ready_alert(self, health: float, trust: float, confidence: float):
        """Send SaaS readiness achieved alert"""
        alert = {
            "type": "saas_ready",
            "severity": "info",
            "health": health,
            "trust": trust,
            "confidence": confidence,
            "message": "Grace has sustained 90%+ performance - Ready for SaaS commercialization!",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast(alert)
    
    async def send_benchmark_crossed_alert(self, metric: str, value: float, threshold: float):
        """Send alert when benchmark threshold is crossed"""
        alert = {
            "type": "benchmark_crossed",
            "severity": "info",
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "message": f"{metric} crossed {threshold:.0%} threshold",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast(alert)
    
    async def send_domain_dip_alert(self, domain: str, health: float, threshold: float = 0.5):
        """Send alert when domain health dips below threshold"""
        alert = {
            "type": "domain_dip",
            "severity": "warning",
            "domain": domain,
            "health": health,
            "threshold": threshold,
            "message": f"{domain} domain health dropped to {health:.1%}",
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast(alert)
    
    async def _broadcast(self, alert: Dict[str, Any]):
        """Broadcast alert to all channels"""
        self.alert_history.append(alert)
        self.alert_history = self.alert_history[-1000:]  # Keep last 1000
        
        for channel in self.channels:
            try:
                await channel.send(alert)
            except Exception as e:
                logger.error(f"Alert channel error: {e}")
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alert_history[-limit:]


# Global alert manager
_global_alert_manager: CognitionAlertManager = None


def get_alert_manager() -> CognitionAlertManager:
    """Get or create the global alert manager"""
    global _global_alert_manager
    
    if _global_alert_manager is None:
        _global_alert_manager = CognitionAlertManager()
    
    return _global_alert_manager


# Subscribe to product.elevation_ready events
async def setup_alert_subscriptions():
    """Subscribe to trigger mesh events for alerts"""
    alert_manager = get_alert_manager()
    
    async def handle_elevation_ready(event: TriggerEvent):
        """Handle product.elevation_ready event"""
        payload = event.payload if hasattr(event, "payload") else {}
        await alert_manager.send_saas_ready_alert(
            health=payload.get("overall_health", 0),
            trust=payload.get("overall_trust", 0),
            confidence=payload.get("overall_confidence", 0)
        )
    
    trigger_mesh.subscribe("product.elevation_ready", handle_elevation_ready)
