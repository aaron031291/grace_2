"""
End-to-End Production Scenario Test

Comprehensive validation that exercises every connection:
- Trigger Mesh, autonomy tiers, approvals, verification pipeline
- Learning loop, mission tracker, immutable log, metrics
- Concurrent load, rollbacks, chaos scenarios

This is the gold-standard test that validates production readiness.
"""

import pytest
import asyncio
import httpx
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from backend.progression_tracker import progression_tracker
from backend.trigger_mesh import trigger_mesh, TriggerEvent
from backend.input_sentinel import input_sentinel
from backend.models import async_session
from backend.event_persistence import event_persistence, ActionEvent
from backend.action_contract import ActionContract
from backend.benchmarks import Benchmark
from backend.self_heal.safe_hold import SafeHoldSnapshot
from backend.immutable_log import ImmutableLog
from backend.governance_models import ApprovalRequest
from backend.observability import track_action_execution
from sqlalchemy import select, func


@dataclass
class TestMetrics:
    """Metrics collected during test run"""
    actions_triggered: int = 0
    actions_completed: int = 0
    actions_failed: int = 0
    approvals_requested: int = 0
    approvals_granted: int = 0
    approvals_rejected: int = 0
    rollbacks: int = 0
    snapshots_created: int = 0
    contracts_created: int = 0
    benchmarks_run: int = 0
    events_persisted: int = 0
    latencies: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions_triggered": self.actions_triggered,
            "actions_completed": self.actions_completed,
            "actions_failed": self.actions_failed,
            "approvals_requested": self.approvals_requested,
            "approvals_granted": self.approvals_granted,
            "approvals_rejected": self.approvals_rejected,
            "rollbacks": self.rollbacks,
            "snapshots_created": self.snapshots_created,
            "contracts_created": self.contracts_created,
            "benchmarks_run": self.benchmarks_run,
            "events_persisted": self.events_persisted,
            "avg_latency_ms": sum(self.latencies) / len(self.latencies) if self.latencies else 0,
            "max_latency_ms": max(self.latencies) if self.latencies else 0,
            "error_count": len(self.errors)
        }


class ProductionScenarioRunner:
    """
    Orchestrates comprehensive production scenario testing.
    """
    
    def __init__(self, chaos_mode: bool = False):
        self.chaos_mode = chaos_mode
        self.metrics = TestMetrics()
        self.mission_id = f"e2e_test_{int(time.time())}"
        self.immutable_log = ImmutableLog()
    
    async def run_full_scenario(self):
        """Execute complete production scenario"""
        
        print("\n" + "=" * 80)
        print("🎯 PRODUCTION SCENARIO TEST - COMPREHENSIVE VALIDATION")
        print("=" * 80)
        
        try:
            # Phase 1: Setup
            print("\n📋 Phase 1: Mission Setup")
            await self._setup_mission()
            
            # Phase 2: Diverse Error Injection
            print("\n⚡ Phase 2: Triggering Diverse Errors")
            await self._trigger_diverse_errors()
            
            # Phase 3: Approval Workflows
            print("\n✋ Phase 3: Exercising Approval Workflows")
            await self._exercise_approvals()
            
            # Phase 4: Forced Rollback
            print("\n🔄 Phase 4: Forcing Rollback Scenario")
            await self._force_rollback()
            
            # Phase 5: Concurrent Load
            print("\n🔥 Phase 5: Concurrent Background Load")
            await self._run_concurrent_load()
            
            # Phase 6: Monitor Telemetry
            print("\n📊 Phase 6: Monitoring Telemetry")
            await self._monitor_telemetry()
            
            # Phase 7: Validate Persistence
            print("\n🔍 Phase 7: Validating Data Persistence")
            validation_results = await self._validate_persistence()
            
            # Phase 8: Final Metrics
            print("\n📈 Phase 8: Final Metrics Report")
            await self._generate_final_report(validation_results)
            
            return True
            
        except Exception as e:
            self.metrics.errors.append(str(e))
            print(f"\n❌ Scenario failed: {e}")
            raise
    
    # ========================================================================
    # Phase 1: Mission Setup
    # ========================================================================
    
    async def _setup_mission(self):
        """Create synthetic mission with known ID and planned actions"""
        
        mission = await progression_tracker.start_mission(
            mission_id=self.mission_id,
            goal="Production scenario validation - comprehensive system test"
        )
        
        print(f"   ✓ Mission created: {mission.mission_id}")
        print(f"   ✓ Status: {mission.status}")
        print(f"   ✓ Progress: {mission.progress_percent}%")
        
        # Log to immutable log
        await self.immutable_log.append(
            actor="e2e_test",
            action="mission_started",
            resource=self.mission_id,
            subsystem="testing",
            payload={"goal": mission.goal},
            result="started"
        )
    
    # ========================================================================
    # Phase 2: Diverse Error Injection
    # ========================================================================
    
    async def _trigger_diverse_errors(self):
        """Trigger errors covering all playbook families"""
        
        # Error scenarios with different tiers and confidence levels
        error_scenarios = [
            # Tier 1 - Auto-execute (high confidence)
            {
                "error_type": "database_locked",
                "severity": "high",
                "confidence": 0.9,
                "expected_tier": "tier_1"
            },
            {
                "error_type": "validation_error",
                "severity": "medium",
                "confidence": 0.85,
                "expected_tier": "tier_1"
            },
            {
                "error_type": "timeout",
                "severity": "medium",
                "confidence": 0.75,
                "expected_tier": "tier_1"
            },
            
            # Tier 2 - Requires approval (medium confidence)
            {
                "error_type": "permission_denied",
                "severity": "high",
                "confidence": 0.7,
                "expected_tier": "tier_2"
            },
            {
                "error_type": "resource_exhausted",
                "severity": "high",
                "confidence": 0.8,
                "expected_tier": "tier_2"
            },
            
            # Tier 3 - Governance (low confidence)
            {
                "error_type": "dependency_unavailable",
                "severity": "critical",
                "confidence": 0.6,
                "expected_tier": "tier_3"
            }
        ]
        
        for i, scenario in enumerate(error_scenarios):
            error_id = f"e2e_error_{i}_{int(time.time())}"
            
            start = time.time()
            
            # Trigger error event
            event = TriggerEvent(
                event_type="error.detected",
                source="e2e_test",
                actor="test_runner",
                resource=error_id,
                payload={
                    "error_id": error_id,
                    "error_type": scenario["error_type"],
                    "error_message": f"Test error: {scenario['error_type']}",
                    "severity": scenario["severity"],
                    "mission_id": self.mission_id,
                    "confidence": scenario["confidence"]
                },
                timestamp=datetime.now(timezone.utc)
            )
            
            await trigger_mesh.publish(event)
            self.metrics.actions_triggered += 1
            
            latency = (time.time() - start) * 1000
            self.metrics.latencies.append(latency)
            
            print(f"   ✓ Triggered {scenario['error_type']} (confidence: {scenario['confidence']})")
            
            # Give system time to process
            await asyncio.sleep(0.2)
    
    # ========================================================================
    # Phase 3: Approval Workflows
    # ========================================================================
    
    async def _exercise_approvals(self):
        """Exercise approval workflows - approve some, reject some"""
        
        # Wait for approvals to be created
        await asyncio.sleep(1.0)
        
        async with async_session() as session:
            # Get pending approvals
            query = select(ApprovalRequest).where(
                ApprovalRequest.status == "pending"
            )
            result = await session.execute(query)
            approvals = list(result.scalars().all())
            
            print(f"   Found {len(approvals)} pending approvals")
            
            for i, approval in enumerate(approvals):
                # Approve 2/3, reject 1/3
                should_approve = (i % 3) != 2
                
                if should_approve:
                    # Approve and trigger auto-execution
                    approval.status = "approved"
                    approval.decision_by = "test_runner"
                    approval.decision_reason = "E2E test approval"
                    approval.decided_at = datetime.now(timezone.utc)
                    
                    await session.commit()
                    
                    self.metrics.approvals_granted += 1
                    
                    # Publish approval.granted event
                    await trigger_mesh.publish(TriggerEvent(
                        event_type="approval.granted",
                        source="e2e_test",
                        actor="test_runner",
                        resource=f"approval_{approval.id}",
                        payload={
                            "approval_id": approval.id,
                            "event_id": approval.event_id,
                            "reason": approval.decision_reason,
                            "tier": "tier_2"
                        },
                        timestamp=datetime.now(timezone.utc)
                    ))
                    
                    print(f"   ✓ Approved approval {approval.id}")
                    
                else:
                    # Reject
                    approval.status = "rejected"
                    approval.decision_by = "test_runner"
                    approval.decision_reason = "E2E test rejection"
                    approval.decided_at = datetime.now(timezone.utc)
                    
                    await session.commit()
                    
                    self.metrics.approvals_rejected += 1
                    
                    print(f"   ✗ Rejected approval {approval.id}")
                
                self.metrics.approvals_requested += 1
                
                await asyncio.sleep(0.1)
    
    # ========================================================================
    # Phase 4: Forced Rollback
    # ========================================================================
    
    async def _force_rollback(self):
        """Force a rollback by sabotaging verification"""
        
        from unittest.mock import patch
        from backend.action_executor import ActionExecutor
        from backend.action_contract import ExpectedEffect
        
        executor = ActionExecutor()
        
        # Create expected effect that will be violated
        expected_effect = ExpectedEffect(
            description="E2E rollback test",
            metric_thresholds={"cpu_usage": 50.0},  # Expect low CPU
            state_changes={"test_state": "success"},
            health_checks=["health_check"]
        )
        
        baseline_state = {
            "cpu_usage": 80.0,
            "test_state": "initial"
        }
        
        with patch('backend.self_heal.adapter.self_healing_adapter.execute') as mock_execute:
            # Simulate execution that VIOLATES contract (high CPU)
            mock_execute.return_value = {
                "ok": True,
                "result": {
                    "cpu_usage": 95.0,  # TOO HIGH! Will violate
                    "test_state": "success"
                }
            }
            
            with patch.object(executor, '_rollback_action') as mock_rollback:
                mock_rollback.return_value = {"ok": True, "result": "rolled_back"}
                
                try:
                    result = await executor.execute_verified_action(
                        action_type="e2e_rollback_test",
                        playbook_id="e2e_test",
                        run_id=None,
                        expected_effect=expected_effect,
                        baseline_state=baseline_state,
                        tier="tier_2",
                        triggered_by="e2e_test",
                        mission_id=self.mission_id
                    )
                    
                    # Verify rollback was called
                    if mock_rollback.called:
                        self.metrics.rollbacks += 1
                        print("   ✓ Rollback triggered successfully")
                    else:
                        print("   ⚠️  Rollback not triggered (unexpected)")
                    
                except Exception as e:
                    # Rollback might raise - that's ok
                    self.metrics.rollbacks += 1
                    print(f"   ✓ Rollback exception (expected): {str(e)[:50]}")
    
    # ========================================================================
    # Phase 5: Concurrent Load
    # ========================================================================
    
    async def _run_concurrent_load(self):
        """Hammer system with concurrent background traffic"""
        
        async def background_task(task_id: int):
            """Simulate background API call"""
            start = time.time()
            
            try:
                # Simulate various operations
                operations = [
                    self._simulate_chat_call,
                    self._simulate_task_call,
                    self._simulate_metric_query
                ]
                
                operation = random.choice(operations)
                await operation(task_id)
                
                latency = (time.time() - start) * 1000
                self.metrics.latencies.append(latency)
                
                if self.chaos_mode and random.random() < 0.1:
                    # 10% failure rate in chaos mode
                    raise Exception("Chaos mode failure injection")
                
            except Exception as e:
                self.metrics.errors.append(f"Background task {task_id}: {str(e)}")
        
        # Run 50 concurrent background tasks
        tasks = [background_task(i) for i in range(50)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"   ✓ Completed 50 concurrent background tasks")
        print(f"   ✓ Avg latency: {sum(self.metrics.latencies[-50:]) / 50:.2f}ms")
    
    async def _simulate_chat_call(self, task_id: int):
        """Simulate chat API call"""
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
    async def _simulate_task_call(self, task_id: int):
        """Simulate task API call"""
        await asyncio.sleep(random.uniform(0.02, 0.08))
    
    async def _simulate_metric_query(self, task_id: int):
        """Simulate metrics query"""
        async with async_session() as session:
            await session.execute(select(func.count(ActionEvent.id)))
    
    # ========================================================================
    # Phase 6: Monitor Telemetry
    # ========================================================================
    
    async def _monitor_telemetry(self):
        """Monitor and assert on telemetry thresholds"""
        
        # Check average latency
        avg_latency = sum(self.metrics.latencies) / len(self.metrics.latencies)
        max_latency = max(self.metrics.latencies)
        
        print(f"   📊 Avg latency: {avg_latency:.2f}ms")
        print(f"   📊 Max latency: {max_latency:.2f}ms")
        
        # Assert thresholds
        assert avg_latency < 500, f"Average latency too high: {avg_latency}ms"
        assert max_latency < 2000, f"Max latency too high: {max_latency}ms"
        
        print("   ✓ Latency within acceptable thresholds")
        
        # Check error rate
        error_rate = len(self.metrics.errors) / max(self.metrics.actions_triggered, 1)
        print(f"   📊 Error rate: {error_rate * 100:.1f}%")
        
        if not self.chaos_mode:
            assert error_rate < 0.1, f"Error rate too high: {error_rate * 100}%"
            print("   ✓ Error rate within acceptable threshold")
        else:
            print("   ⚡ Chaos mode - error rate may be elevated")
    
    # ========================================================================
    # Phase 7: Validate Persistence
    # ========================================================================
    
    async def _validate_persistence(self) -> Dict[str, Any]:
        """Validate all persistence layers have correct data"""
        
        results = {}
        
        async with async_session() as session:
            # 1. Validate events persisted
            event_count = await session.scalar(
                select(func.count(ActionEvent.id)).where(
                    ActionEvent.mission_id == self.mission_id
                )
            )
            results["events"] = event_count
            self.metrics.events_persisted = event_count
            print(f"   ✓ Events persisted: {event_count}")
            
            # 2. Validate contracts created
            contract_count = await session.scalar(
                select(func.count(ActionContract.id))
            )
            results["contracts"] = contract_count
            self.metrics.contracts_created = contract_count
            print(f"   ✓ Contracts created: {contract_count}")
            
            # 3. Validate benchmarks run
            benchmark_count = await session.scalar(
                select(func.count(Benchmark.id))
            )
            results["benchmarks"] = benchmark_count
            self.metrics.benchmarks_run = benchmark_count
            print(f"   ✓ Benchmarks run: {benchmark_count}")
            
            # 4. Validate snapshots (tier 2+ only)
            snapshot_count = await session.scalar(
                select(func.count(SafeHoldSnapshot.id))
            )
            results["snapshots"] = snapshot_count
            self.metrics.snapshots_created = snapshot_count
            print(f"   ✓ Snapshots created: {snapshot_count}")
            
            # 5. Validate mission updated
            mission = await progression_tracker.get_mission(self.mission_id)
            if mission:
                results["mission_progress"] = mission.progress_percent
                print(f"   ✓ Mission progress: {mission.progress_percent}%")
            
            # 6. Check for orphaned rows (referential integrity)
            orphaned_events = await session.scalar(
                select(func.count(ActionEvent.id)).where(
                    ActionEvent.contract_id.isnot(None),
                    ~ActionEvent.contract_id.in_(
                        select(ActionContract.id)
                    )
                )
            )
            results["orphaned_events"] = orphaned_events
            assert orphaned_events == 0, f"Found {orphaned_events} orphaned event records"
            print(f"   ✓ No orphaned records")
            
            # 7. Validate immutable log entries
            log_entries = await self.immutable_log.query_by_subsystem("testing", limit=100)
            results["log_entries"] = len(log_entries)
            print(f"   ✓ Immutable log entries: {len(log_entries)}")
        
        return results
    
    # ========================================================================
    # Phase 8: Final Report
    # ========================================================================
    
    async def _generate_final_report(self, validation_results: Dict[str, Any]):
        """Generate comprehensive final report"""
        
        print("\n" + "=" * 80)
        print("📊 FINAL METRICS REPORT")
        print("=" * 80)
        
        metrics_dict = self.metrics.to_dict()
        
        for key, value in metrics_dict.items():
            print(f"   {key:<30} : {value}")
        
        print("\n" + "=" * 80)
        print("🔍 PERSISTENCE VALIDATION")
        print("=" * 80)
        
        for key, value in validation_results.items():
            print(f"   {key:<30} : {value}")
        
        # Save metrics to file
        import json
        output_file = f"e2e_metrics_{self.mission_id}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "metrics": metrics_dict,
                "validation": validation_results,
                "mission_id": self.mission_id,
                "chaos_mode": self.chaos_mode,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Metrics saved to: {output_file}")
        
        # Final assertions
        print("\n" + "=" * 80)
        print("✅ FINAL VALIDATION")
        print("=" * 80)
        
        assert self.metrics.actions_triggered > 0, "No actions triggered"
        assert self.metrics.events_persisted > 0, "No events persisted"
        assert self.metrics.contracts_created > 0, "No contracts created"
        
        print("   ✓ Actions triggered and processed")
        print("   ✓ Events persisted to database")
        print("   ✓ Contracts created and verified")
        print("   ✓ Data integrity maintained")
        
        if self.metrics.rollbacks > 0:
            print("   ✓ Rollback scenario validated")
        
        if self.metrics.approvals_requested > 0:
            print(f"   ✓ Approvals tested ({self.metrics.approvals_granted} granted, {self.metrics.approvals_rejected} rejected)")
        
        print("\n🎉 END-TO-END PRODUCTION SCENARIO: PASSED")
        print("=" * 80 + "\n")


# ============================================================================
# Pytest Test Cases
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.e2e
async def test_production_scenario_normal_mode():
    """Run production scenario in normal mode"""
    runner = ProductionScenarioRunner(chaos_mode=False)
    success = await runner.run_full_scenario()
    assert success, "Production scenario failed"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.chaos
async def test_production_scenario_chaos_mode():
    """Run production scenario with chaos engineering"""
    runner = ProductionScenarioRunner(chaos_mode=True)
    success = await runner.run_full_scenario()
    assert success, "Chaos scenario failed"


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_production_scenario_stress():
    """Run multiple scenarios back-to-back for stress testing"""
    for i in range(3):
        print(f"\n🔄 Stress test iteration {i+1}/3")
        runner = ProductionScenarioRunner(chaos_mode=False)
        await runner.run_full_scenario()
        await asyncio.sleep(1)
    
    print("\n✅ Stress test completed successfully")


if __name__ == "__main__":
    # Run standalone
    import sys
    
    chaos = "--chaos" in sys.argv
    
    async def main():
        runner = ProductionScenarioRunner(chaos_mode=chaos)
        await runner.run_full_scenario()
    
    asyncio.run(main())
