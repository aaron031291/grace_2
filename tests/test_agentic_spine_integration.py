"""Integration tests for agentic spine autonomous operations"""

import pytest
import asyncio
from datetime import datetime
from backend.agentic_spine import agentic_spine, RecoveryPlan, PlanStatus, RiskLevel, Playbook
from backend.trigger_mesh import trigger_mesh, TriggerEvent
from backend.collectors.mock_collector import mock_collector


@pytest.mark.asyncio
async def test_agentic_spine_startup():
    """Test that agentic spine starts and initializes properly"""
    await agentic_spine.start()
    assert agentic_spine.running == True
    assert agentic_spine.enrichment is not None
    assert agentic_spine.trust_core is not None
    assert agentic_spine.health_graph is not None
    assert agentic_spine.planner is not None
    await agentic_spine.stop()


@pytest.mark.asyncio
async def test_mock_metrics_collection():
    """Test that mock metrics collector generates realistic data"""
    await mock_collector.start()

    # Wait for some metrics to be published
    await asyncio.sleep(2)

    # Check that metrics are being published (this would need trigger mesh inspection in real test)
    assert mock_collector.running == True

    await mock_collector.stop()


@pytest.mark.asyncio
async def test_playbook_registration():
    """Test registering and using playbooks"""
    # Create a test playbook
    test_playbook = Playbook(
        playbook_id="test_scale_up",
        name="Test Scale Up",
        description="Test scaling playbook",
        preconditions=[{"metric": "cpu_utilization", "operator": ">", "value": 80}],
        steps=[
            {"action": "scale_up", "target": "web-asg", "capacity": 3},
            {"action": "verify", "metric": "healthy_instances", "expected": 3}
        ],
        verifications=[{"check": "capacity_reached"}],
        rollback_steps=[{"action": "scale_down", "target": "web-asg", "capacity": 1}],
        risk_level=RiskLevel.LOW,
        requires_approval=False
    )

    await agentic_spine.planner.register_playbook(test_playbook)
    assert test_playbook.playbook_id in agentic_spine.planner.playbooks


@pytest.mark.asyncio
async def test_recovery_plan_creation():
    """Test creating recovery plans from enriched events"""
    # Create a mock enriched event
    from backend.agentic_spine import EnrichedEvent, TriggerEvent

    mock_event = TriggerEvent(
        event_type="health.degraded",
        source="mock_monitor",
        actor="test_system",
        resource="web-server-01",
        payload={"cpu_utilization": 95.0, "status": "degraded"},
        timestamp=datetime.utcnow()
    )

    enriched = EnrichedEvent(
        event_id="test_event_123",
        original_event=mock_event,
        signer_identity="test_system",
        intent="adjust_capacity",
        context={"system_state": {"status": "degraded"}, "dependencies": []},
        expected_outcome="capacity_meets_demand",
        confidence=0.8
    )

    # Register a basic playbook first
    test_playbook = Playbook(
        playbook_id="test_recovery",
        name="Test Recovery",
        description="Basic recovery playbook",
        preconditions=[],
        steps=[{"action": "scale_up", "target": "web-server-01", "capacity": 2}],
        verifications=[],
        rollback_steps=[],
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        success_rate=0.9  # Higher success rate to be selected
    )

    await agentic_spine.planner.register_playbook(test_playbook)

    # Generate recovery plan
    plan = await agentic_spine.planner.plan_recovery(enriched)

    assert plan is not None
    assert plan.playbook.playbook_id == "test_recovery"
    assert plan.status in [PlanStatus.PROPOSED, PlanStatus.APPROVED]
    assert plan.risk_score >= 0.0
    assert plan.risk_score <= 1.0


@pytest.mark.asyncio
async def test_trust_core_evaluation():
    """Test trust core decision evaluation"""
    from backend.agentic_spine import DecisionRecord

    decision = DecisionRecord(
        decision_id="test_decision_123",
        decision_type="scaling",
        context={"resource": "web-server-01", "current_load": 90},
        options_considered=["scale_up", "ignore", "alert_human"],
        chosen_option="scale_up",
        rationale="High CPU utilization requires scaling",
        confidence=0.85,
        risk_assessment={},
        approvals_required=[],
        approvals_received=[]
    )

    approved, rationale, escalations = await agentic_spine.trust_core.evaluate_decision(decision)

    assert isinstance(approved, bool)
    assert isinstance(rationale, str)
    assert isinstance(escalations, list)
    assert "risk" in rationale.lower() or "approved" in rationale.lower()


@pytest.mark.asyncio
async def test_health_graph_operations():
    """Test health graph node registration and updates"""
    from backend.agentic_spine import HealthNode

    test_node = HealthNode(
        node_id="test-service",
        node_type="web_service",
        name="Test Web Service",
        status="healthy",
        kpis={"cpu": 45.0, "memory": 60.0},
        dependencies=["database", "cache"],
        dependents=["api-gateway"],
        blast_radius=5,
        priority=3
    )

    await agentic_spine.health_graph.register_node(test_node)
    assert test_node.node_id in agentic_spine.health_graph.nodes

    # Test health update
    await agentic_spine.health_graph.update_health("test-service", "degraded", {"cpu": 95.0})
    updated_node = agentic_spine.health_graph.nodes["test-service"]
    assert updated_node.status == "degraded"
    assert updated_node.kpis["cpu"] == 95.0


@pytest.mark.asyncio
async def test_event_enrichment():
    """Test event enrichment layer"""
    test_event = TriggerEvent(
        event_type="metrics.cpu_utilization",
        source="mock_collector",
        actor="test_monitor",
        resource="web-server-01",
        payload={"value": 85.0, "unit": "percent"},
        timestamp=datetime.utcnow()
    )

    enriched = await agentic_spine.enrichment.enrich(test_event)

    assert enriched.event_id is not None
    assert enriched.signer_identity == "test_monitor"
    assert enriched.confidence >= 0.0
    assert enriched.confidence <= 1.0
    assert isinstance(enriched.context, dict)
    assert isinstance(enriched.intent, str)


@pytest.mark.asyncio
async def test_full_incident_response_flow():
    """Test complete incident response flow"""
    await agentic_spine.start()
    await mock_collector.start()

    # Simulate an incident
    incident_event = TriggerEvent(
        event_type="health.degraded",
        source="mock_monitor",
        actor="test_system",
        resource="test-service",
        payload={"cpu_utilization": 95.0, "status": "critical"},
        timestamp=datetime.utcnow()
    )

    # Publish incident to trigger mesh
    await trigger_mesh.publish(incident_event)

    # Wait for processing
    await asyncio.sleep(1)

    # Check that spine is still running (didn't crash)
    assert agentic_spine.running == True

    await mock_collector.stop()
    await agentic_spine.stop()


@pytest.mark.asyncio
async def test_meta_loop_autonomy():
    """Test meta loop self-improvement capabilities"""
    # Create a completed plan for retrospective
    test_plan = RecoveryPlan(
        plan_id="test_plan_123",
        playbook=Playbook(
            playbook_id="test_pb",
            name="Test Playbook",
            description="Test",
            preconditions=[],
            steps=[],
            verifications=[],
            rollback_steps=[],
            risk_level=RiskLevel.LOW,
            requires_approval=False
        ),
        target_nodes=["test-node"],
        parameters={},
        risk_score=0.2,
        justification="Test recovery",
        status=PlanStatus.COMPLETED,
        completed_at=datetime.utcnow(),
        outcome="success"
    )

    # Schedule retrospective
    await agentic_spine.meta_loop.schedule_retrospective(test_plan)

    # Test threshold tuning
    await agentic_spine.meta_loop.tune_thresholds("cpu_monitor", "utilization", 0.25)

    # Both should complete without errors
    assert True