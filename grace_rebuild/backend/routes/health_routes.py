from fastapi import APIRouter
from sqlalchemy import select
from ..governance_models import HealthCheck, HealingAction
from ..models import async_session

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/status")
async def status(limit: int = 10):
    async with async_session() as session:
        checks = await session.execute(
            select(HealthCheck).order_by(HealthCheck.created_at.desc()).limit(limit)
        )
        actions = await session.execute(
            select(HealingAction).order_by(HealingAction.created_at.desc()).limit(limit)
        )
    
    return {
        "checks": [
            {
                "component": c.component,
                "status": c.status,
                "latency_ms": c.latency_ms,
                "error": c.error,
                "at": c.created_at
            }
            for c in checks.scalars().all()
        ],
        "actions": [
            {
                "component": a.component,
                "action": a.action,
                "result": a.result,
                "detail": a.detail,
                "at": a.created_at
            }
            for a in actions.scalars().all()
        ],
    }
