import asyncio
from typing import Dict, Set, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

@dataclass
class TriggerEvent:
    """Event flowing through the mesh"""
    event_type: str
    source: str
    actor: str
    resource: str
    payload: dict
    timestamp: datetime
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subsystem: str = ""  # Subsystem identifier for metrics tracking

class TriggerMesh:
    """Event bus connecting all Grace subsystems"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.router_task: Optional[asyncio.Task] = None
        self._running = False
    
    def subscribe(self, event_pattern: str, handler: Callable):
        """Subscribe to event types (synchronous for ease of use)"""
        if event_pattern not in self.subscribers:
            self.subscribers[event_pattern] = set()
        self.subscribers[event_pattern].add(handler)
        print(f"[OK] Subscribed to {event_pattern}")
    
    async def publish(self, event: TriggerEvent):
        """Publish event to mesh"""
        await self.event_queue.put(event)
        
        # Log to immutable log
        from .immutable_log import immutable_log
        await immutable_log.append(
            actor=event.actor,
            action=event.event_type,
            resource=event.resource,
            subsystem=event.source,
            payload=event.payload,
            result="published"
        )
        
        # Log to unified logger (trigger mesh table + data cube)
        try:
            from .unified_logger import unified_logger
            await unified_logger.log_trigger_mesh_event(
                event_id=event.event_id,
                event_type=event.event_type,
                source=event.source,
                actor=event.actor,
                resource=event.resource,
                payload=event.payload,
                handlers_notified=0  # Will be updated when routed
            )
        except Exception as e:
            # Don't fail publish if logging fails
            pass
    
    async def start(self):
        """Start event router"""
        if not self._running:
            self._running = True
            self.router_task = asyncio.create_task(self._route_events())
            print("[OK] Trigger Mesh started")
    
    async def stop(self):
        """Stop event router"""
        self._running = False
        if self.router_task:
            self.router_task.cancel()
        print("[OK] Trigger Mesh stopped")
    
    async def _route_events(self):
        """Background router distributing events"""
        try:
            while self._running:
                event = await self.event_queue.get()
                
                for pattern, handlers in self.subscribers.items():
                    if self._matches_pattern(event.event_type, pattern):
                        for handler in handlers:
                            try:
                                await handler(event)
                            except Exception as e:
                                print(f"[FAIL] Event handler error: {e}")
                
                self.event_queue.task_done()
        except asyncio.CancelledError:
            pass
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Simple wildcard matching"""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type.startswith(prefix)
        return event_type == pattern

trigger_mesh = TriggerMesh()

async def setup_subscriptions():
    """Wire up all subsystem subscriptions"""
    
    async def on_memory_event(event: TriggerEvent):
        if "delete" in event.event_type or "sensitive" in event.payload.get("domain", ""):
            from .hunter import hunter
            await hunter.inspect(event.actor, event.event_type, event.resource, event.payload)
    
    async def on_sandbox_event(event: TriggerEvent):
        if event.payload.get("exit_code", 0) != 0:
            from .remedy import remedy_inference
            await remedy_inference.log_issue(
                user=event.actor,
                source="sandbox",
                summary=f"Sandbox failure: {event.resource}",
                details=event.payload.get("stderr", ""),
                context=event.payload
            )
    
    async def on_governance_event(event: TriggerEvent):
        if event.payload.get("decision") in ["block", "review"]:
            from .learning import learning_engine
            print(f"📋 Governance blocked action - could create task here")
    
    await trigger_mesh.subscribe("memory.*", on_memory_event)
    await trigger_mesh.subscribe("sandbox.*", on_sandbox_event)
    await trigger_mesh.subscribe("governance.*", on_governance_event)
    
    print("[OK] Trigger Mesh subscriptions configured")
