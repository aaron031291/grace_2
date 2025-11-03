from fastapi import APIRouter
from sqlalchemy import func, select
from ..models import ChatMessage, User, async_session

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/summary")
async def summary():
    async with async_session() as session:
        total_messages = await session.scalar(select(func.count(ChatMessage.id)))
        distinct_users = await session.scalar(
            select(func.count(func.distinct(ChatMessage.user)))
        )
        
        user_count = await session.scalar(select(func.count(User.id)))
        
    return {
        "total_messages": total_messages or 0,
        "active_users": distinct_users or 0,
        "registered_users": user_count or 0
    }

@router.get("/user/{username}")
async def user_stats(username: str):
    async with async_session() as session:
        user_messages = await session.scalar(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.user == username)
        )
        
        grace_responses = await session.scalar(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.user == username, ChatMessage.role == "grace")
        )
        
    return {
        "username": username,
        "total_messages": user_messages or 0,
        "grace_responses": grace_responses or 0,
        "user_messages": (user_messages or 0) - (grace_responses or 0)
    }
