from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from ..auth import get_current_user
from ..task_executor import task_executor
from ..verification_middleware import verify_action
from ..schemas import ExecutionResponse, TaskStatusResponse
import asyncio

router = APIRouter(prefix="/api/executor", tags=["executor"])

class TaskSubmit(BaseModel):
    task_type: str
    description: str
    steps: int = 10

@router.post("/submit")
@verify_action("task_execution", lambda data: data.get("task_type", "unknown"))
async def submit_task(
    req: TaskSubmit,
    current_user: str = Depends(get_current_user)
):
    async def demo_task(task_id: str, update_progress):
        """Demo task that shows progress"""
        for i in range(req.steps):
            await asyncio.sleep(0.5)
            progress = ((i + 1) / req.steps) * 100
            await update_progress(task_id, progress)
        return f"Completed {req.steps} steps"
    
    task_id = await task_executor.submit_task(
        current_user,
        req.task_type,
        req.description,
        demo_task
    )
    
    return {"task_id": task_id, "status": "queued"}

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_status(
    task_id: str,
    current_user: str = Depends(get_current_user)
):
    status = await task_executor.get_task_status(task_id)
    if not status:
        return {"task_id": task_id, "status": "not_found", "progress": 0.0}
    return status

@router.get("/tasks")
async def list_tasks(
    limit: int = 20,
    current_user: str = Depends(get_current_user)
):
    tasks = await task_executor.list_tasks(current_user, limit)
    return {"tasks": tasks, "count": len(tasks)}
