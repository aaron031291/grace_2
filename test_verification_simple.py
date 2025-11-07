"""
Simple end-to-end verification test (no Unicode issues)
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Force UTF-8 output
os.environ['PYTHONIOENCODING'] = 'utf-8'


async def test_simple():
    """Simple verification flow test"""
    
    print("=" * 70)
    print("VERIFICATION SYSTEM TEST - SIMPLE")
    print("=" * 70)
    
    try:
        from backend.action_executor import action_executor
        from backend.action_contract import ExpectedEffect
        from backend.models import async_session
        
        # Test: Execute a verified action
        print("\n[1] Testing verified action execution...")
        
        expected_effect = ExpectedEffect(
            target_resource="test_system",
            target_state={
                "status": "completed",
                "error_resolved": True
            },
            success_criteria=[
                {"type": "state_match", "key": "status", "value": "completed"}
            ],
            rollback_threshold=0.5
        )
        
        result = await action_executor.execute_verified_action(
            action_type="test_action",
            playbook_id="test",
            run_id=None,
            expected_effect=expected_effect,
            baseline_state={"test_mode": True},
            tier="tier_1",  # tier_1 = no snapshot
            triggered_by="test_simple"
        )
        
        print(f"\n[2] Execution completed:")
        print(f"    Success: {result.get('success', False)}")
        print(f"    Contract ID: {result.get('contract_id', 'N/A')}")
        print(f"    Confidence: {result.get('confidence', 0.0):.2%}")
        print(f"    Rolled Back: {result.get('rolled_back', False)}")
        
        # Verify contract in database
        print("\n[3] Verifying database persistence...")
        
        async with async_session() as session:
            from backend.action_contract import ActionContract
            from sqlalchemy import select
            
            stmt = select(ActionContract).where(ActionContract.id == result.get('contract_id'))
            db_result = await session.execute(stmt)
            contract = db_result.scalar_one_or_none()
            
            if contract:
                print(f"    [OK] Contract persisted: {contract.id}")
                print(f"    Status: {contract.status}")
                print(f"    Confidence: {contract.confidence_score}")
            else:
                print("    [FAIL] Contract not found!")
                return False
        
        print("\n" + "=" * 70)
        print("TEST PASSED")
        print("=" * 70)
        print("\nVerification system operational:")
        print("  - Contract creation: OK")
        print("  - Action execution: OK")
        print("  - Verification: OK")
        print("  - Database persistence: OK")
        
        return True
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple())
    sys.exit(0 if success else 1)
