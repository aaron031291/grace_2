"""
Real-Time Activity Monitor
Shows what Grace is doing in real-time
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from collections import deque

logger = logging.getLogger(__name__)


class ActivityEvent:
    """Single activity event"""
    
    def __init__(self, activity_type: str, description: str, details: Dict[str, Any] = None):
        self.timestamp = datetime.utcnow()
        self.activity_type = activity_type
        self.description = description
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'type': self.activity_type,
            'description': self.description,
            'details': self.details
        }


class ActivityMonitor:
    """
    Real-time activity monitor
    Broadcasts what Grace is doing to all listeners
    """
    
    def __init__(self, max_events: int = 1000):
        self.events = deque(maxlen=max_events)
        self.listeners = []
        self.current_activity = None
    
    async def start(self):
        """Start activity monitor"""
        logger.info("[ACTIVITY-MONITOR] Started - broadcasting Grace's activities")
    
    async def log_activity(
        self,
        activity_type: str,
        description: str,
        details: Dict[str, Any] = None
    ):
        """
        Log an activity (broadcast to all listeners)
        
        Args:
            activity_type: Type (command, browse, think, learn, etc.)
            description: What Grace is doing
            details: Additional details
        """
        
        event = ActivityEvent(activity_type, description, details)
        self.events.append(event)
        self.current_activity = event
        
        # Print to console
        timestamp = event.timestamp.strftime('%H:%M:%S')
        print(f"[{timestamp}] [{activity_type.upper()}] {description}")
        
        if details:
            for key, value in details.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        
        # Broadcast to WebSocket listeners
        await self._broadcast(event)
    
    async def _broadcast(self, event: ActivityEvent):
        """Broadcast event to all WebSocket listeners"""
        
        # Broadcast via activity streamer if available
        try:
            from .routes.activity_stream import streamer
            await streamer.broadcast(event.to_dict())
        except:
            pass
        
        # Send to direct listeners
        for listener in self.listeners[:]:  # Copy list to avoid modification issues
            try:
                await listener.send(event.to_dict())
            except:
                self.listeners.remove(listener)
    
    def add_listener(self, listener):
        """Add WebSocket listener"""
        self.listeners.append(listener)
    
    def remove_listener(self, listener):
        """Remove WebSocket listener"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def get_recent_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent events"""
        recent = list(self.events)[-count:]
        return [e.to_dict() for e in recent]
    
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Get what Grace is currently doing"""
        if self.current_activity:
            return self.current_activity.to_dict()
        return None


# Global instance
activity_monitor = ActivityMonitor()
