from __future__ import annotations
import os
import json
from typing import Optional, Dict, Any

# Simple notification stub: prints to console and optionally POSTs to a webhook URL
# Controlled via environment variable: NOTIFY_WEBHOOK_URL

try:
    import httpx  # lightweight optional dependency; if missing, we fallback to console only
except Exception:  # pragma: no cover
    httpx = None  # type: ignore


def _webhook_url() -> Optional[str]:
    return os.getenv("NOTIFY_WEBHOOK_URL")


def notify(event: str, payload: Dict[str, Any]) -> None:
    """Send a best-effort notification.

    - Always prints to console for visibility during dev.
    - If NOTIFY_WEBHOOK_URL is set and httpx is available, perform a non-blocking POST.
    """
    try:
        print(f"[notify] {event}: {json.dumps(payload, default=str)[:2000]}")
    except Exception:
        # best-effort logging only
        pass

    url = _webhook_url()
    if not url or httpx is None:
        return
    try:
        # fire-and-forget style; ignore response
        with httpx.Client(timeout=3.0) as client:
            client.post(url, json={"event": event, "payload": payload})
    except Exception:
        # Do not raise from notifications
        pass
