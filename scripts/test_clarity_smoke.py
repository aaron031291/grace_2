#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clarity Framework Smoke Test
Quick validation that clarity framework is working
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.clarity import (
    BaseComponent,
    ComponentStatus,
    get_event_bus,
    Event,
    get_manifest,
    TrustLevel,
    GraceLoopOutput,
    get_mesh_loader
)


class TestComponent(BaseComponent):
    """Simple test component"""
    
    def __init__(self):
        super().__init__()
        self.component_type = "test_component"
    
    async def activate(self):
        self.set_status(ComponentStatus.ACTIVE)
        return True
    
    async def deactivate(self):
        self.set_status(ComponentStatus.STOPPED)
        return True
    
    def get_status(self):
        return {"status": self.status.value}


async def main():
    """Run smoke tests"""
    print("=" * 60)
    print("CLARITY FRAMEWORK SMOKE TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test 1: BaseComponent
    print("\n[1/6] Testing BaseComponent...")
    try:
        comp = TestComponent()
        assert await comp.activate()
        assert comp.status == ComponentStatus.ACTIVE
        assert await comp.deactivate()
        print("    PASS - BaseComponent working")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Test 2: EventBus
    print("[2/6] Testing EventBus...")
    try:
        bus = get_event_bus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.subscribe("test.event", handler)
        await bus.publish(Event(event_type="test.event", source="test"))
        
        assert len(received) == 1
        print("    PASS - EventBus working")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Test 3: GraceLoopOutput
    print("[3/6] Testing GraceLoopOutput...")
    try:
        output = GraceLoopOutput(loop_type="test")
        output.mark_completed({"result": "success"})
        assert output.status == "completed"
        data = output.to_dict()
        assert "loop_id" in data
        print("    PASS - GraceLoopOutput working")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Test 4: ComponentManifest
    print("[4/6] Testing ComponentManifest...")
    try:
        manifest = get_manifest()
        comp = TestComponent()
        comp.status = ComponentStatus.ACTIVE
        
        reg = manifest.register(comp, TrustLevel.HIGH, ["test"])
        assert reg.component_id == comp.component_id
        
        active = manifest.get_active_components()
        assert len([c for c in active if c.component_id == comp.component_id]) > 0
        print("    PASS - ComponentManifest working")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Test 5: TriggerMeshLoader
    print("[5/6] Testing TriggerMeshLoader...")
    try:
        loader = get_mesh_loader()
        events = loader.get_events()
        assert len(events) > 0
        
        info = loader.get_event_info("system.boot.started")
        assert info is not None
        print(f"    PASS - Mesh loaded {len(events)} events")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Test 6: Full Integration
    print("[6/6] Testing Full Integration...")
    try:
        # Create component
        comp = TestComponent()
        
        # Register with manifest
        manifest = get_manifest()
        manifest.register(comp, TrustLevel.MEDIUM, ["integration_test"])
        
        # Activate
        await comp.activate()
        
        # Publish event
        bus = get_event_bus()
        await bus.publish(Event(
            event_type="component.activated",
            source=comp.component_id,
            payload={"test": True}
        ))
        
        # Create loop output
        loop = GraceLoopOutput(loop_type="integration", component_id=comp.component_id)
        loop.mark_completed({"test": "passed"})
        
        # Deactivate
        await comp.deactivate()
        
        print("    PASS - Full integration working")
        passed += 1
    except Exception as e:
        print(f"    FAIL - {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\nClarity Framework is OPERATIONAL")
        return 0
    else:
        print(f"\n{failed} test(s) failed - check clarity framework")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
