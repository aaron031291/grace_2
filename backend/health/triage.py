from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

RECENT_TTL = timedelta(minutes=10)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_recent(dt: datetime | None) -> bool:
    if not dt:
        return False
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (_now() - dt) <= RECENT_TTL


def select_recent(signals: List[Any]) -> List[Any]:
    return [s for s in signals if _is_recent(getattr(s, "created_at", None))]


def diagnose(service_id: int, signals: List[Any]) -> List[Dict[str, Any]]:
    """
    Deterministic, rule-first triage mapping recent signals to diagnoses.

    Returns a list of dicts with keys: code, title, likelihood, impact, reasons, suggested_playbooks
    """
    recent = select_recent(signals)
    diagnoses: List[Dict[str, Any]] = []

    # Helper accumulators
    has_down = any(getattr(s, "status", None) in {"down", "failed"} for s in recent)
    has_critical = any(getattr(s, "severity", None) == "critical" for s in recent)
    has_high = any(getattr(s, "severity", None) == "high" for s in recent)

    # Metric-specific hints
    high_latency = any(
        (getattr(s, "metric_key", None) or "").endswith("latency_ms") and (float(getattr(s, "value", 0)) >= 1000)
        for s in recent
    )
    error_rate = any(
        (getattr(s, "metric_key", None) or "") in {"http_5xx_rate", "error_rate"} and (float(getattr(s, "value", 0)) >= 0.05)
        for s in recent
    )

    if has_down or has_critical:
        diagnoses.append({
            "code": "service_down",
            "title": "Service is down",
            "likelihood": 0.85 if has_down else 0.75,
            "impact": "critical",
            "reasons": [
                r for r in [
                    "Recent 'down/failed' status" if has_down else None,
                    "Critical severity signal present" if has_critical else None,
                ] if r
            ],
            "suggested_playbooks": [
                {"code": "restart_service", "parameters": {"graceful": True}},
                {"code": "rollback_flag", "parameters": {"flag": "new_release", "state": False}},
            ],
        })

    if high_latency and not has_down:
        diagnoses.append({
            "code": "latency_spike",
            "title": "High latency detected",
            "likelihood": 0.7 if has_high else 0.6,
            "impact": "high" if has_high else "medium",
            "reasons": [
                "Recent latency_ms >= 1000",
                "High severity signal present" if has_high else "",
            ],
            "suggested_playbooks": [
                {"code": "scale_up_instances", "parameters": {"min_delta": 1}},
                {"code": "warm_cache", "parameters": {}},
            ],
        })

    if error_rate and not has_down:
        diagnoses.append({
            "code": "elevated_errors",
            "title": "Elevated error rate",
            "likelihood": 0.65,
            "impact": "high" if has_high else "medium",
            "reasons": [
                "Error rate >= 5% in recent window",
            ],
            "suggested_playbooks": [
                {"code": "restart_service", "parameters": {"graceful": True}},
                {"code": "flush_circuit_breakers", "parameters": {}},
            ],
        })

    # Fallback hypothesis if nothing else matched but degraded signals exist
    has_degraded = any(getattr(s, "status", None) == "degraded" for s in recent)
    if not diagnoses and has_degraded:
        diagnoses.append({
            "code": "general_degradation",
            "title": "General degradation observed",
            "likelihood": 0.5,
            "impact": "medium",
            "reasons": ["Recent degraded signals without clear root cause"],
            "suggested_playbooks": [
                {"code": "increase_logging", "parameters": {"level": "DEBUG", "ttl_min": 15}},
            ],
        })

    return diagnoses
