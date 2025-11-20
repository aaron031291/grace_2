from pathlib import Path

import pytest

from backend.learning.governed_learning import (
    ApprovalGate,
    DomainWhitelistAPI,
    DomainWhitelistEntry,
    DomainWhitelistRegistry,
    GapDetectionEngine,
    GovernedLearningJob,
    GovernedLearningOrchestrator,
    LearningJobDashboard,
    LearningJobQueue,
    LearningSimulationFramework,
    SafeModeLearningController,
    SandboxVerifier,
    WorldModelUpdateManager,
)


def test_gap_detection_engine_prioritizes_low_confidence_topics() -> None:
    engine = GapDetectionEngine(target_confidence=0.9)
    queries = [
        {
            "query": "improve trust mttr",
            "topic": "trust",
            "success": 0.4,
            "retrieval_uncertainty": 0.55,
            "impact": 1.4,
        },
        {
            "query": "improve trust mttr",
            "topic": "trust",
            "success": 0.5,
            "retrieval_uncertainty": 0.45,
            "impact": 1.2,
        },
        {
            "query": "rag provenance",
            "topic": "memory",
            "success": 0.9,
            "retrieval_uncertainty": 0.2,
            "impact": 0.6,
        },
    ]
    knowledge_snapshot = {"topics": {"trust": {"confidence": 0.5}, "memory": {"confidence": 0.92}}}

    report = engine.analyze_queries(queries, knowledge_snapshot)

    assert report.signals[0].topic == "trust"
    assert "low_confidence" in report.signals[0].reasons
    assert report.signals[0].priority_score > report.signals[1].priority_score
    assert report.dashboard_cards and report.dashboard_cards[0]["extra"]["topic"] == "trust"


def test_domain_whitelist_registry_validates_actions(tmp_path: Path) -> None:
    config_path = tmp_path / "whitelist.yaml"
    config_path.write_text(
        """
domains:
  research:
    allowed_actions: ["search", "summarize"]
    approval_required: true
    sandbox_profile: research
    templates: ["baseline", "fast-track"]
"""
    )

    registry = DomainWhitelistRegistry.from_config(config_path)
    entry = registry.validate_action("research", "search")
    assert entry.sandbox_profile == "research"
    with pytest.raises(ValueError):
        registry.validate_action("research", "deploy")

    api = DomainWhitelistAPI(registry)
    api.request_domain(
        {
            "domain": "partner_repo",
            "allowed_actions": ["search"],
            "approval_required": True,
            "sandbox_profile": "code",
            "templates": [],
            "max_parallel_jobs": 1,
            "tags": ["pending"],
            "documentation": [],
            "repositories": [],
            "datasets": [],
        },
        requested_by="guardian",
        justification="Need repo access",
    )
    assert "partner_repo" in registry.list_pending()
    registry.approve_pending_domain("partner_repo", "governance", "APPROVED-1")
    assert "partner_repo" in registry.list_domains()


def test_learning_job_queue_enforces_backpressure() -> None:
    queue = LearningJobQueue(capacity=1)
    job = GovernedLearningJob(
        job_id="job-1",
        domain="research",
        action="search",
        payload={},
        allow_network=False,
        sandbox_checks=["unit_tests"],
        approved_by=None,
        priority=0.5,
    )
    queue.enqueue(job)
    with pytest.raises(RuntimeError):
        queue.enqueue(job)
    metrics = queue.metrics()
    assert metrics["pending"] == 1


def test_world_model_manager_tracks_versions_and_rollbacks() -> None:
    manager = WorldModelUpdateManager()
    update_one = manager.apply_update(
        {
            "source": "unit",
            "entries": [{"topic": "rag", "content": "baseline", "confidence": 0.7}],
            "validators": ["guardian"],
        }
    )
    assert update_one["version"] == 1

    update_two = manager.apply_update(
        {
            "source": "unit",
            "entries": [{"topic": "rag", "content": "upgrade", "confidence": 0.9}],
            "validators": ["guardian", "self_heal"],
        }
    )
    assert update_two["version"] == 2
    manager.rollback_to_version(1)
    assert manager.current_version == 1
    assert manager.visualize()["nodes"][0]["revision"] >= 1
    assert manager.audit_log()[-1]["event"] == "rollback"


def test_safe_mode_controller_backoff_and_toggle() -> None:
    controller = SafeModeLearningController(safe_mode=True, max_retries=3, base_backoff=2)
    job = GovernedLearningJob(
        job_id="job",
        domain="docs",
        action="search",
        payload={},
        allow_network=True,
        sandbox_checks=[],
        approved_by=None,
        priority=0.3,
    )
    with pytest.raises(RuntimeError):
        controller.enforce(job)
    job.allow_network = False
    controller.toggle(False)
    controller.enforce(job)
    controller.record_failure(job.job_id, "timeout")
    assert controller.should_retry(job)
    assert controller.compute_backoff(job) >= 2


def test_governed_learning_orchestrator_enforces_approval_and_safe_mode() -> None:
    entry = DomainWhitelistEntry(
        domain="research",
        allowed_actions=["search"],
        approval_required=True,
        sandbox_profile="research",
        templates=["baseline"],
        tags=["ml"],
    )
    registry = DomainWhitelistRegistry([entry])
    queue = LearningJobQueue(capacity=3)
    sandbox = SandboxVerifier(required_checks=["unit_tests"])
    approvals = ApprovalGate()
    safe_mode = SafeModeLearningController(safe_mode=True)
    world_model = WorldModelUpdateManager()
    dashboard = LearningJobDashboard()
    simulation = LearningSimulationFramework()
    orchestrator = GovernedLearningOrchestrator(
        registry,
        queue,
        sandbox,
        approvals,
        safe_mode,
        world_model,
        dashboard,
        simulation,
    )

    with pytest.raises(RuntimeError):
        orchestrator.submit_job(
            {
                "domain": "research",
                "action": "search",
                "approved_by": "guardian",
                "approval_token": "APPROVED-1",
                "allow_network": True,
                "sandbox_checks": ["unit_tests"],
            }
        )

    safe_mode.safe_mode = False
    job = orchestrator.submit_job(
        {
            "domain": "research",
            "action": "search",
            "approved_by": "guardian",
            "approval_token": "APPROVED-1",
            "allow_network": False,
            "sandbox_checks": ["unit_tests"],
            "priority": 0.9,
            "world_model_update": {
                "source": "research_bot",
                "entries": [{"topic": "trust", "content": "playbook", "confidence": 0.8}],
            },
        }
    )
    assert job.job_id

    result = orchestrator.process_next_job()
    assert result and result["status"] == "success"
    snapshot = orchestrator.dashboard_snapshot()
    assert snapshot["world_model_version"] == 1
    assert snapshot["completed_jobs"] == 1
    assert "pending" in snapshot and snapshot["pending"] == 0
