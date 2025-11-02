from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.sql import func
from ..governance_models import SecurityEvent, SecurityRule
from ..models import async_session
from ..auth import get_current_user

router = APIRouter(prefix="/api/hunter", tags=["hunter"])

@router.get("/alerts")
async def list_alerts(status: str = None, limit: int = 50):
    async with async_session() as session:
        query = select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(limit)
        if status:
            query = query.where(SecurityEvent.status == status)
        result = await session.execute(query)
        return [
            {
                "id": ev.id,
                "actor": ev.actor,
                "action": ev.action,
                "resource": ev.resource,
                "severity": ev.severity,
                "status": ev.status,
                "created_at": ev.created_at,
            }
            for ev in result.scalars().all()
        ]

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    status: str,
    note: str = "",
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        event = await session.get(SecurityEvent, alert_id)
        if not event:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        event.status = status
        event.resolved_at = func.now()
        event.resolution_note = note
        await session.commit()
    
    return {"status": event.status}

@router.get("/rules")
async def list_rules():
    async with async_session() as session:
        result = await session.execute(select(SecurityRule))
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "severity": r.severity,
                "action": r.action
            }
            for r in result.scalars().all()
        ]
