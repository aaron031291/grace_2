"""
Unified Event Publisher

Consolidates all event publishing through a single interface to:
- Reduce duplicate .publish() calls across 505+ locations
- Ensure consistent event routing
- Enable centralized event monitoring and governance
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UnifiedEventPublisher:
    """
    Central event publishing service that routes events through appropriate buses.
    """
    
    def __init__(self):
        self._trigger_mesh = None
        self._event_bus = None
        self._domain_event_bus = None
        self._message_bus = None
        
    async def initialize(self):
        """Initialize connections to various event buses"""
        try:
            from backend.triggers.trigger_mesh import get_trigger_mesh
            self._trigger_mesh = get_trigger_mesh()
        except ImportError:
            logger.warning("Trigger mesh not available")
            
        try:
            from backend.services.event_bus import event_bus
            self._event_bus = event_bus
        except ImportError:
            logger.warning("Event bus not available")
            
        try:
            from backend.services.domain_event_bus import domain_event_bus
            self._domain_event_bus = domain_event_bus
        except ImportError:
            logger.warning("Domain event bus not available")
            
        try:
            from backend.services.message_bus import message_bus
            self._message_bus = message_bus
        except ImportError:
            logger.warning("Message bus not available")
    
    async def publish_trigger(
        self,
        trigger_type: str,
        context: Dict[str, Any],
        source: str,
        priority: str = "normal"
    ):
        """
        Publish trigger event through trigger mesh.
        Replaces: await trigger_mesh.publish(TriggerEvent(...))
        """
        if not self._trigger_mesh:
            await self.initialize()
            
        if self._trigger_mesh:
            from backend.triggers.trigger_mesh import TriggerEvent
            
            event = TriggerEvent(
                trigger_type=trigger_type,
                context=context,
                source=source,
                priority=priority
            )
            
            await self._trigger_mesh.publish(event)
            logger.debug(f"Published trigger: {trigger_type} from {source}")
        else:
            logger.warning(f"Trigger mesh unavailable, event dropped: {trigger_type}")
    
    async def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: Optional[str] = None
    ):
        """
        Publish domain event through event bus.
        Replaces: await event_bus.publish(Event(...))
        """
        if not self._event_bus:
            await self.initialize()
            
        if self._event_bus:
            from backend.services.event_bus import Event, EventType
            
            event = Event(
                event_type=event_type,
                payload=payload,
                source=source or "unknown"
            )
            
            await self._event_bus.publish(event)
            logger.debug(f"Published event: {event_type} from {source}")
        else:
            logger.warning(f"Event bus unavailable, event dropped: {event_type}")
    
    async def publish_domain_event(
        self,
        event_type: str,
        domain: str,
        data: Dict[str, Any],
        source: Optional[str] = None
    ):
        """
        Publish domain-specific event through domain event bus.
        Replaces: await domain_event_bus.publish(DomainEvent(...))
        """
        if not self._domain_event_bus:
            await self.initialize()
            
        if self._domain_event_bus:
            from backend.services.domain_event_bus import DomainEvent
            
            event = DomainEvent(
                event_type=event_type,
                domain=domain,
                data=data,
                source=source or "unknown"
            )
            
            await self._domain_event_bus.publish(event)
            logger.debug(f"Published domain event: {domain}.{event_type}")
        else:
            logger.warning(f"Domain event bus unavailable, event dropped: {event_type}")
    
    async def publish_message(
        self,
        topic: str,
        message: Dict[str, Any]
    ):
        """
        Publish message through message bus.
        Replaces: await message_bus.publish(topic, message)
        """
        if not self._message_bus:
            await self.initialize()
            
        if self._message_bus:
            await self._message_bus.publish(topic, message)
            logger.debug(f"Published message to topic: {topic}")
        else:
            logger.warning(f"Message bus unavailable, message dropped: {topic}")


# Global singleton
_unified_publisher: Optional[UnifiedEventPublisher] = None


def get_unified_publisher() -> UnifiedEventPublisher:
    """Get or create the global unified event publisher"""
    global _unified_publisher
    
    if _unified_publisher is None:
        _unified_publisher = UnifiedEventPublisher()
    
    return _unified_publisher


# Convenience functions for common patterns
async def publish_trigger(trigger_type: str, context: Dict[str, Any], source: str, priority: str = "normal"):
    """Publish trigger event (convenience function)"""
    publisher = get_unified_publisher()
    await publisher.publish_trigger(trigger_type, context, source, priority)


async def publish_event(event_type: str, payload: Dict[str, Any], source: Optional[str] = None):
    """Publish domain event (convenience function)"""
    publisher = get_unified_publisher()
    await publisher.publish_event(event_type, payload, source)


async def publish_domain_event(event_type: str, domain: str, data: Dict[str, Any], source: Optional[str] = None):
    """Publish domain-specific event (convenience function)"""
    publisher = get_unified_publisher()
    await publisher.publish_domain_event(event_type, domain, data, source)


async def publish_message(topic: str, message: Dict[str, Any]):
    """Publish message (convenience function)"""
    publisher = get_unified_publisher()
    await publisher.publish_message(topic, message)
