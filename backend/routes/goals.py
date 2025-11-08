from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
import json
from ..auth import get_current_user
from ..models import Goal, async_session
from ..goal_models import GoalDependency, GoalEvaluation
from ..schemas_extended import (
    GoalCriteriaResponse,
    GoalDependencyResponse,
    GoalGraphResponse,
    GoalEvaluationResponse
)

router = APIRouter(prefix="/api/goals", tags=["goals"])

class GoalCreate(BaseModel):
    goal_text: str
    target_date: Optional[datetime] = None
    priority: Optional[str] = "medium"
    value_score: Optional[float] = None
    risk_score: Optional[float] = None
    owner: Optional[str] = None
    category: Optional[str] = None

class GoalUpdate(BaseModel):
    goal_text: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    value_score: Optional[float] = None
    risk_score: Optional[float] = None
    owner: Optional[str] = None
    category: Optional[str] = None
    success_criteria: Optional[Dict[str, Any]] = None

class GoalResponse(BaseModel):
    id: int
    goal_text: str
    target_date: Optional[datetime]
    status: str
    priority: str
    value_score: Optional[float]
    risk_score: Optional[float]
    owner: Optional[str]
    category: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class GoalCriteria(BaseModel):
    criteria: Dict[str, Any]

class GoalDependencyCreate(BaseModel):
    depends_on_id: int
    type: str = "blocks"
    note: Optional[str] = None

@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        query = select(Goal).where(Goal.user == current_user)
        if status:
            query = query.where(Goal.status == status)
        if priority:
            query = query.where(Goal.priority == priority)
        if category:
            query = query.where(Goal.category == category)
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
            target_date=goal.target_date,
            priority=goal.priority or "medium",
            value_score=goal.value_score,
            risk_score=goal.risk_score,
            owner=goal.owner,
            category=goal.category,
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
        
        if goal_update.goal_text is not None:
            goal.goal_text = goal_update.goal_text
        if goal_update.target_date is not None:
            goal.target_date = goal_update.target_date
        if goal_update.status is not None:
            goal.status = goal_update.status
            if goal_update.status == "completed":
                goal.completed_at = datetime.utcnow()
        if goal_update.priority is not None:
            goal.priority = goal_update.priority
        if goal_update.value_score is not None:
            goal.value_score = goal_update.value_score
        if goal_update.risk_score is not None:
            goal.risk_score = goal_update.risk_score
        if goal_update.owner is not None:
            goal.owner = goal_update.owner
        if goal_update.category is not None:
            goal.category = goal_update.category
        if goal_update.success_criteria is not None:
            goal.success_criteria = json.dumps(goal_update.success_criteria)
        
        await session.commit()
        await session.refresh(goal)
        return goal

@router.post("/{goal_id}/criteria", response_model=GoalCriteriaResponse)
async def set_goal_criteria(
    goal_id: int,
    body: GoalCriteria,
    current_user: str = Depends(get_current_user),
):
    async with async_session() as session:
        result = await session.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user == current_user)
        )
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        goal.success_criteria = json.dumps(body.criteria)
        await session.commit()
        return GoalCriteriaResponse(ok=True)

@router.post("/{goal_id}/dependencies", response_model=GoalDependencyResponse)
async def add_goal_dependency(
    goal_id: int,
    body: GoalDependencyCreate,
    current_user: str = Depends(get_current_user),
):
    async with async_session() as session:
        # Ensure both goals belong to the same user
        result = await session.execute(select(Goal).where(Goal.id == goal_id, Goal.user == current_user))
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        result2 = await session.execute(select(Goal).where(Goal.id == body.depends_on_id, Goal.user == current_user))
        parent = result2.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail="Dependency goal not found")
        dep = GoalDependency(goal_id=goal_id, depends_on_goal_id=body.depends_on_id, type=body.type, note=body.note)
        session.add(dep)
        await session.commit()
        return GoalDependencyResponse(ok=True, dependency_id=dep.id)

@router.get("/{goal_id}/graph", response_model=GoalGraphResponse)
async def get_goal_graph(goal_id: int, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        # Fetch goal and its neighborhood
        result = await session.execute(select(Goal).where(Goal.id == goal_id, Goal.user == current_user))
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        deps_res = await session.execute(select(GoalDependency).where((GoalDependency.goal_id == goal_id) | (GoalDependency.depends_on_goal_id == goal_id)))
        deps = deps_res.scalars().all()
        node_ids = set([goal_id]) | {d.depends_on_goal_id for d in deps} | {d.goal_id for d in deps}
        others_res = await session.execute(select(Goal).where(Goal.id.in_(list(node_ids))))
        nodes = [
            {"id": g.id, "text": g.goal_text, "priority": g.priority, "status": g.status}
            for g in others_res.scalars().all()
        ]
        edges = [
            {"from": d.depends_on_goal_id, "to": d.goal_id, "type": d.type, "note": d.note}
            for d in deps
        ]
        return GoalGraphResponse(nodes=nodes, edges=edges)

@router.post("/{goal_id}/evaluate", response_model=GoalEvaluationResponse)
async def evaluate_goal(goal_id: int, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(select(Goal).where(Goal.id == goal_id, Goal.user == current_user))
        goal = result.scalar_one_or_none()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        status = "on_track"
        confidence = 0.6
        explanation = "No success criteria set; defaulting to heuristic based on priority/status."
        if goal.success_criteria:
            try:
                criteria = json.loads(goal.success_criteria)
                # Simple heuristic: if explicit deadline passed and not completed -> at_risk/off_track
                deadline = criteria.get("deadline")
                if deadline and isinstance(deadline, str):
                    try:
                        deadline_dt = datetime.fromisoformat(deadline)
                        if datetime.utcnow() > deadline_dt and goal.status != "completed":
                            status = "at_risk"
                            explanation = "Deadline passed and goal not completed."
                            confidence = 0.8
                    except Exception:
                        pass
                # If criteria has required_status == completed and goal is completed
                required_status = criteria.get("required_status")
                if required_status == "completed" and goal.status == "completed":
                    status = "met"
                    explanation = "Goal marked completed and matches success criteria."
                    confidence = 0.9
            except Exception:
                explanation = "Malformed success_criteria JSON; treating as unknown, leaving 'on_track'."
                status = "on_track"
                confidence = 0.4
        ge = GoalEvaluation(goal_id=goal.id, status=status, explanation=explanation, confidence=confidence)
        session.add(ge)
        await session.commit()
        return GoalEvaluationResponse(goal_id=goal.id, status=status, confidence=confidence, explanation=explanation)
