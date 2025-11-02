from sqlalchemy import Column, Integer, String, DateTime, Text, select, func
from sqlalchemy.sql import func as sql_func
from datetime import datetime, timedelta
from .models import Base, ChatMessage, Task, async_session
from .reflection import Reflection

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True)
    period = Column(String(32))
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    summary_text = Column(Text, nullable=False)
    key_topics = Column(Text)
    tasks_created = Column(Integer, default=0)
    goals_touched = Column(Integer, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=sql_func.now())

class SummaryGenerator:
    """Generates periodic summaries of Grace's activity"""
    
    async def generate_daily_summary(self):
        """Create a summary for the last 24 hours"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        async with async_session() as session:
            messages_result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.created_at >= start_time)
            )
            messages = messages_result.scalars().all()
            
            tasks_result = await session.execute(
                select(Task)
                .where(Task.created_at >= start_time)
            )
            tasks = tasks_result.scalars().all()
            
            reflections_result = await session.execute(
                select(Reflection)
                .where(Reflection.generated_at >= start_time)
            )
            reflections = reflections_result.scalars().all()
            
            user_messages = [m for m in messages if m.role == "user"]
            grace_messages = [m for m in messages if m.role == "grace"]
            
            topics = {}
            for msg in user_messages:
                words = msg.content.lower().split()
                for word in words:
                    if len(word) > 4:
                        topics[word] = topics.get(word, 0) + 1
            
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            top_topics_str = ", ".join([f"{word}({count})" for word, count in top_topics])
            
            auto_tasks = len([t for t in tasks if t.auto_generated])
            
            summary_text = (
                f"📅 Daily Summary for {start_time.strftime('%Y-%m-%d')}\n\n"
                f"💬 Conversations: {len(user_messages)} user messages, {len(grace_messages)} Grace responses\n"
                f"🔍 Reflections Generated: {len(reflections)}\n"
                f"✅ Tasks Created: {len(tasks)} ({auto_tasks} autonomous)\n"
                f"🎯 Top Topics: {top_topics_str}\n"
            )
            
            summary = Summary(
                period="daily",
                period_start=start_time,
                period_end=end_time,
                summary_text=summary_text,
                key_topics=top_topics_str,
                tasks_created=len(tasks),
                goals_touched=0
            )
            session.add(summary)
            await session.commit()
            
            print(f"✓ Generated daily summary: {len(messages)} messages, {len(tasks)} tasks")
            return summary_text

summary_generator = SummaryGenerator()
