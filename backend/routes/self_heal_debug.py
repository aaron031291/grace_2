from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_current_user
from ..settings import settings

# Debug/observability endpoints for self-heal (observe-only). Feature-gated.
router = APIRouter(prefix="/api/self_heal", tags=["self-heal-debug"])  # included conditionally in main


@router.get("/scheduler_counters")
async def scheduler_counters(current_user: str = Depends(get_current_user)):
    """Return in-memory scheduler counters (reset on process restart).
    Safe, read-only, and only available when self-heal features are enabled.
    """
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    try:
        # Lazy import to avoid import-time issues
        from ..self_heal.scheduler import scheduler
        return scheduler.snapshot_counters()
    except Exception:
        # Keep safe and avoid leaking internal errors
        return {"global": {}, "per_service": {}}
