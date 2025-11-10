"""Minimal structured logging helper for backend actions.

Emits JSON lines to stdout with consistent keys and conservative PII handling.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


REDACT_KEYS = {"password", "token", "authorization", "secret", "jwt"}
MAX_VALUE_LEN = int(os.getenv("LOG_TRUNCATE_LEN", "256"))


def _truncate(value: Any) -> Any:
    try:
        s = str(value)
    except Exception:
        return value
    if len(s) > MAX_VALUE_LEN:
        return s[:MAX_VALUE_LEN] + "…"
    return s


def _redact_payload(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return None
    redacted: Dict[str, Any] = {}
    for k, v in payload.items():
        key = str(k).lower()
        if key in REDACT_KEYS:
            redacted[k] = "[REDACTED]"
        else:
            redacted[k] = _truncate(v)
    return redacted


def log_event(
    *,
    action: str,
    actor: str,
    resource: str = "unknown",
    outcome: str = "ok",
    verification_id: Optional[str] = None,
    request_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    extras: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit a structured JSON log line to stdout.

    Only stringifiable values are included; values are truncated.
    """
    try:
        entry: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "actor": actor,
            "resource": resource,
            "outcome": outcome,
        }
        if verification_id:
            entry["verification_id"] = verification_id
        if request_id:
            entry["request_id"] = request_id
        redacted = _redact_payload(payload)
        if redacted:
            entry["payload"] = redacted
        if extras:
            # Shallow merge with truncation
            entry["extras"] = {k: _truncate(v) for k, v in extras.items()}
        print(json.dumps(entry, ensure_ascii=False))
    except Exception:
        # Fail open: logging must not break the request handling
        pass


def ensure_utf8_console() -> None:
    """Best-effort to make console UTF-8 safe on Windows and others.
    - Sets PYTHONIOENCODING=utf-8
    - Reconfigures stdout/stderr to utf-8 with errors='replace'
    - On Windows, attempts to switch console codepages to 65001
    This prevents crashes when logs include emojis or non-ASCII characters.
    """
    try:
        import sys
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        # Reconfigure standard streams if possible (Python 3.7+)
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
        # Windows console code page tweak
        if os.name == "nt":
            try:
                import ctypes
                CP_UTF8 = 65001
                ctypes.windll.kernel32.SetConsoleOutputCP(CP_UTF8)
                ctypes.windll.kernel32.SetConsoleCP(CP_UTF8)
            except Exception:
                # Fall back silently; stream reconfigure usually suffices
                pass
    except Exception:
        # Never raise from a logging/console helper
        pass
