from __future__ import annotations
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth import get_current_user
from ..models import async_session
from ..settings import settings
from ..health_models import Service, HealthSignal, HealthState
from ..health.aggregator import compute_health_state
from ..health.triage import diagnose
from ..schemas_extended import HealthIngestSignalResponse, HealthStateResponse, TriageDiagnoseResponse

router = APIRouter(tags=["health-unified"])  # prefix added conditionally in main


class SignalIngest(BaseModel):
    service: str = Field(..., description="Service name")
    signal_type: str
    metric_key: Optional[str] = None
    value: Optional[float] = None
    status: str = Field(..., description="ok|degraded|down|failed")
    severity: Optional[str] = Field(None, description="low|medium|high|critical")
    fingerprint: Optional[str] = None


async def _get_or_create_service(session: AsyncSession, name: str) -> Service:
    res = await session.execute(select(Service).where(Service.name == name))
    svc = res.scalar_one_or_none()
    if svc:
        return svc
    svc = Service(name=name)
    session.add(svc)
    await session.flush()
    return svc


@router.post("/health/ingest_signal", response_model=HealthIngestSignalResponse)
async def ingest_signal(payload: SignalIngest, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        svc = await _get_or_create_service(session, payload.service)
        sig = HealthSignal(
            service_id=svc.id,
            signal_type=payload.signal_type,
            metric_key=payload.metric_key,
            value=payload.value,
            status=payload.status,
            severity=payload.severity,
            fingerprint=payload.fingerprint,
        )
        session.add(sig)
        await session.commit()
        return HealthIngestSignalResponse(
            ok=True,
            service_id=svc.id,
            signal_id=sig.id,
            execution_trace=None,
            data_provenance=[]
        )


@router.get("/health/state", response_model=HealthStateResponse)
async def get_health_state(service: str = Query(...), current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        svc = await _get_or_create_service(session, service)
        # Load recent signals (we'll fetch a reasonable window)
        res = await session.execute(
            select(HealthSignal).where(HealthSignal.service_id == svc.id).order_by(HealthSignal.created_at.desc()).limit(200)
        )
        signals = res.scalars().all()
        rollup = compute_health_state(svc.id, signals)

        # Upsert HealthState
        existing_res = await session.execute(select(HealthState).where(HealthState.service_id == svc.id))
        st = existing_res.scalar_one_or_none()
        if st:
            st.status = rollup["status"]
            st.confidence = rollup["confidence"]
            st.top_symptoms = rollup.get("top_symptoms")
        else:
            st = HealthState(
                service_id=svc.id,
                status=rollup["status"],
                confidence=rollup["confidence"],
                top_symptoms=rollup.get("top_symptoms"),
            )
            session.add(st)
        await session.commit()
        return HealthStateResponse(
            service=svc.name,
            status=st.status,
            confidence=st.confidence,
            top_symptoms=st.top_symptoms,
            execution_trace=None,
            data_provenance=[]
        )


class DiagnoseRequest(BaseModel):
    service: str


@router.post("/triage/diagnose", response_model=TriageDiagnoseResponse)
async def triage_diagnose(req: DiagnoseRequest, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    async with async_session() as session:
        svc = await _get_or_create_service(session, req.service)
        res = await session.execute(
            select(HealthSignal).where(HealthSignal.service_id == svc.id).order_by(HealthSignal.created_at.desc()).limit(200)
        )
        signals = res.scalars().all()
        findings = diagnose(svc.id, signals)
        return TriageDiagnoseResponse(
            service=svc.name,
            diagnoses=findings,
            execution_trace=None,
            data_provenance=[]
        )
