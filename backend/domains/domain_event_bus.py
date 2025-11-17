"""
Domain Event Bus - Pub/Sub Between Domains
Enables loose coupling with high cohesion
"""

import logging
from typing import Dict, Any, List, Callable, Set, Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """Event published by a domain"""
    event_type: str
    source_domain: str
    timestamp: str
    data: Dict[str, Any]
    signature: str = ""
    event_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type,
            'source_domain': self.source_domain,
            'timestamp': self.timestamp,
            'data': self.data,
            'signature': self.signature,
            'event_id': self.event_id
        }


class DomainEventBus:
    """
    Pub/Sub event bus for inter-domain communication
    Domains can publish events and subscribe to event patterns
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, Set[str]] = {}  # event_pattern -> {domain_ids}
        self.local_handlers: Dict[str, List[Callable]] = {}  # event_type -> [callbacks]
        self.event_history: List[DomainEvent] = []
        self.max_history = 1000
        
        # Pre-defined important event types
        self._register_standard_events()
    
    def _register_standard_events(self):
        """Register standard event types that all domains should know about"""
        standard_events = [
            'domain.registered',
            'domain.health_changed',
            'auth.login',
            'auth.logout',
            'ml.prediction',
            'ml.training_complete',
            'memory.stored',
            'memory.retrieved',
            'error.critical',
            'error.warning',
            'optimization.discovered',
            'insight.shared',
            'healing.started',
            'healing.completed',
            'governance.decision',
            'trust.verification',
        ]
        
        for event_type in standard_events:
            self.subscriptions[event_type] = set()
    
    async def publish(self, event: DomainEvent) -> Dict[str, Any]:
        """
        Publish event to all subscribers
        
        Args:
            event: DomainEvent to publish
        
        Returns:
            Publishing result with delivery stats
        """
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        logger.info(
            f"[EVENT-BUS] Publishing {event.event_type} "
            f"from {event.source_domain}"
        )
        
        # Get subscribers for this event type
        subscribers = self.subscriptions.get(event.event_type, set())
        
        # Also check wildcard subscriptions
        wildcard_pattern = event.event_type.split('.')[0] + '.*'
        subscribers.update(self.subscriptions.get(wildcard_pattern, set()))
        subscribers.update(self.subscriptions.get('*', set()))
        
        # Deliver to subscribers
        delivery_results = []
        
        for subscriber_id in subscribers:
            result = await self._deliver_event(subscriber_id, event)
            delivery_results.append({
                'subscriber': subscriber_id,
                'delivered': result
            })
        
        # Call local handlers
        handlers = self.local_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"[EVENT-BUS] Local handler error: {e}")
        
        return {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'subscribers_notified': len(subscribers),
            'delivery_results': delivery_results,
            'local_handlers_called': len(handlers)
        }
    
    async def _deliver_event(self, subscriber_id: str, event: DomainEvent) -> bool:
        """
        Deliver event to a specific subscriber domain
        """
        try:
            # Get subscriber domain info from registry
            from backend.domains.domain_registry import domain_registry
            
            subscriber = domain_registry.get_domain(subscriber_id)
            if not subscriber:
                logger.warning(f"[EVENT-BUS] Subscriber {subscriber_id} not found")
                return False
            
            # Send event to subscriber
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:{subscriber.port}/domain/event",
                    json=event.to_dict(),
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    logger.debug(
                        f"[EVENT-BUS] Event delivered to {subscriber_id}"
                    )
                    return True
                else:
                    logger.warning(
                        f"[EVENT-BUS] Event delivery failed to {subscriber_id}: "
                        f"status {response.status_code}"
                    )
                    return False
        
        except Exception as e:
            logger.error(f"[EVENT-BUS] Event delivery error to {subscriber_id}: {e}")
            return False
    
    def subscribe(self, domain_id: str, event_pattern: str) -> bool:
        """
        Subscribe domain to event pattern
        
        Args:
            domain_id: Domain subscribing
            event_pattern: Event pattern to subscribe to
                          Examples: 'auth.login', 'ml.*', '*'
        
        Returns:
            Success status
        """
        if event_pattern not in self.subscriptions:
            self.subscriptions[event_pattern] = set()
        
        self.subscriptions[event_pattern].add(domain_id)
        
        logger.info(
            f"[EVENT-BUS] Domain {domain_id} subscribed to '{event_pattern}'"
        )
        
        return True
    
    def unsubscribe(self, domain_id: str, event_pattern: str) -> bool:
        """Unsubscribe domain from event pattern"""
        if event_pattern in self.subscriptions:
            self.subscriptions[event_pattern].discard(domain_id)
            logger.info(
                f"[EVENT-BUS] Domain {domain_id} unsubscribed from '{event_pattern}'"
            )
            return True
        return False
    
    def add_local_handler(self, event_type: str, handler: Callable):
        """
        Add local callback handler for event type
        Useful for in-process event handling
        """
        if event_type not in self.local_handlers:
            self.local_handlers[event_type] = []
        
        self.local_handlers[event_type].append(handler)
        logger.info(f"[EVENT-BUS] Added local handler for '{event_type}'")
    
    def get_subscriptions(self) -> Dict[str, List[str]]:
        """Get all subscriptions"""
        return {
            pattern: list(subscribers)
            for pattern, subscribers in self.subscriptions.items()
        }
    
    def get_event_history(
        self,
        event_type: Optional[str] = None,
        source_domain: Optional[str] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """
        Get event history
        Optionally filter by event type or source domain
        """
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        if source_domain:
            history = [e for e in history if e.source_domain == source_domain]
        
        return history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        total_subscriptions = sum(len(subs) for subs in self.subscriptions.values())
        
        # Count events by type
        event_counts = {}
        for event in self.event_history:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        return {
            'total_event_patterns': len(self.subscriptions),
            'total_subscriptions': total_subscriptions,
            'events_in_history': len(self.event_history),
            'event_counts_by_type': event_counts,
            'local_handlers': len(self.local_handlers)
        }


# Singleton instance
domain_event_bus = DomainEventBus()
