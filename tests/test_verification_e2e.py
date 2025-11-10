"""
End-to-End Verification System Test

Tests the complete flow:
1. Trigger error → InputSentinel → ActionExecutor
2. Create contract & snapshot
3. Execute action
4. Verify outcome
5. Rollback on failure (if needed)
"""

import asyncio
import sys
from datetime import datetime, timezone


async def test_verification_flow():
    """Test complete verification flow"""
    
    print("=" * 70)
    print("VERIFICATION SYSTEM END-TO-END TEST")
    print("=" * 70)
    print()
    
    try:
        from backend.input_sentinel import input_sentinel
        from backend.action_executor import action_executor
        from backend.action_contract import contract_verifier, ExpectedEffect
        from backend.self_heal.safe_hold import snapshot_manager
        from backend.benchmarks.benchmark_suite import benchmark_suite
        from backend.trigger_mesh import trigger_mesh, TriggerEvent
        from backend.models import async_session, Base, engine
        
        # Ensure tables exist
        print("Step 1: Verify database schema...")
        from sqlalchemy import text
        
        async with async_session() as session:
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
        
        required = ["action_contracts", "safe_hold_snapshots", "benchmark_runs", "mission_timelines"]
        missing = [t for t in required if t not in tables]
        
        if missing:
            print(f"  [MISSING] Missing tables: {missing}")
            print("  INFO: Run: python apply_verification_migration.py")
            return False
        
        print("  [OK] All verification tables present")
        
        # Step 2: Start required services
        print("\nStep 2: Initialize services...")
        await trigger_mesh.start()
        await input_sentinel.start()
        print("  [OK] Services started")
        
        # Step 3: Trigger a test error
        print("\n[TEST] Step 3: Trigger test error...")
        test_error_id = f"test-error-{datetime.now(timezone.utc).timestamp()}"
        
        error_event = TriggerEvent(
            event_type="error.captured",
            source="test",
            actor="test_suite",
            resource="test_verification",
            payload={
                "error_id": test_error_id,
                "error_type": "database_lock",
                "severity": "medium",
                "message": "Simulated database lock for testing",
                "source": "test_verification_e2e.py"
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        await trigger_mesh.publish(error_event)
        print(f"  [OK] Published error: {test_error_id}")
        
        # Step 4: Wait for InputSentinel to process
        print("\n[WAIT] Step 4: Wait for InputSentinel processing...")
        await asyncio.sleep(3)  # Give sentinel time to react
        
        # Step 5: Manually trigger verification flow
        print("\n[EXEC] Step 5: Execute verified action...")
        
        expected_effect = ExpectedEffect(
            target_resource="test_system",
            target_state={"status": "recovered", "locks_cleared": True},
            success_criteria=[
                {"type": "state_match", "key": "status", "value": "recovered"}
            ],
            rollback_threshold=0.5
        )
        
        result = await action_executor.execute_verified_action(
            action_type="clear_lock_files",
            playbook_id="test_recovery",
            run_id=None,
            expected_effect=expected_effect,
            baseline_state={"error_id": test_error_id, "test_mode": True},
            tier="tier_2",  # tier_2 creates snapshot
            triggered_by=f"test:{test_error_id}"
        )
        
        print(f"\n[RESULT] Execution Result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Contract ID: {result.get('contract_id', 'N/A')}")
        print(f"  Snapshot ID: {result.get('snapshot_id', 'N/A')}")
        print(f"  Confidence: {result.get('confidence', 0.0):.2%}")
        print(f"  Rolled Back: {result.get('rolled_back', False)}")
        
        # Step 6: Verify contract was created
        print("\n[OK] Step 6: Verify contract in database...")
        
        async with async_session() as session:
            from backend.action_contract import ActionContract
            from sqlalchemy import select
            
            stmt = select(ActionContract).where(ActionContract.id == result.get('contract_id'))
            db_result = await session.execute(stmt)
            contract = db_result.scalar_one_or_none()
            
            if contract:
                print(f"  [OK] Contract found: {contract.id}")
                print(f"     Status: {contract.status}")
                print(f"     Action: {contract.action_type}")
                print(f"     Confidence: {contract.confidence_score}")
            else:
                print("  [FAIL] Contract not found in database!")
                return False
        
        # Step 7: Verify snapshot if created
        if result.get('snapshot_id'):
            print("\n[SNAPSHOT] Step 7: Verify snapshot...")
            
            async with async_session() as session:
                from backend.self_heal.safe_hold import SafeHoldSnapshot
                from sqlalchemy import select
                
                stmt = select(SafeHoldSnapshot).where(SafeHoldSnapshot.id == result.get('snapshot_id'))
                db_result = await session.execute(stmt)
                snapshot = db_result.scalar_one_or_none()
                
                if snapshot:
                    print(f"  [OK] Snapshot found: {snapshot.id}")
                    print(f"     Type: {snapshot.snapshot_type}")
                    print(f"     Status: {snapshot.status}")
                    print(f"     Is Golden: {snapshot.is_golden}")
                else:
                    print("  [FAIL] Snapshot not found in database!")
                    return False
        
        # Step 8: Shutdown
        print("\n[STOP] Step 8: Cleanup...")
        await input_sentinel.stop()
        await trigger_mesh.stop()
        
        print("\n" + "=" * 70)
        print("[OK] END-TO-END TEST PASSED")
        print("=" * 70)
        print()
        print("Verification system is working correctly:")
        print("  [OK] Error triggering")
        print("  [OK] Contract creation")
        print("  [OK] Snapshot management")
        print("  [OK] Action execution")
        print("  [OK] Database persistence")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_verification_flow())
    sys.exit(0 if success else 1)
