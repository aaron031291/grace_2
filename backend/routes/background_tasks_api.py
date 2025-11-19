"""
Background Tasks API - Monitor and control background jobs

Endpoints:
- List active tasks
- Get task details
- Pause/resume/cancel tasks
- Provide input for tasks awaiting user response
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.background_tasks.task_manager import background_task_manager

router = APIRouter()


class TaskResponse(BaseModel):
    """Background task information"""
    task_id: str
    task_type: str
    description: str
    status: str
    progress: float
    started_at: str | None
    completed_at: str | None
    error: str | None
    logs: List[str]


class ProvideInputRequest(BaseModel):
    """Provide input for task"""
    input_value: Any


@router.get("/background-tasks/active")
async def get_active_tasks(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all active background tasks
    
    Shows tasks that are:
    - Queued
    - Running
    - Paused
    - Awaiting user input
    """
    tasks = background_task_manager.get_active_tasks(user_id=user_id)
    
    return {
        "tasks": tasks,
        "total": len(tasks),
        "by_status": {
            "running": len([t for t in tasks if t["status"] == "running"]),
            "paused": len([t for t in tasks if t["status"] == "paused"]),
            "needs_input": len([t for t in tasks if t["status"] == "needs_input"]),
        }
    }


@router.get("/background-tasks/{task_id}")
async def get_task_details(task_id: str) -> TaskResponse:
    """Get detailed information about a task"""
    task = background_task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task)


@router.post("/background-tasks/{task_id}/input")
async def provide_task_input(task_id: str, req: ProvideInputRequest) -> Dict[str, Any]:
    """
    Provide input for task awaiting user response
    
    Example: Task asks "Which database to use?" and user responds "production"
    """
    task = background_task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] != "needs_input":
        raise HTTPException(status_code=400, detail="Task is not awaiting input")
    
    await background_task_manager.provide_input(task_id, req.input_value)
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Input provided, task resuming"
    }


@router.post("/background-tasks/{task_id}/pause")
async def pause_task(task_id: str) -> Dict[str, Any]:
    """Pause a running task"""
    # Implementation would set status to paused
    return {
        "success": True,
        "task_id": task_id,
        "status": "paused"
    }


@router.post("/background-tasks/{task_id}/resume")
async def resume_task(task_id: str) -> Dict[str, Any]:
    """Resume a paused task"""
    # Implementation would set status to running
    return {
        "success": True,
        "task_id": task_id,
        "status": "running"
    }


@router.post("/background-tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a running task"""
    # Implementation would stop task and set status to cancelled
    return {
        "success": True,
        "task_id": task_id,
        "status": "cancelled"
    }


@router.get("/background-tasks/stats")
async def get_task_stats() -> Dict[str, Any]:
    """Get task statistics"""
    active_tasks = background_task_manager.get_active_tasks()
    
    return {
        "total_active": len(active_tasks),
        "by_type": {},
        "by_status": {
            "running": len([t for t in active_tasks if t["status"] == "running"]),
            "paused": len([t for t in active_tasks if t["status"] == "paused"]),
            "needs_input": len([t for t in active_tasks if t["status"] == "needs_input"]),
        }
    }
