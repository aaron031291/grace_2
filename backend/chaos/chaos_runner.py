"""
Layer 1 Chaos Runner
--------------------

Injects concurrent failure scenarios against Grace's core kernels so the
watchdogs, self-healing kernel, and coding agent can learn from real faults.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from backend.core.control_plane import control_plane, KernelState
from backend.core.immutable_log import immutable_log
from backend.core.message_bus import message_bus, MessagePriority

logger = logging.getLogger(__name__)


@dataclass
class ChaosScenario:
    """Single chaos scenario definition."""

    id: str
    description: str
    severity: str
    category: str
    injection: Dict[str, Any]
    verification: Dict[str, Any] = field(default_factory=dict)


class ChaosRunner:
    """Loads chaos scenarios and executes them in concurrent waves."""

    def __init__(
        self,
        scenario_file: Path | str = Path("backend/chaos/scenarios.yaml"),
        log_dir: Path | str = Path("logs/chaos"),
    ) -> None:
        self.scenario_file = Path(scenario_file)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.scenarios: List[ChaosScenario] = self._load_scenarios()
        self.wave_counter = 0

    def _load_scenarios(self) -> List[ChaosScenario]:
        if not self.scenario_file.exists():
            raise FileNotFoundError(f"Chaos scenario file not found: {self.scenario_file}")

        with open(self.scenario_file, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        scenarios: List[ChaosScenario] = []
        for raw in data.get("scenarios", []):
            scenarios.append(
                ChaosScenario(
                    id=raw["id"],
                    description=raw.get("description", ""),
                    severity=raw.get("severity", "medium"),
                    category=raw.get("category", "generic"),
                    injection=raw.get("injection", {}),
                    verification=raw.get("verification", {}),
                )
            )
        if not scenarios:
            raise ValueError("No chaos scenarios defined.")
        return scenarios

    async def run_wave(self, wave_size: int = 2, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a concurrent wave of chaos scenarios."""
        self.wave_counter += 1
        wave_id = f"wave_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.wave_counter}"

        available = [s for s in self.scenarios if severity is None or s.severity == severity]
        if not available:
            raise ValueError(f"No scenarios available for severity '{severity}'.")

        sample_size = min(wave_size, len(available))
        selected = random.sample(available, sample_size)

        logger.info("[CHAOS] Starting wave %s with %d scenarios", wave_id, sample_size)

        baseline = {scenario.id: self._capture_baseline(scenario) for scenario in selected}

        tasks = [
            asyncio.create_task(self._execute_scenario(scenario, wave_id, baseline[scenario.id]))
            for scenario in selected
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        logger.info("[CHAOS] Wave %s complete", wave_id)
        return results

    def _capture_baseline(self, scenario: ChaosScenario) -> Dict[str, Any]:
        """Snapshot relevant state before injecting a fault."""
        baseline: Dict[str, Any] = {}

        kernel = scenario.injection.get("target_kernel")
        if not kernel:
            for check in scenario.verification.get("checks", []):
                kernel = kernel or check.get("target_kernel")
        if kernel and kernel in control_plane.kernels:
            kern = control_plane.kernels[kernel]
            baseline["kernel_state"] = kern.state.value
            baseline["kernel_restart_count"] = kern.restart_count

        file_name = scenario.injection.get("file_name")
        if not file_name:
            for check in scenario.verification.get("checks", []):
                file_name = file_name or check.get("file_name")
        if file_name:
            baseline["snapshot_exists"] = self._snapshot_path(file_name).exists()

        return baseline

    async def _execute_scenario(
        self,
        scenario: ChaosScenario,
        wave_id: str,
        baseline: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Inject a fault, run verifications, and log all telemetry."""
        start_time = datetime.utcnow()
        scenario_log: Dict[str, Any] = {
            "wave_id": wave_id,
            "scenario_id": scenario.id,
            "description": scenario.description,
            "severity": scenario.severity,
            "category": scenario.category,
            "started_at": start_time.isoformat(),
        }

        try:
            injection_result = await self._inject_fault(scenario)
            verification_results = await self._run_verification_checks(scenario, baseline)
            all_checks_passed = all(check.get("passed") for check in verification_results)

            scenario_log.update(
                {
                    "status": "success" if all_checks_passed else "attention",
                    "injection_result": injection_result,
                    "verification": verification_results,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("[CHAOS] Scenario %s failed: %s", scenario.id, exc)
            scenario_log.update(
                {
                    "status": "error",
                    "error": str(exc),
                }
            )

        scenario_log["completed_at"] = datetime.utcnow().isoformat()
        scenario_log["duration_seconds"] = (
            datetime.fromisoformat(scenario_log["completed_at"]) - start_time
        ).total_seconds()

        self._persist_log(scenario_log)
        await self._append_immutable_log(scenario_log)

        return scenario_log

    async def _inject_fault(self, scenario: ChaosScenario) -> Dict[str, Any]:
        action = scenario.injection.get("action")
        if not action:
            raise ValueError(f"Scenario {scenario.id} missing injection action.")

        handler_name = f"_inject_{action}"
        handler = getattr(self, handler_name, None)
        if not handler:
            raise NotImplementedError(f"No injection handler for action '{action}'.")

        logger.info("[CHAOS] Injecting %s (%s)", scenario.id, action)
        return await handler(scenario)

    async def _inject_pause_kernel(self, scenario: ChaosScenario) -> Dict[str, Any]:
        kernel_name = scenario.injection.get("target_kernel")
        duration = scenario.injection.get("duration_seconds", 10)
        if not kernel_name:
            raise ValueError("pause_kernel scenario requires 'target_kernel'.")

        await control_plane.pause_kernel(kernel_name)
        await asyncio.sleep(duration)
        await control_plane.resume_kernel(kernel_name)

        return {"paused_kernel": kernel_name, "duration_seconds": duration}

    async def _inject_spam_topic(self, scenario: ChaosScenario) -> Dict[str, Any]:
        topic = scenario.injection.get("topic")
        count = scenario.injection.get("message_count", 100)
        delay_ms = scenario.injection.get("burst_delay_ms", 10)

        if not topic:
            raise ValueError("spam_topic scenario requires 'topic'.")

        payload_template = {
            "task_type": "chaos_ref_signal",
            "description": "Chaos runner synthetic workload",
            "intent": "stress_topic",
        }

        for _ in range(count):
            payload = dict(payload_template)
            payload["task_id"] = f"chaos-{uuid.uuid4()}"
            await message_bus.publish(
                source="chaos_runner",
                topic=topic,
                payload=payload,
                priority=MessagePriority.HIGH,
            )
            if delay_ms:
                await asyncio.sleep(delay_ms / 1000)

        return {"topic": topic, "messages": count}

    async def _inject_corrupt_snapshot(self, scenario: ChaosScenario) -> Dict[str, Any]:
        file_name = scenario.injection.get("file_name")
        duration = scenario.injection.get("duration_seconds", 10)
        if not file_name:
            raise ValueError("corrupt_snapshot scenario requires 'file_name'.")

        target_path = self._snapshot_path(file_name)
        backup_path = target_path.with_suffix(target_path.suffix + ".chaosbak")

        target_exists = target_path.exists()
        if target_exists:
            target_path.rename(backup_path)

        await asyncio.sleep(duration)

        if backup_path.exists():
            backup_path.rename(target_path)

        return {"file_name": file_name, "temporarily_removed": target_exists}

    async def _run_verification_checks(
        self,
        scenario: ChaosScenario,
        baseline: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        checks = scenario.verification.get("checks", [])
        results: List[Dict[str, Any]] = []

        for check in checks:
            check_type = check.get("type")
            handler_name = f"_verify_{check_type}"
            handler = getattr(self, handler_name, None)
            if not handler:
                results.append(
                    {
                        "type": check_type,
                        "passed": False,
                        "error": f"Unknown verification type '{check_type}'",
                    }
                )
                continue

            result = await handler(check, baseline)
            results.append(result)

        return results

    async def _verify_kernel_state(self, check: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        kernel_name = check.get("target_kernel")
        expected_state = check.get("expected_state", "running")
        kernel = control_plane.kernels.get(kernel_name) if kernel_name else None
        actual_state = kernel.state.value if kernel else "unknown"
        passed = actual_state == expected_state
        return {
            "type": "kernel_state",
            "target_kernel": kernel_name,
            "expected_state": expected_state,
            "actual_state": actual_state,
            "passed": passed,
        }

    async def _verify_restart_within(self, check: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        kernel_name = check.get("target_kernel")
        max_seconds = check.get("max_seconds", 60)
        deadline = datetime.utcnow() + timedelta(seconds=max_seconds)
        passed = False

        while datetime.utcnow() < deadline:
            kernel = control_plane.kernels.get(kernel_name)
            if kernel and kernel.state == KernelState.RUNNING:
                passed = True
                break
            await asyncio.sleep(1)

        return {
            "type": "restart_within",
            "target_kernel": kernel_name,
            "max_seconds": max_seconds,
            "passed": passed,
        }

    async def _verify_message_bus_health(self, _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
        passed = message_bus.running
        return {
            "type": "message_bus_health",
            "running": message_bus.running,
            "passed": passed,
        }

    async def _verify_queue_depth_sample(self, check: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        topic = check.get("topic")
        max_depth = check.get("max_depth", 200)
        depth = self._topic_depth(topic) if topic else -1
        passed = depth <= max_depth if depth >= 0 else False
        return {
            "type": "queue_depth_sample",
            "topic": topic,
            "depth": depth,
            "max_depth": max_depth,
            "passed": passed,
        }

    async def _verify_snapshot_exists(self, check: Dict[str, Any], _: Dict[str, Any]) -> Dict[str, Any]:
        file_name = check.get("file_name")
        path = self._snapshot_path(file_name) if file_name else None
        exists = path.exists() if path else False
        return {
            "type": "snapshot_exists",
            "file_name": file_name,
            "exists": exists,
            "passed": exists,
        }

    def _topic_depth(self, topic: str) -> int:
        queues = message_bus.topics.get(topic, [])
        return sum(queue.qsize() for queue in queues)

    def _snapshot_path(self, file_name: str) -> Path:
        base = Path(".grace_snapshots") / "models"
        base.mkdir(parents=True, exist_ok=True)
        return base / file_name

    def _persist_log(self, data: Dict[str, Any]) -> None:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S%f")
        log_path = self.log_dir / f"{data['scenario_id']}_{timestamp}.json"
        with open(log_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    async def _append_immutable_log(self, data: Dict[str, Any]) -> None:
        await immutable_log.append(
            actor="chaos_runner",
            action="chaos_scenario",
            resource=data["scenario_id"],
            decision={
                "status": data.get("status"),
                "wave_id": data.get("wave_id"),
            },
            metadata=data,
        )


async def main():
    runner = ChaosRunner()
    await runner.run_wave(wave_size=3)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
