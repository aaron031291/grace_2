"""
Proactive Mission Detector

Continuously scans Grace's telemetry, world-model KPIs, and integrity alerts
to auto-create missions when reliability drifts outside safe thresholds.
"""

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid

from backend.world_model import grace_world_model
from backend.mission_control.mission_manifest import (
    MissionManifest,
    SuccessCriterion,
)
from backend.mission_control.mission_controller import mission_controller
from backend.core.htm_readiness import htm_readiness
from backend.governance_system.governance import governance_engine

logger = logging.getLogger(__name__)


@dataclass
class MissionTrigger:
    """Represents a trigger that should open a proactive mission."""

    trigger_type: str
    domain: str
    reason: str
    objective: str
    description: str
    severity: str
    kpi_snapshot: Dict[str, Any] = field(default_factory=dict)
    recommended_tasks: List[Dict[str, Any]] = field(default_factory=list)


class ProactiveMissionDetector:
    """
    Watches KPIs + alerts and launches missions when thresholds are exceeded.
    """

    def __init__(self):
        self.interval_seconds = 600  # 10 minutes
        self.success_rate_threshold = 0.90
        self.mttr_minutes_threshold = 5
        self.mttr_multiplier = 3
        self.queue_depth_threshold = 1000
        self.queue_pressure_duration = timedelta(minutes=5)
        self.validator_repeat_window = timedelta(minutes=30)
        self.trigger_cooldown = timedelta(minutes=30)

        self.running = False
        self._queue_pressure_start: Optional[datetime] = None
        self._validator_history: Dict[str, deque[datetime]] = defaultdict(
            lambda: deque(maxlen=10)
        )
        self._recent_triggers: Dict[str, datetime] = {}

    async def start(self):
        if self.running:
            return
        self.running = True
        asyncio.create_task(self._run_loop())
        logger.info("[PROACTIVE-MISSIONS] Detector started")

    async def stop(self):
        self.running = False

    async def _run_loop(self):
        while self.running:
            try:
                await self._run_cycle()
            except Exception as exc:
                logger.exception("[PROACTIVE-MISSIONS] Cycle failed: %s", exc)
            await asyncio.sleep(self.interval_seconds)

    async def _run_cycle(self):
        kpis = await self._collect_kpis()
        alerts = await self._collect_validator_alerts()
        telemetry = self._collect_telemetry()

        triggers = self._evaluate_triggers(kpis, telemetry, alerts)

        for trigger in triggers:
            await self._create_mission(trigger)

    async def _collect_kpis(self) -> List[Dict[str, Any]]:
        """Collect latest KPI knowledge entries from world model."""
        metrics: List[Dict[str, Any]] = []
        queries = ["success rate", "mttr", "latency", "queue depth", "kpi"]

        for query in queries:
            try:
                results = await grace_world_model.query(
                    query=query,
                    category="system",
                    top_k=25,
                )
            except Exception as exc:
                logger.debug("[PROACTIVE-MISSIONS] KPI query failed (%s): %s", query, exc)
                continue

            for item in results:
                metadata = item.metadata or {}
                metric_type = metadata.get("metric_type")
                if not metric_type:
                    continue

                metrics.append(
                    {
                        "domain": metadata.get("domain", "system"),
                        "metric_type": metric_type,
                        "value": self._to_float(metadata.get("value")),
                        "baseline": self._to_float(metadata.get("baseline")),
                        "timestamp": self._parse_timestamp(
                            metadata.get("timestamp") or item.updated_at
                        ),
                        "context": metadata,
                        "content": item.content,
                    }
                )

        return metrics

    async def _collect_validator_alerts(self) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        try:
            results = await grace_world_model.query(
                query="validator alert",
                category="system",
                top_k=20,
            )
        except Exception as exc:
            logger.debug("[PROACTIVE-MISSIONS] Validator query failed: %s", exc)
            return alerts

        for item in results:
            metadata = item.metadata or {}
            component = metadata.get("component") or metadata.get("resource")
            timestamp = self._parse_timestamp(metadata.get("timestamp") or item.updated_at)
            alerts.append(
                {
                    "component": component or "unknown",
                    "severity": metadata.get("severity", "medium"),
                    "timestamp": timestamp,
                    "content": item.content,
                    "metadata": metadata,
                }
            )

        return alerts

    def _collect_telemetry(self) -> Dict[str, Any]:
        """Grab latest HTM telemetry snapshot."""
        snapshot = {
            "queue_depth": getattr(htm_readiness, "queue_depth", 0),
            "sla_breaches": getattr(htm_readiness, "sla_breaches_recent", 0),
            "timestamp": datetime.utcnow(),
        }
        return snapshot

    def _evaluate_triggers(
        self,
        metrics: List[Dict[str, Any]],
        telemetry: Dict[str, Any],
        alerts: List[Dict[str, Any]],
    ) -> List[MissionTrigger]:
        triggers: List[MissionTrigger] = []
        latest = self._latest_metric_map(metrics)
        now = datetime.utcnow()

        # Success rate triggers
        for metric in latest.values():
            if metric["metric_type"] == "success_rate" and metric["value"] is not None:
                if metric["value"] < self.success_rate_threshold:
                    triggers.append(
                        self._build_trigger(
                            trigger_type="reliability",
                            domain=metric["domain"],
                            reason="success_rate_drop",
                            severity="high",
                            objective=f"Restore {metric['domain']} success rate above 90%",
                            description=metric["content"],
                            kpi_snapshot=self._kpi_snapshot(
                                metric,
                                threshold=self.success_rate_threshold,
                                comparison=">=",
                            ),
                        )
                    )

            if metric["metric_type"] == "mttr_minutes" and metric["value"] is not None:
                threshold = max(
                    self.mttr_minutes_threshold,
                    (metric["baseline"] or self.mttr_minutes_threshold)
                    * self.mttr_multiplier,
                )
                if metric["value"] > threshold:
                    triggers.append(
                        self._build_trigger(
                            trigger_type="stability",
                            domain=metric["domain"],
                            reason="mttr_exceeded",
                            severity="medium",
                            objective=f"Reduce {metric['domain']} MTTR below {threshold:.1f} minutes",
                            description=metric["content"],
                            kpi_snapshot=self._kpi_snapshot(
                                metric, threshold=threshold, comparison="<="
                            ),
                        )
                    )

            if metric["metric_type"].startswith("latency") and metric["value"] is not None:
                baseline = metric["baseline"] or metric["value"]
                threshold = baseline * 1.5
                if metric["value"] > threshold:
                    triggers.append(
                        self._build_trigger(
                            trigger_type="performance",
                            domain=metric["domain"],
                            reason="latency_spike",
                            severity="high",
                            objective=f"Bring {metric['domain']} latency back under {threshold:.0f} ms",
                            description=metric["content"],
                            kpi_snapshot=self._kpi_snapshot(
                                metric, threshold=threshold, comparison="<="
                            ),
                        )
                    )

        # Queue depth trigger
        queue_depth = telemetry.get("queue_depth", 0)
        if queue_depth >= self.queue_depth_threshold:
            if not self._queue_pressure_start:
                self._queue_pressure_start = now
            elif now - self._queue_pressure_start >= self.queue_pressure_duration:
                triggers.append(
                    MissionTrigger(
                        trigger_type="capacity",
                        domain="htm",
                        reason="queue_depth_pressure",
                        severity="high",
                        objective="Reduce HTM queue depth below safe operating range",
                        description="HTM queue depth sustained above threshold",
                        kpi_snapshot={
                            "metric": "queue_depth",
                            "value": queue_depth,
                            "threshold": self.queue_depth_threshold,
                            "comparison": "<=",
                            "timestamp": telemetry["timestamp"].isoformat(),
                        },
                        recommended_tasks=self._task_templates("capacity", "htm"),
                    )
                )
        else:
            self._queue_pressure_start = None

        # Validator repeat alerts
        validator_triggers = self._detect_validator_triggers(alerts, now)
        triggers.extend(validator_triggers)

        return triggers

    def _detect_validator_triggers(
        self, alerts: List[Dict[str, Any]], now: datetime
    ) -> List[MissionTrigger]:
        triggers: List[MissionTrigger] = []

        for alert in alerts:
            component = alert["component"]
            timestamp = alert.get("timestamp") or now
            history = self._validator_history[component]
            history.append(timestamp)

            recent_hits = [
                t for t in history if now - t <= self.validator_repeat_window
            ]

            if len(recent_hits) >= 2:
                triggers.append(
                    MissionTrigger(
                        trigger_type="integrity",
                        domain=component,
                        reason="repeated_validator_alert",
                        severity="critical",
                        objective=f"Stabilize {component} integrity alerts",
                        description=alert["content"],
                        kpi_snapshot={
                            "metric": "validator_alerts",
                            "value": len(recent_hits),
                            "threshold": 1,
                            "comparison": "<=",
                            "timestamps": [t.isoformat() for t in recent_hits],
                        },
                        recommended_tasks=self._task_templates("integrity", component),
                    )
                )
                history.clear()  # Avoid duplicate triggers

        return triggers

    async def _create_mission(self, trigger: MissionTrigger):
        key = f"{trigger.trigger_type}:{trigger.domain}"
        now = datetime.utcnow()

        last_triggered = self._recent_triggers.get(key)
        if last_triggered and now - last_triggered < self.trigger_cooldown:
            logger.debug(
                "[PROACTIVE-MISSIONS] Skipping %s (cooldown active)", key
            )
            return

        manifest_id = f"auto_mission_{uuid.uuid4().hex[:8]}"
        manifest = MissionManifest(
            manifest_id=manifest_id,
            mission_name=f"[AUTO] {trigger.domain} {trigger.trigger_type}".title(),
            description=trigger.description,
            objective=trigger.objective,
            success_criteria=[
                SuccessCriterion(
                    description=f"{trigger.kpi_snapshot.get('metric')} "
                    f"{trigger.kpi_snapshot.get('comparison')} "
                    f"{trigger.kpi_snapshot.get('threshold')}",
                    check_type="metric_threshold",
                    check_parameters={
                        "domain": trigger.domain,
                        "metric": trigger.kpi_snapshot.get("metric"),
                        "comparison": trigger.kpi_snapshot.get("comparison"),
                        "threshold": trigger.kpi_snapshot.get("threshold"),
                    },
                    expected_result="within_threshold",
                )
            ],
            constraints=[],
            initial_context={
                "trigger_reason": trigger.reason,
                "severity": trigger.severity,
                "kpi_snapshot": trigger.kpi_snapshot,
                "recommended_tasks": trigger.recommended_tasks,
            },
            created_by="proactive_mission_detector",
        )

        try:
            await governance_engine.check(
                actor="proactive_mission_detector",
                action="mission.auto_launch",
                resource=trigger.domain,
                payload={"trigger": trigger.reason},
            )
        except Exception as exc:
            logger.debug("[PROACTIVE-MISSIONS] Governance check failed: %s", exc)

        try:
            await mission_controller.start_mission_from_manifest(manifest)
            self._recent_triggers[key] = now
            logger.info(
                "[PROACTIVE-MISSIONS] Mission %s launched (%s)",
                manifest.manifest_id,
                trigger.reason,
            )
        except Exception as exc:
            logger.error(
                "[PROACTIVE-MISSIONS] Failed to start mission %s: %s",
                manifest.manifest_id,
                exc,
            )
            return

        try:
            await grace_world_model.add_knowledge(
                category="system",
                content=(
                    f"Proactive mission {manifest.mission_name} launched due to "
                    f"{trigger.reason} in {trigger.domain}."
                ),
                source="proactive_mission_detector",
                confidence=0.95,
                tags=["mission", "proactive"],
                metadata={
                    "mission_id": manifest.manifest_id,
                    "trigger": trigger.reason,
                    "kpi_snapshot": trigger.kpi_snapshot,
                    "severity": trigger.severity,
                },
            )
        except Exception as exc:
            logger.debug(
                "[PROACTIVE-MISSIONS] Failed to log mission knowledge: %s", exc
            )

    def _latest_metric_map(
        self, metrics: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        latest: Dict[str, Dict[str, Any]] = {}
        for metric in metrics:
            key = f"{metric['domain']}::{metric['metric_type']}"
            existing = latest.get(key)
            if not existing or (
                metric["timestamp"] and metric["timestamp"] > existing.get("timestamp")
            ):
                latest[key] = metric
        return latest

    def _kpi_snapshot(
        self, metric: Dict[str, Any], threshold: float, comparison: str
    ) -> Dict[str, Any]:
        return {
            "metric": metric["metric_type"],
            "value": metric["value"],
            "threshold": threshold,
            "comparison": comparison,
            "domain": metric["domain"],
            "baseline": metric.get("baseline"),
            "timestamp": (
                metric["timestamp"].isoformat() if metric.get("timestamp") else None
            ),
        }

    def _task_templates(self, trigger_type: str, domain: str) -> List[Dict[str, Any]]:
        templates = {
            "reliability": [
                {"type": "diagnose_failures", "domain": domain, "priority": "high"},
                {"type": "stabilize_pipeline", "domain": domain},
                {"type": "validate_success_rate", "domain": domain},
            ],
            "stability": [
                {"type": "analyze_incidents", "domain": domain},
                {"type": "accelerate_repair_playbooks", "domain": domain},
            ],
            "performance": [
                {"type": "profile_latency", "domain": domain, "priority": "high"},
                {"type": "optimize_hot_paths", "domain": domain},
                {"type": "verify_latency_improvements", "domain": domain},
            ],
            "capacity": [
                {"type": "scale_workers", "domain": domain},
                {"type": "rebalance_queue", "domain": domain},
                {"type": "audit_queue_backlog", "domain": domain},
            ],
            "integrity": [
                {"type": "root_cause_validator_alerts", "domain": domain, "priority": "high"},
                {"type": "apply_guardian_playbook", "domain": domain},
                {"type": "verify_integrity_post_fix", "domain": domain},
            ],
        }

        return templates.get(trigger_type, [{"type": "investigate", "domain": domain}])

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None


# Global instance
proactive_mission_detector = ProactiveMissionDetector()
