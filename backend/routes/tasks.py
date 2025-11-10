from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from ..auth import get_current_user
from ..models import Task, async_session
=======
from ..schemas import TaskResponse
>>>>>>> origin/main

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

<<<<<<< HEAD
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    auto_generated: bool
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

        
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
