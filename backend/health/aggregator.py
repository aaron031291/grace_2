from __future__ import annotations
from datetime import datetime, timedelta, timezone
import json
from typing import List, Dict, Any

# TTL window to consider signals "recent"
RECENT_TTL = timedelta(minutes=10)


def compute_health_state(service_id: int, signals: List[Any]) -> Dict[str, Any]:
    """Compute a simple deterministic health state from recent signals.

    signals: iterable of ORM HealthSignal-like objects with attributes:
      - status (str): ok|degraded|down|failed
      - severity (str|None): low|medium|high|critical
      - created_at (datetime)
      - signal_type, metric_key, value
    """
    now = datetime.now(timezone.utc)
    recent = []
    for s in signals:
        created = s.created_at
        # tolerate naive datetimes by assuming UTC
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created and (now - created) <= RECENT_TTL:
            recent.append(s)

    status = "healthy"
    confidence = 0.6

    if any((getattr(s, "severity", None) == "critical") or (getattr(s, "status", None) in ("down", "failed")) for s in recent):
        status = "critical"
        confidence = 0.9
    elif any((getattr(s, "severity", None) == "high") or (getattr(s, "status", None) == "degraded") for s in recent):
        status = "degraded"
        confidence = 0.75

    # Capture up to 5 most recent symptoms
    symptoms = []
    for s in sorted(recent, key=lambda x: x.created_at or now, reverse=True)[:5]:
        symptoms.append({
            "type": getattr(s, "signal_type", None),
            "metric": getattr(s, "metric_key", None),
            "status": getattr(s, "status", None),
            "sev": getattr(s, "severity", None),
            "value": getattr(s, "value", None),
        })

    return {
        "service_id": service_id,
        "status": status,
        "confidence": confidence,
        "top_symptoms": json.dumps(symptoms) if symptoms else None,
    }
