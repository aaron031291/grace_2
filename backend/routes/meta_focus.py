from __future__ import annotations
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from ..auth import get_current_user
from ..settings import settings
from ..models import async_session
from ..health_models import HealthState
from ..self_heal_models import Incident, PlaybookRun

router = APIRouter(prefix="/api/meta", tags=["meta-focus"])  # feature-gated in main


@router.get("/focus")
async def get_focus(current_user: str = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Read-only meta focus vector that surfaces "health distress" pressure for the agentic meta-controller.
    Combines recent degraded/critical health states, open incidents, and recent failed/proposed runs.
    """
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")

    now = datetime.now(timezone.utc)
    recent_cutoff = now - timedelta(hours=1)
    focus: Dict[str, Any] = {
        "health": {
            "degraded": 0,
            "critical": 0,
        },
        "incidents": {
            "open": 0,
        },
        "self_heal": {
            "proposed_last_hour": 0,
            "failed_last_hour": 0,
        },
        "score": 0.0,
        "as_of": now.isoformat(),
    }

    async with async_session() as session:
        # Health state rollups
        hs_res = await session.execute(select(HealthState))
        hs_list = hs_res.scalars().all()
        for st in hs_list:
            status = (getattr(st, "status", "") or "").lower()
            if status == "degraded":
                focus["health"]["degraded"] += 1
            elif status == "critical":
                focus["health"]["critical"] += 1
        
        # Open incidents
        inc_res = await session.execute(select(Incident).where(Incident.status == "open"))
        focus["incidents"]["open"] = len(inc_res.scalars().all())

        # Recent playbook runs
        pr_res = await session.execute(select(PlaybookRun))
        for run in pr_res.scalars().all():
            ct = getattr(run, "created_at", None)
            if ct and ct.tzinfo is None:
                ct = ct.replace(tzinfo=timezone.utc)
            if ct and ct >= recent_cutoff:
                if getattr(run, "status", "") == "proposed":
                    focus["self_heal"]["proposed_last_hour"] += 1
                if getattr(run, "status", "") in {"failed", "rolled_back", "aborted"}:
                    focus["self_heal"]["failed_last_hour"] += 1

    # Compute a simple score: weighted sum
    degraded = focus["health"]["degraded"]
    critical = focus["health"]["critical"]
    open_inc = focus["incidents"]["open"]
    failed = focus["self_heal"]["failed_last_hour"]
    proposed = focus["self_heal"]["proposed_last_hour"]

    # Weights chosen conservatively; tune later
    score = 0.0
    score += degraded * 0.5
    score += critical * 2.0
    score += open_inc * 1.0
    score += failed * 1.5
    score += min(proposed, 5) * 0.2  # proposal pressure but bounded
    focus["score"] = score

    return focus
