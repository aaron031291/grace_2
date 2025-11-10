from sqlalchemy import select, func
from .models import CausalEvent, ChatMessage, async_session
from datetime import datetime, timedelta

class ConfidenceEvaluator:
    """Evaluates and improves confidence scores based on outcomes"""
    
    async def evaluate_response_quality(self, event_id: int) -> float:
        """Score a causal event based on follow-up behavior"""
        async with async_session() as session:
            event = await session.get(CausalEvent, event_id)
            if not event:
                return 0.5
            
            result = await session.execute(
                select(ChatMessage)
                .where(
                    ChatMessage.user == event.user,
                    ChatMessage.id > event.response_message_id
                )
                .order_by(ChatMessage.created_at.asc())
                .limit(3)
            )
            followup_messages = result.scalars().all()
            
            score = 0.5
            
            if event.outcome == "unhandled":
                score = 0.3
                if followup_messages and any("?" in msg.content for msg in followup_messages):
                    score = 0.2
            
            elif event.outcome == "information_provided":
                score = 0.8
                if not followup_messages or len(followup_messages) == 0:
                    score = 0.9
            
            elif event.outcome == "acknowledged":
                score = 0.7
                if followup_messages and followup_messages[0].role == "user":
                    time_gap = (followup_messages[0].created_at - 
                               (await session.get(ChatMessage, event.response_message_id)).created_at)
                    if time_gap.total_seconds() < 5:
                        score = 0.6
                    else:
                        score = 0.8
            
            event.confidence = score
            await session.commit()
            
            return score
    
    async def get_average_confidence(self, user: str) -> dict:
        """Calculate average confidence by event type"""
        async with async_session() as session:
            result = await session.execute(
                select(CausalEvent)
                .where(CausalEvent.user == user)
                .order_by(CausalEvent.created_at.desc())
                .limit(100)
            )
            events = result.scalars().all()
            
            if not events:
                return {"overall": 0.5, "by_type": {}}
            
            by_type = {}
            for event in events:
                if event.event_type not in by_type:
                    by_type[event.event_type] = []
                by_type[event.event_type].append(event.confidence)
            
            avg_by_type = {
                evt_type: round(sum(scores) / len(scores), 2)
                for evt_type, scores in by_type.items()
            }
            
            overall = round(sum(e.confidence for e in events) / len(events), 2)
            
            return {
                "overall": overall,
                "by_type": avg_by_type,
                "sample_size": len(events)
            }
    
    async def periodic_evaluation(self):
        """Run evaluation on recent events"""
        lookback = datetime.utcnow() - timedelta(hours=1)
        async with async_session() as session:
            result = await session.execute(
                select(CausalEvent)
                .where(CausalEvent.created_at >= lookback)
            )
            events = result.scalars().all()
            
            evaluated_count = 0
            for event in events:
                await self.evaluate_response_quality(event.id)
                evaluated_count += 1
            
            print(f"[OK] Evaluated {evaluated_count} causal events")
            return evaluated_count

confidence_evaluator = ConfidenceEvaluator()
