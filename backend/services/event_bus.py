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
    Handler that triggers self-healing on failure events
    """
    event_type = event.get('type')
    payload = event.get('payload', {})
    
    if event_type == 'ingestion.failed':
        print(f"[Self-Healing] Ingestion failure detected: {payload.get('file_path')}")
        print(f"[Self-Healing] Queueing replay playbook...")
        # TODO: Trigger actual playbook
        # from backend.api.self_healing import trigger_playbook
        # await trigger_playbook('ingestion_replay')
    
    elif event_type == 'log_pattern.critical':
        print(f"[Self-Healing] Critical pattern detected: {payload.get('pattern')}")
        print(f"[Self-Healing] Triggering appropriate playbook...")


# Register default handlers
event_bus.subscribe('librarian.file.created', log_to_immutable_on_event)
event_bus.subscribe('ingestion.completed', log_to_immutable_on_event)
event_bus.subscribe('ingestion.failed', trigger_healing_on_failure)
event_bus.subscribe('log_pattern.critical', trigger_healing_on_failure)
