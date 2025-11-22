"""
Learning & Adaptation Engine - Continuous learning from experience
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LearningExperience:
    """A learning experience"""
    experience_id: str
    timestamp: datetime
    context: Dict[str, Any]
    action_taken: Dict[str, Any]
    outcome: Dict[str, Any]
    lessons_learned: List[str]
    confidence: float


@dataclass
class AdaptationOpportunity:
    """An opportunity for system adaptation"""
    opportunity_id: str
    pattern_detected: str
    current_performance: float
    proposed_improvement: Dict[str, Any]
    expected_benefit: float
    risk_level: str


class LearningEngine:
    """
    Learning & Adaptation Engine - Continuous self-improvement through experience

    Learns from every interaction, detects patterns, and proposes adaptations
    to improve system performance and capabilities.
    """

    def __init__(self):
        self.component_id = "learning_engine"
        self.running = False

        # Learning state
        self.experiences: List[LearningExperience] = []
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.adaptation_opportunities: List[AdaptationOpportunity] = []

        # Learning statistics
        self.learning_stats = {
            "experiences_processed": 0,
            "patterns_detected": 0,
            "adaptations_proposed": 0,
            "adaptations_implemented": 0,
            "learning_efficiency": 0.0
        }

        # Learning parameters
        self.learning_rate = 0.1
        self.min_confidence_threshold = 0.6
        self.pattern_detection_threshold = 0.8

    async def initialize(self) -> None:
        """Initialize learning engine"""
        logger.info("[LEARNING] Learning & Adaptation Engine initializing")

        # Load existing learning state
        await self._load_learning_state()

        logger.info("[LEARNING] Learning & Adaptation Engine initialized")

    async def start(self) -> None:
        """Start learning engine"""
        if self.running:
            return

        self.running = True

        # Start learning loops
        asyncio.create_task(self._continuous_learning_loop())
        asyncio.create_task(self._pattern_detection_loop())
        asyncio.create_task(self._adaptation_proposal_loop())

        logger.info("[LEARNING] Learning & Adaptation Engine started")

    async def stop(self) -> None:
        """Stop learning engine"""
        if not self.running:
            return

        self.running = False
        logger.info("[LEARNING] Learning & Adaptation Engine stopped")

    async def _load_learning_state(self) -> None:
        """Load existing learning state from storage"""
        try:
            # In a full implementation, this would load from database
            # For now, initialize fresh
            pass
        except Exception as e:
            logger.warning(f"[LEARNING] Failed to load learning state: {e}")

    async def record_experience(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> str:
        """
        Record a learning experience

        Args:
            context: Situation context
            action: Action taken
            outcome: Result of the action

        Returns:
            Experience ID
        """
        experience_id = f"exp_{int(datetime.now().timestamp() * 1000)}"

        # Analyze the experience for lessons
        lessons = await self._analyze_experience(context, action, outcome)
        confidence = self._calculate_experience_confidence(outcome)

        experience = LearningExperience(
            experience_id=experience_id,
            timestamp=datetime.now(timezone.utc),
            context=context,
            action_taken=action,
            outcome=outcome,
            lessons_learned=lessons,
            confidence=confidence
        )

        self.experiences.append(experience)
        self.learning_stats["experiences_processed"] += 1

        # Emit learning event
        await self._emit_learning_event("experience_recorded", {
            "experience_id": experience_id,
            "lessons_count": len(lessons),
            "confidence": confidence
        })

        logger.debug(f"[LEARNING] Recorded experience: {experience_id}")
        return experience_id

    async def _analyze_experience(
        self,
        context: Dict[str, Any],
        action: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> List[str]:
        """Analyze an experience to extract lessons"""
        lessons = []

        # Success/failure analysis
        success = outcome.get("success", False)
        if success:
            lessons.append("Action was successful in this context")
        else:
            error = outcome.get("error", "unknown")
            lessons.append(f"Action failed: {error}")

        # Performance analysis
        if "performance_metrics" in outcome:
            metrics = outcome["performance_metrics"]
            if metrics.get("response_time", 0) > 5.0:
                lessons.append("Slow response time detected")
            if metrics.get("resource_usage", 0) > 80:
                lessons.append("High resource usage detected")

        # Context pattern analysis
        context_patterns = self._identify_context_patterns(context)
        for pattern in context_patterns:
            lessons.append(f"Context pattern: {pattern}")

        # Action effectiveness
        effectiveness = self._assess_action_effectiveness(action, outcome)
        if effectiveness < 0.5:
            lessons.append("Action was not effective")
        elif effectiveness > 0.8:
            lessons.append("Action was highly effective")

        return lessons

    def _calculate_experience_confidence(self, outcome: Dict[str, Any]) -> float:
        """Calculate confidence in the experience"""
        base_confidence = 0.5

        # Higher confidence for clear outcomes
        if outcome.get("success") is True:
            base_confidence += 0.3
        elif outcome.get("success") is False:
            base_confidence += 0.2

        # Higher confidence for measured outcomes
        if "performance_metrics" in outcome:
            base_confidence += 0.1

        # Lower confidence for uncertain outcomes
        if outcome.get("uncertain", False):
            base_confidence -= 0.2

        return max(0.0, min(1.0, base_confidence))

    def _identify_context_patterns(self, context: Dict[str, Any]) -> List[str]:
        """Identify patterns in the context"""
        patterns = []

        # Time-based patterns
        hour = context.get("hour", datetime.now().hour)
        if 9 <= hour <= 17:
            patterns.append("business_hours")
        elif 18 <= hour <= 23:
            patterns.append("evening_hours")
        else:
            patterns.append("off_hours")

        # Load patterns
        system_load = context.get("system_load", 0.5)
        if system_load > 0.8:
            patterns.append("high_system_load")
        elif system_load < 0.3:
            patterns.append("low_system_load")

        # User pattern
        user_type = context.get("user_type")
        if user_type:
            patterns.append(f"user_type_{user_type}")

        return patterns

    def _assess_action_effectiveness(
        self,
        action: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> float:
        """Assess how effective the action was"""
        success = outcome.get("success", False)
        if success:
            # Successful actions are effective
            return 0.9

        # Analyze failure reasons
        error = outcome.get("error", "").lower()
        if "timeout" in error:
            return 0.3  # Timeout might not be action's fault
        elif "permission" in error:
            return 0.4  # Permission issues are environmental
        elif "network" in error:
            return 0.5  # Network issues are environmental
        else:
            return 0.2  # Likely action-related failure

    async def _continuous_learning_loop(self) -> None:
        """Continuous learning from recent experiences"""
        while self.running:
            try:
                # Process recent experiences
                recent_experiences = [
                    exp for exp in self.experiences
                    if (datetime.now(timezone.utc) - exp.timestamp).seconds < 300  # Last 5 minutes
                ]

                if recent_experiences:
                    # Update learning models
                    await self._update_learning_models(recent_experiences)

                    # Check for adaptation opportunities
                    opportunities = await self._identify_adaptation_opportunities(recent_experiences)
                    self.adaptation_opportunities.extend(opportunities)

                await asyncio.sleep(60)  # Learn every minute

            except Exception as e:
                logger.error(f"[LEARNING] Error in continuous learning loop: {e}")
                await asyncio.sleep(60)

    async def _pattern_detection_loop(self) -> None:
        """Detect patterns in learning data"""
        while self.running:
            try:
                # Analyze experiences for patterns
                patterns_found = await self._detect_patterns()

                for pattern in patterns_found:
                    pattern_key = pattern["pattern"]
                    if pattern_key not in self.patterns:
                        self.patterns[pattern_key] = pattern
                        self.learning_stats["patterns_detected"] += 1

                        await self._emit_learning_event("pattern_detected", {
                            "pattern": pattern_key,
                            "confidence": pattern.get("confidence", 0.0),
                            "occurrences": pattern.get("occurrences", 0)
                        })

                await asyncio.sleep(300)  # Detect patterns every 5 minutes

            except Exception as e:
                logger.error(f"[LEARNING] Error in pattern detection loop: {e}")
                await asyncio.sleep(300)

    async def _adaptation_proposal_loop(self) -> None:
        """Propose system adaptations based on learning"""
        while self.running:
            try:
                # Review adaptation opportunities
                if self.adaptation_opportunities:
                    # Prioritize opportunities
                    prioritized = sorted(
                        self.adaptation_opportunities,
                        key=lambda x: x.expected_benefit,
                        reverse=True
                    )

                    # Propose top opportunities
                    for opportunity in prioritized[:3]:  # Top 3
                        if opportunity.expected_benefit > 0.7:  # High benefit threshold
                            await self._propose_adaptation(opportunity)

                await asyncio.sleep(600)  # Propose adaptations every 10 minutes

            except Exception as e:
                logger.error(f"[LEARNING] Error in adaptation proposal loop: {e}")
                await asyncio.sleep(600)

    async def _update_learning_models(self, experiences: List[LearningExperience]) -> None:
        """Update internal learning models"""
        # Simple model updates based on experience
        success_rate = sum(1 for exp in experiences if exp.outcome.get("success")) / len(experiences)

        # Adjust learning rate based on success
        if success_rate > 0.8:
            self.learning_rate = min(0.5, self.learning_rate * 1.1)  # Increase learning rate
        elif success_rate < 0.5:
            self.learning_rate = max(0.01, self.learning_rate * 0.9)  # Decrease learning rate

        # Update learning efficiency
        self.learning_stats["learning_efficiency"] = success_rate

    async def _identify_adaptation_opportunities(
        self,
        experiences: List[LearningExperience]
    ) -> List[AdaptationOpportunity]:
        """Identify opportunities for system adaptation"""
        opportunities = []

        # Analyze performance patterns
        slow_responses = [
            exp for exp in experiences
            if exp.outcome.get("performance_metrics", {}).get("response_time", 0) > 3.0
        ]

        if len(slow_responses) > len(experiences) * 0.3:  # 30% slow responses
            opportunities.append(AdaptationOpportunity(
                opportunity_id=f"adapt_{int(datetime.now().timestamp())}",
                pattern_detected="slow_response_pattern",
                current_performance=0.7,
                proposed_improvement={
                    "action": "optimize_response_time",
                    "target": "api_endpoints",
                    "method": "caching_improvement"
                },
                expected_benefit=0.6,
                risk_level="low"
            ))

        # Analyze error patterns
        error_experiences = [
            exp for exp in experiences
            if not exp.outcome.get("success", False)
        ]

        if len(error_experiences) > len(experiences) * 0.2:  # 20% errors
            opportunities.append(AdaptationOpportunity(
                opportunity_id=f"adapt_{int(datetime.now().timestamp()) + 1}",
                pattern_detected="high_error_rate",
                current_performance=0.8,
                proposed_improvement={
                    "action": "improve_error_handling",
                    "target": "error_recovery",
                    "method": "circuit_breaker_implementation"
                },
                expected_benefit=0.5,
                risk_level="medium"
            ))

        return opportunities

    async def _detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect patterns in learning data"""
        patterns = []

        if len(self.experiences) < 10:  # Need minimum data
            return patterns

        # Simple pattern detection
        # Group experiences by context patterns
        context_groups = {}
        for exp in self.experiences[-100:]:  # Last 100 experiences
            patterns_in_exp = self._identify_context_patterns(exp.context)
            for pattern in patterns_in_exp:
                if pattern not in context_groups:
                    context_groups[pattern] = []
                context_groups[pattern].append(exp)

        # Find significant patterns
        for pattern_name, experiences in context_groups.items():
            if len(experiences) >= 5:  # At least 5 occurrences
                success_rate = sum(1 for exp in experiences if exp.outcome.get("success")) / len(experiences)

                if success_rate >= self.pattern_detection_threshold:
                    patterns.append({
                        "pattern": pattern_name,
                        "confidence": success_rate,
                        "occurrences": len(experiences),
                        "type": "context_pattern"
                    })

        return patterns

    async def _propose_adaptation(self, opportunity: AdaptationOpportunity) -> None:
        """Propose a system adaptation"""
        self.learning_stats["adaptations_proposed"] += 1

        # In a full implementation, this would submit to governance
        # For now, just log the proposal

        await self._emit_learning_event("adaptation_proposed", {
            "opportunity_id": opportunity.opportunity_id,
            "pattern": opportunity.pattern_detected,
            "expected_benefit": opportunity.expected_benefit,
            "risk_level": opportunity.risk_level
        })

        logger.info(f"[LEARNING] Adaptation proposed: {opportunity.pattern_detected}")

    async def _emit_learning_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit a learning-related event"""
        try:
            # Emit to event bus
            from backend.core.unified_event_publisher import get_unified_publisher
            event_bus = get_unified_publisher()

            await event_bus.publish_event(
                event_type=f"learning.{event_type}",
                payload={
                    **data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "learning_engine": self.component_id
                },
                source=self.component_id
            )
        except Exception as e:
            logger.debug(f"[LEARNING] Failed to emit learning event: {e}")

    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        return {
            "component_id": self.component_id,
            "running": self.running,
            "statistics": self.learning_stats.copy(),
            "experiences_count": len(self.experiences),
            "patterns_count": len(self.patterns),
            "adaptation_opportunities": len(self.adaptation_opportunities),
            "learning_parameters": {
                "learning_rate": self.learning_rate,
                "min_confidence_threshold": self.min_confidence_threshold,
                "pattern_detection_threshold": self.pattern_detection_threshold
            }
        }

    async def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning insights"""
        recent_experiences = sorted(
            self.experiences,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

        insights = []
        for exp in recent_experiences:
            insights.append({
                "experience_id": exp.experience_id,
                "timestamp": exp.timestamp.isoformat(),
                "lessons": exp.lessons_learned,
                "confidence": exp.confidence,
                "outcome_success": exp.outcome.get("success", False)
            })

        return insights


# Global instance
learning_engine = LearningEngine()</code></edit_file>
