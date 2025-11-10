"""PagerDuty integration for incident management and escalation"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from backend.trigger_mesh import trigger_mesh, TriggerEvent


class PagerDutyIntegration:
    """Handles PagerDuty incident creation and management"""

    def __init__(self):
        self.api_key = None
        self.service_id = None
        self.enabled = False
        self.base_url = "https://api.pagerduty.com"

    async def initialize(self, api_key: str = None, service_id: str = None):
        """Initialize PagerDuty integration"""
        self.api_key = api_key
        self.service_id = service_id

        if api_key and service_id:
            self.enabled = True
            print("✅ PagerDuty integration initialized")
        else:
            print("⚠️ PagerDuty integration not configured - set PAGERDUTY_API_KEY and PAGERDUTY_SERVICE_ID")

    async def create_incident(self, title: str, description: str, urgency: str = "high",
                            details: Dict[str, Any] = None) -> Optional[str]:
        """Create a new PagerDuty incident"""
        if not self.enabled:
            return None

        payload = {
            "incident": {
                "type": "incident",
                "title": title,
                "service": {
                    "id": self.service_id,
                    "type": "service_reference"
                },
                "urgency": urgency,
                "body": {
                    "type": "incident_body",
                    "details": description
                },
                "details": details or {}
            }
        }

        try:
            import httpx
            headers = {
                "Authorization": f"Token token={self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.pagerduty+json;version=2"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/incidents",
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                if response.status_code == 201:
                    incident_data = response.json()
                    incident_id = incident_data["incident"]["id"]
                    print(f"✅ PagerDuty incident created: {incident_id}")
                    return incident_id
                else:
                    print(f"❌ PagerDuty incident creation failed: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"❌ PagerDuty API error: {e}")
            return None

    async def resolve_incident(self, incident_id: str, resolution: str = "Resolved by Grace AI") -> bool:
        """Resolve a PagerDuty incident"""
        if not self.enabled:
            return False

        payload = {
            "incident": {
                "type": "incident",
                "status": "resolved",
                "resolution": resolution
            }
        }

        try:
            import httpx
            headers = {
                "Authorization": f"Token token={self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.pagerduty+json;version=2"
            }

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/incidents/{incident_id}",
                    headers=headers,
                    json=payload,
                    timeout=10
                )

                success = response.status_code == 200
                if success:
                    print(f"✅ PagerDuty incident resolved: {incident_id}")
                else:
                    print(f"❌ PagerDuty incident resolution failed: {response.status_code}")
                return success

        except Exception as e:
            print(f"❌ PagerDuty API error: {e}")
            return False

    async def notify_critical_incident(self, incident: Dict[str, Any]) -> Optional[str]:
        """Create PagerDuty incident for critical system issues"""
        title = f"CRITICAL: {incident.get('type', 'System Incident')}"
        description = incident.get('description', 'Critical system incident detected by Grace AI')

        details = {
            "severity": incident.get('severity', 'critical'),
            "resource": incident.get('resource', 'unknown'),
            "detected_by": "Grace AI Agentic Spine",
            "timestamp": datetime.utcnow().isoformat(),
            "context": incident
        }

        return await self.create_incident(title, description, "high", details)

    async def notify_high_risk_action(self, action: Dict[str, Any]) -> Optional[str]:
        """Create PagerDuty incident for high-risk autonomous actions"""
        title = f"HIGH RISK: Autonomous Action {action.get('type', 'Unknown')}"
        description = f"Grace AI is executing high-risk action: {action.get('description', 'Autonomous system action')}"

        details = {
            "risk_score": action.get('risk_score', 0),
            "action_type": action.get('type', 'unknown'),
            "justification": action.get('justification', 'Autonomous decision'),
            "timestamp": datetime.utcnow().isoformat(),
            "context": action
        }

        return await self.create_incident(title, description, "high", details)

    async def escalate_governance_issue(self, issue: Dict[str, Any]) -> Optional[str]:
        """Escalate governance or approval issues"""
        title = f"GOVERNANCE: {issue.get('type', 'Approval Required')}"
        description = f"Governance escalation: {issue.get('description', 'Human approval required for high-risk action')}"

        details = {
            "issue_type": issue.get('type', 'governance'),
            "pending_approvals": issue.get('pending_count', 0),
            "escalation_reason": issue.get('reason', 'High-risk action requires approval'),
            "timestamp": datetime.utcnow().isoformat(),
            "context": issue
        }

        return await self.create_incident(title, description, "low", details)

    async def handle_pagerduty_webhook(self, webhook_data: Dict[str, Any]):
        """Handle incoming PagerDuty webhooks"""
        # Process PagerDuty webhook events
        event_type = webhook_data.get("event", {}).get("type")

        if event_type == "incident.acknowledged":
            print("📨 PagerDuty incident acknowledged")
        elif event_type == "incident.resolved":
            print("📨 PagerDuty incident resolved")
        else:
            print(f"📨 PagerDuty webhook: {event_type}")

        # Could trigger Grace actions based on PagerDuty events
        await trigger_mesh.publish(TriggerEvent(
            event_type="external.pagerduty_event",
            source="pagerduty_integration",
            actor="pagerduty",
            resource="incident",
            payload=webhook_data,
            timestamp=datetime.utcnow()
        ))


# Global instance
pagerduty_integration = PagerDutyIntegration()