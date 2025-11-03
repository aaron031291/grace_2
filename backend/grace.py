from .memory import PersistentMemory
from .knowledge import knowledge_manager

class GraceAutonomous:
    def __init__(self, memory: PersistentMemory):
        self.memory = memory

    async def respond(self, user: str, message: str) -> str:
        normalized = message.lower().strip()
        
        knowledge_results = await knowledge_manager.search_knowledge(message, limit=3)
        has_relevant_knowledge = len(knowledge_results) > 0
        
        if "history" in normalized or "remember" in normalized:
            msgs = await self.memory.recent_messages(user, limit=20)
            if len(msgs) < 2:
                return "We just started chatting. Ask me a few more things and then check history again!"
            history = "\n".join(
                f"{m.role.upper()}: {m.content}" for m in msgs[-10:]
            )
            return f"Here are your last {min(len(msgs), 10)} interactions:\n\n{history}"
        
        if "hello" in normalized or "hi" in normalized:
            return "Hello! I'm Grace. How can I help you today?"
        
        if "how are you" in normalized:
            return "I'm functioning optimally. All systems operational. How can I assist you?"
        
        if "thank" in normalized:
            return "You're welcome! Happy to help."
        
        if "bye" in normalized or "goodbye" in normalized:
            return "Goodbye! Feel free to return anytime."
        
        if not has_relevant_knowledge and len(normalized.split()) > 3:
            await self._propose_research(user, message)
            return (
                "I don't have sufficient knowledge about that topic yet. "
                "I've created a research goal to find trusted sources. "
                "You can approve knowledge ingestion in the governance panel, or teach me directly."
            )
        
        if has_relevant_knowledge:
            top_result = knowledge_results[0]
            return f"Based on my knowledge: {top_result['content'][:200]}..."
        
        return "Thanks for your message. I'm still learning. Try asking about your history or saying hello!"
    
    async def _propose_research(self, user: str, query: str):
        """Create research goal when Grace lacks knowledge"""
        from .models import Goal, async_session
        
        async with async_session() as session:
            goal = Goal(
                user=user,
                goal_text=f"Research and ingest knowledge about: {query}",
                status="active"
            )
            session.add(goal)
            await session.commit()
            print(f"✓ Grace proposed research goal: {query[:50]}...")
