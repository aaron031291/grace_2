import asyncio
from datetime import datetime
from sqlalchemy import select, func, Column, Integer, String, DateTime, Text
from .models import ChatMessage, async_session, Base

class Reflection(Base):
    __tablename__ = "reflections"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    topic = Column(String(128))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReflectionEngine:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.running = False
        self.task = None

    async def analyze_recent_messages(self, user: str, limit: int = 10):
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.user == user)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )
            messages = result.scalars().all()
            
            if not messages:
                return None
            
            topics = {}
            for msg in messages:
                words = msg.content.lower().split()
                for word in ["task", "history", "hello", "help", "thank"]:
                    if word in words:
                        topics[word] = topics.get(word, 0) + 1
            
            if not topics:
                return None
            
            most_common = max(topics.items(), key=lambda x: x[1])
            
            reflection_content = (
                f"Reflection: User '{user}' has been discussing '{most_common[0]}' "
                f"frequently ({most_common[1]} times in recent messages). "
                f"Total messages analyzed: {len(messages)}"
            )
            
            reflection = Reflection(
                user=user,
                content=reflection_content,
                topic=most_common[0]
            )
            session.add(reflection)
            await session.commit()
            
            return reflection_content

    async def get_reflections(self, user: str, limit: int = 5):
        async with async_session() as session:
            result = await session.execute(
                select(Reflection)
                .where(Reflection.user == user)
                .order_by(Reflection.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()

    async def reflection_loop(self):
        while self.running:
            try:
                async with async_session() as session:
                    result = await session.execute(
                        select(func.distinct(ChatMessage.user))
                    )
                    users = result.scalars().all()
                    
                    for user in users:
                        await self.analyze_recent_messages(user)
                
            except Exception as e:
                print(f"Reflection loop error: {e}")
            
            await asyncio.sleep(self.interval)

    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.reflection_loop())
            print(f"✓ Reflection engine started (interval: {self.interval}s)")

    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            print("✓ Reflection engine stopped")

reflection_engine = ReflectionEngine(interval_seconds=120)
