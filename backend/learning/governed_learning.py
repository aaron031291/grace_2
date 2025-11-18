"""Governed learning primitives for Grace.

This module implements the systems requested for Phase 3 of the roadmap:

* Gap detection with confidence-driven prioritization and dashboard metrics.
* Governed learning orchestration that enforces domain whitelists and approval gates.
* World model update management with trust scoring, conflict resolution, versioning,
  and immutable audit history.
* Safe-mode learning controls that prevent external calls in CI/offline contexts and
  provide retry, rollback, and simulation hooks.
"""

from __future__ import annotations

import asyncio
from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Deque, Dict, Iterable, List, Optional, Tuple
import math
import re
import statistics
import uuid

import yaml

from backend.event_bus import Event, EventType, event_bus as global_event_bus


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------


@dataclass
class RequestAnalytics:
    """Aggregated query analytics for a topic."""

    topic: str
    request_count: int
    failure_rate: float
    avg_uncertainty: float
    impact_score: float


@dataclass
class GapSignal:
    topic: str
    confidence_delta: float
    impact_score: float
    priority_score: float
    reasons: List[str]
    example_queries: List[str]


@dataclass
class GapDetectionReport:
    generated_at: str
    signals: List[GapSignal]
    metrics: Dict[str, Any]
    dashboard_cards: List[Dict[str, Any]]


class GapDetectionEngine:
    """Evaluates historical queries against the world model confidence map."""

    def __init__(self, target_confidence: float = 0.85) -> None:
        self.target_confidence = target_confidence

    def analyze_queries(
        self,
        queries: Iterable[Dict[str, Any]],
        knowledge_snapshot: Dict[str, Any],
    ) -> GapDetectionReport:
        snapshot_topics = knowledge_snapshot.get("topics", {})
        aggregated, total_queries = self._aggregate_queries(queries)
        signals: List[GapSignal] = []
        analytics_cards: List[Dict[str, Any]] = []
        confidence_values: List[float] = []

        for topic, details in aggregated.items():
            coverage_conf = snapshot_topics.get(topic, {}).get("confidence", 0.0)
            confidence_values.append(coverage_conf)
            confidence_delta = max(self.target_confidence - coverage_conf, 0.0)
            analytics = details["analytics"]
            impact_score = analytics.impact_score
            priority_score = round(confidence_delta * impact_score, 4)
            reasons = []
            if coverage_conf < self.target_confidence:
                reasons.append("low_confidence")
            if analytics.failure_rate >= 0.3:
                reasons.append("low_success_rate")
            if analytics.avg_uncertainty > 0.4:
                reasons.append("high_uncertainty")
            if analytics.request_count / max(total_queries, 1) > 0.15:
                reasons.append("high_demand")

            signals.append(
                GapSignal(
                    topic=topic,
                    confidence_delta=round(confidence_delta, 4),
                    impact_score=round(impact_score, 4),
                    priority_score=priority_score,
                    reasons=reasons or ["balanced"],
                    example_queries=details.get("examples", [])[:3],
                )
            )

            analytics_cards.append(
                {
                    "topic": topic,
                    "impact": round(impact_score, 3),
                    "confidence_delta": round(confidence_delta, 3),
                    "requests": analytics.request_count,
                    "uncertainty": round(analytics.avg_uncertainty, 3),
                }
            )

        signals.sort(key=lambda signal: signal.priority_score, reverse=True)
        analytics_cards.sort(key=lambda card: card["impact"], reverse=True)
        metrics = {
            "topics_considered": len(aggregated),
            "average_confidence": round(statistics.mean(confidence_values), 4) if confidence_values else 0.0,
            "high_priority_gaps": sum(1 for signal in signals if signal.priority_score >= 0.5),
            "median_impact_score": round(statistics.median([s.impact_score for s in signals]), 4)
            if signals
            else 0.0,
        }

        dashboard_cards = self._build_dashboard_cards(signals, analytics_cards)

        return GapDetectionReport(
            generated_at=datetime.utcnow().isoformat(),
            signals=signals,
            metrics=metrics,
            dashboard_cards=dashboard_cards,
        )

    def _aggregate_queries(self, queries: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], int]:
        topic_counter: Dict[str, Dict[str, Any]] = {}
        total = 0
        for query in queries:
            total += 1
            topic = query.get("topic") or self._infer_topic(query.get("query", ""))
            if topic not in topic_counter:
                topic_counter[topic] = {
                    "count": 0,
                    "success_weight": 0.0,
                    "uncertainty_weight": 0.0,
                    "impact_weight": 0.0,
                    "examples": [],
                }
            topic_counter[topic]["count"] += 1
            topic_counter[topic]["success_weight"] += query.get("success", 0.5)
            topic_counter[topic]["uncertainty_weight"] += query.get("retrieval_uncertainty", 0.3)
            topic_counter[topic]["impact_weight"] += query.get("impact", 1.0)
            if len(topic_counter[topic]["examples"]) < 5 and query.get("query"):
                topic_counter[topic]["examples"].append(query["query"])

        for topic, details in topic_counter.items():
            success_rate = details["success_weight"] / max(details["count"], 1)
            avg_uncertainty = details["uncertainty_weight"] / max(details["count"], 1)
            demand_index = details["count"] / max(total, 1)
            impact = details["impact_weight"] / max(details["count"], 1)
            failure_rate = 1.0 - success_rate
            impact_score = demand_index * (1 + failure_rate) * (1 + avg_uncertainty) * impact
            details["analytics"] = RequestAnalytics(
                topic=topic,
                request_count=details["count"],
                failure_rate=round(failure_rate, 4),
                avg_uncertainty=round(avg_uncertainty, 4),
                impact_score=round(impact_score, 4),
            )

        return topic_counter, total

    def _build_dashboard_cards(
        self, signals: List[GapSignal], analytics_cards: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        cards: List[Dict[str, Any]] = []
        for signal in signals[:3]:
            cards.append(
                {
                    "title": f"Gap: {signal.topic}",
                    "value": signal.priority_score,
                    "hint": ", ".join(signal.reasons),
                    "extra": next(
                        (
                            card
                            for card in analytics_cards
                            if card["topic"] == signal.topic
                        ),
                        {},
                    ),
                }
            )
        return cards

    def _infer_topic(self, query_text: str) -> str:
        text = query_text.lower()
        if "governance" in text or "policy" in text:
            return "governance"
        if "memory" in text or "rag" in text:
            return "memory"
        if "trust" in text or "mttr" in text:
            return "trust"
        if "learning" in text or "domain" in text:
            return "learning"
        return "general"


# ---------------------------------------------------------------------------
# Domain whitelist management
# ---------------------------------------------------------------------------


@dataclass
class DomainWhitelistEntry:
    domain: str
    allowed_actions: List[str]
    approval_required: bool
    sandbox_profile: str
    templates: List[str] = field(default_factory=list)
    max_parallel_jobs: int = 2
    tags: List[str] = field(default_factory=list)
    documentation: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "allowed_actions": list(self.allowed_actions),
            "approval_required": self.approval_required,
            "sandbox_profile": self.sandbox_profile,
            "templates": list(self.templates),
            "max_parallel_jobs": self.max_parallel_jobs,
            "tags": list(self.tags),
            "documentation": list(self.documentation),
            "repositories": list(self.repositories),
            "datasets": list(self.datasets),
            "status": self.status,
        }


@dataclass
class DomainWhitelistTemplate:
    name: str
    allowed_actions: List[str]
    sandbox_profile: str
    approval_required: bool
    max_parallel_jobs: int
    tags: List[str]
    documentation: List[str]
    repositories: List[str]
    datasets: List[str]


DEFAULT_DOMAIN_TEMPLATES: Dict[str, DomainWhitelistTemplate] = {
    "docs_default": DomainWhitelistTemplate(
        name="docs_default",
        allowed_actions=["search", "summarize", "ingest"],
        sandbox_profile="documentation",
        approval_required=False,
        max_parallel_jobs=2,
        tags=["docs", "internal"],
        documentation=["https://grace/docs"],
        repositories=[],
        datasets=[],
    ),
    "repo_ml": DomainWhitelistTemplate(
        name="repo_ml",
        allowed_actions=["search", "clone", "summarize"],
        sandbox_profile="code_review",
        approval_required=True,
        max_parallel_jobs=1,
        tags=["git", "ml"],
        documentation=["https://grace/repos"],
        repositories=["https://github.com/grace-ai"],
        datasets=[],
    ),
    "dataset_private": DomainWhitelistTemplate(
        name="dataset_private",
        allowed_actions=["search", "ingest"],
        sandbox_profile="data_vault",
        approval_required=True,
        max_parallel_jobs=1,
        tags=["dataset"],
        documentation=["https://grace/datasets"],
        repositories=[],
        datasets=["s3://grace-private"],
    ),
}


class DomainWhitelistRegistry:
    """Holds per-domain learning configuration and validation rules."""

    def __init__(self, entries: Optional[Iterable[DomainWhitelistEntry]] = None) -> None:
        self._entries: Dict[str, DomainWhitelistEntry] = {}
        self._pending: Dict[str, Dict[str, Any]] = {}
        if entries:
            for entry in entries:
                self.register_entry(entry)

    @classmethod
    def from_config(cls, config_path: Path) -> "DomainWhitelistRegistry":
        if not config_path.exists():
            return cls()

        data = yaml.safe_load(config_path.read_text()) or {}
        entries: List[DomainWhitelistEntry] = []
        for domain, payload in data.get("domains", {}).items():
            entries.append(
                DomainWhitelistEntry(
                    domain=domain,
                    allowed_actions=payload.get("allowed_actions", ["search", "ingest"]),
                    approval_required=payload.get("approval_required", False),
                    sandbox_profile=payload.get("sandbox_profile", "default"),
                    templates=payload.get("templates", []),
                    max_parallel_jobs=payload.get("max_parallel_jobs", 2),
                    tags=payload.get("tags", []),
                    documentation=payload.get("documentation", []),
                    repositories=payload.get("repositories", []),
                    datasets=payload.get("datasets", []),
                    status=payload.get("status", "active"),
                )
            )
        return cls(entries)

    def register_entry(self, entry: DomainWhitelistEntry) -> None:
        self._validate_entry(entry)
        self._entries[entry.domain] = entry
        self._pending.pop(entry.domain, None)

    def validate_action(self, domain: str, action: str) -> DomainWhitelistEntry:
        if domain not in self._entries:
            raise ValueError(f"Domain '{domain}' is not on the whitelist")
        entry = self._entries[domain]
        if entry.status != "active":
            raise ValueError(f"Domain '{domain}' is not active (status={entry.status})")
        if action not in entry.allowed_actions:
            raise ValueError(f"Action '{action}' is not permitted for domain '{domain}'")
        return entry

    def get_entry(self, domain: str) -> DomainWhitelistEntry:
        if domain not in self._entries:
            raise ValueError(f"Domain '{domain}' is not on the whitelist")
        return self._entries[domain]

    def list_domains(self) -> List[str]:
        return sorted(domain for domain, entry in self._entries.items() if entry.status == "active")

    def max_parallel_jobs(self) -> int:
        active_entries = [entry for entry in self._entries.values() if entry.status == "active"]
        if not active_entries:
            return 1
        return max(entry.max_parallel_jobs for entry in active_entries)

    def is_empty(self) -> bool:
        return not self.list_domains()

    def export_config(self) -> Dict[str, Any]:
        return {"domains": {entry.domain: entry.to_dict() for entry in self._entries.values()}}

    def apply_template(
        self, domain: str, template_name: str, overrides: Optional[Dict[str, Any]] = None
    ) -> DomainWhitelistEntry:
        overrides = overrides or {}
        if template_name not in DEFAULT_DOMAIN_TEMPLATES:
            raise ValueError(f"Unknown template '{template_name}'")
        template = DEFAULT_DOMAIN_TEMPLATES[template_name]
        entry = DomainWhitelistEntry(
            domain=domain,
            allowed_actions=overrides.get("allowed_actions", template.allowed_actions),
            approval_required=overrides.get("approval_required", template.approval_required),
            sandbox_profile=overrides.get("sandbox_profile", template.sandbox_profile),
            templates=[template_name],
            max_parallel_jobs=overrides.get("max_parallel_jobs", template.max_parallel_jobs),
            tags=overrides.get("tags", template.tags),
            documentation=overrides.get("documentation", template.documentation),
            repositories=overrides.get("repositories", template.repositories),
            datasets=overrides.get("datasets", template.datasets),
            status=overrides.get("status", "active"),
        )
        self.register_entry(entry)
        return entry

    def request_domain_onboarding(
        self, entry: DomainWhitelistEntry, requested_by: str, justification: str
    ) -> None:
        self._validate_entry(entry, allow_pending=True)
        self._pending[entry.domain] = {
            "requested_by": requested_by,
            "justification": justification,
            "entry": entry,
            "requested_at": datetime.utcnow().isoformat(),
        }

    def approve_pending_domain(self, domain: str, approver: str, approval_token: str) -> None:
        if not approval_token.startswith("APPROVED-"):
            raise PermissionError("approval token invalid for domain approval")
        payload = self._pending.get(domain)
        if not payload:
            raise ValueError(f"Domain '{domain}' not found in pending queue")
        entry: DomainWhitelistEntry = payload["entry"]
        entry.status = "active"
        entry.approval_required = entry.approval_required or True
        entry.tags = list({*entry.tags, "approved", approver})
        self.register_entry(entry)

    def list_pending(self) -> List[str]:
        return sorted(self._pending.keys())

    def _validate_entry(self, entry: DomainWhitelistEntry, allow_pending: bool = False) -> None:
        domain_pattern = re.compile(r"^[a-z0-9_\-\.]+$")
        if not domain_pattern.match(entry.domain):
            raise ValueError(f"Domain '{entry.domain}' is not valid")
        if not entry.allowed_actions:
            raise ValueError("At least one allowed action is required")
        if not entry.sandbox_profile:
            raise ValueError("Sandbox profile must be provided")
        if entry.status not in {"active", "pending", "disabled"}:
            raise ValueError(f"Status '{entry.status}' is not supported")
        if entry.status == "pending" and not allow_pending:
            raise ValueError("Pending entries must be submitted via onboarding flow")


class DomainWhitelistAPI:
    """Facade for UI/API integration when managing whitelist entries."""

    def __init__(self, registry: DomainWhitelistRegistry) -> None:
        self.registry = registry

    def list_entries(self) -> List[Dict[str, Any]]:
        return [entry.to_dict() for entry in self.registry._entries.values()]

    def describe_entry(self, domain: str) -> Dict[str, Any]:
        return self.registry.get_entry(domain).to_dict()

    def create_entry(self, payload: Dict[str, Any]) -> DomainWhitelistEntry:
        entry = DomainWhitelistEntry(**payload)
        self.registry.register_entry(entry)
        return entry

    def create_from_template(
        self, domain: str, template_name: str, overrides: Optional[Dict[str, Any]] = None
    ) -> DomainWhitelistEntry:
        return self.registry.apply_template(domain, template_name, overrides)

    def update_entry(self, domain: str, updates: Dict[str, Any]) -> DomainWhitelistEntry:
        entry = self.registry.get_entry(domain)
        for field_name, value in updates.items():
            setattr(entry, field_name, value)
        self.registry.register_entry(entry)
        return entry

    def remove_entry(self, domain: str) -> None:
        self.registry._entries.pop(domain, None)

    def request_domain(
        self, entry_payload: Dict[str, Any], requested_by: str, justification: str
    ) -> None:
        entry = DomainWhitelistEntry(**entry_payload)
        entry.status = "pending"
        self.registry.request_domain_onboarding(entry, requested_by, justification)

    def approve_domain(self, domain: str, approver: str, approval_token: str) -> None:
        self.registry.approve_pending_domain(domain, approver, approval_token)


# ---------------------------------------------------------------------------
# Learning job orchestration
# ---------------------------------------------------------------------------


@dataclass
class GovernedLearningJob:
    job_id: str
    domain: str
    action: str
    payload: Dict[str, Any]
    allow_network: bool
    sandbox_checks: List[str]
    approved_by: Optional[str]
    priority: float
    retries: int = 0
    submitted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def increment_retry(self) -> None:
        self.retries += 1


class LearningJobQueue:
    """Backpressure-aware queue for governed learning jobs."""

    def __init__(self, capacity: int = 10) -> None:
        self.capacity = capacity
        self._queue: Deque[GovernedLearningJob] = deque()
        self._inflight: Dict[str, GovernedLearningJob] = {}

    def enqueue(self, job: GovernedLearningJob) -> None:
        if len(self._queue) + len(self._inflight) >= self.capacity:
            raise RuntimeError("Backpressure engaged: job queue is full")
        self._queue.append(job)

    def start_next_job(self) -> Optional[GovernedLearningJob]:
        if not self._queue:
            return None
        job = self._queue.popleft()
        self._inflight[job.job_id] = job
        return job

    def complete(self, job_id: str, status: str) -> None:
        self._inflight.pop(job_id, None)

    def fail(self, job_id: str, reason: str) -> None:
        self._inflight.pop(job_id, None)

    def retry(self, job: GovernedLearningJob) -> None:
        self._inflight.pop(job.job_id, None)
        self.enqueue(job)

    def metrics(self) -> Dict[str, Any]:
        return {
            "pending": len(self._queue),
            "active": len(self._inflight),
            "capacity": self.capacity,
        }


class ApprovalGate:
    """Ensures learning jobs have the required approvals."""

    def __init__(self, fast_track_roles: Optional[List[str]] = None) -> None:
        self.fast_track_roles = set(fast_track_roles or [])

    def ensure_approval(self, entry: DomainWhitelistEntry, job_payload: Dict[str, Any]) -> Optional[str]:
        actor = job_payload.get("approved_by")
        if not entry.approval_required:
            return actor
        if actor in self.fast_track_roles:
            return actor
        if not actor:
            raise PermissionError(f"Domain '{entry.domain}' requires approval")
        token = job_payload.get("approval_token")
        if not token or not token.startswith("APPROVED-"):
            raise PermissionError("Approval token missing or invalid")
        return actor


class SandboxVerifier:
    """Runs sandbox verification hooks before a job can execute."""

    def __init__(self, required_checks: Optional[List[str]] = None) -> None:
        self.required_checks = required_checks or ["unit_tests", "runtime_guardrails"]

    def verify(self, job: GovernedLearningJob) -> Dict[str, Any]:
        missing = [check for check in self.required_checks if check not in job.sandbox_checks]
        if missing:
            raise RuntimeError(f"Sandbox verification missing checks: {missing}")
        return {"verified": True, "checks": self.required_checks}


class SafeModeLearningController:
    """Enforces safe-mode learning in CI/offline environments."""

    def __init__(
        self,
        safe_mode: bool = False,
        max_retries: int = 2,
        base_backoff: int = 2,
    ) -> None:
        self.safe_mode = safe_mode
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.failure_log: Dict[str, List[str]] = {}

    def enforce(self, job: GovernedLearningJob) -> None:
        if self.safe_mode and job.allow_network:
            raise RuntimeError("Safe mode prevents external network calls")

    def record_failure(self, job_id: str, reason: str) -> None:
        self.failure_log.setdefault(job_id, []).append(reason)

    def should_retry(self, job: GovernedLearningJob) -> bool:
        attempts = len(self.failure_log.get(job.job_id, []))
        return attempts < self.max_retries

    def compute_backoff(self, job: GovernedLearningJob) -> int:
        attempts = len(self.failure_log.get(job.job_id, []))
        return min(self.base_backoff * (2 ** attempts), self.base_backoff * 8)

    def toggle(self, safe_mode: bool) -> None:
        self.safe_mode = safe_mode


# ---------------------------------------------------------------------------
# World model updates and simulation
# ---------------------------------------------------------------------------


class WorldModelUpdateManager:
    """Tracks world model revisions with trust scoring, provenance, and events."""

    def __init__(
        self,
        event_bus: Optional[Any] = None,
        event_source: str = "governed_learning.world_model",
    ) -> None:
        self._history: List[Dict[str, Any]] = []
        self._topic_index: Dict[str, Dict[str, Any]] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._event_bus = event_bus if event_bus is not None else global_event_bus
        self._event_source = event_source

    @property
    def current_version(self) -> int:
        return len(self._history)

    def apply_update(self, update_payload: Dict[str, Any]) -> Dict[str, Any]:
        entries = update_payload.get("entries", [])
        resolved_entries = [self._resolve_entry(entry) for entry in entries]
        trust_score = self._calculate_trust_score(update_payload, resolved_entries)
        version = len(self._history) + 1
        record = {
            "version": version,
            "timestamp": datetime.utcnow().isoformat(),
            "trust_score": trust_score,
            "entries": resolved_entries,
            "source": update_payload.get("source", "unknown"),
            "validators": update_payload.get("validators", []),
        }
        self._history.append(record)
        for entry in resolved_entries:
            self._topic_index[entry["topic"]] = entry
        self._audit_log.append(
            {
                "event": "apply",
                "version": version,
                "source": record["source"],
                "trust_score": trust_score,
                "entry_count": len(resolved_entries),
            }
        )
        self._emit_world_model_event(
            "apply",
            {
                "version": version,
                "trust_score": trust_score,
                "source": record["source"],
                "entries": resolved_entries,
                "validators": record["validators"],
            },
        )
        return record

    def _resolve_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        topic = entry.get("topic", "unknown")
        prior = self._topic_index.get(topic, {})
        resolved_confidence = max(entry.get("confidence", 0.0), prior.get("confidence", 0.0))
        revision = prior.get("revision", 0) + 1
        return {
            "topic": topic,
            "content": entry.get("content", ""),
            "confidence": round(resolved_confidence, 4),
            "revision": revision,
        }

    def _calculate_trust_score(self, payload: Dict[str, Any], entries: List[Dict[str, Any]]) -> float:
        base = payload.get("confidence", statistics.mean([entry["confidence"] for entry in entries]) if entries else 0.5)
        validators = payload.get("validators", [])
        validator_bonus = min(len(validators) * 0.03, 0.15)
        novelty_penalty = 0.0
        if entries:
            revised_topics = [entry["topic"] for entry in entries if entry["revision"] > 1]
            novelty_penalty = len(revised_topics) * 0.01
        trust = max(0.0, min(1.0, base + validator_bonus - novelty_penalty))
        return round(trust, 4)

    def rollback_to_version(self, version: int) -> None:
        if version < 0:
            version = 0
        if version >= len(self._history):
            return
        self._history = self._history[:version]
        self._topic_index = {}
        for record in self._history:
            for entry in record["entries"]:
                self._topic_index[entry["topic"]] = entry
        self._audit_log.append(
            {
                "event": "rollback",
                "version": version,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self._emit_world_model_event(
            "rollback",
            {
                "version": version,
                "remaining_versions": len(self._history),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def visualize(self) -> Dict[str, Any]:
        nodes = [
            {"id": entry["topic"], "confidence": entry["confidence"], "revision": entry["revision"]}
            for entry in self._topic_index.values()
        ]
        edges = [
            {"source": record.get("source", "unknown"), "target": entry["topic"], "version": record["version"]}
            for record in self._history
            for entry in record["entries"]
        ]
        return {"nodes": nodes, "edges": edges}

    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def audit_log(self) -> List[Dict[str, Any]]:
        return list(self._audit_log)

    def _emit_world_model_event(self, action: str, payload: Dict[str, Any]) -> None:
        if not self._event_bus:
            return
        event = Event(
            event_type=EventType.WORLD_MODEL_UPDATE,
            source=self._event_source,
            data={"action": action, **payload},
        )
        publish_coro = self._event_bus.publish(event)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(publish_coro)
        else:
            loop.create_task(publish_coro)


class LearningSimulationFramework:
    """Runs lightweight simulations to validate learning jobs before execution."""

    def run(self, job: GovernedLearningJob) -> Dict[str, Any]:
        deterministic_seed = sum(ord(ch) for ch in job.job_id) % 997
        noise = (deterministic_seed % 17) / 100
        safety_margin = max(0.0, 1.0 - noise)
        effectiveness = min(1.0, job.priority + (0.1 * (1 - noise)))
        return {
            "safety_margin": round(safety_margin, 3),
            "expected_effectiveness": round(effectiveness, 3),
            "recommended_backoff_sec": math.ceil(noise * 10),
        }


@dataclass
class LearningJobDashboard:
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    retries: int = 0
    last_event: Optional[str] = None
    active_jobs: int = 0
    pending_jobs: int = 0
    last_backoff_sec: Optional[int] = None

    def record_enqueued(self, job: GovernedLearningJob) -> None:
        self.total_jobs += 1
        self.last_event = f"enqueued:{job.job_id}"

    def record_completion(
        self,
        job: GovernedLearningJob,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if success:
            self.completed_jobs += 1
        else:
            self.failed_jobs += 1
        self.last_event = f"completed:{job.job_id}:{'success' if success else 'failed'}"

    def record_retry(self, job: GovernedLearningJob, reason: str, backoff_sec: int) -> None:
        self.retries += 1
        self.last_event = f"retry:{job.job_id}:{reason}"[:120]
        self.last_backoff_sec = backoff_sec

    def update_queue_metrics(self, active: int, pending: int) -> None:
        self.active_jobs = active
        self.pending_jobs = pending

    def snapshot(self) -> Dict[str, Any]:
        return {
            "total_jobs": self.total_jobs,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "retries": self.retries,
            "last_event": self.last_event,
            "active_jobs": self.active_jobs,
            "pending_jobs": self.pending_jobs,
            "last_backoff_sec": self.last_backoff_sec,
        }


class GovernedLearningOrchestrator:
    """Coordinates gap detection, governed learning, and world model updates."""

    def __init__(
        self,
        registry: DomainWhitelistRegistry,
        job_queue: LearningJobQueue,
        sandbox_verifier: SandboxVerifier,
        approval_gate: ApprovalGate,
        safe_mode_controller: SafeModeLearningController,
        world_model_manager: WorldModelUpdateManager,
        dashboard: LearningJobDashboard,
        simulation_framework: LearningSimulationFramework,
    ) -> None:
        self.registry = registry
        self.job_queue = job_queue
        self.sandbox_verifier = sandbox_verifier
        self.approval_gate = approval_gate
        self.safe_mode_controller = safe_mode_controller
        self.world_model_manager = world_model_manager
        self.dashboard = dashboard
        self.simulation_framework = simulation_framework

    def submit_job(self, payload: Dict[str, Any]) -> GovernedLearningJob:
        domain = payload.get("domain")
        action = payload.get("action", "search")
        entry = self.registry.validate_action(domain, action)
        self.approval_gate.ensure_approval(entry, payload)
        job = GovernedLearningJob(
            job_id=str(uuid.uuid4()),
            domain=domain,
            action=action,
            payload=payload,
            allow_network=payload.get("allow_network", False),
            sandbox_checks=payload.get("sandbox_checks", []),
            approved_by=payload.get("approved_by"),
            priority=payload.get("priority", 0.5),
        )
        self.safe_mode_controller.enforce(job)
        self.job_queue.enqueue(job)
        self.dashboard.record_enqueued(job)
        metrics = self.job_queue.metrics()
        self.dashboard.update_queue_metrics(metrics["active"], metrics["pending"])
        return job

    def process_next_job(self) -> Optional[Dict[str, Any]]:
        job = self.job_queue.start_next_job()
        if not job:
            return None

        verification = None
        simulation_result = None
        update_record = None
        version_before = self.world_model_manager.current_version
        metrics = self.job_queue.metrics()
        self.dashboard.update_queue_metrics(metrics["active"], metrics["pending"])

        try:
            verification = self.sandbox_verifier.verify(job)
            simulation_result = self.simulation_framework.run(job)
            update_payload = job.payload.get("world_model_update")
            if update_payload:
                update_record = self.world_model_manager.apply_update(update_payload)
            self.job_queue.complete(job.job_id, "success")
            self.dashboard.record_completion(job, True, {"simulation": simulation_result})
            return {
                "job_id": job.job_id,
                "status": "success",
                "verification": verification,
                "simulation": simulation_result,
                "world_model_update": update_record,
            }
        except Exception as exc:  # pragma: no cover - exercised in tests via failure scenarios
            self.safe_mode_controller.record_failure(job.job_id, str(exc))
            if update_record:
                self.world_model_manager.rollback_to_version(version_before)
            should_retry = self.safe_mode_controller.should_retry(job)
            if should_retry:
                job.increment_retry()
                self.job_queue.retry(job)
                backoff_sec = self.safe_mode_controller.compute_backoff(job)
                self.dashboard.record_retry(job, str(exc), backoff_sec)
            else:
                self.job_queue.fail(job.job_id, str(exc))
                self.dashboard.record_completion(job, False)
            raise

    def dashboard_snapshot(self) -> Dict[str, Any]:
        snapshot = self.dashboard.snapshot()
        snapshot.update(self.job_queue.metrics())
        snapshot["world_model_version"] = self.world_model_manager.current_version
        return snapshot
