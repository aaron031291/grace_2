import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func, Column, Integer, DateTime, Text, Float
from .models import ChatMessage, async_session, Base
from .learning import learning_engine
from .evaluation import confidence_evaluator

class Reflection(Base):
    __tablename__ = "reflections"
    id = Column(Integer, primary_key=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    summary = Column(Text, nullable=False)
    insight = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)

class ReflectionService:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self._task = None
        self._running = False

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run())
            print(f"✓ Reflection service started (interval: {self.interval}s)")

    async def stop(self):
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
            self._task = None
            print("✓ Reflection service stopped")

    async def _run(self):
        try:
            while self._running:
                await self.generate_reflection()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass

    async def generate_reflection(self):
        lookback = datetime.utcnow() - timedelta(hours=1)
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage).where(ChatMessage.created_at >= lookback)
            )
            messages = result.scalars().all()

            if not messages:
                return

            total = len(messages)
            user_msgs = sum(1 for m in messages if m.role == "user")
            grace_msgs = total - user_msgs

            user_topics = {}
            for msg in messages:
                if msg.role == "user":
                    words = msg.content.lower().split()
                    for w in words:
                        if len(w) > 3:
                            user_topics[w] = user_topics.get(w, 0) + 1

            top_words = sorted(user_topics.items(), key=lambda x: x[1], reverse=True)
            top_words = [word for word, count in top_words[:3]]

            summary = (
                f"In the last hour, {user_msgs} user messages and {grace_msgs} responses."
            )
            insight = ""
            if top_words:
                insight = f"Common user words: {', '.join(top_words)}"

            from .causal_graph import CausalGraph
            try:
                graph = CausalGraph()
                start = datetime.utcnow() - timedelta(hours=1)
                await graph.build_from_events(start, datetime.utcnow())
                influential = graph.get_most_influential_events(limit=3)
                if influential:
                    insight += f" | Influential events: {', '.join(e['event_type'] for e in influential)}"
            except Exception as e:
                print(f"⚠ Causal graph analysis failed: {e}")

            reflection = Reflection(
                summary=summary, 
                insight=insight, 
                confidence=0.5
            )
            session.add(reflection)
            await session.commit()
            print(f"✓ Generated reflection: {summary}")
            
            if top_words and user_topics:
                most_common_word = max(user_topics.items(), key=lambda x: x[1])
                action_created = await learning_engine.process_reflection(
                    "admin", 
                    most_common_word[0], 
                    most_common_word[1]
                )
                if action_created:
                    print(f"✓ Learning engine created task from pattern: {most_common_word[0]}")
            
            eval_count = await confidence_evaluator.periodic_evaluation()
            if eval_count > 0:
                print(f"✓ Confidence evaluator processed {eval_count} events")

reflection_service = ReflectionService(interval_seconds=10)
