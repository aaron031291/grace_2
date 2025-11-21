"""
Unified Audit Logger

Provides a single entrypoint for writing immutable audit events so every
subsystem shares the same append-only log with cryptographic chaining.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from backend.logging.immutable_log import immutable_log


class UnifiedAuditLogger:
    """
    Synchronous-friendly wrapper around the immutable log.
    Use `log_event` for fire-and-forget audit entries, or `log_event_async`
    inside async contexts.
    """

    def __init__(self) -> None:
        self._log = immutable_log

    async def log_event_async(
        self,
        *,
        actor: str,
        action: str,
        resource: str = "system",
        subsystem: str = "audit",
        result: str = "success",
        payload: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
    ) -> int:
        payload = payload or {}
        payload.setdefault("timestamp", datetime.utcnow().isoformat())

        return await self._log.append(
            actor=actor,
            action=action,
            resource=resource,
            subsystem=subsystem,
            payload=payload,
            result=result,
            signature=signature,
        )

    def log_event(
        self,
        *,
        actor: str,
        action: str,
        resource: str = "system",
        subsystem: str = "audit",
        result: str = "success",
        payload: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
    ) -> int:
        coro = self.log_event_async(
            actor=actor,
            action=action,
            resource=resource,
            subsystem=subsystem,
            result=result,
            payload=payload,
            signature=signature,
        )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            loop.create_task(coro)
            return 0
        return asyncio.run(coro)


_audit_logger = UnifiedAuditLogger()


def get_audit_logger() -> UnifiedAuditLogger:
    return _audit_logger


def audit_log(
    *,
    actor: str,
    action: str,
    resource: str = "system",
    subsystem: str = "audit",
    result: str = "success",
    payload: Optional[Dict[str, Any]] = None,
    signature: Optional[str] = None,
) -> int:
    """Compatibility helper so legacy callsites can import audit_log."""
    return _audit_logger.log_event(
        actor=actor,
        action=action,
        resource=resource,
        subsystem=subsystem,
        result=result,
        payload=payload,
        signature=signature,
    )
