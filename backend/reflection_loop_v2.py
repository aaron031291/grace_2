"""
Reflection Loop v2 - Enhanced Plan-Act-Reflect-Revise for continuous improvement
Grace learns from outcomes using structured reflection and persistent storage
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from backend.event_bus import event_bus, Event, EventType
from backend.core.unified_event_publisher import publish_event_obj
from backend.action_gateway import action_gateway
from backend.reflection_models import Reflection
from backend.reflection_prompt_system import reflection_prompt_system
from backend.database import get_db
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession


class ReflectionLoop:
    """
    Enhanced Plan-Act-Reflect-Revise loop for Grace's continuous improvement
    Uses structured reflection prompts and persistent database storage
    """

    def __init__(self):
        self.trust_scores = {}  # Keep in memory for fast access

        event_bus.subscribe(EventType.LEARNING_OUTCOME, self.on_learning_outcome)

    async def on_learning_outcome(self, event: Event) -> None:
        """Handle learning outcome events"""
        outcome = event.data
        trace_id = outcome.get("trace_id")

        if trace_id:
            await self.reflect_on_outcome(trace_id, outcome)

    async def reflect_on_outcome(
        self,
        trace_id: str,
        outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on action outcome using structured prompts and store in database
        """

        async with get_db() as db:
            # Get action details
            action_log = action_gateway.get_action_log()
            action = next((a for a in action_log if a["trace_id"] == trace_id), None)

            if not action:
                return {"error": "Action not found"}

            # Gather historical context
            historical_context = await self._gather_historical_context(db, action)

            # Prepare action data for reflection
            action_data = {
                "trace_id": trace_id,
                "action_type": action["action_type"],
                "agent": action["agent"],
                "success": outcome.get("success", False),
                "execution_time_ms": outcome.get("execution_time_ms"),
                "timestamp": datetime.now().isoformat(),
                "context": action.get("context", {})
            }

            # Generate and process reflection
            try:
                from backend.grace_llm import grace_llm
                reflection_prompt = await reflection_prompt_system.generate_reflection_prompt(
                    action_data, historical_context, "comprehensive"
                )
                llm_response = await grace_llm.generate(reflection_prompt)
                structured_reflection = await reflection_prompt_system.process_reflection_response(
                    llm_response, action_data
                )
            except Exception as e:
                structured_reflection = self._generate_basic_reflection(action, outcome)

            # Update trust scores
            await self._update_trust_scores(action, outcome, structured_reflection)

            # Create and store reflection record
            reflection_record = Reflection(
                trace_id=trace_id,
                action_type=action["action_type"],
                agent=action["agent"],
                success=outcome.get("success", False),
                timestamp=datetime.now(),
                execution_time_ms=outcome.get("execution_time_ms"),
                confidence_score=structured_reflection.get("confidence_levels", {}).get("analysis_confidence", 0.5),
                trust_score_before=self.trust_scores.get(f"{action['agent']}:{action['action_type']}", 0.5),
                performance_analysis=structured_reflection.get("performance_analysis"),
                identified_improvements=structured_reflection.get("identified_improvements"),
                generated_insights=structured_reflection.get("generated_insights"),
                strategy_updates=structured_reflection.get("strategy_updates"),
                context=action.get("context"),
                error_details=outcome.get("error"),
                tags=self._generate_tags(action, outcome),
                learned_patterns=structured_reflection.get("generated_insights", {}).get("patterns"),
                confidence_in_insights=structured_reflection.get("confidence_levels", {}).get("insight_confidence", 0.5)
            )

            reflection_record.trust_score_after = self.trust_scores.get(f"{action['agent']}:{action['action_type']}", 0.5)

            db.add(reflection_record)
            await db.commit()
            await db.refresh(reflection_record)

            # Publish event
            await publish_event_obj(Event(
                event_type=EventType.WORLD_MODEL_UPDATE,
                source="reflection_loop",
                data=reflection_record.to_dict(),
                trace_id=trace_id
            ))

            print(f"[ReflectionLoop] Stored reflection for {trace_id}")
            return reflection_record.to_dict()

    async def _gather_historical_context(self, db: AsyncSession, action: Dict[str, Any]) -> Dict[str, Any]:
        """Gather historical context for reflection analysis"""

        agent = action["agent"]
        action_type = action["action_type"]

        # Recent agent reflections
        agent_reflections_result = await db.execute(
            select(Reflection).where(
                and_(
                    Reflection.agent == agent,
                    Reflection.timestamp >= datetime.now() - timedelta(days=1)
                )
            ).order_by(desc(Reflection.timestamp)).limit(10)
        )
        agent_reflections = agent_reflections_result.scalars().all()

        # Recent action type reflections
        action_reflections_result = await db.execute(
            select(Reflection).where(
                and_(
                    Reflection.action_type == action_type,
                    Reflection.timestamp >= datetime.now() - timedelta(days=1)
                )
            ).order_by(desc(Reflection.timestamp)).limit(10)
        )
        action_reflections = action_reflections_result.scalars().all()

        # Calculate metrics
        agent_success_rate = (
            sum(1 for r in agent_reflections if r.success) / len(agent_reflections) * 100
            if agent_reflections else 50.0
        )

        action_success_rate = (
            sum(1 for r in action_reflections if r.success) / len(action_reflections) * 100
            if action_reflections else 50.0
        )

        return {
            "agent_success_rate": round(agent_success_rate, 1),
            "action_success_rate": round(action_success_rate, 1),
            "recent_performance": f"{sum(1 for r in agent_reflections[-5:] if r.success)}/{len(agent_reflections[-5:])} recent successes" if agent_reflections else "No recent data",
            "total_similar_actions": len(action_reflections),
            "success_trend": self._calculate_trend(agent_reflections),
            "agent_performance": f"{agent_success_rate:.1f}% success rate",
            "similar_actions": len(action_reflections)
        }

    def _calculate_trend(self, reflections: List[Reflection]) -> str:
        """Calculate success trend"""
        if len(reflections) < 5:
            return "insufficient_data"

        recent = reflections[:5]
        older = reflections[5:] if len(reflections) >= 10 else recent

        recent_rate = sum(1 for r in recent if r.success) / len(recent)
        older_rate = sum(1 for r in older if r.success) / len(older) if older else recent_rate

        if recent_rate > older_rate + 0.1:
            return "improving"
        elif recent_rate < older_rate - 0.1:
            return "declining"
        else:
            return "stable"

    def _generate_basic_reflection(self, action: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback reflection when LLM fails"""
        success = outcome.get("success", False)
        return {
            "performance_analysis": {
                "strengths": ["Action completed"] if success else [],
                "weaknesses": ["Action failed"] if not success else [],
                "efficiency_rating": 7 if success else 3,
                "unexpected_factors": [outcome.get("error", "Unknown")] if not success else []
            },
            "identified_improvements": {
                "high_priority": ["Add error handling"] if not success else [],
                "medium_priority": ["Monitor performance"],
                "low_priority": ["Optimize execution"],
                "alternative_approaches": []
            },
            "generated_insights": {
                "patterns": [f"{'Success' if success else 'Failure'} pattern"],
                "predictors": [], "contextual_factors": [], "strategic_implications": []
            },
            "strategy_updates": {
                "trust_adjustments": [], "validation_requirements": [],
                "monitoring_changes": ["Add outcome monitoring"], "contingency_plans": []
            },
            "confidence_levels": {
                "analysis_confidence": 0.7, "improvement_confidence": 0.5,
                "insight_confidence": 0.4, "strategy_confidence": 0.5
            }
        }

    async def _update_trust_scores(
        self, action: Dict[str, Any], outcome: Dict[str, Any], reflection: Dict[str, Any]
    ) -> None:
        """Update trust scores based on reflection"""
        agent_key = f"{action['agent']}:{action['action_type']}"
        current_trust = self.trust_scores.get(agent_key, 0.5)
        adjustment = 0.05 if outcome.get("success") else -0.08
        self.trust_scores[agent_key] = max(0.0, min(1.0, current_trust + adjustment))

    def _generate_tags(self, action: Dict[str, Any], outcome: Dict[str, Any]) -> List[str]:
        """Generate tags for categorization"""
        tags = ["success" if outcome.get("success") else "failure"]
        if outcome.get("error"):
            tags.append("error")
        tags.extend([f"agent:{action['agent']}", f"action:{action['action_type']}", "reflection:analyzed"])
        return tags

    async def plan_action(self, agent: str, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Plan action using historical reflection data"""

        async with get_db() as db:
            agent_key = f"{agent}:{action_type}"
            trust_score = self.trust_scores.get(agent_key, 0.5)

            # Get recent reflections
            reflections_result = await db.execute(
                select(Reflection).where(
                    and_(Reflection.agent == agent, Reflection.action_type == action_type)
                ).order_by(desc(Reflection.timestamp)).limit(20)
            )
            reflections = reflections_result.scalars().all()

            success_rate = sum(1 for r in reflections if r.success) / len(reflections) if reflections else 0.5

            # Gather insights
            insights = []
            for reflection in reflections[:5]:
                if reflection.generated_insights and "patterns" in reflection.generated_insights:
                    insights.extend(reflection.generated_insights["patterns"])

            plan = {
                "agent": agent, "action_type": action_type,
                "trust_score": trust_score, "success_rate": success_rate,
                "confidence": (trust_score + success_rate) / 2,
                "recommendations": [], "learned_insights": list(set(insights)),
                "timestamp": datetime.now().isoformat()
            }

            # Generate recommendations
            if plan["confidence"] < 0.3:
                plan["recommendations"].append("Low confidence - consider alternative approach")
            elif plan["confidence"] < 0.6:
                plan["recommendations"].append("Moderate confidence - proceed with caution")
            else:
                plan["recommendations"].append("High confidence - proceed")

            recent_failures = [r for r in reflections[:5] if not r.success]
            if len(recent_failures) >= 3:
                plan["recommendations"].append("Multiple recent failures - review strategy")

            print(f"[ReflectionLoop] Planned {action_type} for {agent}: confidence={plan['confidence']:.2f}")
            return plan

    def get_agent_trust_score(self, agent: str, action_type: str) -> float:
        """Get trust score for agent/action combination"""
        agent_key = f"{agent}:{action_type}"
        return self.trust_scores.get(agent_key, 0.5)

    async def get_reflections(
        self, limit: int = 100, agent: str = None, action_type: str = None, success: bool = None
    ) -> List[Dict[str, Any]]:
        """Query reflections with filtering"""

        async with get_db() as db:
            query = select(Reflection).order_by(desc(Reflection.timestamp))

            if agent:
                query = query.where(Reflection.agent == agent)
            if action_type:
                query = query.where(Reflection.action_type == action_type)
            if success is not None:
                query = query.where(Reflection.success == success)

            query = query.limit(limit)
            result = await db.execute(query)
            reflections = result.scalars().all()

            return [r.to_dict() for r in reflections]

    async def get_strategy_updates(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get strategy updates from recent reflections"""

        async with get_db() as db:
            reflections_result = await db.execute(
                select(Reflection).order_by(desc(Reflection.timestamp)).limit(limit)
            )
            reflections = reflections_result.scalars().all()

            updates = []
            for reflection in reflections:
                if reflection.strategy_updates:
                    updates.append({
                        "reflection_id": reflection.id,
                        "timestamp": reflection.timestamp.isoformat(),
                        "agent": reflection.agent,
                        "action_type": reflection.action_type,
                        "updates": reflection.strategy_updates
                    })

            return updates

    async def get_insights_summary(self, days: int = 7) -> Dict[str, Any]:
        """Generate insights summary from recent reflections"""

        async with get_db() as db:
            cutoff_date = datetime.now() - timedelta(days=days)

            reflections_result = await db.execute(
                select(Reflection).where(Reflection.timestamp >= cutoff_date)
                .order_by(desc(Reflection.timestamp))
            )
            reflections = reflections_result.scalars().all()

            summary = {
                "total_reflections": len(reflections),
                "success_rate": sum(1 for r in reflections if r.success) / len(reflections) if reflections else 0,
                "common_patterns": {},
                "improvement_suggestions": {},
                "agent_performance": {},
                "time_period": f"{days} days"
            }

            # Aggregate data
            for reflection in reflections:
                agent = reflection.agent
                if agent not in summary["agent_performance"]:
                    agent_refs = [r for r in reflections if r.agent == agent]
                    summary["agent_performance"][agent] = {
                        "total_actions": len(agent_refs),
                        "success_rate": sum(1 for r in agent_refs if r.success) / len(agent_refs) if agent_refs else 0
                    }

                # Aggregate patterns and improvements
                if reflection.generated_insights and "patterns" in reflection.generated_insights:
                    for pattern in reflection.generated_insights["patterns"]:
                        summary["common_patterns"][pattern] = summary["common_patterns"].get(pattern, 0) + 1

                if reflection.identified_improvements and "high_priority" in reflection.identified_improvements:
                    for improvement in reflection.identified_improvements["high_priority"]:
                        summary["improvement_suggestions"][improvement] = summary["improvement_suggestions"].get(improvement, 0) + 1

            return summary


reflection_loop = ReflectionLoop()</content>
</edit_file>
