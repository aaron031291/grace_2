"""
Tasks API - Mission and job management

Endpoints:
- List active tasks/missions/jobs
- Pause/resume/cancel tasks
- Get task details and progress
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.event_bus import event_bus, Event, EventType

router = APIRouter()

# Mock task storage (replace with actual task manager)
active_tasks: Dict[str, Dict[str, Any]] = {}


class TaskInfo(BaseModel):
    """Task information"""
    task_id: str
    task_type: str
    status: str
    progress: float
    description: str
    started_at: str
    updated_at: str
    metadata: Dict[str, Any]
    can_pause: bool = True
    can_cancel: bool = True


@router.get("/tasks/active", response_model=List[TaskInfo])
async def get_active_tasks() -> List[TaskInfo]:
    """
    Get all active tasks, missions, and learning jobs
    
    Returns:
        List of active tasks with status and progress
    """
    tasks = []
    
    # Get from world model service
    try:
        from backend.world_model.world_model_service import world_model_service
        context = await world_model_service.query_context()
        
        # Add active missions
        for mission in context.get("active_missions", []):
            tasks.append(TaskInfo(
                task_id=mission.get("mission_id", "unknown"),
                task_type="mission",
                status=mission.get("status", "unknown"),
                progress=mission.get("progress", 0.0),
                description=mission.get("description", ""),
                started_at=mission.get("started_at", datetime.utcnow().isoformat()),
                updated_at=mission.get("updated_at", datetime.utcnow().isoformat()),
                metadata=mission.get("metadata", {}),
            ))
        
        # Add learning jobs
        for job in context.get("learning_jobs", []):
            tasks.append(TaskInfo(
                task_id=job.get("job_id", "unknown"),
                task_type="learning_job",
                status=job.get("status", "unknown"),
                progress=job.get("progress", 0.0),
                description=job.get("description", ""),
                started_at=job.get("started_at", datetime.utcnow().isoformat()),
                updated_at=job.get("updated_at", datetime.utcnow().isoformat()),
                metadata=job.get("metadata", {}),
            ))
    except Exception as e:
        print(f"[TasksAPI] Error fetching tasks: {e}")
    
    # Add from local storage
    for task in active_tasks.values():
        tasks.append(TaskInfo(**task))
    
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskInfo)
async def get_task(task_id: str) -> TaskInfo:
    """Get specific task details"""
    if task_id in active_tasks:
        return TaskInfo(**active_tasks[task_id])
    
    raise HTTPException(status_code=404, detail="Task not found")


@router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: str) -> Dict[str, Any]:
    """Pause a running task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    if not task.get("can_pause", True):
        raise HTTPException(status_code=400, detail="Task cannot be paused")
    
    task["status"] = "paused"
    task["updated_at"] = datetime.utcnow().isoformat()
    
    await event_bus.publish(Event(
        event_type=EventType.TASK_PAUSED,
        source="tasks_api",
        data={"task_id": task_id}
    ))
    
    return {
        "success": True,
        "task_id": task_id,
        "status": "paused",
        "message": "Task paused"
    }


@router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: str) -> Dict[str, Any]:
    """Resume a paused task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    if task["status"] != "paused":
        raise HTTPException(status_code=400, detail="Task is not paused")
    
    task["status"] = "running"
    task["updated_at"] = datetime.utcnow().isoformat()
    
    await event_bus.publish(Event(
        event_type=EventType.TASK_STARTED,
        source="tasks_api",
        data={"task_id": task_id}
    ))
    
    return {
        "success": True,
        "task_id": task_id,
        "status": "running",
        "message": "Task resumed"
    }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    if not task.get("can_cancel", True):
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    
    task["status"] = "cancelled"
    task["updated_at"] = datetime.utcnow().isoformat()
    
    await event_bus.publish(Event(
        event_type=EventType.TASK_COMPLETED,
        source="tasks_api",
        data={
            "task_id": task_id,
            "status": "cancelled"
        }
    ))
    
    # Remove from active tasks
    del active_tasks[task_id]
    
    return {
        "success": True,
        "task_id": task_id,
        "status": "cancelled",
        "message": "Task cancelled"
    }


@router.get("/tasks/stats")
async def get_task_stats() -> Dict[str, Any]:
    """Get task statistics"""
    total = len(active_tasks)
    running = sum(1 for t in active_tasks.values() if t["status"] == "running")
    paused = sum(1 for t in active_tasks.values() if t["status"] == "paused")
    
    return {
        "total_tasks": total,
        "running": running,
        "paused": paused,
        "by_type": {
            task_type: sum(1 for t in active_tasks.values() if t["task_type"] == task_type)
            for task_type in set(t["task_type"] for t in active_tasks.values())
        }
    }
