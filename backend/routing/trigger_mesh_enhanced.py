"""
Trigger Mesh - Complete Implementation
Constitutional wiring harness on top of the event bus with YAML-based routing,
constitutional validation, and trust score enforcement.
"""

import asyncio
import yaml
from typing import Dict, Set, Callable, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import uuid


@dataclass
class TriggerEvent:
    """Event flowing through the mesh"""
    event_type: str
    source: str
    actor: str
    resource: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subsystem: str = ""
    trust_score: float = 1.0
    requires_validation: bool = False


@dataclass
class RouteMetadata:
    """Metadata for a routing rule"""
    requires_constitutional_validation: bool = False
    min_trust_score: float = 0.0
    priority_level: int = 0  # Higher = more priority
    audit_required: bool = False
    alert_on_failure: bool = False


@dataclass
class RoutingRule:
    """Complete routing rule with metadata"""
    source: str
    event_type: str
    targets: List[str]
    metadata: RouteMetadata = field(default_factory=RouteMetadata)


class TriggerMesh:
    """
    Constitutional event routing mesh with:
    - YAML-based routing configuration
    - Constitutional validation hooks
    - Trust score enforcement
    - Priority event handling
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        # Phase 1: Routing map
        self.routing_map: Dict[tuple, List[RoutingRule]] = {}
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.component_handlers: Dict[str, Callable] = {}
        
        # Event processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.Queue = asyncio.Queue()
        self.router_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Configuration
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "trigger_mesh.yaml"
        self.config: Dict[str, Any] = {}
        
        # Phase 3: Governance & trust
        self.governance_validator: Optional[Callable] = None
        self.trust_scorer: Optional[Callable] = None
        
        # Statistics
        self.events_routed = 0
        self.events_blocked = 0
        self.events_validated = 0
    
    def load_config(self) -> Dict[str, Any]:
        """
        Phase 1: Load trigger_mesh.yaml and normalize into routing map
        
        Returns:
            Loaded configuration dictionary
        """
        
        if not self.config_path.exists():
            print(f"⚠ Trigger mesh config not found at {self.config_path}, using empty config")
            return {}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        
        # Normalize events into routing map
        events = self.config.get('events', [])
        routing_rules = self.config.get('routing_rules', {})
        
        for event_def in events:
            event_type = event_def.get('event_type')
            publishers = event_def.get('publishers', [])
            subscribers = event_def.get('subscribers', [])
            
            # Get metadata for this event type
            metadata = self._extract_metadata(event_type, event_def, routing_rules)
            
            # Create routing rules for each publisher
            for publisher in publishers:
                if publisher == 'any_component':
                    # Wildcard publisher
                    key = ('*', event_type)
                else:
                    key = (publisher, event_type)
                
                rule = RoutingRule(
                    source=publisher,
                    event_type=event_type,
                    targets=subscribers,
                    metadata=metadata
                )
                
                if key not in self.routing_map:
                    self.routing_map[key] = []
                
                self.routing_map[key].append(rule)
        
        print(f"✓ Loaded {len(events)} event definitions into routing map")
        print(f"✓ Created {len(self.routing_map)} routing entries")
        
        return self.config
    
    def _extract_metadata(
        self,
        event_type: str,
        event_def: Dict[str, Any],
        routing_rules: Dict[str, Any]
    ) -> RouteMetadata:
        """Extract routing metadata from event definition and routing rules"""
        
        metadata = RouteMetadata()
        
        # Check if event requires validation
        metadata.requires_constitutional_validation = event_def.get(
            'requires_constitutional_validation',
            False
        )
        
        # Check if event requires minimum trust score
        metadata.min_trust_score = event_def.get('min_trust_score', 0.0)
        
        # Check if event is high priority
        priority_events = routing_rules.get('priority_events', [])
        if event_type in priority_events:
            metadata.priority_level = 10
        
        # Check if event should be audited
        audit_events = routing_rules.get('audit_events', [])
        metadata.audit_required = event_type in audit_events
        
        # Check if event should trigger alerts
        alert_events = routing_rules.get('alert_events', [])
        metadata.alert_on_failure = event_type in alert_events
        
        return metadata
    
    def register_component_handler(self, component_id: str, handler: Callable):
        """
        Register a handler function for a component
        
        Args:
            component_id: Component identifier
            handler: Async function to handle events
        """
        self.component_handlers[component_id] = handler
        print(f"✓ Registered handler for component: {component_id}")
    
    def subscribe(self, event_pattern: str, handler: Callable):
        """
        Subscribe to event types with pattern matching
        
        Args:
            event_pattern: Event type pattern (supports wildcards)
            handler: Async function to handle events
        """
        if event_pattern not in self.subscribers:
            self.subscribers[event_pattern] = set()
        
        self.subscribers[event_pattern].add(handler)
        print(f"✓ Subscribed to {event_pattern}")
        
        # Return no-op awaitable for compatibility
        class _NoOpAwaitable:
            def __await__(self):
                if False:
                    yield None
                return None
        
        return _NoOpAwaitable()
    
    async def emit(self, event: TriggerEvent):
        """
        Phase 2: Emit event through the mesh with routing
        
        Args:
            event: Event to emit
        """
        
        # Phase 3: Constitutional validation
        if event.requires_validation or await self._requires_validation(event):
            if not await self._validate_constitutional(event):
                print(f"⚠ Event blocked by constitutional validation: {event.event_type}")
                self.events_blocked += 1
                await self._log_blocked_event(event, "constitutional_violation")
                return
            
            self.events_validated += 1
        
        # Phase 3: Trust score validation
        if not await self._validate_trust_score(event):
            print(f"⚠ Event blocked by trust score check: {event.event_type} (score: {event.trust_score})")
            self.events_blocked += 1
            await self._log_blocked_event(event, "insufficient_trust")
            return
        
        # Route event based on priority
        routing_rules = self._lookup_routes(event)
        
        if routing_rules and any(r.metadata.priority_level > 0 for r in routing_rules):
            await self.priority_queue.put((event, routing_rules))
        else:
            await self.event_queue.put((event, routing_rules))
        
        # Log to immutable log
        await self._log_event(event, routing_rules)
        
        self.events_routed += 1
    
    async def publish(self, event: TriggerEvent):
        """Alias for emit() for backward compatibility"""
        await self.emit(event)
    
    def _lookup_routes(self, event: TriggerEvent) -> List[RoutingRule]:
        """
        Look up routing rules for an event
        
        Args:
            event: Event to route
            
        Returns:
            List of applicable routing rules
        """
        
        routes = []
        
        # Exact match: (source, event_type)
        key = (event.source, event.event_type)
        if key in self.routing_map:
            routes.extend(self.routing_map[key])
        
        # Wildcard source match: (*, event_type)
        wildcard_key = ('*', event.event_type)
        if wildcard_key in self.routing_map:
            routes.extend(self.routing_map[wildcard_key])
        
        # Pattern-based subscribers (backward compatibility)
        for pattern, handlers in self.subscribers.items():
            if self._matches_pattern(event.event_type, pattern):
                # Create dynamic route for pattern subscribers
                route = RoutingRule(
                    source='*',
                    event_type=event.event_type,
                    targets=[],
                    metadata=RouteMetadata()
                )
                routes.append(route)
        
        return routes
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Simple wildcard pattern matching"""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix)
        return event_type == pattern
    
    async def _requires_validation(self, event: TriggerEvent) -> bool:
        """Check if event requires constitutional validation"""
        
        routes = self._lookup_routes(event)
        
        for route in routes:
            if route.metadata.requires_constitutional_validation:
                return True
        
        return False
    
    async def _validate_constitutional(self, event: TriggerEvent) -> bool:
        """
        Phase 3: Validate event against constitutional principles
        
        Args:
            event: Event to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        
        if self.governance_validator is None:
            # No validator configured, allow event
            return True
        
        try:
            result = await self.governance_validator(event)
            return result
        except Exception as e:
            print(f"✗ Constitutional validation error: {e}")
            return False
    
    async def _validate_trust_score(self, event: TriggerEvent) -> bool:
        """
        Phase 3: Validate event source has sufficient trust score
        
        Args:
            event: Event to validate
            
        Returns:
            True if trust score is sufficient, False otherwise
        """
        
        routes = self._lookup_routes(event)
        
        for route in routes:
            if route.metadata.min_trust_score > 0:
                # Get trust score for source component
                trust_score = await self._get_trust_score(event.source)
                
                if trust_score < route.metadata.min_trust_score:
                    print(f"⚠ Event rejected: trust score {trust_score} < required {route.metadata.min_trust_score}")
                    return False
        
        return True
    
    async def _get_trust_score(self, component_id: str) -> float:
        """Get trust score for a component"""
        
        if self.trust_scorer is None:
            # No trust scorer configured, return default
            return 1.0
        
        try:
            score = await self.trust_scorer(component_id)
            return score
        except Exception as e:
            print(f"✗ Trust score lookup error: {e}")
            return 0.0
    
    async def start(self):
        """Start event router"""
        
        if not self._running:
            self._running = True
            self.router_task = asyncio.create_task(self._route_events())
            print("✓ Trigger Mesh router started")
    
    async def stop(self):
        """Stop event router"""
        
        self._running = False
        
        if self.router_task:
            self.router_task.cancel()
            try:
                await self.router_task
            except asyncio.CancelledError:
                pass
        
        print("✓ Trigger Mesh router stopped")
    
    async def _route_events(self):
        """
        Background router distributing events to targets
        Priority events are processed first
        """
        
        try:
            while self._running:
                # Process priority events first
                if not self.priority_queue.empty():
                    event, routes = await self.priority_queue.get()
                    await self._dispatch_event(event, routes)
                    self.priority_queue.task_done()
                # Then process normal events
                elif not self.event_queue.empty():
                    event, routes = await self.event_queue.get()
                    await self._dispatch_event(event, routes)
                    self.event_queue.task_done()
                else:
                    # Sleep briefly if no events
                    await asyncio.sleep(0.01)
        
        except asyncio.CancelledError:
            pass
    
    async def _dispatch_event(self, event: TriggerEvent, routes: List[RoutingRule]):
        """
        Dispatch event to all targets
        
        Args:
            event: Event to dispatch
            routes: Routing rules to apply
        """
        
        dispatched_to = set()
        
        # Dispatch to component handlers via routing rules
        for route in routes:
            for target in route.targets:
                if target in dispatched_to:
                    continue
                
                dispatched_to.add(target)
                
                if target in self.component_handlers:
                    try:
                        await self.component_handlers[target](event)
                    except Exception as e:
                        print(f"✗ Target handler error ({target}): {e}")
                        
                        if route.metadata.alert_on_failure:
                            await self._emit_alert(event, target, str(e))
        
        # Dispatch to pattern subscribers
        for pattern, handlers in self.subscribers.items():
            if self._matches_pattern(event.event_type, pattern):
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        print(f"✗ Subscriber handler error: {e}")
    
    async def _log_event(self, event: TriggerEvent, routes: List[RoutingRule]):
        """Log event to immutable log if audit required"""
        
        should_audit = any(r.metadata.audit_required for r in routes)
        
        if not should_audit:
            return
        
        try:
            from backend.logging_system.immutable_log import immutable_log
            
            await immutable_log.append(
                actor=event.actor,
                action=event.event_type,
                resource=event.resource,
                subsystem=event.source,
                payload={
                    **event.payload,
                    'event_id': event.event_id,
                    'targets': [r.targets for r in routes]
                },
                result="routed"
            )
        except Exception as e:
            print(f"✗ Event logging error: {e}")
    
    async def _log_blocked_event(self, event: TriggerEvent, reason: str):
        """Log blocked event to immutable log"""
        
        try:
            from backend.logging_system.immutable_log import immutable_log
            
            await immutable_log.append(
                actor=event.actor,
                action=f"BLOCKED:{event.event_type}",
                resource=event.resource,
                subsystem=event.source,
                payload={
                    **event.payload,
                    'event_id': event.event_id,
                    'block_reason': reason
                },
                result="blocked"
            )
        except Exception as e:
            print(f"✗ Blocked event logging error: {e}")
    
    async def _emit_alert(self, event: TriggerEvent, failed_target: str, error: str):
        """Emit alert for failed event dispatch"""
        
        alert_event = TriggerEvent(
            event_type="system.alert.dispatch_failure",
            source="trigger_mesh",
            actor="system",
            resource=f"{event.event_type}→{failed_target}",
            payload={
                'original_event': event.event_type,
                'failed_target': failed_target,
                'error': error,
                'event_id': event.event_id
            }
        )
        
        # Emit alert (without validation to avoid loops)
        await self.event_queue.put((alert_event, []))
    
    def set_governance_validator(self, validator: Callable):
        """
        Set the constitutional validator function
        
        Args:
            validator: Async function(event: TriggerEvent) -> bool
        """
        self.governance_validator = validator
        print("✓ Constitutional validator registered")
    
    def set_trust_scorer(self, scorer: Callable):
        """
        Set the trust score provider function
        
        Args:
            scorer: Async function(component_id: str) -> float
        """
        self.trust_scorer = scorer
        print("✓ Trust scorer registered")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        return {
            'events_routed': self.events_routed,
            'events_blocked': self.events_blocked,
            'events_validated': self.events_validated,
            'routing_rules': len(self.routing_map),
            'component_handlers': len(self.component_handlers),
            'subscribers': sum(len(handlers) for handlers in self.subscribers.values())
        }


# Global trigger mesh instance
trigger_mesh = TriggerMesh()
