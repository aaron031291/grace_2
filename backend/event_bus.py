"""
Event Bus - Unified communication layer for all Grace agents
All agents publish/subscribe to typed events through this single bus
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum

class EventType(Enum):
    AGENT_ACTION = "agent_action"
    GOVERNANCE_CHECK = "governance_check"
    MEMORY_UPDATE = "memory_update"
    WORLD_MODEL_UPDATE = "world_model_update"
    SELF_HEALING_TRIGGER = "self_healing_trigger"
    LEARNING_OUTCOME = "learning_outcome"
    MISSION_STATUS = "mission_status"
    VERIFICATION_RESULT = "verification_result"

class Event:
    def __init__(
        self,
        event_type: EventType,
        source: str,
        data: Dict[str, Any],
        trace_id: Optional[str] = None
    ):
        self.event_type = event_type
        self.source = source
        self.data = data
        self.trace_id = trace_id or f"trace_{datetime.now().timestamp()}"
        self.timestamp = datetime.now().isoformat()
        self.event_id = f"evt_{datetime.now().timestamp()}_{source}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp
        }

class EventBus:
    """
    Unified Event Bus for Grace's agentic organism
    All agents communicate through this single bus
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_log: List[Event] = []
        self.max_log_size = 10000
        
    async def publish(self, event: Event) -> None:
        """Publish event to all subscribers"""
        self.event_log.append(event)
        
        if len(self.event_log) > self.max_log_size:
            self.event_log = self.event_log[-self.max_log_size:]
        
        print(f"[EventBus] Published: {event.event_type.value} from {event.source}")
        
        if event.event_type in self.subscribers:
            tasks = []
            for callback in self.subscribers[event.event_type]:
                tasks.append(self._safe_callback(callback, event))
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_callback(self, callback: Callable, event: Event) -> None:
        """Execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            print(f"[EventBus] Callback error: {e}")
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        print(f"[EventBus] Subscribed to {event_type.value}")
    
    def get_recent_events(self, limit: int = 100, event_type: Optional[EventType] = None) -> List[Dict[str, Any]]:
        """Get recent events from log"""
        events = self.event_log[-limit:]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [e.to_dict() for e in events]
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all events for a specific trace"""
        return [e.to_dict() for e in self.event_log if e.trace_id == trace_id]

event_bus = EventBus()
