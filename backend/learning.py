from sqlalchemy import select
from .models import Task, ChatMessage, async_session
from datetime import datetime

class LearningEngine:
    """Converts reflections into actionable tasks"""
    
    async def process_reflection(self, user: str, topic: str, frequency: int):
        """Generate learning actions based on reflection insights"""
        
        action_created = False
        
        if topic in ["task", "todo"] and frequency >= 2:
            async with async_session() as session:
                existing = await session.execute(
                    select(Task).where(
                        Task.user == user,
                        Task.title.contains("task management"),
                        Task.status == "pending"
                    )
                )
                if not existing.scalar_one_or_none():
                    task = Task(
                        user=user,
                        title="Set up task management system",
                        description=f"User mentioned 'task' {frequency} times - they need task tracking",
                        priority="high",
                        auto_generated=True
                    )
                    session.add(task)
                    await session.commit()
                    action_created = True
                    print(f"✓ Auto-generated task for {user}: task management")
        
        elif topic in ["help", "question"] and frequency >= 2:
            async with async_session() as session:
                task = Task(
                    user=user,
                    title="Improve help responses",
                    description=f"User asked for help {frequency} times - expand knowledge base",
                    priority="medium",
                    auto_generated=True
                )
                session.add(task)
                await session.commit()
                action_created = True
                print(f"✓ Auto-generated task for {user}: improve help")
        
        elif frequency >= 3:
            async with async_session() as session:
                task = Task(
                    user=user,
                    title=f"Research topic: {topic}",
                    description=f"User mentioned '{topic}' {frequency} times - this is important to them",
                    priority="low",
                    auto_generated=True
                )
                session.add(task)
                await session.commit()
                action_created = True
                print(f"✓ Auto-generated research task for {user}: {topic}")
        
        return action_created

learning_engine = LearningEngine()
