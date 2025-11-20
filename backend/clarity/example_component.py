# -*- coding: utf-8 -*-
"""
Example Component - Demonstrates Clarity Framework usage
"""

import asyncio
from typing import Dict, Any

from .base_component import BaseComponent, ComponentStatus
from .event_bus import get_event_bus, Event
from .loop_output import GraceLoopOutput
from .component_manifest import get_manifest, TrustLevel
from backend.core.unified_event_publisher import publish_event_obj


class ExampleGraceComponent(BaseComponent):
    """
    Example component showing how to use the Clarity Framework.
    Use this as a template for new Grace components.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.component_type = "example_component"
        if config:
            self.config.update(config)
        
        # Component-specific state
        self.processing_count = 0
        self.event_bus = get_event_bus()
    
    async def activate(self) -> bool:
        """Activate the component"""
        try:
            self.set_status(ComponentStatus.ACTIVATING)
            
            # Subscribe to events
            self.event_bus.subscribe("task.request", self._handle_task)
            
            # Register with manifest
            manifest = get_manifest()
            manifest.register(
                self,
                trust_level=TrustLevel.MEDIUM,
                role_tags=["example", "demo"]
            )
            
            self.set_status(ComponentStatus.ACTIVE)
            self.activated_at = self.created_at
            
            # Publish activation event
            await publish_event_obj(Event(
                event_type="component.activated",
                source=self.component_id,
                payload={"component_type": self.component_type}
            ))
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate the component"""
        try:
            self.set_status(ComponentStatus.DEACTIVATING)
            
            # Unsubscribe from events
            self.event_bus.unsubscribe("task.request", self._handle_task)
            
            # Unregister from manifest
            manifest = get_manifest()
            manifest.unregister(self.component_id)
            
            self.set_status(ComponentStatus.STOPPED)
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "status": self.status.value,
            "processing_count": self.processing_count,
            "config": self.config,
            "metadata": self.metadata
        }
    
    async def _handle_task(self, event: Event):
        """Handle task request event"""
        # Create loop output for traceability
        loop_output = GraceLoopOutput(
            loop_type="task_processing",
            component_id=self.component_id
        )
        
        try:
            # Simulate processing
            task_data = event.payload
            result = await self._process_task(task_data)
            
            # Mark loop as completed
            loop_output.mark_completed(
                results=result,
                confidence=0.95
            )
            
            self.processing_count += 1
            
            # Publish result event
            await publish_event_obj(Event(
                event_type="task.completed",
                source=self.component_id,
                payload={
                    "loop_id": loop_output.loop_id,
                    "results": result
                }
            ))
            
        except Exception as e:
            loop_output.mark_failed(str(e))
            await publish_event_obj(Event(
                event_type="task.failed",
                source=self.component_id,
                payload={"error": str(e)}
            ))
    
    async def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task (example implementation)"""
        # Simulate async work
        await asyncio.sleep(0.1)
        
        return {
            "processed": True,
            "input": task_data,
            "output": f"Processed: {task_data.get('name', 'unknown')}"
        }


# Example usage
async def demo():
    """Demonstrate the clarity framework"""
    
    # Create and activate component
    component = ExampleGraceComponent(config={"debug": True})
    success = await component.activate()
    
    if success:
        print(f"Component activated: {component.component_id}")
        
        # Get event bus and publish a task
        bus = get_event_bus()
        await bus.publish(Event(
            event_type="task.request",
            source="demo",
            payload={"name": "test_task", "priority": "high"}
        ))
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Check status
        status = component.get_status()
        print(f"Status: {status}")
        
        # Check manifest
        manifest = get_manifest()
        stats = manifest.get_stats()
        print(f"Manifest stats: {stats}")
        
        # Deactivate
        await component.deactivate()
        print("Component deactivated")


if __name__ == "__main__":
    asyncio.run(demo())
