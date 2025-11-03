from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from ..auth import get_current_user
from ..models import ChatMessage, async_session

router = APIRouter(prefix="/api/memory", tags=["memory"])

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class HistoryStats(BaseModel):
    total_messages: int
    user_messages: int
    grace_messages: int
    first_message: Optional[datetime]
    last_message: Optional[datetime]

@router.get("/history", response_model=List[MessageResponse])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        messages = result.scalars().all()
        return list(reversed(messages))

@router.get("/stats", response_model=HistoryStats)
async def get_stats(current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        messages_result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.asc())
        )
        all_messages = messages_result.scalars().all()
        
        if not all_messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "grace_messages": 0,
                "first_message": None,
                "last_message": None
            }
        
        user_msgs = sum(1 for m in all_messages if m.role == "user")
        grace_msgs = len(all_messages) - user_msgs
        
        return {
            "total_messages": len(all_messages),
            "user_messages": user_msgs,
            "grace_messages": grace_msgs,
            "first_message": all_messages[0].created_at,
            "last_message": all_messages[-1].created_at
        }
