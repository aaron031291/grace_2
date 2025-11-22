"""
Closed-Loop Learning System

Captures execution outcomes and feeds them back into the knowledge system.

Flow:
1. Agent/LLM executes a plan
2. Outcome is captured (success/failure, metrics, narrative)
3. Events published (insight.generated, mission.learned)
4. Vector integration ingests the narrative
5. Classifier decides which world-model category to update
6. Knowledge becomes available for future queries

This creates a true feedback loop: answer → action → learning → back into RAG
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from backend.events.unified_publisher import publish_domain_event

logger = logging.getLogger(__name__)


class OutcomeType(Enum):
    """Types of execution outcomes"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ERROR = "error"


class LearningCategory(Enum):
    """Categories for learned knowledge"""
    SOLUTION = "solution"  # Successful approaches
    PITFALL = "pitfall"    # Common mistakes to avoid
    PATTERN = "pattern"    # Recurring patterns
    INSIGHT = "insight"    # New understandings
    TECHNIQUE = "technique"  # Useful methods


@dataclass
class ExecutionOutcome:
    """Structured execution outcome"""
    execution_id: str
    task_description: str
    approach_taken: str
    outcome_type: OutcomeType
    outcome_narrative: str
    metrics: Dict[str, Any]
    learning_points: List[str]
    confidence: float = 0.8
    domain_id: Optional[str] = None
    agent_id: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class ClosedLoopLearning:
    """
    Closed-loop learning system
    
    Captures outcomes and feeds them back into knowledge systems
    """
    
    def __init__(self):
        self._initialized = False
        self.outcomes_captured = 0
        self.insights_generated = 0
        self.knowledge_items_created = 0
    
    async def initialize(self):
        """Initialize closed-loop learning"""
        if self._initialized:
            return
        
        logger.info("[CLOSED-LOOP] Initializing closed-loop learning system")
        
        # Subscribe to execution events
        try:
            from backend.domains import domain_event_bus
            
            domain_event_bus.subscribe("execution.completed", self._handle_execution_completed)
            domain_event_bus.subscribe("task.completed", self._handle_task_completed)
            domain_event_bus.subscribe("plan.executed", self._handle_plan_executed)
            
            logger.info("[CLOSED-LOOP] Subscribed to execution events")
        except Exception as e:
            logger.warning(f"[CLOSED-LOOP] Could not subscribe to events: {e}")
        
        self._initialized = True
        logger.info("[CLOSED-LOOP] Closed-loop learning ready")
    
    async def capture_outcome(self, outcome: ExecutionOutcome) -> Dict[str, Any]:
        """
        Capture an execution outcome and process it
        
        Args:
            outcome: Structured execution outcome
            
        Returns:
            {
                "outcome_id": str,
                "learning_category": str,
                "knowledge_id": str,
                "embedding_id": str,
                "success": bool
            }
        """
        self.outcomes_captured += 1
        
        try:
            # Step 1: Classify the learning
            learning_category = await self._classify_learning(outcome)
            
            # Step 2: Generate insight narrative
            insight_narrative = await self._generate_insight_narrative(outcome, learning_category)
            
            # Step 3: Publish insight event
            await self._publish_insight_event(outcome, insight_narrative, learning_category)
            
            # Step 4: Ingest into vector store
            embedding_id = await self._ingest_to_vector_store(outcome, insight_narrative)
            
            # Step 5: Add to world model
            knowledge_id = await self._add_to_world_model(outcome, insight_narrative, learning_category)
            
            self.insights_generated += 1
            self.knowledge_items_created += 1
            
            logger.info(
                f"[CLOSED-LOOP] Captured outcome: {outcome.execution_id} "
                f"({outcome.outcome_type.value}) → {learning_category.value}"
            )
            
            return {
                "outcome_id": outcome.execution_id,
                "learning_category": learning_category.value,
                "knowledge_id": knowledge_id,
                "embedding_id": embedding_id,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Failed to capture outcome: {e}")
            return {
                "outcome_id": outcome.execution_id,
                "success": False,
                "error": str(e)
            }
    
    async def _classify_learning(self, outcome: ExecutionOutcome) -> LearningCategory:
        """
        Classify what type of learning this represents
        
        Uses simple heuristics + optional LLM classification
        """
        # Simple classification based on outcome type
        if outcome.outcome_type == OutcomeType.SUCCESS:
            # Successful execution = solution or technique
            if "pattern" in outcome.outcome_narrative.lower():
                return LearningCategory.PATTERN
            elif "method" in outcome.outcome_narrative.lower() or "approach" in outcome.outcome_narrative.lower():
                return LearningCategory.TECHNIQUE
            else:
                return LearningCategory.SOLUTION
        
        elif outcome.outcome_type == OutcomeType.FAILURE:
            # Failure = pitfall to avoid
            return LearningCategory.PITFALL
        
        elif outcome.outcome_type == OutcomeType.PARTIAL:
            # Partial = insight about limitations
            return LearningCategory.INSIGHT
        
        else:
            return LearningCategory.INSIGHT
    
    async def _generate_insight_narrative(
        self,
        outcome: ExecutionOutcome,
        category: LearningCategory
    ) -> str:
        """
        Generate a narrative description of the insight
        
        This narrative will be embedded and searchable
        """
        narrative_parts = []
        
        # Title based on category
        if category == LearningCategory.SOLUTION:
            narrative_parts.append(f"Successful Solution: {outcome.task_description}")
        elif category == LearningCategory.PITFALL:
            narrative_parts.append(f"Pitfall to Avoid: {outcome.task_description}")
        elif category == LearningCategory.PATTERN:
            narrative_parts.append(f"Pattern Observed: {outcome.task_description}")
        elif category == LearningCategory.TECHNIQUE:
            narrative_parts.append(f"Useful Technique: {outcome.task_description}")
        else:
            narrative_parts.append(f"Insight: {outcome.task_description}")
        
        # Add context
        narrative_parts.append(f"\nApproach: {outcome.approach_taken}")
        narrative_parts.append(f"\nOutcome: {outcome.outcome_narrative}")
        
        # Add learning points
        if outcome.learning_points:
            narrative_parts.append("\nKey Learnings:")
            for point in outcome.learning_points:
                narrative_parts.append(f"- {point}")
        
        # Add metrics if significant
        if outcome.metrics:
            narrative_parts.append(f"\nMetrics: {self._format_metrics(outcome.metrics)}")
        
        return "\n".join(narrative_parts)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for narrative"""
        formatted = []
        for key, value in metrics.items():
            if isinstance(value, float):
                formatted.append(f"{key}={value:.2f}")
            else:
                formatted.append(f"{key}={value}")
        return ", ".join(formatted)
    
    async def _publish_insight_event(
        self,
        outcome: ExecutionOutcome,
        narrative: str,
        category: LearningCategory
    ):
        """Publish insight event to domain event bus"""
        try:
            await publish_domain_event(
                event_type="insight.generated",
                domain_id=outcome.domain_id or "system",
                data={
                    "execution_id": outcome.execution_id,
                    "insight_title": f"{category.value.title()}: {outcome.task_description[:50]}",
                    "insight_text": narrative,
                    "confidence": outcome.confidence,
                    "tags": [category.value, outcome.outcome_type.value],
                    "domain_id": outcome.domain_id or "system",
                    "timestamp": outcome.timestamp
                }
            )
            
        except Exception as e:
            logger.warning(f"[CLOSED-LOOP] Could not publish insight event: {e}")
    
    async def _ingest_to_vector_store(
        self,
        outcome: ExecutionOutcome,
        narrative: str
    ) -> str:
        """Ingest narrative into vector store for semantic search"""
        try:
            from backend.services.vector_store import vector_store
            
            result = await vector_store.add_text(
                content=narrative,
                source=f"execution/{outcome.execution_id}",
                metadata={
                    "execution_id": outcome.execution_id,
                    "outcome_type": outcome.outcome_type.value,
                    "domain_id": outcome.domain_id,
                    "agent_id": outcome.agent_id,
                    "confidence": outcome.confidence,
                    "timestamp": outcome.timestamp,
                    "learning": True
                },
                source_type="execution_outcome",
                source_id=outcome.execution_id
            )
            
            return result.get("embedding_id", "")
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Failed to ingest to vector store: {e}")
            return ""
    
    async def _add_to_world_model(
        self,
        outcome: ExecutionOutcome,
        narrative: str,
        category: LearningCategory
    ) -> str:
        """Add to world model as curated knowledge"""
        try:
            from backend.world_model import grace_world_model
            
            knowledge_id = await grace_world_model.add_knowledge(
                category='domain',
                content=narrative,
                source=f"{outcome.domain_id or 'system'}_execution",
                confidence=outcome.confidence,
                tags=[
                    category.value,
                    outcome.outcome_type.value,
                    'execution',
                    'learned'
                ] + (outcome.learning_points[:2] if outcome.learning_points else []),
                metadata={
                    "execution_id": outcome.execution_id,
                    "outcome_type": outcome.outcome_type.value,
                    "learning_category": category.value,
                    "domain_id": outcome.domain_id,
                    "agent_id": outcome.agent_id,
                    "metrics": outcome.metrics
                }
            )
            
            return knowledge_id
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Failed to add to world model: {e}")
            return ""
    
    async def _handle_execution_completed(self, event):
        """Handle execution.completed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            outcome = ExecutionOutcome(
                execution_id=data.get("execution_id", f"exec_{datetime.utcnow().timestamp()}"),
                task_description=data.get("task_description", "Unknown task"),
                approach_taken=data.get("approach", "Unknown approach"),
                outcome_type=OutcomeType(data.get("outcome_type", "success")),
                outcome_narrative=data.get("outcome_narrative", "Task completed"),
                metrics=data.get("metrics", {}),
                learning_points=data.get("learning_points", []),
                confidence=data.get("confidence", 0.8),
                domain_id=data.get("domain_id"),
                agent_id=data.get("agent_id")
            )
            
            await self.capture_outcome(outcome)
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Error handling execution completed: {e}")
    
    async def _handle_task_completed(self, event):
        """Handle task.completed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            outcome = ExecutionOutcome(
                execution_id=data.get("task_id", f"task_{datetime.utcnow().timestamp()}"),
                task_description=data.get("task_description", "Task"),
                approach_taken=data.get("solution", "Task solution"),
                outcome_type=OutcomeType.SUCCESS if data.get("success") else OutcomeType.FAILURE,
                outcome_narrative=data.get("result", "Task result"),
                metrics={"success": data.get("success", False)},
                learning_points=[],
                confidence=0.85,
                domain_id=data.get("domain_id"),
                agent_id=data.get("agent_id")
            )
            
            await self.capture_outcome(outcome)
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Error handling task completed: {e}")
    
    async def _handle_plan_executed(self, event):
        """Handle plan.executed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            success = data.get("success", False)
            outcome = ExecutionOutcome(
                execution_id=data.get("plan_id", f"plan_{datetime.utcnow().timestamp()}"),
                task_description=data.get("plan_description", "Plan execution"),
                approach_taken=data.get("steps_summary", "Multi-step plan"),
                outcome_type=OutcomeType.SUCCESS if success else OutcomeType.FAILURE,
                outcome_narrative=data.get("outcome", "Plan executed"),
                metrics=data.get("metrics", {}),
                learning_points=data.get("lessons_learned", []),
                confidence=0.9 if success else 0.7,
                domain_id=data.get("domain_id"),
                agent_id=data.get("agen_id")
            )
            
            await self.capture_outcome(outcome)
            
        except Exception as e:
            logger.error(f"[CLOSED-LOOP] Error handling plan executed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get closed-loop learning statistics"""
        return {
            "initialized": self._initialized,
            "outcomes_captured": self.outcomes_captured,
            "insights_generated": self.insights_generated,
            "knowledge_items_created": self.knowledge_items_created
        }


# Global instance
closed_loop_learning = ClosedLoopLearning()


# Convenience function for manual outcome capture
async def capture_execution_outcome(
    task_description: str,
    approach: str,
    success: bool,
    narrative: str,
    learning_points: Optional[List[str]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Manually capture an execution outcome
    
    Use this when you want to explicitly record learning from an execution
    """
    outcome = ExecutionOutcome(
        execution_id=f"manual_{datetime.utcnow().timestamp()}",
        task_description=task_description,
        approach_taken=approach,
        outcome_type=OutcomeType.SUCCESS if success else OutcomeType.FAILURE,
        outcome_narrative=narrative,
        metrics=metrics or {},
        learning_points=learning_points or [],
        **kwargs
    )
    
    return await closed_loop_learning.capture_outcome(outcome)
