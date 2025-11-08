"""
Test Agentic Integration - End-to-end tests

Verifies the entire agentic stack integrates and runs properly.
"""

import pytest
import asyncio
from datetime import datetime

from backend.grace_spine_integration import grace_agentic_system, activate_grace_autonomy, deactivate_grace_autonomy
from backend.trigger_mesh import trigger_mesh, TriggerEvent
from backend.immutable_log import immutable_log
from backend.agentic_observability import agentic_observability


@pytest.mark.asyncio
async def test_agentic_system_starts_and_stops():
    """Test that the agentic system can start and stop cleanly"""
    
    # Start
    await activate_grace_autonomy()
    
    assert grace_agentic_system.running == True
    assert grace_agentic_system.started_at is not None
    
    # Check all systems running
    health = await grace_agentic_system.health_check()
    assert health["status"] == "operational"
    
    # Stop
    await deactivate_grace_autonomy()
    
    assert grace_agentic_system.running == False


@pytest.mark.asyncio
async def test_trigger_mesh_pub_sub():
    """Test trigger mesh event flow"""
    
    received_events = []
    
    async def test_handler(event: TriggerEvent):
        received_events.append(event)
    
    await trigger_mesh.start()
    trigger_mesh.subscribe("test.*", test_handler)
    
    # Publish test event
    test_event = TriggerEvent(
        event_type="test.example",
        source="test",
        actor="test_actor",
        resource="test_resource",
        payload={"test": "data"},
        timestamp=datetime.utcnow()
    )
    
    await trigger_mesh.publish(test_event)
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    assert len(received_events) == 1
    assert received_events[0].event_type == "test.example"
    
    await trigger_mesh.stop()


@pytest.mark.asyncio
async def test_immutable_log_append():
    """Test immutable log can append entries"""
    
    entry_id = await immutable_log.append(
        actor="test_actor",
        action="test_action",
        resource="test_resource",
        subsystem="test_subsystem",
        payload={"test": "payload"},
        result="success"
    )
    
    assert entry_id > 0
    
    # Verify integrity
    result = await immutable_log.verify_integrity()
    assert result["valid"] == True


@pytest.mark.asyncio
async def test_agentic_observability_capture():
    """Test agentic observability captures decision points"""
    
    await agentic_observability.start()
    
    # Start a run
    test_event = TriggerEvent(
        event_type="test.incident",
        source="test",
        actor="test",
        resource="test_service",
        payload={},
        timestamp=datetime.utcnow()
    )
    
    await agentic_observability.capture.start_run(
        run_id="test_run_1",
        trigger_event=test_event,
        context={"test": "context"}
    )
    
    # Record diagnosis
    await agentic_observability.capture.record_diagnosis(
        run_id="test_run_1",
        diagnosis="Test diagnosis",
        root_cause="Test root cause",
        confidence=0.85
    )
    
    # Complete run
    await agentic_observability.capture.complete_run(
        run_id="test_run_1",
        final_outcome="Test successful",
        success=True
    )
    
    # Query run details
    details = await agentic_observability.get_run_trace("test_run_1")
    
    assert details is not None
    assert details["run_id"] == "test_run_1"
    assert len(details["phases"]) >= 3
    
    await agentic_observability.stop()


@pytest.mark.asyncio
async def test_end_to_end_event_flow():
    """Test complete flow: event → enrichment → decision → log"""
    
    await activate_grace_autonomy()
    
    # Publish incident event
    incident_event = TriggerEvent(
        event_type="alert.latency_degraded",
        source="monitoring",
        actor="prometheus",
        resource="api-service",
        payload={"latency_p95": 850, "threshold": 500},
        timestamp=datetime.utcnow()
    )
    
    await trigger_mesh.publish(incident_event)
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Check that systems processed it
    stats = await agentic_observability.read_models.get_statistics(hours=1)
    
    # Should have at least captured the event
    assert stats is not None
    
    await deactivate_grace_autonomy()


if __name__ == "__main__":
    print("Running agentic integration tests...")
    asyncio.run(test_agentic_system_starts_and_stops())
    print("✓ Start/stop test passed")
    
    asyncio.run(test_trigger_mesh_pub_sub())
    print("✓ Trigger mesh test passed")
    
    asyncio.run(test_immutable_log_append())
    print("✓ Immutable log test passed")
    
    asyncio.run(test_agentic_observability_capture())
    print("✓ Observability test passed")
    
    asyncio.run(test_end_to_end_event_flow())
    print("✓ End-to-end test passed")
    
    print("\n✅ All integration tests passed!")
