"""
Mission Outcome Logger

Listens for mission lifecycle updates and records outcomes into the world model
so Grace can explain what she fixed (or where she failed) with citations.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent
from backend.mission_control.hub import mission_control_hub
from backend.mission_control.schemas import MissionStatus, MissionPackage
from backend.world_model import grace_world_model
from backend.governance_system.governance import governance_engine

logger = logging.getLogger(__name__)


class MissionOutcomeLogger:
    """Subscribes to mission events and logs outcomes into Grace's world model."""

    def __init__(self):
        self.started = False
        self.logged_missions: Set[str] = set()

    async def start(self):
        if self.started:
            return

        await trigger_mesh.subscribe("mission.*", self._handle_event)
        self.started = True
        logger.info("[MISSION-OUTCOME] Outcome logger subscribed to mission events")

    async def _handle_event(self, event: TriggerEvent):
        payload = event.payload or {}
        mission_id = payload.get("mission_id") or event.resource
        status = payload.get("status")

        if not mission_id or not status:
            return

        # Only log terminal states
        if status not in {
            MissionStatus.RESOLVED.value,
            MissionStatus.FAILED.value,
            MissionStatus.ESCALATED.value,
        }:
            return

        if mission_id in self.logged_missions:
            return

        mission = await mission_control_hub.get_mission(mission_id)
        if not mission:
            return

        await self._record_outcome(mission, status)
        self.logged_missions.add(mission_id)

    async def _record_outcome(self, mission: MissionPackage, status: str):
        """Persist mission outcome into world model with helpful metadata."""
        tests_info = self._summarize_tests(mission.evidence.test_results)
        metrics_info = self._summarize_metrics(mission.evidence.metrics_snapshot)
        actions_info = self._summarize_actions(mission.remediation_history)

        summary = self._build_summary(mission, status, tests_info, metrics_info)

        metadata = {
            "mission_id": mission.mission_id,
            "status": status,
            "subsystem_id": mission.subsystem_id,
            "severity": mission.severity.value,
            "tests_passed": tests_info["passed"],
            "tests_total": tests_info["total"],
            "metrics": metrics_info["metrics"],
            "last_action": actions_info.get("last_action"),
            "actions_count": actions_info.get("count"),
            "detected_by": mission.detected_by,
            "assigned_to": mission.assigned_to,
            "resolved_at": (
                mission.resolved_at.isoformat() if mission.resolved_at else None
            ),
            "objective": mission.tags.get("objective")
            if mission.tags
            else mission.subsystem_id,
        }

        try:
            await grace_world_model.add_knowledge(
                category="system",
                content=summary,
                source="mission_outcome_logger",
                confidence=0.95 if status == MissionStatus.RESOLVED.value else 0.75,
                tags=["mission", "outcome", status],
                metadata=metadata,
            )
        except Exception as exc:
            logger.error(
                "[MISSION-OUTCOME] Failed to log mission %s outcome: %s",
                mission.mission_id,
                exc,
            )

        try:
            await governance_engine.log_event(
                actor="mission_outcome_logger",
                action="mission.outcome_recorded",
                resource=mission.mission_id,
                metadata={"status": status, "subsystem": mission.subsystem_id},
            )
        except Exception:
            # Governance logging is best effort
            pass

        logger.info(
            "[MISSION-OUTCOME] Recorded mission outcome %s (%s)", mission.mission_id, status
        )

    def _build_summary(
        self,
        mission: MissionPackage,
        status: str,
        tests_info: Dict[str, Any],
        metrics_info: Dict[str, Any],
    ) -> str:
        objective = mission.tags.get("objective") if mission.tags else None
        objective_text = objective or f"Stabilize {mission.subsystem_id}"
        status_text = status.replace("_", " ").title()
        tests_text = (
            f"{tests_info['passed']}/{tests_info['total']} tests passed"
            if tests_info["total"]
            else "No automated tests recorded"
        )
        metrics_text = (
            ", ".join(
                f"{m['id']}={m['value']}"
                for m in metrics_info["metrics"][:3]
            )
            or "No metrics captured"
        )

        return (
            f"Mission {mission.mission_id} ({objective_text}) {status_text}. "
            f"{tests_text}. Key metrics: {metrics_text}."
        )

    @staticmethod
    def _summarize_tests(test_results: List[Any]) -> Dict[str, Any]:
        total = len(test_results)
        passed = len([t for t in test_results if getattr(t, "passed", False)])
        return {"total": total, "passed": passed}

    @staticmethod
    def _summarize_metrics(metrics: List[Any]) -> Dict[str, Any]:
        summarized = []
        for m in metrics:
            summarized.append(
                {
                    "id": getattr(m, "metric_id", "unknown"),
                    "value": getattr(m, "value", None),
                    "timestamp": getattr(m, "timestamp", None),
                }
            )
        return {"metrics": summarized}

    @staticmethod
    def _summarize_actions(actions: List[Any]) -> Dict[str, Any]:
        if not actions:
            return {"count": 0}
        last_action = actions[-1]
        return {
            "count": len(actions),
            "last_action": getattr(last_action, "action", None),
            "last_actor": getattr(last_action, "actor", None),
        }


mission_outcome_logger = MissionOutcomeLogger()
