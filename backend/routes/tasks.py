from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from ..auth import get_current_user
from ..models import Task, async_session
from ..schemas import TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .where(Task.user == current_user)
            .order_by(Task.created_at.desc())
        )
        return result.scalars().all()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        new_task = Task(
            user=current_user,
            title=task.title,
            description=task.description,
            priority=task.priority
        )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.user == current_user)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task_update.title:
            task.title = task_update.title
        if task_update.description:
            task.description = task_update.description
        if task_update.status:
            task.status = task_update.status
            if task_update.status == "completed":
                task.completed_at = datetime.utcnow()
        if task_update.priority:
            task.priority = task_update.priority
        
        await session.commit()
        await session.refresh(task)
        return task
