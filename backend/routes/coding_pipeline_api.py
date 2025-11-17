"""
Coding Pipeline API - Autonomous software development
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/coding", tags=["coding"])

class CodingTaskRequest(BaseModel):
    description: str
    repository: str
    branch: str = "main"

@router.post("/tasks")
async def create_coding_task(req: CodingTaskRequest) -> Dict[str, Any]:
    """
    Create a new autonomous coding task
    
    Pipeline stages:
    1. Fetch context (codebase, requirements, tests)
    2. Propose diff (code changes)
    3. Run tests (unit, integration, lint)
    4. Collect diagnostics (errors, warnings)
    5. Request approval (governance gate)
    6. Merge (with verification)
    7. Observe (post-merge metrics)
    """
    try:
        from backend.autonomy.coding_pipeline import get_coding_pipeline
        import uuid
        
        pipeline = get_coding_pipeline()
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = await pipeline.start_task(
            task_id=task_id,
            description=req.description,
            repository=req.repository,
            branch=req.branch
        )
        
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "created_at": task.created_at.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a coding task"""
    try:
        from backend.autonomy.coding_pipeline import get_coding_pipeline
        
        pipeline = get_coding_pipeline()
        task = pipeline.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "task_id": task.task_id,
            "description": task.description,
            "status": task.status.value,
            "current_stage": task.current_stage.value if task.current_stage else None,
            "repository": task.repository,
            "branch": task.branch,
            "test_results": task.test_results,
            "diagnostics": task.diagnostics,
            "approval_request_id": task.approval_request_id,
            "merge_commit_sha": task.merge_commit_sha,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

@router.get("/stats")
async def get_pipeline_stats() -> Dict[str, Any]:
    """Get coding pipeline statistics"""
    try:
        from backend.autonomy.coding_pipeline import get_coding_pipeline
        
        pipeline = get_coding_pipeline()
        stats = pipeline.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "pipeline": stats,
            "targets": {
                "success_rate_target": 90.0,
                "average_time_target_minutes": 15.0,
                "targets_met": {
                    "success_rate": stats["success_rate"] >= 90.0,
                    "average_time": stats["average_time_seconds"] <= 900
                }
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
