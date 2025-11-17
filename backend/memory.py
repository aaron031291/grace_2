"""
Persistent Memory Module
Simple memory storage for chat messages
"""

from typing import Optional
from backend.models import ChatMessage, async_session


class PersistentMemory:
    """Persistent memory for chat conversations"""
    
    def __init__(self):
        pass
    
    async def store(self, user: str, role: str, content: str) -> int:
        """
        Store a message in persistent memory
        
        Args:
            user: Username
            role: 'user' or 'grace'
            content: Message content
        
        Returns:
            Message ID
        """
        async with async_session() as session:
            message = ChatMessage(
                user=user,
                role=role,
                content=content
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message.id
    
    async def retrieve(self, user: str, limit: int = 50) -> list:
        """
        Retrieve recent messages for a user
        
        Args:
            user: Username
            limit: Max messages to retrieve
        
        Returns:
            List of messages
        """
        from sqlalchemy import select
        
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.user == user)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )
            
            messages = result.scalars().all()
            
            return [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat() if msg.created_at else None
                }
                for msg in reversed(messages)  # Return in chronological order
            ]
