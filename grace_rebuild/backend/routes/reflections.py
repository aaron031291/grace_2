from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from ..auth import get_current_user
from ..reflection import reflection_engine

router = APIRouter(prefix="/api/reflections", tags=["reflections"])

class ReflectionResponse(BaseModel):
    id: int
    content: str
    topic: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ReflectionResponse])
async def get_reflections(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    reflections = await reflection_engine.get_reflections(current_user, limit)
    return reflections

@router.post("/trigger")
async def trigger_reflection(current_user: str = Depends(get_current_user)):
    result = await reflection_engine.analyze_recent_messages(current_user)
    if result:
        return {"status": "created", "reflection": result}
    return {"status": "no_data", "message": "Not enough messages to reflect on"}
