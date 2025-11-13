"""
Event Bus
Central event emission and subscription system for kernel actions
"""

from typing import Dict, List, Callable, Any
from datetime import datetime
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for kernel and agent communication.
    
    Supports:
    - Event emission with metadata
    - Event subscriptions with callbacks
    - Event logging to database
    - Real-time websocket broadcasting (optional)
    """
    
    def __init__(self, registry=None):
        self.registry = registry
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: List[Dict] = []
        self._max_history = 1000
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to all subscribers and log it.
        
        Args:
            event_type: Event type (e.g., 'kernel.started', 'agent.completed')
            data: Event payload data
        """
        event = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'event_id': f"{event_type}_{datetime.utcnow().timestamp()}"
        }
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Log event
        logger.info(f"Event: {event_type} - {data.get('kernel_id', 'unknown')}")
        
        # Store in database
        await self._store_event(event)
        
        # Notify subscribers
        await self._notify_subscribers(event_type, event)
    
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to (or '*' for all events)
            callback: Async function to call when event occurs
        """
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Remove a subscription"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    async def _notify_subscribers(self, event_type: str, event: Dict):
        """Notify all subscribers of an event"""
        # Notify specific event subscribers
        for callback in self._subscribers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Subscriber callback failed: {e}")
        
        # Notify wildcard subscribers
        for callback in self._subscribers.get('*', []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Wildcard subscriber failed: {e}")
    
    async def _store_event(self, event: Dict):
        """Store event in clarity_events table"""
        if not self.registry:
            return
        
        try:
            self.registry.insert_row('clarity_events', {
                'event_type': event['event_type'],
                'source': event['data'].get('kernel_id', 'unknown'),
                'data': event['data'],
                'timestamp': event['timestamp']
            })
        except Exception as e:
            logger.warning(f"Could not store event: {e}")
    
    def get_recent_events(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get recent events from history"""
        if event_type:
            events = [e for e in self._event_history if e['event_type'] == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()


# Global event bus instance
_global_event_bus: EventBus = None


def get_event_bus(registry=None) -> EventBus:
    """Get or create the global event bus"""
    global _global_event_bus
    
    if _global_event_bus is None:
        _global_event_bus = EventBus(registry=registry)
    
    return _global_event_bus


class EventLogger:
    """
    Logs events to various destinations.
    Can be attached to event bus as a subscriber.
    """
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
    
    async def log_event(self, event: Dict):
        """Log an event"""
        event_type = event['event_type']
        timestamp = event['timestamp']
        data = event['data']
        
        log_msg = f"[{timestamp}] {event_type}: {data}"
        
        # Log to file if configured
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_msg + '\n')
            except Exception as e:
                logger.error(f"Failed to write to log file: {e}")
        
        # Log to console
        logger.info(log_msg)
