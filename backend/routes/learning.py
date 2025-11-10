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

        # Aggregates: success rates per diagnosis->action overall and time buckets (24h, 7d)
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        buckets = {
            "all": None,
            "24h": now - timedelta(hours=24),
            "7d": now - timedelta(days=7),
        }

        def _is_success(action_s: str, outcome_s: str) -> bool:
            a = action_s or ""
            o = outcome_s or ""
            return ('"status": "succeeded"' in a) or ('"status": "succeeded"' in o) or ('"result": "ok"' in o)

        aggregates: Dict[str, Dict[str, Dict[str, int]]] = {b: {} for b in buckets.keys()}
        for r in rows:
            # Determine creation time
            ts = getattr(r, "created_at", None)
            for b_name, cutoff in buckets.items():
                if cutoff is not None and ts and ts < cutoff:
                    continue
                diag = (r.diagnosis or "unknown").strip()
                act = (r.action or "unknown").strip()
                key = f"{diag}::{act}"
                bucket = aggregates[b_name].setdefault(key, {"total": 0, "success": 0})
                bucket["total"] += 1
                if _is_success(r.action or "", r.outcome or ""):
                    bucket["success"] += 1

        def _to_list(stats_map: Dict[str, Dict[str, int]]):
            return [
                {
                    "path": k,
                    "total": v["total"],
                    "success": v["success"],
                    "success_rate": (v["success"] / v["total"]) if v["total"] else 0.0,
                }
                for k, v in stats_map.items()
            ]

        agg = {name: _to_list(data) for name, data in aggregates.items()}

        return {"entries": entries, "count": len(entries), "aggregates": agg}
