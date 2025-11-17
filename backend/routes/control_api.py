"""
Grace Control API
Endpoints for pause/resume/stop controls
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..grace_control_center import grace_control

router = APIRouter(prefix="/api/control", tags=["Control"])


class ControlAction(BaseModel):
    action: str  # resume, pause, emergency_stop
    triggered_by: Optional[str] = 'user'


class TaskSubmission(BaseModel):
    name: str
    type: str
    description: str
    priority: str = 'normal'
    metadata: dict = {}


@router.on_event("startup")
async def startup():
    """Initialize control center"""
    await grace_control.start()


@router.get("/state")
async def get_state():
    """
    Get current system state
    
    Returns system state and automation status
    Co-pilot is always available, automation may be paused
    """
    
    state = grace_control.get_state()
    
    return state


@router.post("/resume")
async def resume_automation(action: ControlAction):
    """
    Resume Grace's automation
    
    Starts workers and processes queued tasks
    LLM co-pilot remains active throughout
    """
    
    result = await grace_control.resume_automation(
        resumed_by=action.triggered_by
    )
    
    return result


@router.post("/pause")
async def pause_automation(action: ControlAction):
    """
    Pause Grace's automation
    
    Stops workers, queues new tasks
    LLM co-pilot remains active for queries
    """
    
    result = await grace_control.pause_automation(
        paused_by=action.triggered_by
    )
    
    return result


@router.post("/emergency-stop")
async def emergency_stop(action: ControlAction):
    """
    Emergency stop - halt all automation immediately
    
    More aggressive than pause - clears task queue
    Use for critical situations
    """
    
    result = await grace_control.emergency_stop(
        stopped_by=action.triggered_by
    )
    
    return result


@router.post("/queue-task")
async def queue_task(task: TaskSubmission):
    """
    Queue a task for execution
    
    If system is running: executes immediately
    If system is paused: queues for later
    """
    
    task_dict = {
        'name': task.name,
        'type': task.type,
        'description': task.description,
        'priority': task.priority,
        'metadata': task.metadata
    }
    
    result = await grace_control.queue_task(task_dict)
    
    return result


@router.get("/queue")
async def get_queue():
    """Get task queue status"""
    
    pending = grace_control.task_queue.get_pending_tasks()
    
    return {
        'total_tasks': len(grace_control.task_queue.queue),
        'pending_tasks': len(pending),
        'tasks': pending
    }


@router.get("/workers")
async def get_workers():
    """Get automation worker status"""
    
    return {
        'workers': grace_control.automation_workers,
        'count': len(grace_control.automation_workers)
    }
