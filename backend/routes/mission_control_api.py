"""
Mission Control API
REST API for mission management and autonomous operations

Endpoints:
- GET /mission-control/status - Overall system status
- POST /mission-control/missions - Create new mission
- GET /mission-control/missions - List missions
- GET /mission-control/missions/{mission_id} - Get mission details
- POST /mission-control/missions/{mission_id}/execute - Execute mission
- GET /mission-control/subsystems - List subsystem health
- GET /mission-control/metrics - Get metrics catalog
- GET /mission-control/trust-scores - Get trust scores
- POST /mission-control/capa - Create CAPA ticket
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.auth.auth_handler import get_current_user
from backend.mission_control.schemas import (
    MissionPackage, MissionStatus, Severity, MissionContext,
    WorkspaceInfo, AcceptanceCriteria, TrustRequirements, TestResult, MetricObservation
)
from backend.mission_control.hub import mission_control_hub
from backend.mission_control.autonomous_coding_pipeline import autonomous_coding_pipeline
from backend.mission_control.self_healing_workflow import self_healing_workflow
from backend.autonomy.autonomous_mission_creator import autonomous_mission_creator
from backend.mission_control.mission_manifest import MissionManifest
from backend.mission_control.mission_controller import mission_controller, DynamicMissionPlan

router = APIRouter(prefix="/mission-control", tags=["Mission Control"])


# ========== Request Models ==========

class CreateMissionRequest(BaseModel):
    """Request to create a new mission"""
    subsystem_id: str
    severity: str  # critical, high, medium, low
    detected_by: str
    assigned_to: str
    symptoms: List[Dict[str, Any]]
    workspace_repo_path: str
    workspace_branch: str
    acceptance_criteria: Dict[str, Any]
    trust_requirements: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, str]] = None


class CreateMissionFromManifestRequest(BaseModel):
    """Request to create a dynamic mission from a declarative manifest."""
    manifest: Dict[str, Any]


class ExecuteMissionRequest(BaseModel):
    """Request to execute a mission"""
    mission_type: str  # coding or healing


# ========== Status Endpoints ==========

@router.get("/status")
async def get_mission_control_status(current_user: str = Depends(get_current_user)):
    """Get overall Mission Control status"""
    try:
        status = await mission_control_hub.get_status()
        return status.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subsystems")
async def get_subsystem_health(current_user: str = Depends(get_current_user)):
    """Get health status of all subsystems"""
    try:
        status = await mission_control_hub.get_status()
        return {
            "subsystems": [s.dict() for s in status.subsystems],
            "total": len(status.subsystems),
            "healthy": len([s for s in status.subsystems if s.status == "healthy"]),
            "degraded": len([s for s in status.subsystems if s.status == "degraded"]),
            "critical": len([s for s in status.subsystems if s.status == "critical"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/missions/create-from-manifest")
async def create_mission_from_manifest(
    request: CreateMissionFromManifestRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Creates and starts a new dynamic, high-end agentic mission from a manifest.
    """
    try:
        # Re-construct the dataclass from the request dict
        manifest_data = request.manifest
        manifest = MissionManifest(**manifest_data)
        
        plan = await mission_controller.start_mission_from_manifest(manifest)
        
        return {
            "success": True,
            "mission_id": plan.mission_id,
            "status": plan.status.value,
            "message": "Dynamic mission initiated. Goal decomposition is in progress."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create mission from manifest: {e}")


@router.get("/missions/dynamic/{mission_id}", response_model=Dict)
async def get_dynamic_mission_plan(
    mission_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Gets the real-time status and plan of a dynamic, agentic mission.
    """
    plan = mission_controller.get_mission_status(mission_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Dynamic mission not found.")
    
    # A simple serialization for now. A real implementation would handle the recursive structure.
    def serialize_plan(p: DynamicMissionPlan):
        def serialize_goal(g: MissionGoal):
            return {
                "goal_id": g.goal_id,
                "description": g.description,
                "status": g.status.value,
                "sub_steps": [serialize_goal(s) if isinstance(s, MissionGoal) else s.to_dict() for s in g.sub_steps]
            }
        return {
            "mission_id": p.mission_id,
            "status": p.status.value,
            "root_goal": serialize_goal(p.root_goal)
        }
        
    return serialize_plan(plan)


# ========== Mission Endpoints ==========

@router.post("/missions/legacy")
async def create_legacy_mission(
    request: CreateMissionRequest,
    current_user: str = Depends(get_current_user)
):
    """Create a new mission (Legacy Endpoint)"""
    try:
        # Get current system state
        status = await mission_control_hub.get_status()
        
        # Generate mission ID
        mission_id = f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.subsystem_id}"
        
        # Parse severity
        try:
            severity = Severity(request.severity)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {request.severity}")
        
        # Create mission context
        context = MissionContext(
            git_sha=status.git_sha,
            config_hash="sha256:current",
            env=status.environment,
            branch=status.git_branch,
            version=status.grace_version
        )
        
        # Create workspace info
        workspace = WorkspaceInfo(
            repo_path=request.workspace_repo_path,
            working_branch=request.workspace_branch
        )
        
        # Create acceptance criteria
        acceptance_criteria = AcceptanceCriteria(**request.acceptance_criteria)
        
        # Create trust requirements
        trust_requirements = TrustRequirements(
            **(request.trust_requirements or {})
        )
        
        # Create mission package
        mission = MissionPackage(
            mission_id=mission_id,
            subsystem_id=request.subsystem_id,
            severity=severity,
            detected_by=request.detected_by,
            assigned_to=request.assigned_to,
            context=context,
            symptoms=[],  # Will be populated from request
            workspace=workspace,
            acceptance_criteria=acceptance_criteria,
            trust_requirements=trust_requirements,
            tags=request.tags or {}
        )
        
        # Add symptoms
        from ..mission_control.schemas import Symptom
        for symptom_data in request.symptoms:
            mission.symptoms.append(Symptom(**symptom_data))
        
        # Create mission in hub
        mission_id = await mission_control_hub.create_mission(mission)
        
        return {
            "success": True,
            "mission_id": mission_id,
            "status": mission.status.value,
            "message": "Mission created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missions")
async def list_missions(
    status: Optional[str] = Query(None, description="Filter by status"),
    subsystem_id: Optional[str] = Query(None, description="Filter by subsystem"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=500),
    current_user: str = Depends(get_current_user)
):
    """List missions with optional filtering"""
    try:
        missions = []
        
        for mission_id, mission in mission_control_hub.missions.items():
            # Apply filters
            if status and mission.status.value != status:
                continue
            if subsystem_id and mission.subsystem_id != subsystem_id:
                continue
            if severity and mission.severity.value != severity:
                continue
            
            missions.append({
                "mission_id": mission.mission_id,
                "subsystem_id": mission.subsystem_id,
                "severity": mission.severity.value,
                "status": mission.status.value,
                "detected_by": mission.detected_by,
                "assigned_to": mission.assigned_to,
                "created_at": mission.created_at.isoformat(),
                "updated_at": mission.updated_at.isoformat(),
                "symptoms_count": len(mission.symptoms),
                "remediation_events_count": len(mission.remediation_history)
            })
        
        # Sort by created_at descending
        missions.sort(key=lambda m: m["created_at"], reverse=True)
        
        return {
            "total": len(missions),
            "missions": missions[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missions/{mission_id}")
async def get_mission(
    mission_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get mission details"""
    try:
        mission = await mission_control_hub.get_mission(mission_id)
        
        if not mission:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
        
        return mission.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/missions/{mission_id}/execute")
async def execute_mission(
    mission_id: str,
    request: ExecuteMissionRequest,
    current_user: str = Depends(get_current_user)
):
    """Execute a mission"""
    try:
        mission = await mission_control_hub.get_mission(mission_id)
        
        if not mission:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
        
        # Check if mission is in correct state
        if mission.status != MissionStatus.OPEN:
            raise HTTPException(
                status_code=400,
                detail=f"Mission must be in OPEN status, currently: {mission.status.value}"
            )
        
        # Update status
        mission.status = MissionStatus.IN_PROGRESS
        await mission_control_hub.update_mission(mission_id, mission)
        
        # Execute based on type
        if request.mission_type == "coding":
            result = await autonomous_coding_pipeline.execute_mission(mission)
        elif request.mission_type == "healing":
            result = await self_healing_workflow.execute_mission(mission)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid mission type: {request.mission_type}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Metrics & Catalog Endpoints ==========

@router.get("/metrics")
async def get_metrics_catalog(current_user: str = Depends(get_current_user)):
    """Get metrics catalog"""
    try:
        return {
            "metrics": mission_control_hub.metrics_catalog,
            "total": len(mission_control_hub.metrics_catalog)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Trust Score Endpoints ==========

@router.get("/trust-scores")
async def get_trust_scores(current_user: str = Depends(get_current_user)):
    """Get all trust scores"""
    try:
        return {
            "trust_scores": mission_control_hub.trust_scores,
            "total": len(mission_control_hub.trust_scores)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trust-scores/{agent_id}")
async def get_agent_trust_score(
    agent_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get trust score for specific agent"""
    try:
        score = mission_control_hub.get_trust_score(agent_id)
        return {
            "agent_id": agent_id,
            "trust_score": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== CAPA Endpoints ==========

@router.post("/capa")
async def create_capa_ticket(
    mission_id: str = Query(..., description="Related mission ID"),
    title: str = Query(..., description="CAPA ticket title"),
    description: str = Query(..., description="CAPA ticket description"),
    current_user: str = Depends(get_current_user)
):
    """Create CAPA ticket"""
    try:
        # Get mission
        mission = await mission_control_hub.get_mission(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
        
        # Create CAPA ticket
        capa_id = f"capa_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        mission_control_hub.capa_tickets[capa_id] = {
            "capa_id": capa_id,
            "mission_id": mission_id,
            "title": title,
            "description": description,
            "created_by": current_user,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open"
        }
        
        return {
            "success": True,
            "capa_id": capa_id,
            "message": "CAPA ticket created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capa")
async def list_capa_tickets(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: str = Depends(get_current_user)
):
    """List CAPA tickets"""
    try:
        tickets = []
        
        for capa_id, ticket in mission_control_hub.capa_tickets.items():
            if status and ticket.get("status") != status:
                continue
            tickets.append(ticket)
        
        return {
            "total": len(tickets),
            "tickets": tickets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Agent Queue Endpoints ==========

@router.get("/queue/next")
async def get_next_mission_for_agent(
    agent_id: str = Query(..., description="Agent ID"),
    agent_role: str = Query(..., description="Agent role"),
    current_user: str = Depends(get_current_user)
):
    """Get next mission for an agent"""
    try:
        mission = await mission_control_hub.get_next_mission(agent_id, agent_role)

        if not mission:
            return {
                "has_mission": False,
                "message": "No missions available for this agent"
            }

        return {
            "has_mission": True,
            "mission": mission.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Autonomous Mission Endpoints ==========

@router.get("/autonomous/missions")
async def list_autonomous_missions(current_user: str = Depends(get_current_user)):
    """List all autonomous missions created by Grace"""
    try:
        missions = []
        for mission_id, mission in autonomous_mission_creator.missions.items():
            missions.append({
                "mission_id": mission.mission_id,
                "title": mission.title,
                "description": mission.description,
                "rationale": mission.rationale,
                "phase": mission.phase.value,
                "trust_score": mission.trust_score,
                "kpi_score": mission.kpi_metrics.calculate_overall_score(),
                "consensus_reached": mission.consensus_reached,
                "approved_for_live": mission.approved_for_live,
                "created_at": mission.created_at.isoformat(),
                "parliament_session_id": mission.parliament_session_id
            })

        return {
            "total": len(missions),
            "missions": missions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autonomous/missions/{mission_id}")
async def get_autonomous_mission(
    mission_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get autonomous mission details"""
    try:
        mission = autonomous_mission_creator.missions.get(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")

        return {
            "mission_id": mission.mission_id,
            "title": mission.title,
            "description": mission.description,
            "rationale": mission.rationale,
            "phase": mission.phase.value,
            "trust_score": mission.trust_score,
            "kpi_metrics": {
                "performance_improvement": mission.kpi_metrics.performance_improvement,
                "error_rate_reduction": mission.kpi_metrics.error_rate_reduction,
                "latency_improvement": mission.kpi_metrics.latency_improvement,
                "memory_efficiency": mission.kpi_metrics.memory_efficiency,
                "code_quality_score": mission.kpi_metrics.code_quality_score,
                "test_coverage": mission.kpi_metrics.test_coverage,
                "security_score": mission.kpi_metrics.security_score,
                "overall_score": mission.kpi_metrics.calculate_overall_score()
            },
            "sandbox_results": mission.sandbox_results,
            "user_feedback": mission.user_feedback,
            "consensus_reached": mission.consensus_reached,
            "approved_for_live": mission.approved_for_live,
            "parliament_session_id": mission.parliament_session_id,
            "created_at": mission.created_at.isoformat(),
            "tested_at": mission.tested_at.isoformat() if mission.tested_at else None,
            "consensus_at": mission.consensus_at.isoformat() if mission.consensus_at else None,
            "executed_at": mission.executed_at.isoformat() if mission.executed_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/missions")
async def create_autonomous_mission(
    title: str = Query(..., description="Mission title"),
    description: str = Query(..., description="Mission description"),
    rationale: str = Query(..., description="Why Grace thinks this will help"),
    current_user: str = Depends(get_current_user)
):
    """Create an autonomous mission (Grace or user can trigger)"""
    try:
        mission = await autonomous_mission_creator.create_autonomous_mission(
            title=title,
            description=description,
            rationale=rationale
        )

        return {
            "success": True,
            "mission_id": mission.mission_id,
            "phase": mission.phase.value,
            "message": "Autonomous mission created, testing in sandbox..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/missions/{mission_id}/feedback")
async def add_mission_feedback(
    mission_id: str,
    feedback: str = Query(..., description="Your feedback"),
    current_user: str = Depends(get_current_user)
):
    """Add feedback to autonomous mission"""
    try:
        await autonomous_mission_creator.add_user_feedback(mission_id, feedback)

        return {
            "success": True,
            "message": "Feedback added"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/missions/{mission_id}/consensus")
async def reach_mission_consensus(
    mission_id: str,
    approved: bool = Query(..., description="Approve mission for live execution"),
    current_user: str = Depends(get_current_user)
):
    """Reach consensus on autonomous mission"""
    try:
        await autonomous_mission_creator.reach_consensus(mission_id, approved)

        mission = autonomous_mission_creator.missions.get(mission_id)

        return {
            "success": True,
            "approved": approved,
            "trust_score": mission.trust_score,
            "will_execute_to_live": approved and mission.trust_score >= autonomous_mission_creator.trust_threshold,
            "message": "Consensus reached" if approved else "Mission rejected"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

