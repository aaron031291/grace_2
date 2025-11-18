"""Codex initialization module.

This module provides the scaffolding for CODEx (Cognitive Operations & Diagnostic
Executor). It wires together:

* A configuration parser so Codex can operate deterministically in CI/offline mode
* A loop audit loader that understands the key recursive systems Grace relies on
* A hook tracer that inspects the event bus to ensure agentic modules are registered
* An analysis dispatcher that produces baseline reports Codex can build on
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import json
import os

import yaml

from backend.event_bus import Event, EventBus, EventType, event_bus as global_event_bus

DEFAULT_CODEX_CONFIG: Dict[str, Any] = {
    "loops": [
        {
            "name": "memory_core",
            "module": "backend.memory",
            "entrypoint": "MemoryCore",
            "description": "Ensures memory ingest/writeback feedback loop remains recursive",
            "expected_feedback": True,
            "telemetry_keys": ["last_heartbeat", "drift_score", "write_latency_ms"],
        },
        {
            "name": "trust_framework",
            "module": "backend.trust_framework",
            "entrypoint": "TrustFramework",
            "description": "Evaluates trust/confidence loops before governance actions",
            "expected_feedback": True,
            "telemetry_keys": ["trust_score", "confidence_score"],
        },
        {
            "name": "governance_core",
            "module": "backend.governance",
            "entrypoint": "GovernanceCore",
            "description": "Approval + policy evaluation feedback loop",
            "expected_feedback": True,
            "telemetry_keys": ["pending_approvals", "policy_violations"],
        },
        {
            "name": "mldl_intelligence",
            "module": "backend.learning",
            "entrypoint": "LearningIntelligenceLoop",
            "description": "MLDL analytics to memory routing loop",
            "expected_feedback": True,
            "telemetry_keys": ["queued_jobs", "success_rate"],
        },
        {
            "name": "mission_orchestrator",
            "module": "backend.orchestration",
            "entrypoint": "MissionOrchestrator",
            "description": "Action planning / execution loop",
            "expected_feedback": True,
            "telemetry_keys": ["active_missions", "loop_iterations"],
        },
    ],
    "hook_expectations": {
        EventType.AGENT_ACTION.value: {
            "expected_publishers": [
                "backend.autonomy.autonomous_executor.AutonomousExecutor",
                "backend.missions.mission_control.MissionControl",
            ],
            "expected_subscribers": [
                "backend.guardian.guardian_agent.GuardianAgent",
                "backend.self_heal.self_heal_coordinator.SelfHealCoordinator",
            ],
            "payload_contract": {"required_keys": ["action", "actor", "metadata"]},
        },
        EventType.MEMORY_UPDATE.value: {
            "expected_publishers": [
                "backend.memory.memory_services.MemoryWriteService",
                "backend.learning.ingestion.MemoryIngestionAgent",
            ],
            "expected_subscribers": [
                "backend.world_model.world_model_controller.WorldModelController",
                "backend.metrics_service.MemoryMetricsAdapter",
            ],
            "payload_contract": {"required_keys": ["memory_id", "source", "confidence"]},
        },
    },
    "analysis": {
        "default_runtime_depth": 128,
        "emit_reports": True,
        "offline_mode": True,
    },
    "identity_tracking": {
        "canonical_signature": "component::subsystem::agent",
        "event_source": "codex_init_module",
        "fallback_component": "codex",
        "allowed_components": [
            "memory_core",
            "guardian",
            "governance",
            "mldl",
            "mission_orchestrator",
            "codex",
        ],
    },
    "intelligence_links": [
        {
            "name": "mldl_to_memory",
            "source": "mldl_intelligence",
            "target": "memory_core",
            "required_fields": ["last_insight", "memory_updates"],
            "description": "Ensures MLDL insights propagate into memory writes.",
        },
        {
            "name": "memory_to_governance",
            "source": "memory_core",
            "target": "governance_core",
            "required_fields": ["policy_inputs", "approval_required"],
            "description": "Validates governance sees memory changes.",
        },
        {
            "name": "governance_to_action",
            "source": "governance_core",
            "target": "mission_orchestrator",
            "required_fields": ["approval_status", "action_contract"],
            "description": "Confirms approved intents get routed to orchestration.",
        },
    ],
    "evolution_targets": [
        {
            "path": "backend/codex/codex_init_module.py",
            "max_lines": 600,
            "placeholder_markers": ["TODO", "FIXME", "pass", "NotImplemented"],
        },
        {
            "path": "backend/event_bus.py",
            "max_lines": 400,
            "placeholder_markers": ["TODO", "FIXME"],
        },
    ],
}


@dataclass
class LoopDefinition:
    name: str
    module: str
    entrypoint: str
    description: str = ""
    expected_feedback: bool = True
    telemetry_keys: List[str] = field(default_factory=list)


@dataclass
class LoopDriftObservation:
    loop: LoopDefinition
    status: str
    drift_score: float
    feedback_active: bool
    notes: str = ""
    telemetry: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop": {
                "name": self.loop.name,
                "module": self.loop.module,
                "entrypoint": self.loop.entrypoint,
                "description": self.loop.description,
            },
            "status": self.status,
            "drift_score": self.drift_score,
            "feedback_active": self.feedback_active,
            "notes": self.notes,
            "telemetry": self.telemetry,
        }


@dataclass
class LoopDriftReport:
    generated_at: str
    observations: List[LoopDriftObservation]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "observations": [obs.to_dict() for obs in self.observations],
            "summary": self.summary,
        }


@dataclass
class HookTraceEntry:
    event_type: str
    subscribers: List[str]
    missing_subscribers: List[str]
    unexpected_subscribers: List[str]
    recent_emitters: List[str]
    payload_contract: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "subscribers": self.subscribers,
            "missing_subscribers": self.missing_subscribers,
            "unexpected_subscribers": self.unexpected_subscribers,
            "recent_emitters": self.recent_emitters,
            "payload_contract": self.payload_contract,
        }


@dataclass
class SystemHookIntegrityMap:
    generated_at: str
    hooks: List[HookTraceEntry]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "hooks": [hook.to_dict() for hook in self.hooks],
        }


@dataclass
class IntelligenceLinkContract:
    name: str
    source: str
    target: str
    required_fields: List[str]
    description: str = ""


@dataclass
class IntelligenceLinkObservation:
    contract: IntelligenceLinkContract
    status: str
    issues: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract": {
                "name": self.contract.name,
                "source": self.contract.source,
                "target": self.contract.target,
                "required_fields": self.contract.required_fields,
                "description": self.contract.description,
            },
            "status": self.status,
            "issues": self.issues,
            "metadata": self.metadata,
        }


@dataclass
class IntelligenceFlowReport:
    generated_at: str
    observations: List[IntelligenceLinkObservation]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "observations": [obs.to_dict() for obs in self.observations],
            "summary": self.summary,
        }


@dataclass
class IdentityDriftEntry:
    event_id: str
    source: str
    reason: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source": self.source,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentIdentityDriftReport:
    generated_at: str
    drift_events: List[IdentityDriftEntry]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "drift_events": [entry.to_dict() for entry in self.drift_events],
            "summary": self.summary,
        }


@dataclass
class EvolutionSuggestion:
    path: str
    exists: bool
    line_count: int
    placeholder_hits: List[Tuple[int, str]]
    needs_attention: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "exists": self.exists,
            "line_count": self.line_count,
            "placeholder_hits": self.placeholder_hits,
            "needs_attention": self.needs_attention,
            "notes": self.notes,
        }


@dataclass
class CodeEvolutionReport:
    generated_at: str
    suggestions: List[EvolutionSuggestion]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "suggestions": [suggestion.to_dict() for suggestion in self.suggestions],
            "summary": self.summary,
        }


class CodexConfigParser:
    """Loads Codex configuration with sensible defaults."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config_path = config_path or Path("config/codex_config.yaml")
        self.defaults = defaults or DEFAULT_CODEX_CONFIG
        self._cached_config: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        if self._cached_config is not None:
            return self._cached_config

        data: Dict[str, Any] = {}
        if self.config_path and self.config_path.exists():
            data = self._parse_file(self.config_path)

        merged = self._merge_dicts(self.defaults, data)
        self._cached_config = merged
        return merged

    def invalidate_cache(self) -> None:
        self._cached_config = None

    def _parse_file(self, path: Path) -> Dict[str, Any]:
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(path.read_text()) or {}
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text())

        raise ValueError(f"Unsupported Codex config format: {path.suffix}")

    def _merge_dicts(self, defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for key, value in defaults.items():
            if isinstance(value, dict):
                merged[key] = value.copy()
            elif isinstance(value, list):
                merged[key] = list(value)
            else:
                merged[key] = value

        for key, value in overrides.items():
            if key not in merged:
                merged[key] = value
                continue

            if isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = self._merge_dicts(merged[key], value)
            else:
                merged[key] = value

        return merged


class CodexLoopAuditLoader:
    """Builds loop drift reports based on configured definitions."""

    def __init__(self, config_parser: CodexConfigParser) -> None:
        self.config_parser = config_parser

    def load_definitions(self) -> List[LoopDefinition]:
        config = self.config_parser.load()
        loops: List[LoopDefinition] = []
        for loop in config.get("loops", []):
            loops.append(
                LoopDefinition(
                    name=loop.get("name", "unknown"),
                    module=loop.get("module", ""),
                    entrypoint=loop.get("entrypoint", ""),
                    description=loop.get("description", ""),
                    expected_feedback=loop.get("expected_feedback", True),
                    telemetry_keys=loop.get("telemetry_keys", []),
                )
            )
        return loops

    def build_report(self, loop_states: Optional[Dict[str, Dict[str, Any]]] = None) -> LoopDriftReport:
        definitions = self.load_definitions()
        loop_states = loop_states or {}
        observations: List[LoopDriftObservation] = []

        for definition in definitions:
            state = loop_states.get(definition.name, {})
            drift_score = float(state.get("drift_score", 0.0))
            feedback_active = bool(state.get("feedback_active", definition.expected_feedback))
            last_heartbeat = state.get("last_heartbeat")

            status = "healthy"
            notes = state.get("notes", "")
            if not feedback_active:
                status = "warning"
                notes = notes or "Feedback loop disabled"
            if drift_score >= 0.5:
                status = "critical"
            elif drift_score >= 0.2 and status != "critical":
                status = "warning"

            if not last_heartbeat:
                status = "unknown"
                notes = notes or "No telemetry heartbeat detected"

            telemetry = {key: state.get(key) for key in definition.telemetry_keys if key in state}
            if last_heartbeat:
                telemetry["last_heartbeat"] = last_heartbeat

            observations.append(
                LoopDriftObservation(
                    loop=definition,
                    status=status,
                    drift_score=drift_score,
                    feedback_active=feedback_active,
                    notes=notes,
                    telemetry=telemetry,
                )
            )

        summary = {
            "total_loops": len(observations),
            "critical": sum(1 for obs in observations if obs.status == "critical"),
            "warning": sum(1 for obs in observations if obs.status == "warning"),
            "healthy": sum(1 for obs in observations if obs.status == "healthy"),
            "unknown": sum(1 for obs in observations if obs.status == "unknown"),
        }

        return LoopDriftReport(
            generated_at=datetime.utcnow().isoformat(),
            observations=observations,
            summary=summary,
        )


class CodexHookTracer:
    """Produces a hook integrity map from the event bus."""

    def __init__(
        self,
        event_bus_instance: EventBus,
        hook_expectations: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.event_bus = event_bus_instance
        self.hook_expectations = hook_expectations or {}

    def build_trace(self, recent_limit: int = 5) -> SystemHookIntegrityMap:
        hooks: List[HookTraceEntry] = []
        for event_type in EventType:
            callbacks = self.event_bus.subscribers.get(event_type, [])
            subscriber_signatures = [self._describe_callback(callback) for callback in callbacks]

            expectation = self.hook_expectations.get(event_type.value, {})
            expected = set(expectation.get("expected_subscribers", []))
            present = set(subscriber_signatures)
            missing = sorted(expected - present)
            unexpected = sorted(present - expected)

            recent_events = self.event_bus.get_recent_events(limit=recent_limit, event_type=event_type)
            emitters = sorted({event["source"] for event in recent_events})

            hooks.append(
                HookTraceEntry(
                    event_type=event_type.value,
                    subscribers=subscriber_signatures,
                    missing_subscribers=missing,
                    unexpected_subscribers=unexpected,
                    recent_emitters=emitters,
                    payload_contract=expectation.get("payload_contract", {}),
                )
            )

        return SystemHookIntegrityMap(
            generated_at=datetime.utcnow().isoformat(),
            hooks=hooks,
        )

    def _describe_callback(self, callback: Any) -> str:
        module = getattr(callback, "__module__", "unknown")
        qualname = getattr(callback, "__qualname__", repr(callback))
        return f"{module}.{qualname}"


class CodexIntelligenceFlowValidator:
    """Validates that intelligence flows traverse all required steps."""

    def __init__(self, contracts: Iterable[Dict[str, Any]]) -> None:
        self.contracts = [
            IntelligenceLinkContract(
                name=contract.get("name", "unknown"),
                source=contract.get("source", ""),
                target=contract.get("target", ""),
                required_fields=contract.get("required_fields", []),
                description=contract.get("description", ""),
            )
            for contract in contracts
        ]

    def validate(
        self,
        flow_inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        loop_states: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> IntelligenceFlowReport:
        flow_inputs = flow_inputs or {}
        loop_states = loop_states or {}
        observations: List[IntelligenceLinkObservation] = []

        for contract in self.contracts:
            raw_metadata = flow_inputs.get(contract.name) or loop_states.get(contract.target, {})
            issues: List[str] = []
            metadata = dict(raw_metadata)
            status = "healthy"

            if not raw_metadata:
                status = "critical"
                issues.append("No telemetry for contract")

            for field in contract.required_fields:
                if field not in raw_metadata:
                    issues.append(f"Missing field: {field}")

            if issues and status != "critical":
                status = "warning"

            if raw_metadata and raw_metadata.get("latency_ms"):
                latency = raw_metadata["latency_ms"]
                metadata["latency_ms"] = latency
                if latency and latency > raw_metadata.get("latency_budget_ms", 5000):
                    issues.append("Latency budget exceeded")
                    status = "warning"

            observations.append(
                IntelligenceLinkObservation(
                    contract=contract,
                    status=status,
                    issues=issues,
                    metadata=metadata,
                )
            )

        summary = {
            "total_contracts": len(observations),
            "critical": sum(1 for obs in observations if obs.status == "critical"),
            "warning": sum(1 for obs in observations if obs.status == "warning"),
            "healthy": sum(1 for obs in observations if obs.status == "healthy"),
        }

        return IntelligenceFlowReport(
            generated_at=datetime.utcnow().isoformat(),
            observations=observations,
            summary=summary,
        )


class AgentIdentityDriftAnalyzer:
    """Evaluates whether emitted events follow the canonical identity contract."""

    def __init__(self, event_bus_instance: EventBus, identity_config: Dict[str, Any]) -> None:
        self.event_bus = event_bus_instance
        self.identity_config = identity_config

    def build_report(self, event_log: Optional[List[Dict[str, Any]]] = None) -> AgentIdentityDriftReport:
        canonical = self.identity_config.get("canonical_signature", "")
        allowed_components = set(self.identity_config.get("allowed_components", []))
        delimiter = "::" if "::" in canonical else ":"

        if event_log is None:
            event_log = self.event_bus.get_recent_events(limit=250)

        drift_entries: List[IdentityDriftEntry] = []
        for event in event_log:
            source = event.get("source", "")
            reason = self._detect_drift(source, delimiter, allowed_components)
            if reason:
                drift_entries.append(
                    IdentityDriftEntry(
                        event_id=event.get("event_id", "unknown"),
                        source=source,
                        reason=reason,
                        timestamp=event.get("timestamp", datetime.utcnow().isoformat()),
                    )
                )

        summary = {
            "total_events": len(event_log),
            "drift_events": len(drift_entries),
            "drift_ratio": (len(drift_entries) / len(event_log)) if event_log else 0.0,
        }

        return AgentIdentityDriftReport(
            generated_at=datetime.utcnow().isoformat(),
            drift_events=drift_entries,
            summary=summary,
        )

    def _detect_drift(self, source: str, delimiter: str, allowed_components: Iterable[str]) -> Optional[str]:
        if not source:
            return "missing_source"

        segments = source.split(delimiter)
        if len(segments) < 3:
            return "incomplete_signature"

        component = segments[0]
        if allowed_components and component not in allowed_components:
            return f"unknown_component:{component}"

        return None


class CodeEvolutionAdvisor:
    """Scans configured files for placeholder code and drift risks."""

    def __init__(self, targets: Iterable[Dict[str, Any]], repo_root: Optional[Path] = None) -> None:
        self.targets = list(targets)
        self.repo_root = repo_root or Path(os.getcwd())

    def analyze(self) -> CodeEvolutionReport:
        suggestions: List[EvolutionSuggestion] = []
        for target in self.targets:
            suggestions.append(self._inspect_target(target))

        summary = {
            "total_targets": len(suggestions),
            "needs_attention": sum(1 for suggestion in suggestions if suggestion.needs_attention),
        }

        return CodeEvolutionReport(
            generated_at=datetime.utcnow().isoformat(),
            suggestions=suggestions,
            summary=summary,
        )

    def _inspect_target(self, target: Dict[str, Any]) -> EvolutionSuggestion:
        rel_path = target.get("path", "")
        placeholder_markers = target.get("placeholder_markers", [])
        max_lines = int(target.get("max_lines", 500))
        path = (self.repo_root / rel_path).resolve()
        repo_root_resolved = self.repo_root.resolve()
        if repo_root_resolved not in path.parents and path != repo_root_resolved:
            # Prevent scanning paths outside of repo root
            return EvolutionSuggestion(
                path=rel_path,
                exists=False,
                line_count=0,
                placeholder_hits=[],
                needs_attention=True,
                notes="Path escapes repository root",
            )

        if not path.exists():
            return EvolutionSuggestion(
                path=rel_path,
                exists=False,
                line_count=0,
                placeholder_hits=[],
                needs_attention=True,
                notes="File missing",
            )

        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        placeholder_hits = self._collect_placeholders(lines, placeholder_markers)
        needs_attention = bool(placeholder_hits) or len(lines) > max_lines
        notes_parts = []
        if len(lines) > max_lines:
            notes_parts.append(f"line_budget_exceeded:{len(lines)}/{max_lines}")
        if placeholder_hits:
            notes_parts.append(f"placeholder_hits:{len(placeholder_hits)}")
        notes = ",".join(notes_parts) if notes_parts else "healthy"

        return EvolutionSuggestion(
            path=rel_path,
            exists=True,
            line_count=len(lines),
            placeholder_hits=placeholder_hits,
            needs_attention=needs_attention,
            notes=notes,
        )

    def _collect_placeholders(
        self,
        lines: List[str],
        markers: Iterable[str],
    ) -> List[Tuple[int, str]]:
        hits: List[Tuple[int, str]] = []
        markers = list(markers)
        for idx, line in enumerate(lines, start=1):
            if any(marker in line for marker in markers):
                hits.append((idx, line.strip()))
        return hits


class CodexAnalysisDispatcher:
    """Runs Codex analyses and returns structured payloads."""

    def __init__(
        self,
        loop_loader: CodexLoopAuditLoader,
        hook_tracer: CodexHookTracer,
        flow_validator: CodexIntelligenceFlowValidator,
        identity_analyzer: AgentIdentityDriftAnalyzer,
        evolution_advisor: CodeEvolutionAdvisor,
    ) -> None:
        self.loop_loader = loop_loader
        self.hook_tracer = hook_tracer
        self.flow_validator = flow_validator
        self.identity_analyzer = identity_analyzer
        self.evolution_advisor = evolution_advisor

    def run_all(
        self,
        loop_states: Optional[Dict[str, Dict[str, Any]]] = None,
        flow_inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        event_log: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        loop_report = self.loop_loader.build_report(loop_states=loop_states)
        hook_map = self.hook_tracer.build_trace()
        flow_report = self.flow_validator.validate(flow_inputs=flow_inputs, loop_states=loop_states)
        identity_report = self.identity_analyzer.build_report(event_log=event_log)
        evolution_report = self.evolution_advisor.analyze()

        return {
            "loop_drift_report": loop_report.to_dict(),
            "hook_integrity_map": hook_map.to_dict(),
            "intelligence_flow_report": flow_report.to_dict(),
            "identity_drift_report": identity_report.to_dict(),
            "code_evolution_report": evolution_report.to_dict(),
        }


class CodexInitModule:
    """Entry-point used by Grace to bootstrap Codex."""

    def __init__(
        self,
        event_bus_instance: Optional[EventBus] = None,
        config_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
    ) -> None:
        self.config_parser = CodexConfigParser(config_path=config_path)
        self.event_bus = event_bus_instance or global_event_bus
        self.repo_root = repo_root or Path(os.getcwd())

        config = self.config_parser.load()
        self.loop_loader = CodexLoopAuditLoader(self.config_parser)
        self.hook_tracer = CodexHookTracer(
            event_bus_instance=self.event_bus,
            hook_expectations=config.get("hook_expectations", {}),
        )
        self.flow_validator = CodexIntelligenceFlowValidator(config.get("intelligence_links", []))
        self.identity_analyzer = AgentIdentityDriftAnalyzer(
            event_bus_instance=self.event_bus,
            identity_config=config.get("identity_tracking", {}),
        )
        self.evolution_advisor = CodeEvolutionAdvisor(
            targets=config.get("evolution_targets", []),
            repo_root=self.repo_root,
        )
        self.dispatcher = CodexAnalysisDispatcher(
            self.loop_loader,
            self.hook_tracer,
            self.flow_validator,
            self.identity_analyzer,
            self.evolution_advisor,
        )

    def bootstrap(
        self,
        loop_states: Optional[Dict[str, Dict[str, Any]]] = None,
        flow_inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        event_log: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Run the baseline Codex analyses and return structured reports."""
        return self.dispatcher.run_all(
            loop_states=loop_states,
            flow_inputs=flow_inputs,
            event_log=event_log,
        )

    def reload_config(self) -> Dict[str, Any]:
        """Force Codex to reload its configuration and propagate updates."""
        self.config_parser.invalidate_cache()
        config = self.config_parser.load()
        self.hook_tracer.hook_expectations = config.get("hook_expectations", {})
        self.flow_validator = CodexIntelligenceFlowValidator(config.get("intelligence_links", []))
        self.identity_analyzer = AgentIdentityDriftAnalyzer(
            event_bus_instance=self.event_bus,
            identity_config=config.get("identity_tracking", {}),
        )
        self.evolution_advisor = CodeEvolutionAdvisor(
            targets=config.get("evolution_targets", []),
            repo_root=self.repo_root,
        )
        self.dispatcher = CodexAnalysisDispatcher(
            self.loop_loader,
            self.hook_tracer,
            self.flow_validator,
            self.identity_analyzer,
            self.evolution_advisor,
        )
        return config

    async def emit_reports(
        self,
        loop_states: Optional[Dict[str, Dict[str, Any]]] = None,
        flow_inputs: Optional[Dict[str, Dict[str, Any]]] = None,
        event_log: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Publish Codex analysis events on the event bus for observability."""
        config = self.config_parser.load()
        if not config.get("analysis", {}).get("emit_reports", False):
            return

        payload = self.bootstrap(
            loop_states=loop_states,
            flow_inputs=flow_inputs,
            event_log=event_log,
        )
        report_event = Event(
            event_type=EventType.VERIFICATION_RESULT,
            source=config.get("identity_tracking", {}).get("event_source", "codex"),
            data={"codex_report": payload},
        )
        await self.event_bus.publish(report_event)
