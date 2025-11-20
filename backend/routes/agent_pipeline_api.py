"""
Agent Pipeline API
Control and monitor tiered agent execution pipelines
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/agent-pipeline",
    tags=["Agent Pipeline"]
)


class PipelineRequest(BaseModel):
    """Request to create a pipeline"""
    task: str
    context: Optional[Dict[str, Any]] = None
    phases: Optional[List[str]] = None  # ['research', 'design', 'implement', 'test', 'deploy']


class GuardianControlRequest(BaseModel):
    """Guardian control command"""
    pipeline_id: str
    action: str  # 'pause', 'resume', 'override'
    override_data: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_orchestrator_status():
    """
    Get agent orchestrator status
    
    Returns:
        Orchestrator status and statistics
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        stats = agent_orchestrator.get_stats()
        
        return {
            "status": "active" if agent_orchestrator.running else "inactive",
            "statistics": stats,
            "configuration": {
                "max_concurrent_pipelines": agent_orchestrator.max_concurrent_pipelines,
                "auto_recover_on_failure": agent_orchestrator.auto_recover_on_failure
            }
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.post("/execute")
async def execute_pipeline(request: PipelineRequest):
    """
    Execute an agent pipeline
    
    Args:
        request: Pipeline request with task and context
        
    Returns:
        Pipeline ID
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        from backend.agents_core.tiered_agent_framework import AgentPhase
        
        # Parse phases if provided
        phases = None
        if request.phases:
            try:
                phases = [AgentPhase(p) for p in request.phases]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid phase: {e}")
        
        # Execute pipeline
        pipeline_id = await agent_orchestrator.execute_pipeline(
            task=request.task,
            context=request.context,
            phases=phases
        )
        
        return {
            "pipeline_id": pipeline_id,
            "status": "started",
            "task": request.task
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.get("/pipelines")
async def get_pipelines(status: Optional[str] = None):
    """
    Get all pipelines
    
    Args:
        status: Filter by status (pending, running, completed, failed)
        
    Returns:
        List of pipelines
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        pipelines = agent_orchestrator.get_pipelines(status=status)
        
        return {
            "pipelines": pipelines,
            "total": len(pipelines)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.get("/pipelines/{pipeline_id}")
async def get_pipeline_details(pipeline_id: str):
    """
    Get detailed information about a pipeline
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        Pipeline details including phases and artifacts
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        pipeline = agent_orchestrator.get_pipeline(pipeline_id)
        
        if not pipeline:
            raise HTTPException(status_code=404, detail=f"Pipeline not found: {pipeline_id}")
        
        return pipeline
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.get("/pipelines/{pipeline_id}/artifacts")
async def get_pipeline_artifacts(pipeline_id: str):
    """
    Get all artifacts from a pipeline
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        List of artifacts
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        pipeline_data = agent_orchestrator.get_pipeline(pipeline_id)
        
        if not pipeline_data:
            raise HTTPException(status_code=404, detail=f"Pipeline not found: {pipeline_id}")
        
        # Extract artifacts from all phases
        artifacts = []
        
        for phase_name, phase_result in pipeline_data.get('phase_results', {}).items():
            artifacts.extend(phase_result.get('artifacts', []))
        
        return {
            "pipeline_id": pipeline_id,
            "artifacts": artifacts,
            "total": len(artifacts)
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.post("/guardian/control")
async def guardian_control(request: GuardianControlRequest):
    """
    Guardian control command (pause/resume/override pipeline)
    
    Args:
        request: Control request
        
    Returns:
        Confirmation
    """
    try:
        from backend.core.message_bus import message_bus
        
        if request.action == 'pause':
            await message_bus.publish('guardian.pause_pipeline', {
                'pipeline_id': request.pipeline_id
            })
            
            logger.info(f"[AGENT-PIPELINE-API] Guardian paused pipeline: {request.pipeline_id}")
            
            return {
                "status": "paused",
                "pipeline_id": request.pipeline_id
            }
        
        elif request.action == 'resume':
            await message_bus.publish('guardian.resume_pipeline', {
                'pipeline_id': request.pipeline_id
            })
            
            logger.info(f"[AGENT-PIPELINE-API] Guardian resumed pipeline: {request.pipeline_id}")
            
            return {
                "status": "resumed",
                "pipeline_id": request.pipeline_id
            }
        
        elif request.action == 'override':
            await message_bus.publish('guardian.override_pipeline', {
                'pipeline_id': request.pipeline_id,
                'override': request.override_data or {}
            })
            
            logger.info(f"[AGENT-PIPELINE-API] Guardian override applied: {request.pipeline_id}")
            
            return {
                "status": "override_applied",
                "pipeline_id": request.pipeline_id
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
    
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Message bus not available: {e}")


@router.get("/dashboard")
async def get_pipeline_dashboard():
    """
    Get comprehensive pipeline dashboard
    
    Returns:
        Dashboard with stats, active pipelines, recent completions
    """
    try:
        from backend.agents_core.agent_orchestrator import agent_orchestrator
        
        stats = agent_orchestrator.get_stats()
        active_pipelines = agent_orchestrator.get_pipelines(status="running")
        completed_pipelines = agent_orchestrator.get_pipelines(status="completed")[:10]  # Last 10
        failed_pipelines = agent_orchestrator.get_pipelines(status="failed")[:10]  # Last 10
        
        # Calculate success rate
        total_finished = stats.get('pipelines_completed', 0) + stats.get('pipelines_failed', 0)
        success_rate = (
            (stats.get('pipelines_completed', 0) / max(1, total_finished)) * 100
            if total_finished > 0 else 0
        )
        
        return {
            "overview": {
                "status": "active" if agent_orchestrator.running else "inactive",
                "success_rate": round(success_rate, 2),
                "total_artifacts": stats.get('total_artifacts', 0)
            },
            "statistics": stats,
            "active_pipelines": {
                "pipelines": active_pipelines,
                "count": len(active_pipelines)
            },
            "recent_completions": {
                "successful": completed_pipelines,
                "failed": failed_pipelines
            },
            "configuration": {
                "max_concurrent": agent_orchestrator.max_concurrent_pipelines,
                "auto_recovery": agent_orchestrator.auto_recover_on_failure
            }
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator not initialized: {e}")


@router.get("/phases")
async def get_available_phases():
    """
    Get all available agent phases
    
    Returns:
        List of phase names and descriptions
    """
    try:
        from backend.agents_core.tiered_agent_framework import AgentPhase, AGENT_REGISTRY
        
        phases = []
        
        for phase, agent_class in AGENT_REGISTRY.items():
            agent = agent_class()
            phases.append({
                "phase": phase.value,
                "agent_id": agent.agent_id,
                "description": agent.description
            })
        
        return {
            "phases": phases,
            "default_pipeline": [p.value for p in AgentPhase]
        }
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Agent framework not initialized: {e}")
