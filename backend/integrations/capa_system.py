from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    # Prefer Pydantic v2
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - basic fallback
    class BaseModel:  # type: ignore
        def __init__(self, **data):
            self.__dict__.update(data)
        def model_dump(self) -> Dict[str, Any]:  # minimal compat
            return dict(self.__dict__)
    def Field(default=None, **kwargs):  # type: ignore
        return default


class CAPATicket(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)  # type: ignore[arg-type]
    metadata: Dict[str, Any] = Field(default_factory=dict)  # type: ignore[arg-type]
    status: str = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)  # type: ignore[arg-type]


class CAPASystem:
    """
    Minimal CAPA integration adapter.

    Provides an async `create_capa` that accepts a `category` parameter and returns a CAPATicket.
    Replace/extend this adapter to forward tickets to your real CAPA provider or database.
    """

    VALID_CATEGORIES = {"security", "quality", "reliability", "compliance", "performance"}

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
        if category and category not in self.VALID_CATEGORIES:
            valid = ", ".join(sorted(self.VALID_CATEGORIES))
            raise ValueError(f"Invalid category: {category} (valid: {valid})")

        ticket = CAPATicket(
            id=f"capa_{int(datetime.utcnow().timestamp() * 1000)}",
            title=title,
            description=description,
            severity=severity,
            category=category,
            tags=tags or [],
            metadata=metadata or {},
        )

        # TODO: Persist to DB or send to external CAPA system.
        return ticket


__all__ = ["CAPASystem", "CAPATicket"]
