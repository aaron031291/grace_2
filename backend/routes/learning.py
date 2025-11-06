from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc

from ..auth import get_current_user
from ..settings import settings
from ..models import async_session
from ..self_heal_models import LearningLog

router = APIRouter(prefix="/api/self_heal", tags=["self-heal-learning"])  # feature-gated in main


@router.get("/learning")
async def get_learning(service: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=500), current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        q = select(LearningLog)
        if service:
            q = q.where(LearningLog.service == service)
        q = q.order_by(desc(LearningLog.created_at)).limit(limit)
        res = await session.execute(q)
        rows = res.scalars().all()

        entries: List[Dict[str, Any]] = [
            {
                "id": r.id,
                "service": r.service,
                "signal_ref": r.signal_ref,
                "diagnosis": r.diagnosis,
                "action": r.action,
                "outcome": r.outcome,
                "created_at": r.created_at,
            }
            for r in rows
        ]

        # Simple aggregate: success rate by diagnosis->action if outcome contains "succeeded"
        stats: Dict[str, Dict[str, int]] = {}
        for r in rows:
            diag = (r.diagnosis or "unknown").strip()
            act = (r.action or "unknown").strip()
            key = f"{diag}::{act}"
            d = stats.setdefault(key, {"total": 0, "success": 0})
            d["total"] += 1
            if r.outcome and ("succeeded" in r.outcome or '"status": "succeeded"' in r.outcome):
                d["success"] += 1

        # Convert stats to list with rates
        agg = [
            {
                "path": k,
                "total": v["total"],
                "success": v["success"],
                "success_rate": (v["success"] / v["total"]) if v["total"] else 0.0,
            }
            for k, v in stats.items()
        ]

        return {"entries": entries, "count": len(entries), "aggregates": agg}
