from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import get_current_user
from ..settings import settings
from ..self_heal import playbooks as pb
from ..schemas_extended import PlaybooksListResponse

router = APIRouter(prefix="/api/playbooks", tags=["playbooks"])  # feature-gated in main via settings


class PlanRequest(BaseModel):
    service: str = Field(..., description="Service name (e.g., backend_api)")
    diagnosis: Optional[str] = Field(None, description="Diagnosis code (e.g., service_down, latency_spike)")
    severity: Optional[str] = Field(None, description="low|medium|high|critical")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Template parameter overrides")


@router.get("/", summary="List available playbook templates")
async def list_playbooks(current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        # Router is conditionally included, but double-guard for safety
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    return {"templates": pb.list_templates(), "count": len(pb.list_templates())}


@router.post("/plan", summary="Produce a dry-run recovery plan from templates")
async def plan_playbooks(req: PlanRequest, current_user: str = Depends(get_current_user)):
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Endpoint disabled")
    plan = pb.plan(
        service=req.service,
        diagnosis_code=req.diagnosis,
        severity=req.severity,
        parameters=req.parameters or {},
    )
    return plan
