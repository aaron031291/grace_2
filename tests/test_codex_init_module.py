import asyncio
from pathlib import Path

import pytest

from backend.codex.codex_init_module import (
    AgentIdentityDriftAnalyzer,
    CodexAnalysisDispatcher,
    CodexConfigParser,
    CodexHookTracer,
    CodexInitModule,
    CodexIntelligenceFlowValidator,
    CodexLoopAuditLoader,
    CodeEvolutionAdvisor,
    DEFAULT_CODEX_CONFIG,
)
from backend.event_bus import Event, EventBus, EventType


def test_codex_config_parser_merges_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "codex.yaml"
    config_path.write_text(
        """
loops:
  - name: custom_loop
    module: backend.custom
    entrypoint: Custom
    description: Custom loop
    expected_feedback: false
    telemetry_keys: [custom_metric]
analysis:
  emit_reports: false
"""
    )

    parser = CodexConfigParser(config_path=config_path)
    config = parser.load()

    assert any(loop["name"] == "custom_loop" for loop in config["loops"])
    # Ensure defaults are still present
    assert config["analysis"]["default_runtime_depth"] == DEFAULT_CODEX_CONFIG["analysis"][
        "default_runtime_depth"
    ]
    assert config["analysis"]["emit_reports"] is False


def test_codex_loop_loader_builds_report() -> None:
    parser = CodexConfigParser(config_path=None, defaults={"loops": DEFAULT_CODEX_CONFIG["loops"]})
    loader = CodexLoopAuditLoader(parser)

    loop_states = {
        "memory_core": {
            "drift_score": 0.1,
            "feedback_active": True,
            "last_heartbeat": "2024-01-01T00:00:00Z",
            "write_latency_ms": 12,
        },
        "trust_framework": {
            "drift_score": 0.55,
            "feedback_active": True,
            "last_heartbeat": "2024-01-01T00:00:05Z",
        },
    }

    report = loader.build_report(loop_states=loop_states)

    assert report.summary["total_loops"] == len(DEFAULT_CODEX_CONFIG["loops"])
    statuses = {obs.loop.name: obs.status for obs in report.observations}
    assert statuses["memory_core"] == "healthy"
    assert statuses["trust_framework"] == "critical"


def test_codex_intelligence_flow_validator_reports_missing_fields() -> None:
    contracts = [
        {
            "name": "mldl_to_memory",
            "source": "mldl",
            "target": "memory_core",
            "required_fields": ["last_insight"],
        }
    ]
    validator = CodexIntelligenceFlowValidator(contracts)

    report = validator.validate(
        flow_inputs={
            "mldl_to_memory": {"latency_ms": 6000, "latency_budget_ms": 1000},
        }
    )

    obs = report.observations[0]
    assert obs.status == "warning"
    assert any("Missing field" in issue for issue in obs.issues)
    assert any("Latency budget" in issue for issue in obs.issues)


def test_agent_identity_drift_analyzer_flags_unknown_components() -> None:
    bus = EventBus()
    event = Event(event_type=EventType.MEMORY_UPDATE, source="rogue::unit::agent", data={})
    bus.event_log.append(event)

    analyzer = AgentIdentityDriftAnalyzer(
        event_bus_instance=bus,
        identity_config={
            "canonical_signature": "component::subsystem::agent",
            "allowed_components": ["trusted"],
        },
    )

    report = analyzer.build_report()
    assert report.summary["drift_events"] == 1
    assert report.drift_events[0].reason.startswith("unknown_component")


def test_code_evolution_advisor_detects_placeholders(tmp_path: Path) -> None:
    file_path = tmp_path / "module.py"
    file_path.write_text("""\n# sample\ndef foo():\n    pass\n""")

    advisor = CodeEvolutionAdvisor(
        targets=[{"path": file_path.name, "max_lines": 10, "placeholder_markers": ["pass"]}],
        repo_root=tmp_path,
    )

    report = advisor.analyze()
    assert report.summary["needs_attention"] == 1
    assert report.suggestions[0].placeholder_hits


def test_codex_hook_tracer_records_subscribers() -> None:
    bus = EventBus()

    async def subscriber(_: Event) -> None:
        return None

    bus.subscribe(EventType.AGENT_ACTION, subscriber)
    asyncio.run(
        bus.publish(
            Event(
                event_type=EventType.AGENT_ACTION,
                source="tests.codex",
                data={"action": "ping"},
            )
        )
    )

    tracer = CodexHookTracer(
        event_bus_instance=bus,
        hook_expectations={
            EventType.AGENT_ACTION.value: {
                "expected_subscribers": [
                    "tests.test_codex_init_module.test_codex_hook_tracer_records_subscribers.<locals>.subscriber"
                ],
                "payload_contract": {"required_keys": ["action"]},
            }
        },
    )

    integrity_map = tracer.build_trace()
    agent_action_entry = next(
        hook for hook in integrity_map.hooks if hook.event_type == EventType.AGENT_ACTION.value
    )
    assert agent_action_entry.missing_subscribers == []
    assert "tests.codex" in agent_action_entry.recent_emitters


def test_codex_init_module_bootstrap_runs_dispatcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bus = EventBus()
    config_file = tmp_path / "codex.yaml"
    config_file.write_text(
        """
analysis:
  emit_reports: true
loops: []
hook_expectations: {}
intelligence_links:
  - name: sample
    source: a
    target: b
    required_fields: ["field"]
identity_tracking:
  canonical_signature: component::subsystem::agent
  allowed_components: [component]
evolution_targets:
  - path: tests/test_codex_init_module.py
    max_lines: 1000
    placeholder_markers: ["TODO"]
"""
    )

    init_module = CodexInitModule(event_bus_instance=bus, config_path=config_file, repo_root=Path.cwd())

    result = init_module.bootstrap(
        loop_states={
            "memory_core": {"drift_score": 0.05, "feedback_active": True, "last_heartbeat": "now"}
        },
        flow_inputs={"sample": {"field": "ok"}},
        event_log=[{"event_id": "1", "source": "component::sub::agent", "timestamp": "now"}],
    )

    assert "loop_drift_report" in result
    assert "hook_integrity_map" in result
    assert "intelligence_flow_report" in result
    assert "identity_drift_report" in result
    assert "code_evolution_report" in result

    dispatcher = CodexAnalysisDispatcher(
        init_module.loop_loader,
        init_module.hook_tracer,
        init_module.flow_validator,
        init_module.identity_analyzer,
        init_module.evolution_advisor,
    )
    rerun = dispatcher.run_all()
    assert rerun["hook_integrity_map"]["hooks"]
