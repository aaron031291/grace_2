"""
Action Executor - Verified Execution Wrapper

Wraps agentic actions with comprehensive verification:
1. Creates action contract (expected vs actual)
2. Takes safe-hold snapshot before execution
3. Executes action through self-heal adapter
4. Runs benchmark to detect drift
5. Verifies outcome matches contract
6. Rolls back if verification fails

This is the "trust but verify" layer for all high-impact actions.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import asyncio

from .action_contract import contract_verifier, ExpectedEffect
from .self_heal.safe_hold import snapshot_manager
from .benchmarks import benchmark_suite
from .progression_tracker import progression_tracker
from .immutable_log import immutable_log


class ActionExecutor:
    """
    Executes agentic actions with full verification and rollback capability.
    Ensures actions perform their intended effects or safely rolls back.
    """
    
    async def execute_verified_action(
        self,
        action_type: str,
        playbook_id: Optional[str],
        run_id: Optional[int],
        expected_effect: ExpectedEffect,
        baseline_state: Dict[str, Any],
        tier: str = "tier_1",
        triggered_by: Optional[str] = None,
        mission_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an action with full contract verification.
        
        Steps:
        1. Create action contract
        2. Take safe-hold snapshot (for tier 2+)
        3. Execute action
        4. Run post-execution benchmark
        5. Verify contract
        6. Rollback if failed
        
        Returns:
            Result dict with success, contract, snapshot, and verification info
        """
        
        print(f"  🔐 Executing verified action: {action_type} (tier: {tier})")
        
        # Step 1: Create action contract
        contract = await contract_verifier.create_contract(
            action_type=action_type,
            expected_effect=expected_effect,
            baseline_state=baseline_state,
            playbook_id=playbook_id,
            run_id=run_id,
            triggered_by=triggered_by,
            tier=tier
        )
        
        print(f"    📝 Contract created: {contract.id}")
        
        # Step 2: Take snapshot for tier 2+ actions
        snapshot = None
        if tier in ["tier_2", "tier_3"]:
            snapshot = await snapshot_manager.create_snapshot(
                snapshot_type="pre_action",
                triggered_by=triggered_by,
                action_contract_id=contract.id,
                playbook_run_id=run_id,
                notes=f"Pre-action snapshot for {action_type}"
            )
            print(f"    📸 Safe-hold snapshot: {snapshot.id}")
        
        # Step 3: Execute action through self-heal adapter
        try:
            from .self_heal.adapter import self_healing_adapter
            
            # Mark contract as executing
            from .models import async_session
            async with async_session() as session:
                db_contract = await session.get(contract.__class__, contract.id)
                if db_contract:
                    db_contract.status = "executing"
                    db_contract.executed_at = datetime.now(timezone.utc)
                    if snapshot:
                        db_contract.safe_hold_snapshot_id = snapshot.id
                    await session.commit()
            
            # Execute the action
            execution_result = await self_healing_adapter.execute_action(
                action_type=action_type,
                parameters=baseline_state.get("parameters", {})
            )
            
            print(f"    ⚙️  Action executed: {execution_result.get('ok', False)}")
            
        except Exception as e:
            print(f"    ❌ Execution failed: {str(e)}")
            
            # Mark contract as failed
            async with async_session() as session:
                db_contract = await session.get(contract.__class__, contract.id)
                if db_contract:
                    db_contract.status = "failed"
                    await session.commit()
            
            # Rollback if snapshot exists
            if snapshot:
                await self._perform_rollback(snapshot.id, contract.id, mission_id)
            
            return {
                "success": False,
                "error": str(e),
                "contract_id": contract.id,
                "snapshot_id": snapshot.id if snapshot else None,
                "rolled_back": (snapshot is not None)
            }
        
        # Step 4: Run post-execution benchmark
        benchmark_result = None
        if tier in ["tier_2", "tier_3"]:
            # Full regression suite for high-tier actions
            benchmark_result = await benchmark_suite.run_regression_suite(
                triggered_by=f"post_action:{contract.id}",
                compare_to_baseline=True
            )
        else:
            # Quick smoke tests for tier 1
            benchmark_result = await benchmark_suite.run_smoke_tests(
                triggered_by=f"post_action:{contract.id}"
            )
        
        print(f"    🧪 Benchmark: {'✅ PASS' if benchmark_result['passed'] else '❌ FAIL'}")
        
        # Step 5: Capture actual state and verify contract
        actual_state = {
            "execution_result": execution_result,
            "benchmark_passed": benchmark_result["passed"],
            "benchmark_metrics": benchmark_result.get("metrics", {})
        }
        
        verification_result = await contract_verifier.verify_execution(
            contract_id=contract.id,
            actual_state=actual_state,
            metrics=benchmark_result.get("metrics", {})
        )
        
        confidence = verification_result.get("confidence", 0.0)
        verified_success = verification_result.get("success", False)
        
        print(f"    ✅ Verification: confidence={confidence:.2f}, success={verified_success}")
        
        # Step 6: Decide on rollback
        should_rollback = (
            not verified_success or
            verification_result.get("rollback_recommended", False) or
            (benchmark_result.get("drift_detected", False) and tier in ["tier_2", "tier_3"])
        )
        
        if should_rollback and snapshot:
            print(f"    🔙 Rollback recommended (confidence={confidence:.2f})")
            rollback_result = await self._perform_rollback(snapshot.id, contract.id, mission_id)
            
            return {
                "success": False,
                "contract_id": contract.id,
                "snapshot_id": snapshot.id,
                "verification": verification_result,
                "benchmark": benchmark_result,
                "rolled_back": True,
                "rollback_result": rollback_result
            }
        
        # Success path
        if mission_id:
            # Update progression tracker
            await progression_tracker.record_action_completed(
                mission_id=mission_id,
                action_contract_id=contract.id,
                success=verified_success,
                new_safe_point_id=snapshot.id if (snapshot and verified_success) else None
            )
        
        # Mark snapshot as golden if verification passed well
        if snapshot and confidence >= 0.95:
            await snapshot_manager.validate_snapshot(
                snapshot_id=snapshot.id,
                benchmark_results=benchmark_result
            )
        
        print(f"    ✅ Action completed successfully")
        
        return {
            "success": True,
            "contract_id": contract.id,
            "snapshot_id": snapshot.id if snapshot else None,
            "verification": verification_result,
            "benchmark": benchmark_result,
            "confidence": confidence,
            "rolled_back": False
        }
    
    async def _perform_rollback(
        self,
        snapshot_id: str,
        contract_id: str,
        mission_id: Optional[str]
    ) -> Dict[str, Any]:
        """Perform rollback to snapshot"""
        
        print(f"    🔄 Initiating rollback to snapshot {snapshot_id}")
        
        # Restore snapshot
        restore_result = await snapshot_manager.restore_snapshot(
            snapshot_id=snapshot_id,
            dry_run=False
        )
        
        # Update contract status
        from .models import async_session
        async with async_session() as session:
            from .action_contract import ActionContract
            contract = await session.get(ActionContract, contract_id)
            if contract:
                contract.status = "rolled_back"
                await session.commit()
        
        # Update mission progression
        if mission_id:
            await progression_tracker.record_rollback(
                mission_id=mission_id,
                rolled_back_to=snapshot_id
            )
        
        # Log rollback
        await immutable_log.append(
            actor="action_executor",
            action="rollback_executed",
            resource=contract_id,
            subsystem="action_executor",
            payload={
                "contract_id": contract_id,
                "snapshot_id": snapshot_id,
                "mission_id": mission_id
            },
            result="rolled_back"
        )
        
        print(f"    ✅ Rollback completed")
        
        return restore_result


# Singleton instance
action_executor = ActionExecutor()
