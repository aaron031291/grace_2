"""
Copilot Pipeline API - Phase 4
Autonomous coding pipeline endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/copilot/pipeline", tags=["copilot-pipeline"])


class PipelineRunRequest(BaseModel):
    task_description: str
    target_repo: Optional[str] = None
    target_branch: Optional[str] = None


@router.post("/run")
async def run_pipeline(request: PipelineRunRequest) -> Dict[str, Any]:
    """
    Run the autonomous coding pipeline
    
    7 steps:
    1. Fetch context
    2. Propose diff
    3. Run tests
    4. Collect diagnostics
    5. Request approval (BLOCKS)
    6. Merge
    7. Observe
    """
    try:
        from backend.copilot.autonomous_pipeline import autonomous_pipeline
        
        job = await autonomous_pipeline.run_pipeline(
            task_description=request.task_description,
            target_repo=request.target_repo,
            target_branch=request.target_branch
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "current_step": job.current_step,
            "steps_completed": job.steps_completed,
            "approval_status": job.approval_status,
            "message": f"Pipeline {job.status}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/status/{job_id}")
async def get_pipeline_status(job_id: str) -> Dict[str, Any]:
    """Get status of a pipeline job"""
    try:
        from backend.copilot.autonomous_pipeline import autonomous_pipeline
        
        status = autonomous_pipeline.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/{job_id}")
async def rollback_pipeline(job_id: str) -> Dict[str, Any]:
    """Rollback a failed pipeline job"""
    try:
        from backend.copilot.autonomous_pipeline import autonomous_pipeline
        
        result = await autonomous_pipeline.rollback_job(job_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Rollback failed"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_pipeline_health() -> Dict[str, Any]:
    """Get pipeline health status"""
    import os
    
    return {
        "status": "operational",
        "offline_mode": os.getenv("OFFLINE_MODE", "false").lower() == "true",
        "components": {
            "code_generator": "available",
            "approval_gate": "available",
            "safe_hold_snapshot": "available",
            "github_integration": "available" if os.getenv("GITHUB_TOKEN") else "simulated"
        }
    }
