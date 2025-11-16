"""
Mission Outcome Logger

Listens for mission lifecycle events, summarizes the outcome, and records it
in Grace's world model so she can explain what she fixed or shipped.
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
from backend.mission_control.hub import mission_control_hub
from backend.mission_control.schemas import MissionPackage, MissionStatus, MetricObservation
from backend.world_model import grace_world_model

logger = logging.getLogger(__name__)


class MissionOutcomeLogger:
    """Captures mission results and feeds them back into the world model."""

    def __init__(self):
        self.running = False
        self._processed: deque[str] = deque(maxlen=500)

    async def start(self):
        if self.running:
            return
        self.running = True
        await trigger_mesh.subscribe("mission.*", self._handle_event)
        logger.info("[MISSION-OUTCOMES] Outcome logger started")

    async def stop(self):
        self.running = False

    async def _handle_event(self, event: TriggerEvent):
        if not self.running:
            return

        if event.event_type != "mission.updated":
            return

        mission_id = event.payload.get("mission_id")
        status = event.payload.get("status")
        if not mission_id or not status:
            return

        if status not in {MissionStatus.RESOLVED.value, MissionStatus.FAILED.value}:
            return

        key = f"{mission_id}:{status}"
        if key in self._processed:
            return

        mission = await mission_control_hub.get_mission(mission_id)
        if not mission:
            return

        await self._record_outcome(mission)
        self._processed.append(key)

    async def _record_outcome(self, mission: MissionPackage):
        summary = self._build_summary(mission)
        metadata = self._build_metadata(mission)

        try:
            await grace_world_model.add_knowledge(
                category="system",
                content=summary,
                source="mission_outcome_logger",
                confidence=0.93 if mission.status == MissionStatus.RESOLVED else 0.7,
                tags=["mission", "outcome"],
                metadata=metadata,
            )
            logger.info(
                "[MISSION-OUTCOMES] Captured mission %s outcome (%s)",
                mission.mission_id,
                mission.status.value,
            )
        except Exception as exc:
            logger.error(
                "[MISSION-OUTCOMES] Failed to write mission outcome: %s", exc
            )

    def _build_summary(self, mission: MissionPackage) -> str:
        tests_total = len(mission.evidence.test_results)
        tests_passed = len([t for t in mission.evidence.test_results if t.passed])
        remediation_count = len(mission.remediation_history)

        metric_lines = self._format_metrics(mission.evidence.metrics_snapshot)
        metric_text = (
            " ; ".join(metric_lines) if metric_lines else "No metric snapshots recorded"
        )

        return (
            f"Mission {mission.mission_id} targeting {mission.subsystem_id} "
            f"finished with status {mission.status.value} (severity {mission.severity.value}). "
            f"Detected by {mission.detected_by} and assigned to {mission.assigned_to}. "
            f"Tests passed: {tests_passed}/{tests_total}. "
            f"Metrics: {metric_text}. "
            f"Remediation steps executed: {remediation_count}."
        )

    def _build_metadata(self, mission: MissionPackage) -> Dict[str, any]:
        metrics_meta = [
            {
                "metric_id": obs.metric_id,
                "value": obs.value,
                "timestamp": obs.timestamp.isoformat(),
            }
            for obs in mission.evidence.metrics_snapshot[:5]
        ]

        return {
            "mission_id": mission.mission_id,
            "status": mission.status.value,
            "severity": mission.severity.value,
            "subsystem": mission.subsystem_id,
            "detected_by": mission.detected_by,
            "assigned_to": mission.assigned_to,
            "tests_total": len(mission.evidence.test_results),
            "tests_passed": len([t for t in mission.evidence.test_results if t.passed]),
            "metrics": metrics_meta,
            "remediation_steps": len(mission.remediation_history),
            "tags": mission.tags,
        }

    def _format_metrics(self, observations: List[MetricObservation]) -> List[str]:
        lines: List[str] = []
        for obs in observations[:5]:
            metric_line = f"{obs.metric_id}={obs.value:.2f}"
            lines.append(metric_line)
        return lines


mission_outcome_logger = MissionOutcomeLogger()
