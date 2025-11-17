"""
Trigger-Playbook Integration
Connects the trigger system to self-healing playbooks

Workflow:
1. Trigger fires → publishes event.incident
2. This integration subscribes to event.incident
3. Looks up appropriate playbook
4. Executes playbook
5. Publishes incident.resolved
6. Updates trust scores
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from backend.core.message_bus import message_bus, MessagePriority
from backend.self_heal.auto_healing_playbooks import playbook_registry


class TriggerPlaybookIntegration:
    """
    Integrates triggers with playbooks
    
    Layer 1 Integration:
    - Subscribes to event.incident from trigger system
    - Executes playbooks from playbook registry
    - Publishes incident.resolved
    - Updates trust scores in Clarity
    - Logs to immutable log
    """
    
    def __init__(self):
        self.active_incidents = {}
        self.resolved_incidents = []
        
        self._incident_task: Optional[asyncio.Task] = None
        self._task_queue_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start integration"""
        
        # Subscribe to incident events
        self._incident_task = asyncio.create_task(self._monitor_incidents())
        
        # Subscribe to task queue
        self._task_queue_task = asyncio.create_task(self._process_task_queue())
        
        print("[TRIGGER-PLAYBOOK] Integration started")
    
    async def _monitor_incidents(self):
        """Monitor event.incident events"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="trigger_playbook_integration",
                topic="event.incident"
            )
            
            while True:
                msg = await queue.get()
                await self._handle_incident(msg.payload)
        
        except Exception as e:
            print(f"[TRIGGER-PLAYBOOK] Incident monitor error: {e}")
    
    async def _process_task_queue(self):
        """Process task.enqueue events"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="trigger_playbook_integration",
                topic="task.enqueue"
            )
            
            while True:
                msg = await queue.get()
                
                if msg.payload.get("task_type") == "self_healing":
                    await self._execute_healing_task(msg.payload)
        
        except Exception as e:
            print(f"[TRIGGER-PLAYBOOK] Task queue error: {e}")
    
    async def _handle_incident(self, incident: Dict[str, Any]):
        """Handle an incident event"""
        
        incident_id = f"{incident['trigger_id']}_{incident['fire_count']}"
        trigger_type = incident.get("trigger_type")
        playbook_name = incident.get("playbook")
        severity = incident.get("severity")
        
        print(f"[TRIGGER-PLAYBOOK] 🚨 Incident: {trigger_type} (severity: {severity})")
        print(f"[TRIGGER-PLAYBOOK] 📋 Executing playbook: {playbook_name}")
        
        # Store incident
        self.active_incidents[incident_id] = {
            **incident,
            "incident_id": incident_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "executing"
        }
        
        # Execute playbook
        try:
            result = await playbook_registry.execute(
                playbook_name,
                incident.get("context", {})
            )
            
            # Mark as resolved
            self.active_incidents[incident_id]["status"] = "resolved"
            self.active_incidents[incident_id]["completed_at"] = datetime.utcnow().isoformat()
            self.active_incidents[incident_id]["result"] = result
            
            # Move to resolved
            self.resolved_incidents.append(self.active_incidents.pop(incident_id))
            
            # Publish resolution
            await message_bus.publish(
                source="trigger_playbook_integration",
                topic="incident.resolved",
                payload={
                    "incident_id": incident_id,
                    "trigger_type": trigger_type,
                    "playbook": playbook_name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.NORMAL
            )
            
            print(f"[TRIGGER-PLAYBOOK] ✅ Incident resolved: {incident_id}")
            
            # Update trust score (successful healing)
            await self._update_trust(incident, result, success=True)
        
        except Exception as e:
            print(f"[TRIGGER-PLAYBOOK] ❌ Playbook execution failed: {e}")
            
            self.active_incidents[incident_id]["status"] = "failed"
            self.active_incidents[incident_id]["error"] = str(e)
            
            # Update trust score (failed healing)
            await self._update_trust(incident, {"error": str(e)}, success=False)
    
    async def _execute_healing_task(self, task: Dict[str, Any]):
        """Execute a queued healing task"""
        
        playbook_name = task.get("playbook")
        context = task.get("context", {})
        incident_id = task.get("incident_id")
        
        print(f"[TRIGGER-PLAYBOOK] 📋 Executing queued task: {playbook_name}")
        
        try:
            result = await playbook_registry.execute(playbook_name, context)
            
            # Publish task completion
            await message_bus.publish(
                source="trigger_playbook_integration",
                topic="task.completed",
                payload={
                    "incident_id": incident_id,
                    "playbook": playbook_name,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.NORMAL
            )
            
            print(f"[TRIGGER-PLAYBOOK] ✅ Task completed: {incident_id}")
        
        except Exception as e:
            print(f"[TRIGGER-PLAYBOOK] ❌ Task failed: {e}")
            
            await message_bus.publish(
                source="trigger_playbook_integration",
                topic="task.failed",
                payload={
                    "incident_id": incident_id,
                    "playbook": playbook_name,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.HIGH
            )
    
    async def _update_trust(
        self,
        incident: Dict[str, Any],
        result: Dict[str, Any],
        success: bool
    ):
        """Update trust scores based on healing outcome"""
        
        trust_delta = 0.05 if success else -0.10
        
        await message_bus.publish(
            source="trigger_playbook_integration",
            topic="trust.score.update",
            payload={
                "component": "self_healing",
                "delta": trust_delta,
                "reason": f"playbook_{incident.get('playbook')}_{'success' if success else 'failed'}",
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.NORMAL
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "active_incidents": len(self.active_incidents),
            "resolved_incidents": len(self.resolved_incidents),
            "recent_resolutions": self.resolved_incidents[-10:] if self.resolved_incidents else []
        }
    
    async def shutdown(self):
        """Stop integration"""
        if self._incident_task:
            self._incident_task.cancel()
        if self._task_queue_task:
            self._task_queue_task.cancel()


# Global instance
trigger_playbook_integration = TriggerPlaybookIntegration()
