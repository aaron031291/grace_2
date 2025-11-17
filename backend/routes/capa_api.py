"""
CAPA API - Corrective and Preventive Actions
ISO 9001 requirement for quality management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/capa", tags=["CAPA"])


# Models

class CreateCAPARequest(BaseModel):
    title: str
    description: str
    capa_type: str  # corrective, preventive
    severity: str  # critical, high, medium, low
    source: str
    related_update_id: Optional[str] = None
    detected_by: str = "system"
    evidence: Optional[Dict[str, Any]] = None


class RootCauseAnalysisRequest(BaseModel):
    capa_id: str
    root_cause: str
    analysis: Dict[str, Any]
    analyst: str = "system"


class PlanActionsRequest(BaseModel):
    capa_id: str
    corrective_actions: List[Dict[str, Any]]
    preventive_actions: Optional[List[Dict[str, Any]]] = None
    implementation_plan: Optional[Dict[str, Any]] = None
    planner: str = "system"


# Routes

@router.post("/create")
async def create_capa(request: CreateCAPARequest):
    """Create new CAPA record"""
    
    try:
        from backend.capa_system import capa_system, CAPAType, CAPASeverity
        
        capa_id = await capa_system.create_capa(
            title=request.title,
            description=request.description,
            capa_type=CAPAType(request.capa_type),
            severity=CAPASeverity(request.severity),
            source=request.source,
            related_update_id=request.related_update_id,
            detected_by=request.detected_by,
            evidence=request.evidence
        )
        
        return {
            "capa_id": capa_id,
            "status": "created",
            "message": f"CAPA created: {request.title}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create CAPA: {e}")


@router.post("/root-cause")
async def submit_root_cause(request: RootCauseAnalysisRequest):
    """Submit root cause analysis"""
    
    try:
        from backend.capa_system import capa_system
        
        await capa_system.conduct_root_cause_analysis(
            capa_id=request.capa_id,
            root_cause=request.root_cause,
            analysis=request.analysis,
            analyst=request.analyst
        )
        
        return {
            "capa_id": request.capa_id,
            "status": "analyzed",
            "message": "Root cause analysis recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan-actions")
async def plan_actions(request: PlanActionsRequest):
    """Plan corrective and preventive actions"""
    
    try:
        from backend.capa_system import capa_system
        
        await capa_system.plan_actions(
            capa_id=request.capa_id,
            corrective_actions=request.corrective_actions,
            preventive_actions=request.preventive_actions,
            implementation_plan=request.implementation_plan,
            planner=request.planner
        )
        
        return {
            "capa_id": request.capa_id,
            "status": "planned",
            "message": "Actions planned"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{capa_id}")
async def get_capa(capa_id: str):
    """Get CAPA record"""
    
    try:
        from backend.capa_system import capa_system
        
        record = capa_system.get_capa(capa_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="CAPA not found")
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_open_capas(severity: Optional[str] = None):
    """List open CAPA records"""
    
    try:
        from backend.capa_system import capa_system, CAPASeverity
        
        severity_filter = CAPASeverity(severity) if severity else None
        
        records = capa_system.list_open_capas(severity=severity_filter)
        
        return {
            "open_capas": records,
            "count": len(records)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/stats")
async def get_capa_metrics():
    """Get CAPA system metrics"""
    
    try:
        from backend.capa_system import capa_system
        
        metrics = capa_system.get_capa_metrics()
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
