from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from ..auth import get_current_user
from ..settings import settings
from ..models import async_session
from ..self_heal_models import Incident, IncidentEvent
from ..integrations.notify import notify
from ..schemas_extended import IncidentNotifyResponse, IncidentAckResponse, IncidentDetailResponse

router = APIRouter(prefix="/api/incidents", tags=["incidents"])  # feature-gated in main


class IncidentNotify(BaseModel):
    service: str = Field(...)
    severity: Optional[str] = Field(None, description="low|medium|high|critical")
    title: Optional[str] = None
    summary: Optional[str] = None
    event_type: str = Field("notification")
    details: Optional[Dict[str, Any]] = None


class IncidentAck(BaseModel):
    id: int
    actor: Optional[str] = None


@router.post("/notify")
async def incident_notify(body: IncidentNotify, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        inc = Incident(service=body.service, severity=body.severity, title=body.title, summary=body.summary)
        session.add(inc)
        await session.flush()
        ev = IncidentEvent(
            incident_id=inc.id,
            event_type=body.event_type or "notification",
            details=(body.details and str(body.details)) or body.summary,
        )
        session.add(ev)
        await session.commit()

        # Fire a best-effort notification
        try:
            notify(
                event="incident.notify",
                payload={
                    "id": inc.id,
                    "service": body.service,
                    "severity": body.severity,
                    "title": body.title,
                    "summary": body.summary,
                    "event_type": body.event_type,
                },
            )
        except Exception:
            pass

        return {"ok": True, "incident_id": inc.id}


@router.post("/ack")
async def incident_ack(body: IncidentAck, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        res = await session.execute(select(Incident).where(Incident.id == body.id))
        inc = res.scalar_one_or_none()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")
        inc.status = "ack"
        ev = IncidentEvent(
            incident_id=inc.id,
            event_type="ack",
            details=f"ack_by={body.actor or current_user}",
        )
        session.add(ev)
        await session.commit()

        try:
            notify(
                event="incident.ack",
                payload={"id": inc.id, "service": inc.service, "actor": body.actor or current_user},
            )
        except Exception:
            pass

        return {"ok": True, "incident_id": inc.id, "status": inc.status}


@router.get("/{incident_id}")
async def get_incident(incident_id: int, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        res = await session.execute(select(Incident).where(Incident.id == incident_id))
        inc = res.scalar_one_or_none()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")
        evs = await session.execute(select(IncidentEvent).where(IncidentEvent.incident_id == incident_id).order_by(IncidentEvent.created_at.asc()))
        events = [
            {
                "id": e.id,
                "type": e.event_type,
                "details": e.details,
                "created_at": e.created_at,
            }
            for e in evs.scalars().all()
        ]
        return {
            "id": inc.id,
            "service": inc.service,
            "severity": inc.severity,
            "status": inc.status,
            "title": inc.title,
            "summary": inc.summary,
            "created_at": inc.created_at,
            "resolved_at": inc.resolved_at,
            "events": events,
        }
