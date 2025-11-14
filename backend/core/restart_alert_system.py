"""
Restart Alert System
Monitors restart events and notifies co-pilot/admin

Subscribes to:
- kernel.restart.initiated
- kernel.restart.success  
- kernel.restart.failed
- grace.restart.initiated
- grace.restart.success
- grace.restart.failed
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import json

from backend.core.message_bus import message_bus


class RestartAlertSystem:
    """Monitors and reports on all restart events"""
    
    def __init__(self):
        self.alerts = []
        self.alert_dir = Path("alerts")
        self.alert_dir.mkdir(exist_ok=True)
        
        self._subscription_tasks = []
    
    async def start(self):
        """Start monitoring restart events"""
        
        # Subscribe to kernel restart events
        topics = [
            "kernel.restart.initiated",
            "kernel.restart.success",
            "kernel.restart.failed",
            "kernel.restart.max_attempts",
            "system.critical_kernel_down"
        ]
        
        for topic in topics:
            task = asyncio.create_task(self._monitor_topic(topic))
            self._subscription_tasks.append(task)
        
        print("[ALERT-SYS] Restart alert system monitoring active")
    
    async def _monitor_topic(self, topic: str):
        """Monitor a specific topic"""
        try:
            queue = await message_bus.subscribe(
                subscriber="restart_alerts",
                topic=topic
            )
            
            while True:
                msg = await queue.get()
                await self._handle_restart_event(topic, msg.payload)
        
        except Exception as e:
            print(f"[ALERT-SYS] Error monitoring {topic}: {e}")
    
    async def _handle_restart_event(self, event_type: str, payload: Dict[str, Any]):
        """Handle a restart event"""
        
        alert = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }
        
        self.alerts.append(alert)
        
        # Determine severity
        if "failed" in event_type or "critical" in event_type:
            severity = "CRITICAL"
        elif "initiated" in event_type:
            severity = "WARNING"
        else:
            severity = "INFO"
        
        # Log to console
        kernel_name = payload.get("kernel_name", "unknown")
        reason = payload.get("reason", "unknown")
        
        if severity == "CRITICAL":
            print(f"[ALERT-SYS] 🚨 CRITICAL: {event_type} - {kernel_name}")
        elif severity == "WARNING":
            print(f"[ALERT-SYS] ⚠️ WARNING: {event_type} - {kernel_name} (reason: {reason})")
        else:
            print(f"[ALERT-SYS] ℹ️ INFO: {event_type} - {kernel_name}")
        
        # Save alert to file
        await self._save_alert(alert, severity)
        
        # Send to co-pilot (future: email, Slack, Discord, etc.)
        await self._notify_copilot(alert, severity)
    
    async def _save_alert(self, alert: Dict[str, Any], severity: str):
        """Save alert to file"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        alert_file = self.alert_dir / f"{severity.lower()}_{timestamp}.json"
        
        try:
            with open(alert_file, 'w') as f:
                json.dump(alert, f, indent=2)
        except Exception as e:
            print(f"[ALERT-SYS] Failed to save alert: {e}")
    
    async def _notify_copilot(self, alert: Dict[str, Any], severity: str):
        """Notify co-pilot of restart event"""
        
        # Future integrations:
        # - Send email notification
        # - Post to Slack/Discord
        # - Push notification to mobile app
        # - Update dashboard
        
        # For now, just create a notification file
        notification_file = self.alert_dir / "latest_notification.json"
        
        notification = {
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "event": alert["event_type"],
            "summary": self._create_summary(alert),
            "requires_attention": severity in ["CRITICAL", "WARNING"]
        }
        
        try:
            with open(notification_file, 'w') as f:
                json.dump(notification, f, indent=2)
        except:
            pass
    
    def _create_summary(self, alert: Dict[str, Any]) -> str:
        """Create human-readable summary"""
        
        event_type = alert["event_type"]
        payload = alert["payload"]
        
        if "kernel.restart.initiated" in event_type:
            kernel = payload.get("kernel_name")
            reason = payload.get("reason")
            return f"Kernel '{kernel}' is being restarted (reason: {reason})"
        
        elif "kernel.restart.success" in event_type:
            kernel = payload.get("kernel_name")
            return f"Kernel '{kernel}' restarted successfully"
        
        elif "kernel.restart.failed" in event_type:
            kernel = payload.get("kernel_name")
            error = payload.get("error")
            return f"Kernel '{kernel}' restart FAILED: {error}"
        
        elif "max_attempts" in event_type:
            kernel = payload.get("kernel_name")
            attempts = payload.get("restart_attempts")
            return f"Kernel '{kernel}' hit max restart attempts ({attempts}) - MANUAL INTERVENTION NEEDED"
        
        elif "critical_kernel_down" in event_type:
            kernel = payload.get("kernel_name")
            return f"CRITICAL KERNEL DOWN: {kernel} - System stability at risk"
        
        return str(payload)
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts[-count:]
    
    async def shutdown(self):
        """Stop alert system"""
        for task in self._subscription_tasks:
            task.cancel()


# Global instance
restart_alert_system = RestartAlertSystem()
