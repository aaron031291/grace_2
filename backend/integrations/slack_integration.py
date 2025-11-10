"""Slack integration for Grace notifications and alerts"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from backend.trigger_mesh import trigger_mesh, TriggerEvent


class SlackIntegration:
    """Handles Slack notifications and webhook integrations"""

    def __init__(self):
        self.webhook_url = None
        self.bot_token = None
        self.channel = "#grace-alerts"
        self.enabled = False

    async def initialize(self, webhook_url: str = None, bot_token: str = None, channel: str = "#grace-alerts"):
        """Initialize Slack integration"""
        self.webhook_url = webhook_url
        self.bot_token = bot_token
        self.channel = channel

        if webhook_url or bot_token:
            self.enabled = True
            print("✅ Slack integration initialized")
        else:
            print("⚠️ Slack integration not configured - set SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN")

    async def send_notification(self, title: str, message: str, color: str = "good",
                              fields: list = None, channel: str = None) -> bool:
        """Send a notification to Slack"""
        if not self.enabled:
            return False

        payload = {
            "channel": channel or self.channel,
            "username": "Grace AI",
            "icon_emoji": ":robot_face:",
            "attachments": [{
                "title": title,
                "text": message,
                "color": color,
                "fields": fields or [],
                "ts": datetime.utcnow().timestamp()
            }]
        }

        try:
            if self.webhook_url:
                # Use webhook
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.webhook_url,
                        json=payload,
                        timeout=10
                    )
                    return response.status_code == 200
            elif self.bot_token:
                # Use bot API
                import httpx
                headers = {"Authorization": f"Bearer {self.bot_token}"}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://slack.com/api/chat.postMessage",
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    result = response.json()
                    return result.get("ok", False)
        except Exception as e:
            print(f"❌ Slack notification failed: {e}")
            return False

        return False

    async def notify_incident(self, incident: Dict[str, Any]):
        """Send incident notification"""
        title = f"🚨 Incident: {incident.get('type', 'Unknown')}"
        message = incident.get('description', 'Incident detected')

        fields = [
            {"title": "Severity", "value": incident.get('severity', 'unknown'), "short": True},
            {"title": "Resource", "value": incident.get('resource', 'unknown'), "short": True},
            {"title": "Time", "value": datetime.utcnow().strftime('%H:%M:%S UTC'), "short": True}
        ]

        color = "danger" if incident.get('severity') == 'critical' else "warning"

        return await self.send_notification(title, message, color, fields)

    async def notify_recovery(self, recovery: Dict[str, Any]):
        """Send recovery action notification"""
        title = f"🔧 Recovery: {recovery.get('action', 'Unknown')}"
        message = f"Grace initiated recovery: {recovery.get('description', 'Automated recovery action')}"

        fields = [
            {"title": "Playbook", "value": recovery.get('playbook', 'unknown'), "short": True},
            {"title": "Risk Score", "value": f"{recovery.get('risk_score', 0):.2f}", "short": True},
            {"title": "Status", "value": recovery.get('status', 'executing'), "short": True}
        ]

        color = "good" if recovery.get('status') == 'completed' else "warning"

        return await self.send_notification(title, message, color, fields)

    async def notify_system_health(self, health: Dict[str, Any]):
        """Send system health summary"""
        title = "🏥 System Health Report"
        message = f"Overall health: {health.get('overall_health', 0):.1f}%"

        fields = [
            {"title": "Health Score", "value": f"{health.get('overall_health', 0):.1f}%", "short": True},
            {"title": "Trust Score", "value": f"{health.get('overall_trust', 0):.1f}%", "short": True},
            {"title": "Systems Running", "value": f"{health.get('subsystems_running', 0)}/{health.get('total_subsystems', 0)}", "short": True}
        ]

        color = "good" if health.get('overall_health', 0) > 80 else "warning" if health.get('overall_health', 0) > 60 else "danger"

        return await self.send_notification(title, message, color, fields)

    async def handle_slack_event(self, event: TriggerEvent):
        """Handle incoming Slack events/commands"""
        # This would handle Slack commands sent to Grace
        # For now, just acknowledge
        print(f"📨 Slack event received: {event.event_type}")


# Global instance
slack_integration = SlackIntegration()