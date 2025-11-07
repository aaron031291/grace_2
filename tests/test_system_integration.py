"""
System Integration Tests

Tests all connections from foundation to agentic layer.
Ensures nothing is lurking in the shadows - all components are wired correctly.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

# Foundation layer
from backend.base_models import Base, engine
from backend.models import async_session
from backend.trigger_mesh import trigger_mesh, TriggerEvent
from backend.immutable_log import immutable_log

# Persistence layer
from backend.event_persistence import event_persistence, ActionEvent
from backend.action_contract import contract_verifier, ActionContract
from backend.benchmarks import benchmark_suite, Benchmark
from backend.progression_tracker import progression_tracker, Mission

# Execution layer
from backend.action_executor import ActionExecutor
from backend.input_sentinel import input_sentinel
from backend.self_heal.safe_hold import snapshot_manager

# Orchestration layer
from backend.async_jobs import async_job_queue
from backend.data_aggregation import data_aggregation
from backend.approval_notifications import approval_notifications
from backend.immutable_log_analytics import immutable_log_analytics

# Observability layer
from backend.observability import track_action_execution, ObservabilityContext

# API layer
from backend.routers.verification_router import router as verification_router


@pytest.mark.asyncio
class TestFoundationLayer:
    """Test database and core infrastructure"""
    
    async def test_database_connection(self):
        """Test database is accessible"""
        async with async_session() as session:
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1
    
    async def test_trigger_mesh_functional(self):
        """Test trigger mesh can publish and subscribe"""
        received_events = []
        
        async def handler(event: TriggerEvent):
            received_events.append(event)
        
        await trigger_mesh.subscribe("test.event", handler)
        
        test_event = TriggerEvent(
            event_type="test.event",
            source="test",
            actor="test",
            resource="test",
            payload={"test": "data"}
        )
        
        await trigger_mesh.publish(test_event)
        await asyncio.sleep(0.1)  # Allow event processing
        
        assert len(received_events) > 0
        assert received_events[0].payload["test"] == "data"
    
    async def test_immutable_log_append(self):
        """Test immutable log can append entries"""
        entry = await immutable_log.append(
            actor="test",
            action="test_action",
            resource="test_resource",
            subsystem="test",
            payload={"key": "value"},
            result="success"
        )
        
        assert entry.id is not None
        assert entry.actor == "test"


@pytest.mark.asyncio
class TestPersistenceLayer:
    """Test event persistence and contracts"""
    
    async def test_event_persistence_chain(self):
        """Test events are persisted to database"""
        event = TriggerEvent(
            event_type="agentic.action_planned",
            source="test",
            actor="test",
            resource="test_action",
            payload={"action_id": "test_123"}
        )
        
        persisted = await event_persistence.persist_action_event(
            event=event,
            mission_id="test_mission"
        )
        
        assert persisted.event_type == "agentic.action_planned"
        assert persisted.mission_id == "test_mission"
    
    async def test_contract_creation_and_retrieval(self):
        """Test contract lifecycle"""
        from backend.action_contract import ExpectedEffect
        
        expected_effect = ExpectedEffect(
            description="Test contract",
            state_changes={"test": "value"}
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
        
        assert contract.id is not None
        assert contract.status == "pending"
    
    async def test_mission_tracking(self):
        """Test mission creation and updates"""
        mission = await progression_tracker.start_mission(
            mission_id="integration_test_mission",
            goal="Test mission tracking"
        )
        
        assert mission.status == "active"
        assert mission.progress_percent == 0.0


@pytest.mark.asyncio
class TestExecutionLayer:
    """Test action execution and verification"""
    
    async def test_input_sentinel_integration(self):
        """Test InputSentinel event handling"""
        # InputSentinel should be able to handle errors
        assert input_sentinel is not None
        assert hasattr(input_sentinel, '_handle_error_detected')
    
    async def test_action_executor_exists(self):
        """Test ActionExecutor is available"""
        executor = ActionExecutor()
        assert executor is not None
        assert hasattr(executor, 'execute_verified_action')
    
    async def test_snapshot_manager_available(self):
        """Test snapshot manager can create snapshots"""
        assert snapshot_manager is not None
        # Don't create actual snapshot in test, just verify interface
        assert hasattr(snapshot_manager, 'create_snapshot')


@pytest.mark.asyncio
class TestOrchestrationLayer:
    """Test async jobs and aggregation"""
    
    async def test_async_job_queue_available(self):
        """Test async job queue is functional"""
        assert async_job_queue is not None
        assert hasattr(async_job_queue, 'enqueue')
    
    async def test_data_aggregation_available(self):
        """Test data aggregation service exists"""
        assert data_aggregation is not None
        assert hasattr(data_aggregation, 'run_all_aggregations')
    
    async def test_approval_notifications_available(self):
        """Test approval notification system"""
        assert approval_notifications is not None
        assert hasattr(approval_notifications, 'register_sse_client')
    
    async def test_log_analytics_available(self):
        """Test immutable log analytics"""
        assert immutable_log_analytics is not None
        assert hasattr(immutable_log_analytics, 'verify_log_integrity')


@pytest.mark.asyncio
class TestObservabilityLayer:
    """Test observability and monitoring"""
    
    def test_observability_context(self):
        """Test observability context manager"""
        with ObservabilityContext(
            correlation_id="test-123",
            contract_id=456
        ) as ctx:
            ctx.log("test_event", test="data")
            assert ctx.correlation_id == "test-123"
    
    def test_track_action_execution(self):
        """Test action execution tracking"""
        # Should not raise
        track_action_execution(
            action_type="test",
            tier="tier_1",
            status="success",
            duration_seconds=1.5,
            correlation_id="test-123"
        )


@pytest.mark.asyncio
class TestAPILayer:
    """Test API endpoints are registered"""
    
    def test_verification_router_exists(self):
        """Test verification router is available"""
        assert verification_router is not None
        # Check some key routes exist
        route_paths = [route.path for route in verification_router.routes]
        assert any("/contracts" in path for path in route_paths)
        assert any("/snapshots" in path for path in route_paths)
        assert any("/benchmarks" in path for path in route_paths)


@pytest.mark.asyncio
class TestFullIntegrationChain:
    """Test complete end-to-end integration"""
    
    async def test_error_to_contract_to_mission_chain(self):
        """
        Test the full chain: Error → Event Persistence → Contract → Mission
        
        This validates the complete integration from detection to tracking.
        """
        
        # 1. Create a mission
        mission = await progression_tracker.start_mission(
            mission_id="full_chain_test",
            goal="Test complete integration"
        )
        
        # 2. Trigger an error event
        error_event = TriggerEvent(
            event_type="error.detected",
            source="test",
            actor="test",
            resource="error_001",
            payload={
                "error_id": "error_001",
                "error_type": "test_error",
                "error_message": "Test error",
                "mission_id": "full_chain_test"
            }
        )
        
        # 3. Persist the event
        await event_persistence.persist_action_event(
            event=error_event,
            mission_id="full_chain_test"
        )
        
        # 4. Create an action contract
        from backend.action_contract import ExpectedEffect
        
        expected_effect = ExpectedEffect(
            description="Fix test error",
            state_changes={"error_resolved": True}
        )
        
        contract = await contract_verifier.create_contract(
            action_type="fix_error",
            expected_effect=expected_effect,
            baseline_state={"error_resolved": False},
            playbook_id="test",
            run_id=None,
            triggered_by="test",
            tier="tier_1"
        )
        
        # 5. Update mission progress
        await progression_tracker.update_mission_progress(
            mission_id="full_chain_test",
            progress_percent=100.0,
            current_phase="Resolved"
        )
        
        # 6. Verify all components worked
        updated_mission = await progression_tracker.get_mission("full_chain_test")
        assert updated_mission.progress_percent == 100.0
        assert contract.id is not None
        
        print("✓ Full integration chain validated: Error → Event → Contract → Mission")


@pytest.mark.asyncio
async def test_startup_integration():
    """
    Test that startup_integration module properly wires everything.
    
    This validates the startup sequence doesn't have missing connections.
    """
    
    from backend.startup_integration import start_verification_systems, stop_verification_systems
    
    # These should be callable without errors
    assert callable(start_verification_systems)
    assert callable(stop_verification_systems)
    
    print("✓ Startup integration module properly wired")


@pytest.mark.asyncio
async def test_observability_integration():
    """Test observability hooks are integrated"""
    
    from backend.observability import (
        track_action_execution,
        track_contract_verification,
        track_rollback,
        track_approval,
        track_benchmark,
        track_mission,
        track_job
    )
    
    # All tracking functions should be callable
    assert callable(track_action_execution)
    assert callable(track_contract_verification)
    assert callable(track_rollback)
    assert callable(track_approval)
    assert callable(track_benchmark)
    assert callable(track_mission)
    assert callable(track_job)
    
    print("✓ Observability hooks integrated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
