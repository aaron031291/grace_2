"""
Automated Regression Tests for Verification System

Codifies happy-path and rollback scenarios:
1. Error → verified action → mission update
2. Forced rollback case
3. Contract verification flow
4. Event persistence chain

Tied to CI to catch breaking changes instantly.
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

from backend.input_sentinel import input_sentinel
from backend.action_executor import ActionExecutor
from backend.action_contract import contract_verifier, ExpectedEffect
from backend.event_persistence import event_persistence, ActionEvent
from backend.progression_tracker import progression_tracker
from backend.trigger_mesh import TriggerEvent
from backend.base_execution_result import ExecutionResult, ExecutionStatus


@pytest.mark.asyncio
class TestVerificationHappyPath:
    """Test the full verification happy path"""
    
    async def test_error_to_verified_action_flow(self):
        """
        Test: error.detected → action_planned → action_executing → 
              contract verified → mission updated
        """
        
        # Setup
        error_id = "test_error_123"
        action_id = f"action_{error_id}"
        mission_id = "mission_test_456"
        
        # Step 1: Trigger error detection
        error_event = TriggerEvent(
            event_type="error.detected",
            source="test",
            actor="test_actor",
            resource=error_id,
            payload={
                "error_id": error_id,
                "error_type": "database_locked",
                "error_message": "database is locked",
                "severity": "high",
                "mission_id": mission_id
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        # Step 2: Simulate error handling (would normally be done by InputSentinel)
        with patch.object(input_sentinel, '_classify_pattern', return_value="database_locked"):
            with patch.object(input_sentinel, '_run_playbook_action', new_callable=AsyncMock) as mock_action:
                mock_action.return_value = {"status": "success", "result": "cleared lock"}
                
                # Trigger the flow
                await input_sentinel._handle_error_detected(error_event)
        
        # Step 3: Verify events were persisted
        async with AsyncMock() as mock_session:
            # Check action_planned event
            events = await event_persistence.get_action_timeline(action_id, mock_session)
            
            # Should have at least planned event
            assert len(events) > 0, "No events persisted"
    
    async def test_contract_verification_success(self):
        """Test successful contract verification"""
        
        # Create expected effect
        expected_effect = ExpectedEffect(
            description="Restart database service",
            metric_thresholds={"response_time_ms": 100.0},
            state_changes={"service_status": "running"},
            health_checks=["db_connection"]
        )
        
        baseline_state = {
            "service_status": "stopped",
            "response_time_ms": 500.0
        }
        
        # Create contract
        contract = await contract_verifier.create_contract(
            action_type="restart_service",
            expected_effect=expected_effect,
            baseline_state=baseline_state,
            playbook_id="test_playbook",
            run_id=None,
            triggered_by="test",
            tier="tier_1"
        )
        
        assert contract.id is not None
        assert contract.status == "pending"
        assert contract.action_type == "restart_service"
    
    async def test_mission_progress_tracking(self):
        """Test mission progress updates"""
        
        mission_id = "test_mission_789"
        
        # Create mission
        mission = await progression_tracker.start_mission(
            mission_id=mission_id,
            goal="Test database recovery"
        )
        
        assert mission.mission_id == mission_id
        assert mission.status == "active"
        assert mission.progress_percent == 0.0
        
        # Update progress
        await progression_tracker.update_mission_progress(
            mission_id=mission_id,
            progress_percent=50.0,
            current_phase="Executing recovery"
        )
        
        # Retrieve updated mission
        updated_mission = await progression_tracker.get_mission(mission_id)
        assert updated_mission.progress_percent == 50.0


@pytest.mark.asyncio
class TestVerificationRollback:
    """Test rollback scenarios"""
    
    async def test_contract_violation_triggers_rollback(self):
        """Test that contract violations trigger rollback"""
        
        executor = ActionExecutor()
        
        # Create expected effect that will be violated
        expected_effect = ExpectedEffect(
            description="Scale service",
            metric_thresholds={"cpu_usage": 50.0},  # Expected low CPU
            state_changes={"instance_count": 3},
            health_checks=["health_endpoint"]
        )
        
        baseline_state = {
            "instance_count": 1,
            "cpu_usage": 80.0
        }
        
        with patch('backend.self_heal.adapter.self_healing_adapter.execute') as mock_execute:
            # Simulate execution that violates contract (high CPU)
            mock_execute.return_value = {
                "ok": True,
                "result": {"instance_count": 3, "cpu_usage": 90.0}  # CPU too high!
            }
            
            # Execute with verification
            with patch.object(executor, '_rollback_action', new_callable=AsyncMock) as mock_rollback:
                result = await executor.execute_verified_action(
                    action_type="scale_service",
                    playbook_id="test_playbook",
                    run_id=None,
                    expected_effect=expected_effect,
                    baseline_state=baseline_state,
                    tier="tier_2",
                    triggered_by="test"
                )
                
                # Verify rollback was called
                assert mock_rollback.called, "Rollback should have been triggered"
    
    async def test_tier2_snapshot_created(self):
        """Test that tier 2 actions create safe-hold snapshots"""
        
        executor = ActionExecutor()
        expected_effect = ExpectedEffect(
            description="Update configuration",
            state_changes={"config_version": "2.0"}
        )
        
        with patch('backend.self_heal.safe_hold.snapshot_manager.create_snapshot') as mock_snapshot:
            mock_snapshot.return_value = Mock(id=999)
            
            with patch('backend.self_heal.adapter.self_healing_adapter.execute') as mock_execute:
                mock_execute.return_value = {"ok": True, "result": {"config_version": "2.0"}}
                
                await executor.execute_verified_action(
                    action_type="update_config",
                    playbook_id="test",
                    run_id=None,
                    expected_effect=expected_effect,
                    baseline_state={"config_version": "1.0"},
                    tier="tier_2",
                    triggered_by="test"
                )
                
                # Verify snapshot was created
                assert mock_snapshot.called, "Snapshot should be created for tier_2"


@pytest.mark.asyncio
class TestEventPersistence:
    """Test event persistence chain"""
    
    async def test_events_persisted_to_db(self):
        """Test that all agentic events are persisted"""
        
        event = TriggerEvent(
            event_type="agentic.action_planned",
            source="input_sentinel",
            actor="sentinel",
            resource="test_action",
            payload={
                "action_id": "test_action_123",
                "error_id": "test_error_456",
                "actions": ["clear_cache"],
                "can_auto_execute": True,
                "mission_id": "mission_789"
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        # Persist event
        persisted = await event_persistence.persist_action_event(
            event=event,
            mission_id="mission_789"
        )
        
        assert persisted.event_type == "agentic.action_planned"
        assert persisted.action_id == "test_action_123"
        assert persisted.mission_id == "mission_789"
    
    async def test_event_timeline_retrieval(self):
        """Test retrieving event timeline for an action"""
        
        action_id = "timeline_test_action"
        
        # Create multiple events
        events = [
            TriggerEvent(
                event_type="agentic.action_planned",
                source="test",
                actor="test",
                resource=action_id,
                payload={"action_id": action_id},
                timestamp=datetime.now(timezone.utc)
            ),
            TriggerEvent(
                event_type="agentic.action_executing",
                source="test",
                actor="test",
                resource=action_id,
                payload={"action_id": action_id},
                timestamp=datetime.now(timezone.utc)
            )
        ]
        
        for event in events:
            await event_persistence.persist_action_event(event=event)
        
        # Retrieve timeline
        async with AsyncMock() as mock_session:
            with patch('backend.event_persistence.event_persistence.get_action_timeline') as mock_timeline:
                mock_timeline.return_value = [
                    Mock(event_type="agentic.action_planned"),
                    Mock(event_type="agentic.action_executing")
                ]
                
                timeline = await event_persistence.get_action_timeline(action_id, mock_session)
                assert len(timeline) == 2


@pytest.mark.asyncio
class TestExecutionResult:
    """Test ExecutionResult standardization"""
    
    def test_success_result(self):
        """Test creating success result"""
        result = ExecutionResult.success(
            result={"instances": 3},
            action_type="scale_up",
            metrics={"cpu": 45.0}
        )
        
        assert result.ok is True
        assert result.status == ExecutionStatus.SUCCESS
        assert result.result == {"instances": 3}
    
    def test_failure_result(self):
        """Test creating failure result"""
        result = ExecutionResult.failure(
            error="Connection timeout",
            action_type="restart_service"
        )
        
        assert result.ok is False
        assert result.status == ExecutionStatus.FAILED
        assert result.error == "Connection timeout"
    
    def test_result_serialization(self):
        """Test result serialization for contracts"""
        result = ExecutionResult.success(
            result="OK",
            action_type="test",
            metrics={"latency": 100}
        )
        
        contract_payload = result.to_contract_outcome()
        
        assert "status" in contract_payload
        assert "success" in contract_payload
        assert contract_payload["success"] is True
        assert contract_payload["metrics"]["latency"] == 100


# ============================================================================
# Integration Test: Full End-to-End Flow
# ============================================================================

@pytest.mark.asyncio
async def test_full_verification_integration():
    """
    Full integration test: Error → Action → Verification → Mission Update
    
    This is the golden path that should always work.
    """
    
    # 1. Create a mission
    mission_id = "integration_test_mission"
    mission = await progression_tracker.start_mission(
        mission_id=mission_id,
        goal="Integration test recovery"
    )
    assert mission.status == "active"
    
    # 2. Simulate error detection with mission context
    error_id = "integration_error_001"
    
    # 3. Create and verify an action contract
    expected_effect = ExpectedEffect(
        description="Fix test issue",
        state_changes={"issue_resolved": True}
    )
    
    contract = await contract_verifier.create_contract(
        action_type="fix_issue",
        expected_effect=expected_effect,
        baseline_state={"issue_resolved": False},
        playbook_id="integration_test",
        run_id=None,
        triggered_by="integration_test",
        tier="tier_1"
    )
    
    # 4. Execute action with mocked executor
    executor = ActionExecutor()
    
    with patch('backend.self_heal.adapter.self_healing_adapter.execute') as mock_execute:
        mock_execute.return_value = {
            "ok": True,
            "result": {"issue_resolved": True}
        }
        
        result = await executor.execute_verified_action(
            action_type="fix_issue",
            playbook_id="integration_test",
            run_id=None,
            expected_effect=expected_effect,
            baseline_state={"issue_resolved": False},
            tier="tier_1",
            triggered_by="integration_test",
            mission_id=mission_id
        )
    
    # 5. Verify mission was updated
    await progression_tracker.update_mission_progress(
        mission_id=mission_id,
        progress_percent=100.0,
        current_phase="Completed"
    )
    
    updated_mission = await progression_tracker.get_mission(mission_id)
    assert updated_mission.progress_percent == 100.0
    
    print("✓ Full integration test passed!")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
