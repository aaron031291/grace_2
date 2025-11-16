"""
Mission Follow-up Planner

Automatically opens refinement missions whenever recent mission outcomes
indicate failed/escalated states or incomplete success (tests still failing,
missing metrics, etc.).
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uuid

from backend.world_model import grace_world_model
from backend.mission_control.mission_manifest import (
    MissionManifest,
    SuccessCriterion,
    Constraint,
)
from backend.mission_control.mission_controller import mission_controller
from backend.governance_system.governance import governance_engine

logger = logging.getLogger(__name__)


class MissionFollowUpPlanner:
    """Scans mission outcome knowledge and launches follow-up missions."""

    def __init__(self):
        self.interval_seconds = 900  # 15 minutes
        self.lookback_hours = 6
        self.max_results = 50
        self.running = False
        self._processed: Dict[str, datetime] = {}

    async def start(self):
        if self.running:
            return
        self.running = True
        asyncio.create_task(self._run_loop())
        logger.info("[MISSION-FOLLOWUP] Planner started")

    async def stop(self):
        self.running = False

    async def _run_loop(self):
        while self.running:
            try:
                await self._run_cycle()
            except Exception as exc:
                logger.exception("[MISSION-FOLLOWUP] Cycle failed: %s", exc)
            await asyncio.sleep(self.interval_seconds)

    async def _run_cycle(self):
        outcomes = await self._fetch_recent_outcomes()
        for outcome in outcomes:
            metadata = outcome.get("metadata") or {}
            mission_id = metadata.get("mission_id")
            if not mission_id:
                continue

            status = metadata.get("status", "").lower()
            key = f"{mission_id}:{status}"

            if key in self._processed:
                continue

            if not self._needs_follow_up(metadata):
                continue

            await self._launch_follow_up(outcome)
            self._processed[key] = datetime.utcnow()

        # Clean cache (older than 1 day)
        cutoff = datetime.utcnow() - timedelta(days=1)
        self._processed = {
            k: v for k, v in self._processed.items() if v >= cutoff
        }

    async def _fetch_recent_outcomes(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            entries = await grace_world_model.query(
                query="mission outcome",
                category="system",
                top_k=self.max_results,
            )
        except Exception as exc:
            logger.debug("[MISSION-FOLLOWUP] Outcome query failed: %s", exc)
            return results

        cutoff = datetime.utcnow() - timedelta(hours=self.lookback_hours)
        for entry in entries:
            metadata = entry.metadata or {}
            updated_at = self._parse_timestamp(entry.updated_at)
            if updated_at and updated_at < cutoff:
                continue

            results.append(
                {
                    "knowledge": entry,
                    "metadata": metadata,
                    "updated_at": updated_at or datetime.utcnow(),
                }
            )

        return results

    def _needs_follow_up(self, metadata: Dict[str, Any]) -> bool:
        status = (metadata.get("status") or "").lower()
        if status in {"failed", "escalated"}:
            return True

        if status != "resolved":
            return False

        tests_total = metadata.get("tests_total") or 0
        tests_passed = metadata.get("tests_passed") or 0
        if tests_total and tests_passed < tests_total:
            return True

        metrics = metadata.get("metrics") or []
        if not metrics:
            return True

        # Look for null metric values
        for metric in metrics:
            if metric.get("value") is None:
                return True

        return False

    async def _launch_follow_up(self, outcome: Dict[str, Any]):
        metadata = outcome["metadata"]
        mission_id = metadata.get("mission_id")
        status = metadata.get("status", "unknown")
        subsystem = metadata.get("subsystem") or metadata.get("subsystem_id") or "system"
        tests_total = metadata.get("tests_total") or 0
        tests_passed = metadata.get("tests_passed") or 0

        manifest_id = f"followup_{mission_id}_{uuid.uuid4().hex[:6]}"
        objective = (
            f"Complete remediation for {subsystem} after mission {mission_id} "
            f"ended with status {status}."
        )

        success_criteria = [
            SuccessCriterion(
                description="All automated tests must pass",
                check_type="automated_tests",
                check_parameters={
                    "expected_pass_count": tests_total,
                },
                expected_result="tests_passed",
            )
        ]

        if metadata.get("metrics"):
            metric = metadata["metrics"][0]
            success_criteria.append(
                SuccessCriterion(
                    description=f"Restore {metric.get('id', 'metric')} to healthy range",
                    check_type="metric_threshold",
                    check_parameters={
                        "metric_id": metric.get("id"),
                        "comparison": "<=",
                        "threshold": metric.get("value") or 0,
                    },
                    expected_result="metric_within_threshold",
                )
            )

        manifest = MissionManifest(
            manifest_id=manifest_id,
            mission_name=f"[FOLLOW-UP] {subsystem}",
            description=objective,
            objective=objective,
            success_criteria=success_criteria,
            constraints=[
                Constraint(
                    description="Complete follow-up within 2 hours",
                    constraint_type="time_limit",
                    value="2h",
                )
            ],
            initial_context={
                "origin_mission_id": mission_id,
                "origin_status": status,
                "tests_summary": {
                    "passed": tests_passed,
                    "total": tests_total,
                },
                "metrics_snapshot": metadata.get("metrics"),
            },
            created_by="mission_follow_up_planner",
        )

        try:
            await governance_engine.check(
                actor="mission_follow_up_planner",
                action="mission.follow_up_launch",
                resource=subsystem,
                payload={"origin_mission_id": mission_id, "status": status},
            )
        except Exception as exc:
            logger.debug("[MISSION-FOLLOWUP] Governance check failed: %s", exc)

        try:
            await mission_controller.start_mission_from_manifest(manifest)
            logger.info(
                "[MISSION-FOLLOWUP] Follow-up mission %s launched for %s",
                manifest_id,
                mission_id,
            )
        except Exception as exc:
            logger.error(
                "[MISSION-FOLLOWUP] Failed to start follow-up mission %s: %s",
                manifest_id,
                exc,
            )

    @staticmethod
    def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None


mission_follow_up_planner = MissionFollowUpPlanner()
