# -*- coding: utf-8 -*-
"""
Orchestrator Integration - Wire clarity framework into GraceUnifiedOrchestrator
"""

from typing import Dict, Any
from datetime import datetime

from .event_bus import get_event_bus, Event
from .component_manifest import get_manifest, TrustLevel
from .loop_output import GraceLoopOutput
from .mesh_loader import get_mesh_loader


class ClarityIntegration:
    """
    Clarity framework integration for the orchestrator.
    Provides helper methods for publishing events, tracking components, etc.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self.manifest = get_manifest()
        self.mesh_loader = get_mesh_loader()
        self.orchestrator_id = "grace_unified_orchestrator"
    
    async def publish_boot_event(self, stage: str, status: str, details: Dict[str, Any] = None):
        """Publish a boot stage event"""
        event_type = f"system.boot.{status}"
        
        await self.event_bus.publish(Event(
            event_type=event_type,
            source=self.orchestrator_id,
            payload={
                "stage": stage,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                **(details or {})
            }
        ))
    
    async def publish_component_event(self, component_id: str, event_status: str, details: Dict[str, Any] = None):
        """Publish a component lifecycle event"""
        event_type = f"component.{event_status}"
        
        await self.event_bus.publish(Event(
            event_type=event_type,
            source=component_id,
            payload={
                "component_id": component_id,
                "status": event_status,
                **(details or {})
            }
        ))
    
    async def publish_stage_completion(self, stage_name: str, success: bool, results: Dict[str, Any] = None):
        """Publish stage completion as a loop output"""
        loop_output = GraceLoopOutput(
            loop_type="boot_stage",
            component_id=self.orchestrator_id
        )
        
        loop_output.metadata["stage_name"] = stage_name
        
        if success:
            loop_output.mark_completed(results or {}, confidence=1.0)
        else:
            loop_output.mark_failed(results.get("error", "Unknown error") if results else "Stage failed")
        
        # Publish event with loop output
        await self.event_bus.publish(Event(
            event_type="loop.completed" if success else "loop.failed",
            source=self.orchestrator_id,
            payload={
                "loop_output": loop_output.to_dict(),
                "stage_name": stage_name
            }
        ))
        
        return loop_output
    
    def register_component(self, component_id: str, component_type: str, 
                          trust_level: TrustLevel = TrustLevel.MEDIUM,
                          role_tags: list = None):
        """Register a component in the manifest"""
        from .base_component import BaseComponent, ComponentStatus
        
        # Create a minimal component representation
        class ComponentStub(BaseComponent):
            def __init__(self, cid, ctype):
                super().__init__()
                self.component_id = cid
                self.component_type = ctype
                self.status = ComponentStatus.ACTIVE
            
            async def activate(self):
                return True
            
            async def deactivate(self):
                return True
            
            def get_status(self):
                return {"status": self.status.value}
        
        stub = ComponentStub(component_id, component_type)
        return self.manifest.register(stub, trust_level, role_tags or [])
    
    def get_clarity_status(self) -> Dict[str, Any]:
        """Get overall clarity framework status"""
        return {
            "event_bus": self.event_bus.get_stats(),
            "manifest": self.manifest.get_stats(),
            "mesh_config": {
                "total_events": len(self.mesh_loader.get_events()),
                "priority_events": len(self.mesh_loader.get_priority_events()),
                "audit_events": len(self.mesh_loader.get_audit_events())
            }
        }
    
    async def emit_health_event(self, component_id: str, health_status: str, details: Dict[str, Any] = None):
        """Emit a health monitoring event"""
        event_type = f"health.{health_status}"
        
        await self.event_bus.publish(Event(
            event_type=event_type,
            source=component_id,
            payload={
                "component_id": component_id,
                "health_status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                **(details or {})
            }
        ))


# Global integration instance
_clarity_integration: ClarityIntegration = None


def get_clarity_integration() -> ClarityIntegration:
    """Get the global clarity integration instance"""
    global _clarity_integration
    if _clarity_integration is None:
        _clarity_integration = ClarityIntegration()
    return _clarity_integration
