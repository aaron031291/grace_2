from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import ChatMessage, async_session

class PersistentMemory:
    async def store(self, user: str, role: str, content: str):
        async with async_session() as session:
            msg = ChatMessage(user=user, role=role, content=content)
            session.add(msg)
            await session.commit()

    async def recent_messages(self, user: str, limit: int = 20):
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.user == user)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )
            return list(reversed(result.scalars().all()))
