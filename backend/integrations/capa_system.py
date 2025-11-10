from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CAPATicket:
    id: str
    title: str
    description: str
    severity: str
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Compatibility for callers expecting Pydantic-like API
    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)


class CAPASystem:
    """
    Minimal CAPA integration adapter.

    Provides an async `create_capa` that accepts a `category` parameter and returns a CAPATicket.
    Replace/extend this adapter to forward tickets to your real CAPA provider or database.
    """

    VALID_CATEGORIES = {"security", "quality", "reliability", "compliance", "performance"}

    def __init__(self, *, strict: bool = False):
        self.strict = strict

    def _normalize_category(self, category: Optional[str]) -> Optional[str]:
        if not category:
            return None
        c = str(category).strip().lower()
        mapping = {
            "sec": "security",
            "perf": "performance",
        }
        c = mapping.get(c, c)
        if c in self.VALID_CATEGORIES:
            return c
        if self.strict:
            valid = ", ".join(sorted(self.VALID_CATEGORIES))
            raise ValueError(f"Invalid category: {category} (valid: {valid})")
        logger.warning("Invalid CAPA category '%s'; coercing to None", category)
        return None

    async def create_capa(
        self,
        *,
        title: str,
        description: str,
        severity: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CAPATicket:
        norm_cat = self._normalize_category(category)

        ticket = CAPATicket(
            id=f"capa_{int(datetime.utcnow().timestamp() * 1000)}",
            title=title,
            description=description,
            severity=severity,
            category=norm_cat,
            tags=list(tags or []),
            metadata=dict(metadata or {}),
        )

        # TODO: Persist to DB or send to external CAPA system.
        return ticket


# Feature flag for auto-creation in diagnostics flows
ENABLE_CAPA_AUTOCREATE = os.getenv("ENABLE_CAPA_AUTOCREATE", "0").lower() in ("1", "true", "yes")


def _category_for_diagnostic(diag_type: str) -> Optional[str]:
    t = (diag_type or "").lower()
    if any(k in t for k in ("xss", "sql", "sec", "leak", "tamper", "vuln")):
        return "security"
    if "latency" in t or "perf" in t or "throughput" in t:
        return "performance"
    if any(k in t for k in ("availability", "downtime", "error_rate", "crash", "failover")):
        return "reliability"
    if any(k in t for k in ("compliance", "gdpr", "sox", "hipaa")):
        return "compliance"
    return "quality"


async def auto_create_from_diagnostic(diag: Dict[str, Any], *, capa: Optional[CAPASystem] = None) -> Optional[CAPATicket]:
    """Auto-create a CAPA ticket for high/critical diagnostics when enabled.

    Returns the created ticket or None if not created.
    """
    if not ENABLE_CAPA_AUTOCREATE:
        return None

    capa = capa or CAPASystem()

    severity = str(diag.get("severity", "")).lower()
    status = str(diag.get("status", "")).lower()
    if severity not in ("critical", "high"):
        return None
    if status and status not in ("degraded", "failed", "critical"):
        return None

    diag_type = diag.get("diagnosis") or diag.get("type") or diag.get("name") or "issue"
    category = _category_for_diagnostic(diag_type)

    title = f"{severity.title()}: {diag_type} detected"
    description = (
        diag.get("details")
        or diag.get("summary")
        or "Auto-created from diagnostic finding"
    )

    try:
        ticket = await capa.create_capa(
            title=title,
            description=description,
            severity=severity,
            category=category,
            tags=["auto", "diagnostics"],
            metadata={"diagnostic": diag},
        )
        logger.info(
            "CAPA auto-created id=%s category=%s severity=%s", ticket.id, ticket.category, ticket.severity
        )
        return ticket
    except Exception as e:
        logger.exception("CAPA auto-creation failed: %s", e)
        return None


__all__ = ["CAPASystem", "CAPATicket", "auto_create_from_diagnostic", "ENABLE_CAPA_AUTOCREATE"]
