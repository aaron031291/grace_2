from sqlalchemy import select
from .models import CausalEvent, ChatMessage, async_session
from datetime import datetime, timedelta

class CausalTracker:
    """Track cause-effect relationships in conversations"""
    
    async def log_interaction(self, user: str, trigger_msg_id: int, response_msg_id: int):
        """Log a user message -> Grace response pair"""
        async with async_session() as session:
            trigger_msg = await session.get(ChatMessage, trigger_msg_id)
            response_msg = await session.get(ChatMessage, response_msg_id)
            
            if not trigger_msg or not response_msg:
                return
            
            event_type = self._classify_event_type(trigger_msg.content)
            outcome = self._classify_outcome(trigger_msg.content, response_msg.content)
            
            event = CausalEvent(
                user=user,
                trigger_message_id=trigger_msg_id,
                response_message_id=response_msg_id,
                event_type=event_type,
                outcome=outcome,
                confidence=0.7
            )
            session.add(event)
            await session.commit()
    
    def _classify_event_type(self, content: str) -> str:
        """Classify the type of user message"""
        lower = content.lower()
        
        if any(word in lower for word in ["hello", "hi", "hey"]):
            return "greeting"
        elif any(word in lower for word in ["history", "remember", "show"]):
            return "memory_query"
        elif any(word in lower for word in ["how are you", "status"]):
            return "status_check"
        elif "?" in content:
            return "question"
        elif any(word in lower for word in ["thank", "thanks"]):
            return "gratitude"
        else:
            return "statement"
    
    def _classify_outcome(self, trigger: str, response: str) -> str:
        """Classify whether the response was successful"""
        if "still learning" in response.lower():
            return "unhandled"
        elif "hello" in response.lower() or "how can i help" in response.lower():
            return "acknowledged"
        elif "history" in trigger.lower() and len(response) > 100:
            return "information_provided"
        else:
            return "responded"
    
    async def get_patterns(self, user: str, limit: int = 100):
        """Analyze causal patterns for a user"""
        async with async_session() as session:
            result = await session.execute(
                select(CausalEvent)
                .where(CausalEvent.user == user)
                .order_by(CausalEvent.created_at.desc())
                .limit(limit)
            )
            events = result.scalars().all()
            
            if not events:
                return {"total": 0, "patterns": {}}
            
            event_types = {}
            outcomes = {}
            
            for event in events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
                outcomes[event.outcome] = outcomes.get(event.outcome, 0) + 1
            
            unhandled_rate = outcomes.get("unhandled", 0) / len(events) if events else 0
            
            return {
                "total_interactions": len(events),
                "event_types": event_types,
                "outcomes": outcomes,
                "unhandled_rate": round(unhandled_rate * 100, 2),
                "most_common_event": max(event_types.items(), key=lambda x: x[1])[0] if event_types else None
            }

causal_tracker = CausalTracker()
