# -*- coding: utf-8 -*-
"""
Tests for Grace Clarity Framework
"""

import pytest
import asyncio
from typing import Dict, Any

from backend.clarity import (
    BaseComponent,
    ComponentStatus,
    EventBus,
    Event,
    get_event_bus,
    GraceLoopOutput,
    GraceComponentManifest,
    TrustLevel,
    get_manifest,
    get_mesh_loader
)


class TestBaseComponent:
    """Test BaseComponent class"""
    
    def test_component_creation(self):
        """Test basic component creation"""
        
        class TestComponent(BaseComponent):
            async def activate(self):
                return True
            
            async def deactivate(self):
                return True
            
            def get_status(self):
                return {"status": self.status.value}
        
        component = TestComponent()
        assert component.component_id is not None
        assert component.status == ComponentStatus.CREATED
        assert component.component_type == "base_component"
    
    @pytest.mark.asyncio
    async def test_component_lifecycle(self):
        """Test component activation/deactivation"""
        
        class TestComponent(BaseComponent):
            def __init__(self):
                super().__init__()
                self.activated = False
                self.deactivated = False
            
            async def activate(self):
                self.activated = True
                self.set_status(ComponentStatus.ACTIVE)
                return True
            
            async def deactivate(self):
                self.deactivated = True
                self.set_status(ComponentStatus.STOPPED)
                return True
            
            def get_status(self):
                return {"status": self.status.value}
        
        component = TestComponent()
        
        # Activate
        success = await component.activate()
        assert success is True
        assert component.activated is True
        assert component.status == ComponentStatus.ACTIVE
        
        # Deactivate
        success = await component.deactivate()
        assert success is True
        assert component.deactivated is True
        assert component.status == ComponentStatus.STOPPED


class TestEventBus:
    """Test EventBus functionality"""
    
    @pytest.mark.asyncio
    async def test_event_publishing(self):
        """Test event publishing and subscription"""
        bus = EventBus()
        received_events = []
        
        def handler(event: Event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        
        event = Event(
            event_type="test.event",
            source="test_source",
            payload={"data": "test"}
        )
        
        await bus.publish(event)
        
        assert len(received_events) == 1
        assert received_events[0].event_type == "test.event"
        assert received_events[0].payload["data"] == "test"
    
    @pytest.mark.asyncio
    async def test_async_handler(self):
        """Test async event handlers"""
        bus = EventBus()
        received_events = []
        
        async def async_handler(event: Event):
            await asyncio.sleep(0.01)
            received_events.append(event)
        
        bus.subscribe("async.event", async_handler)
        
        await bus.publish(Event(
            event_type="async.event",
            source="test",
            payload={}
        ))
        
        # Give async handler time to complete
        await asyncio.sleep(0.05)
        
        assert len(received_events) == 1
    
    def test_event_history(self):
        """Test event history tracking"""
        bus = EventBus()
        
        asyncio.run(bus.publish(Event(event_type="test1", source="src1")))
        asyncio.run(bus.publish(Event(event_type="test2", source="src2")))
        
        history = bus.get_history()
        assert len(history) == 2
        
        # Filter by type
        filtered = bus.get_history(event_type="test1")
        assert len(filtered) == 1
        assert filtered[0].event_type == "test1"


class TestLoopOutput:
    """Test GraceLoopOutput class"""
    
    def test_loop_output_creation(self):
        """Test loop output creation"""
        output = GraceLoopOutput(
            loop_type="reasoning",
            component_id="test_component"
        )
        
        assert output.loop_id is not None
        assert output.loop_type == "reasoning"
        assert output.status == "completed"
    
    def test_loop_completion(self):
        """Test marking loop as completed"""
        output = GraceLoopOutput(loop_type="test")
        
        results = {"answer": 42, "confidence": 0.95}
        output.mark_completed(results, confidence=0.95)
        
        assert output.status == "completed"
        assert output.results == results
        assert output.confidence == 0.95
        assert output.completed_at is not None
    
    def test_loop_failure(self):
        """Test marking loop as failed"""
        output = GraceLoopOutput(loop_type="test")
        
        output.mark_failed("Test error")
        
        assert output.status == "failed"
        assert output.metadata["error"] == "Test error"
        assert output.completed_at is not None
    
    def test_loop_serialization(self):
        """Test loop output serialization"""
        output = GraceLoopOutput(loop_type="test")
        output.mark_completed({"result": "success"})
        
        data = output.to_dict()
        
        assert "loop_id" in data
        assert "loop_type" in data
        assert data["status"] == "completed"
        assert data["results"]["result"] == "success"


class TestComponentManifest:
    """Test GraceComponentManifest class"""
    
    def test_component_registration(self):
        """Test registering a component"""
        manifest = GraceComponentManifest()
        
        class TestComponent(BaseComponent):
            async def activate(self):
                return True
            async def deactivate(self):
                return True
            def get_status(self):
                return {}
        
        component = TestComponent()
        component.status = ComponentStatus.ACTIVE
        
        reg = manifest.register(
            component,
            trust_level=TrustLevel.HIGH,
            role_tags=["test", "demo"]
        )
        
        assert reg.component_id == component.component_id
        assert reg.trust_level == TrustLevel.HIGH
        assert "test" in reg.role_tags
    
    def test_manifest_queries(self):
        """Test manifest query methods"""
        manifest = GraceComponentManifest()
        
        class TestComponent(BaseComponent):
            async def activate(self):
                return True
            async def deactivate(self):
                return True
            def get_status(self):
                return {}
        
        # Register multiple components
        comp1 = TestComponent()
        comp1.status = ComponentStatus.ACTIVE
        manifest.register(comp1, TrustLevel.HIGH, ["memory"])
        
        comp2 = TestComponent()
        comp2.status = ComponentStatus.ACTIVE
        manifest.register(comp2, TrustLevel.LOW, ["compute"])
        
        # Test queries
        active = manifest.get_active_components()
        assert len(active) == 2
        
        memory_comps = manifest.get_components_by_role("memory")
        assert len(memory_comps) == 1
        
        trusted = manifest.get_components_by_trust(TrustLevel.HIGH)
        assert len(trusted) == 1


class TestMeshLoader:
    """Test TriggerMeshLoader class"""
    
    def test_mesh_loading(self):
        """Test loading trigger mesh configuration"""
        loader = get_mesh_loader()
        
        events = loader.get_events()
        assert len(events) > 0
        
        # Check for expected events
        event_types = [e['event_type'] for e in events]
        assert 'system.boot.started' in event_types
        assert 'component.activated' in event_types
    
    def test_routing_rules(self):
        """Test routing rules"""
        loader = get_mesh_loader()
        
        priority = loader.get_priority_events()
        audit = loader.get_audit_events()
        alert = loader.get_alert_events()
        
        assert len(priority) > 0
        assert len(audit) > 0
        assert len(alert) > 0
    
    def test_event_info(self):
        """Test getting event information"""
        loader = get_mesh_loader()
        
        info = loader.get_event_info('system.boot.started')
        assert info is not None
        assert 'publishers' in info
        assert 'subscribers' in info


class TestClarityIntegration:
    """Test integration between all clarity components"""
    
    @pytest.mark.asyncio
    async def test_full_integration(self):
        """Test full clarity framework integration"""
        
        # Create component
        class TestComponent(BaseComponent):
            def __init__(self):
                super().__init__()
                self.component_type = "test_component"
                self.event_bus = get_event_bus()
            
            async def activate(self):
                self.set_status(ComponentStatus.ACTIVATING)
                
                # Subscribe to events
                self.event_bus.subscribe("test.task", self.handle_task)
                
                self.set_status(ComponentStatus.ACTIVE)
                
                # Publish activation event
                await self.event_bus.publish(Event(
                    event_type="component.activated",
                    source=self.component_id,
                    payload={"component_type": self.component_type}
                ))
                
                return True
            
            async def deactivate(self):
                self.set_status(ComponentStatus.STOPPED)
                return True
            
            def get_status(self):
                return {"status": self.status.value}
            
            async def handle_task(self, event: Event):
                """Handle task event"""
                loop_output = GraceLoopOutput(
                    loop_type="task_processing",
                    component_id=self.component_id
                )
                
                loop_output.mark_completed({"processed": True})
                
                await self.event_bus.publish(Event(
                    event_type="task.completed",
                    source=self.component_id,
                    payload={"loop_output": loop_output.to_dict()}
                ))
        
        # Create and activate component
        component = TestComponent()
        await component.activate()
        
        # Register with manifest
        manifest = get_manifest()
        manifest.register(component, TrustLevel.HIGH, ["test"])
        
        # Publish task
        await component.event_bus.publish(Event(
            event_type="test.task",
            source="test_runner",
            payload={"task_id": "test_123"}
        ))
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Verify status
        status = component.get_status()
        assert status["status"] == "active"
        
        # Check manifest
        reg = manifest.get_registration(component.component_id)
        assert reg is not None
        assert reg.trust_level == TrustLevel.HIGH
        
        # Deactivate
        await component.deactivate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
