from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from ..auth import get_current_user
from ..models import Goal, async_session

router = APIRouter(prefix="/api/goals", tags=["goals"])

class GoalCreate(BaseModel):
    goal_text: str
    target_date: Optional[datetime] = None

class GoalUpdate(BaseModel):
    goal_text: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None

class GoalResponse(BaseModel):
    id: int
    goal_text: str
    target_date: Optional[datetime]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        query = select(Goal).where(Goal.user == current_user)
        if status:
            query = query.where(Goal.status == status)
        query = query.order_by(Goal.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()

@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        new_goal = Goal(
            user=current_user,
            goal_text=goal.goal_text,
            target_date=goal.target_date
        )
        session.add(new_goal)
        await session.commit()
        await session.refresh(new_goal)
        return new_goal

@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user == current_user)
        )
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        if goal_update.goal_text:
            goal.goal_text = goal_update.goal_text
        if goal_update.target_date:
            goal.target_date = goal_update.target_date
        if goal_update.status:
            goal.status = goal_update.status
            if goal_update.status == "completed":
                goal.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(goal)
        return goal
