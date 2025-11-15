"""
Advanced monitoring triggers used by the coding agent and self-healing loops.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TelemetryDriftTrigger:
    """Detect API schema drift by comparing live responses to known schemas."""

    def __init__(self, known_schemas: Dict[str, Dict], base_url: str = "http://localhost:8000"):
        self.known_schemas = known_schemas or {}
        self.base_url = base_url.rstrip("/")

    async def check(self) -> Optional[Dict]:
        issues = []

        if not self.known_schemas:
            return None

        try:
            import httpx
        except ImportError:  # pragma: no cover - dependency optional
            logger.warning("httpx not installed - telemetry drift checks skipped")
            return None

        async with httpx.AsyncClient(timeout=5.0) as client:
            for endpoint, expected_schema in self.known_schemas.items():
                url = f"{self.base_url}{endpoint}"
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    actual = response.json()

                    expected_fields = set(expected_schema.keys())
                    actual_fields = set(actual.keys())

                    missing = expected_fields - actual_fields
                    extra = actual_fields - expected_fields

                    if missing or extra:
                        issues.append(
                            {
                                "type": "schema_drift",
                                "endpoint": endpoint,
                                "missing_fields": sorted(missing),
                                "extra_fields": sorted(extra),
                                "severity": "high",
                            }
                        )
                except Exception as exc:  # pragma: no cover - network variability
                    logger.warning("Telemetry drift check failed for %s: %s", url, exc)

        if issues:
            return {
                "trigger": "telemetry_drift",
                "issues": issues,
                "action": "regenerate_client",
                "target": "coding_agent",
            }

        return None


class ResourcePressureTrigger:
    """
    Monitor CPU/memory pressure. Falls back to load average when psutil missing.
    """

    def __init__(self, cpu_threshold: float = 85.0, memory_threshold: float = 90.0):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    async def check(self) -> Optional[Dict]:
        issues = []

        try:
            import psutil  # type: ignore

            cpu_percent = await asyncio.get_running_loop().run_in_executor(
                None, lambda: psutil.cpu_percent(interval=1.0)
            )
            memory = psutil.virtual_memory()

            if cpu_percent > self.cpu_threshold:
                issues.append(
                    {
                        "type": "high_cpu",
                        "value": cpu_percent,
                        "threshold": self.cpu_threshold,
                        "severity": "high",
                    }
                )

            if memory.percent > self.memory_threshold:
                issues.append(
                    {
                        "type": "high_memory",
                        "value": memory.percent,
                        "threshold": self.memory_threshold,
                        "severity": "high",
                    }
                )
        except ImportError:
            logger.warning("psutil not installed - resource monitoring degraded")
            if hasattr(os, "getloadavg"):
                load_avg = os.getloadavg()[0]
                if load_avg > 4.0:
                    issues.append(
                        {
                            "type": "high_load_average",
                            "load_avg": load_avg,
                            "severity": "high",
                        }
                    )
        except Exception as exc:  # pragma: no cover
            logger.error("Resource pressure trigger failed: %s", exc)

        if issues:
            return {
                "trigger": "resource_pressure",
                "issues": issues,
                "action": "shed_load",
                "target": "self_healing",
            }

        return None


class PredictiveFailureAnalyzer:
    """Predict failure risk for files using ML when available."""

    def __init__(self, artifact_dir: Optional[Path] = None):
        base_dir = artifact_dir or Path(__file__).resolve().parents[1] / "ml_artifacts"
        self.model_path = base_dir / "failure_predictor.pkl"
        self._model = None
        self.failure_predictions: Dict[str, float] = {}

    def predict_failure_risk(self, file_path: str) -> float:
        try:
            model = self._load_model()
            if model is None:
                return self._heuristic_risk(file_path)

            features = self._extract_code_features(file_path)
            if features is None:
                return 0.0

            proba = model.predict_proba([features])[0][1]
            risk = float(proba)
            self.failure_predictions[file_path] = risk
            return risk
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Failure prediction fallback for %s: %s", file_path, exc)
            return self._heuristic_risk(file_path)

    # ------------------------------------------------------------------
    # PRIVATE HELPERS
    # ------------------------------------------------------------------
    def _load_model(self):
        if self._model is not None or not self.model_path.exists():
            return self._model

        try:
            import joblib  # type: ignore

            self._model = joblib.load(self.model_path)
        except Exception as exc:
            logger.warning("Unable to load failure predictor model: %s", exc)
            self._model = None
        return self._model

    def _heuristic_risk(self, file_path: str) -> float:
        path = Path(file_path)
        if not path.exists():
            return 0.0

        try:
            code = path.read_text()
        except Exception:
            return 0.0

        lines = code.splitlines()
        risk = 0.0

        if len(lines) > 500:
            risk += 0.2

        if code.count("except Exception") > 5:
            risk += 0.3

        if code.count("TODO") > 3:
            risk += 0.2

        risk = min(risk, 0.95)
        self.failure_predictions[file_path] = risk
        return risk

    def _extract_code_features(self, file_path: str) -> Optional[List[float]]:
        path = Path(file_path)
        if not path.exists():
            return None

        code = path.read_text()
        lines = code.splitlines()
        line_count = len(lines)

        def safe_ratio(numerator: int, denominator: int) -> float:
            return numerator / denominator if denominator else float(numerator)

        features: List[float] = [
            float(line_count),
            float(code.count("except Exception")),
            float(code.count("TODO")),
            float(code.count("import ")),
            float(code.count("def ")),
            float(code.count("class ")),
            float(len(code)) / max(line_count, 1),
            safe_ratio(code.count("async "), code.count("def ")),
        ]
        return features
