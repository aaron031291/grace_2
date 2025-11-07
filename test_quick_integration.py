"""
Quick Integration Test - Validates Core System Wiring

Tests the essential connections without requiring all models.
"""

import asyncio
from datetime import datetime, timezone

print("\n" + "=" * 70)
print("GRACE QUICK INTEGRATION TEST")
print("=" * 70 + "\n")

async def test_integration():
    passed = 0
    failed = 0
    
    # Test 1: Database Connection
    print("[1/8] Testing Database Connection...")
    try:
        from backend.models import async_session
        from sqlalchemy import text
        
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        print("  [OK] Database accessible")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 2: Trigger Mesh
    print("[2/8] Testing Trigger Mesh...")
    try:
        from backend.trigger_mesh import trigger_mesh, TriggerEvent
        
        test_event = TriggerEvent(
            event_type="test.quick_integration",
            source="test",
            actor="test",
            resource="test",
            payload={"test": True},
            timestamp=datetime.now(timezone.utc)
        )
        
        await trigger_mesh.publish(test_event)
        print("  [OK] Trigger Mesh operational")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 3: Immutable Log
    print("[3/8] Testing Immutable Log...")
    try:
        from backend.immutable_log import ImmutableLog
        
        log = ImmutableLog()
        entry = await log.append(
            actor="test",
            action="quick_test",
            resource="test",
            subsystem="testing",
            payload={"test": True},
            result="testing"
        )
        
        print(f"  [OK] Immutable log working (entry created)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 4: Event Persistence
    print("[4/8] Testing Event Persistence...")
    try:
        from backend.event_persistence import event_persistence
        from backend.trigger_mesh import TriggerEvent
        
        event = TriggerEvent(
            event_type="agentic.action_planned",
            source="test",
            actor="test",
            resource="test_action",
            payload={"action_id": "test_123", "test": True},
            timestamp=datetime.now(timezone.utc)
        )
        
        persisted = await event_persistence.persist_action_event(
            event=event,
            mission_id="test_mission"
        )
        
        print(f"  [OK] Event persistence working (ID: {persisted.id})")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 5: Action Contracts
    print("[5/8] Testing Action Contracts...")
    try:
        from backend.action_contract import contract_verifier, ExpectedEffect
        
        expected_effect = ExpectedEffect(
            target_resource="test_resource",
            target_state={"test": "value"},
            success_criteria=[{"metric": "success", "threshold": 1.0}]
        )
        
        contract = await contract_verifier.create_contract(
            action_type="test_action",
            expected_effect=expected_effect,
            baseline_state={"test": "initial"},
            playbook_id="test",
            run_id=None,
            triggered_by="test",
            tier="tier_1"
        )
        
        print(f"  [OK] Action contracts working (ID: {contract.id})")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 6: InputSentinel
    print("[6/8] Testing InputSentinel...")
    try:
        from backend.input_sentinel import input_sentinel
        
        assert input_sentinel is not None
        assert hasattr(input_sentinel, '_handle_error_detected')
        print("  [OK] InputSentinel loaded")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 7: Observability
    print("[7/8] Testing Observability...")
    try:
        from backend.observability import track_action_execution, ObservabilityContext
        
        # Track an action
        track_action_execution(
            action_type="test",
            tier="tier_1",
            status="success",
            duration_seconds=0.5,
            correlation_id="test-123"
        )
        
        # Use context
        with ObservabilityContext(correlation_id="test-456") as ctx:
            ctx.log("test_event", test=True)
        
        print("  [OK] Observability hooks working")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Test 8: Verification Router
    print("[8/8] Testing Verification Router...")
    try:
        from backend.routers.verification_router import router
        
        assert router is not None
        route_paths = [route.path for route in router.routes]
        assert any("/contracts" in path for path in route_paths)
        print("  [OK] Verification router loaded")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\n  Total: {passed + failed}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All core integrations working!")
        print("\nNext steps:")
        print("  1. Start backend: cd backend && uvicorn main:app --reload")
        print("  2. Test endpoints: curl http://localhost:8000/api/verification/health")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")
        print("System is partially working but may need attention")
    
    print("=" * 70 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(test_integration())
    exit(0 if success else 1)
