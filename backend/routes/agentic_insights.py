"""
Agentic Insights API - Expose agentic decision observability

Provides HTTP endpoints for ops teams to monitor what GRACE is doing,
why she's doing it, and how it's going.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..agentic_observability import agentic_observability, InsightVerbosity


router = APIRouter(prefix="/agent", tags=["Agentic Insights"])


class RunSummary(BaseModel):
    """Summary of an agentic run"""
    run_id: str
    started_at: datetime
    current_phase: str
    signal: Optional[str]
    plan: Optional[str]
    risk_score: Optional[float]
    approval_required: bool


class RunPhase(BaseModel):
    """Phase in agentic run timeline"""
    phase: str
    timestamp: datetime
    what: Optional[str]
    why: Optional[str]
    confidence: Optional[float]
    risk_score: Optional[float]
    guardrails_passed: Optional[bool]
    approved_by: Optional[str]


class RunDetails(BaseModel):
    """Detailed trace of agentic run"""
    run_id: str
    started_at: datetime
    phases: List[RunPhase]
    outcome: Optional[str]
    verified: Optional[bool]


class DecisionSummary(BaseModel):
    """Summary of a decision"""
    run_id: str
    timestamp: datetime
    signal: Optional[str]
    plan: Optional[str]
    outcome: Optional[str]
    success: Optional[bool]
    risk_score: Optional[float]


class PendingApproval(BaseModel):
    """Approval awaiting human decision"""
    run_id: str
    timestamp: datetime
    plan: Optional[str]
    risk_score: Optional[float]
    rationale: Optional[str]


class AgenticStatistics(BaseModel):
    """Performance statistics"""
    total_runs: int
    successful_runs: int
    success_rate: float
    average_risk_score: float
    autonomous_decisions: int
    autonomy_rate: float
    pending_approvals: int


class DashboardSummary(BaseModel):
    """Complete dashboard data"""
    current_state: dict
    active_runs: List[dict]
    pending_approvals: List[dict]
    recent_decisions: List[dict]
    statistics_24h: dict
    statistics_7d: dict


@router.get("/status", summary="Get current agentic status")
async def get_status():
    """Get current status of agentic system"""
    
    dashboard = await agentic_observability.get_dashboard()
    
    return {
        "status": dashboard["current_state"]["status"],
        "active_runs": dashboard["current_state"]["active_run_count"],
        "pending_approvals": dashboard["current_state"]["pending_approval_count"],
        "highest_risk": dashboard["current_state"]["highest_risk_run"]
    }


@router.get("/runs/active", response_model=List[RunSummary], summary="Get active runs")
async def get_active_runs():
    """Get all currently active agentic runs"""
    
    runs = await agentic_observability.read_models.get_active_runs()
    return runs


@router.get("/runs/{run_id}", response_model=RunDetails, summary="Get run details")
async def get_run_details(run_id: str):
    """Get detailed trace of a specific agentic run"""
    
    details = await agentic_observability.get_run_trace(run_id)
    
    if not details:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    return details


@router.get("/runs/{run_id}/timeline", summary="Get run timeline visualization")
async def get_run_timeline(run_id: str):
    """Get visual timeline of agentic run for dashboards"""
    
    timeline = await agentic_observability.dashboard.get_run_timeline(run_id)
    
    if not timeline:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    return timeline


@router.get("/decisions/recent", response_model=List[DecisionSummary], summary="Get recent decisions")
async def get_recent_decisions(
    hours: int = Query(24, ge=1, le=168, description="Lookback period in hours"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results")
):
    """Get recent agentic decisions"""
    
    decisions = await agentic_observability.read_models.get_recent_decisions(
        hours=hours,
        limit=limit
    )
    
    return decisions


@router.get("/approvals/pending", response_model=List[PendingApproval], summary="Get pending approvals")
async def get_pending_approvals():
    """Get runs awaiting human approval"""
    
    pending = await agentic_observability.read_models.get_pending_approvals()
    return pending


@router.get("/statistics", response_model=AgenticStatistics, summary="Get performance statistics")
async def get_statistics(
    hours: int = Query(24, ge=1, le=720, description="Lookback period in hours")
):
    """Get agentic performance statistics"""
    
    stats = await agentic_observability.read_models.get_statistics(hours=hours)
    return stats


@router.get("/dashboard", response_model=DashboardSummary, summary="Get complete dashboard")
async def get_dashboard():
    """Get complete dashboard summary for ops visibility"""
    
    dashboard = await agentic_observability.get_dashboard()
    return dashboard


@router.post("/verbosity", summary="Set observability verbosity")
async def set_verbosity(level: str):
    """
    Set verbosity level for agentic insights
    
    Levels:
    - minimal: Only outcomes
    - summary: Key decisions (default)
    - detailed: Full decision trail
    - debug: Everything
    """
    
    try:
        verbosity = InsightVerbosity[level.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verbosity level. Must be one of: minimal, summary, detailed, debug"
        )
    
    await agentic_observability.set_verbosity(verbosity)
    
    return {"verbosity": level, "message": f"Verbosity set to {level}"}


@router.get("/search", summary="Search agentic runs")
async def search_runs(
    signal_type: Optional[str] = None,
    outcome: Optional[str] = None,
    min_risk: Optional[float] = None,
    max_risk: Optional[float] = None,
    approved_by: Optional[str] = None,
    hours: int = Query(168, ge=1, le=720)
):
    """Search agentic runs by criteria"""
    
    return {
        "message": "Search functionality coming soon",
        "filters": {
            "signal_type": signal_type,
            "outcome": outcome,
            "risk_range": [min_risk, max_risk],
            "approved_by": approved_by,
            "hours": hours
        }
    }


@router.get("/health", summary="Observability system health")
async def health_check():
    """Check health of observability system"""
    
    return {
        "status": "healthy" if agentic_observability.running else "stopped",
        "verbosity": agentic_observability.capture.verbosity.value,
        "active_tracking": len(agentic_observability.capture.active_runs)
    }
