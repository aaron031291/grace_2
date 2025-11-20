"""
Event Bus Service
Pub/sub system for inter-service communication
Connects log watchers, self-healing, and immutable logs
"""

import asyncio
from typing import Dict, Any, Callable, List
from datetime import datetime
from collections import defaultdict


class EventBus:
    """
    Simple pub/sub event bus for decoupled service communication
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    async def publish(self, event_type: str, payload: Dict[str, Any]):
        """
        Publish an event to all subscribers
        
        Args:
            event_type: Type of event (e.g., 'librarian.file.created')
            payload: Event data
        """
        event = {
            'type': event_type,
            'payload': payload,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        subscribers = self.subscribers.get(event_type, [])
        for subscriber in subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                print(f"[EventBus] Error in subscriber for {event_type}: {e}")
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Event to listen for (or '*' for all events)
            handler: Function to call when event occurs
        """
        self.subscribers[event_type].append(handler)
        print(f"[EventBus] Subscribed {handler.__name__} to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Remove a subscription"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
    
    def get_recent_events(self, limit: int = 50, event_type: str = None) -> List[Dict[str, Any]]:
        """Get recent events from history"""
        if event_type:
            filtered = [e for e in self.event_history if e['type'] == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            'total_subscribers': sum(len(subs) for subs in self.subscribers.values()),
            'event_types': len(self.subscribers),
            'events_in_history': len(self.event_history),
            'subscriptions_by_type': {
                event_type: len(subs)
                for event_type, subs in self.subscribers.items()
            }
        }


# Global event bus instance
event_bus = EventBus()


# ==== Example Event Handlers ====

async def log_to_immutable_on_event(event: Dict[str, Any]):
    """
    Handler that logs important events to immutable log
    """
    event_type = event.get('type')
    
    # Log specific event types to immutable log
    if event_type in [
        'librarian.file.created',
        'librarian.file.modified',
        'ingestion.completed',
        'ingestion.failed',
        'self_healing.triggered',
        'schema.approved',
    ]:
        print(f"[ImmutableLog] Recording: {event_type}")
        # TODO: Integrate with actual immutable log
        # from backend.immutable_log import immutable_log
        # await immutable_log.append(event)


async def trigger_healing_on_failure(event: Dict[str, Any]):
    """
    Consolidated handler that triggers self-healing on failure events.
    Routes through unified trigger mesh for consistency.
    """
    event_type = event.get('type')
    payload = event.get('payload', {})
    
    from backend.self_heal.trigger_playbook_integration import trigger_playbook_integration
    
    if event_type == 'ingestion.failed':
        context = {
            "error_type": "ingestion_failed",
            "file_path": payload.get('file_path'),
            "error_details": payload.get('error'),
            "triggered_by": "event_bus"
        }
        
        await trigger_playbook_integration.trigger_healing(
            trigger_type="ingestion_failure",
            context=context,
            playbook_hint="ingestion_replay"
        )
    
    elif event_type == 'log_pattern.critical':
        line_lower = payload.get('line', '').lower()
        
        if "timeout" in line_lower:
            playbook_hint = "pipeline_timeout_fix"
        elif "build failed" in line_lower or "typescript" in line_lower:
            playbook_hint = "typescript_build_fix"
        else:
            playbook_hint = "verification_fix"
        
        context = {
            "error_type": "critical_pattern",
            "pattern": payload.get('pattern'),
            "log_line": payload.get('line'),
            "source": payload.get('source'),
            "triggered_by": "log_watcher"
        }
        
        await trigger_playbook_integration.trigger_healing(
            trigger_type="critical_log_pattern",
            context=context,
            playbook_hint=playbook_hint
        )


# Register default handlers
event_bus.subscribe('librarian.file.created', log_to_immutable_on_event)
event_bus.subscribe('ingestion.completed', log_to_immutable_on_event)
event_bus.subscribe('ingestion.failed', trigger_healing_on_failure)
event_bus.subscribe('log_pattern.critical', trigger_healing_on_failure)
