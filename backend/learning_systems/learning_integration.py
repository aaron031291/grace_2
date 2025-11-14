"""
Learning Integration - Continuous improvement through decision outcomes

Logs every decision -> outcome, feeds analytics/ML to refine detection,
playbook selection, and threshold tuning. Self-upgrades heuristics when
confidence crosses thresholds (with full audit trail).
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json

from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent


@dataclass
class OutcomeRecord:
    """Decision outcome for learning"""
    record_id: str
    decision_id: str
    decision_type: str
    context: Dict[str, Any]
    action_taken: str
    parameters: Dict[str, Any]
    expected_outcome: str
    actual_outcome: str
    success: bool
    latency_seconds: float
    side_effects: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LearningInsight:
    """Learned insight from outcomes"""
    insight_id: str
    pattern: str
    confidence: float
    evidence_count: int
    recommendation: str
    heuristic_update: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HeuristicUpdate:
    """Self-upgrade to decision heuristics"""
    update_id: str
    subsystem: str
    parameter: str
    old_value: Any
    new_value: Any
    justification: str
    confidence: float
    approved: bool = False
    applied_at: Optional[datetime] = None


class OutcomeTracker:
    """Tracks decision -> outcome pairs for learning"""
    
    def __init__(self):
        self.outcomes: List[OutcomeRecord] = []
        self.outcome_index: Dict[str, OutcomeRecord] = {}
    
    async def record_outcome(
        self,
        decision_id: str,
        decision_type: str,
        context: Dict,
        action_taken: str,
        parameters: Dict,
        expected_outcome: str,
        actual_outcome: str,
        success: bool,
        latency_seconds: float
    ) -> OutcomeRecord:
        """Record outcome of a decision"""
        
        record = OutcomeRecord(
            record_id=f"outcome_{datetime.utcnow().timestamp()}",
            decision_id=decision_id,
            decision_type=decision_type,
            context=context,
            action_taken=action_taken,
            parameters=parameters,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            success=success,
            latency_seconds=latency_seconds,
            side_effects=[]
        )
        
        self.outcomes.append(record)
        self.outcome_index[record.record_id] = record
        
        await immutable_log.append(
            actor="learning_system",
            action="outcome_recorded",
            resource=record.record_id,
            subsystem="outcome_tracker",
            payload={
                "decision_id": decision_id,
                "decision_type": decision_type,
                "success": success,
                "latency": latency_seconds
            },
            result="recorded"
        )
        
        return record
    
    async def get_outcomes_for_pattern(
        self,
        decision_type: str,
        lookback_hours: int = 168
    ) -> List[OutcomeRecord]:
        """Get recent outcomes matching a pattern"""
        cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        return [
            o for o in self.outcomes
            if o.decision_type == decision_type and o.timestamp >= cutoff
        ]
    
    async def calculate_success_rate(
        self,
        decision_type: str,
        context_filter: Optional[Dict] = None
    ) -> float:
        """Calculate success rate for a decision type"""
        
        outcomes = await self.get_outcomes_for_pattern(decision_type)
        
        if context_filter:
            outcomes = [
                o for o in outcomes
                if all(o.context.get(k) == v for k, v in context_filter.items())
            ]
        
        if not outcomes:
            return 0.0
        
        successes = sum(1 for o in outcomes if o.success)
        return successes / len(outcomes)


class PatternAnalyzer:
    """Analyzes outcome patterns to extract insights"""
    
    def __init__(self, outcome_tracker: OutcomeTracker):
        self.tracker = outcome_tracker
        self.insights: Dict[str, LearningInsight] = {}
    
    async def analyze_patterns(self) -> List[LearningInsight]:
        """Analyze outcomes to find patterns and insights"""
        
        insights = []
        
        decision_types = set(o.decision_type for o in self.tracker.outcomes)
        
        for decision_type in decision_types:
            outcomes = await self.tracker.get_outcomes_for_pattern(decision_type)
            
            if len(outcomes) < 10:
                continue
            
            success_rate = sum(1 for o in outcomes if o.success) / len(outcomes)
            avg_latency = sum(o.latency_seconds for o in outcomes) / len(outcomes)
            
            if success_rate < 0.6:
                insight = await self._generate_improvement_insight(
                    decision_type, outcomes, success_rate
                )
                insights.append(insight)
            
            if avg_latency > 10.0:
                insight = await self._generate_performance_insight(
                    decision_type, outcomes, avg_latency
                )
                insights.append(insight)
            
            context_patterns = await self._find_context_correlations(outcomes)
            for pattern in context_patterns:
                insights.append(pattern)
        
        for insight in insights:
            self.insights[insight.insight_id] = insight
        
        return insights
    
    async def _generate_improvement_insight(
        self,
        decision_type: str,
        outcomes: List[OutcomeRecord],
        success_rate: float
    ) -> LearningInsight:
        """Generate insight about improving success rate"""
        
        failures = [o for o in outcomes if not o.success]
        common_contexts = await self._find_common_context(failures)
        
        recommendation = f"Review {decision_type} decisions in contexts: {common_contexts}"
        
        heuristic = {
            "type": "threshold_adjustment",
            "target": f"{decision_type}_confidence_threshold",
            "adjustment": "increase_by_0.1",
            "reason": f"low_success_rate_{success_rate:.2f}"
        }
        
        return LearningInsight(
            insight_id=f"insight_{datetime.utcnow().timestamp()}",
            pattern=f"low_success_rate_{decision_type}",
            confidence=0.8,
            evidence_count=len(failures),
            recommendation=recommendation,
            heuristic_update=heuristic
        )
    
    async def _generate_performance_insight(
        self,
        decision_type: str,
        outcomes: List[OutcomeRecord],
        avg_latency: float
    ) -> LearningInsight:
        """Generate insight about performance"""
        
        return LearningInsight(
            insight_id=f"insight_{datetime.utcnow().timestamp()}",
            pattern=f"high_latency_{decision_type}",
            confidence=0.75,
            evidence_count=len(outcomes),
            recommendation=f"Optimize {decision_type} execution - avg latency {avg_latency:.2f}s"
        )
    
    async def _find_context_correlations(
        self,
        outcomes: List[OutcomeRecord]
    ) -> List[LearningInsight]:
        """Find context factors that correlate with success/failure"""
        
        insights = []
        
        context_keys = set()
        for outcome in outcomes:
            context_keys.update(outcome.context.keys())
        
        for key in context_keys:
            success_with_key = [o for o in outcomes if key in o.context and o.success]
            failure_with_key = [o for o in outcomes if key in o.context and not o.success]
            
            if len(failure_with_key) > len(success_with_key) * 2:
                insights.append(LearningInsight(
                    insight_id=f"insight_{datetime.utcnow().timestamp()}_{key}",
                    pattern=f"context_{key}_correlates_with_failure",
                    confidence=0.65,
                    evidence_count=len(failure_with_key),
                    recommendation=f"Review decisions with context key '{key}' - high failure correlation"
                ))
        
        return insights
    
    async def _find_common_context(self, outcomes: List[OutcomeRecord]) -> Dict:
        """Find common context elements across outcomes"""
        if not outcomes:
            return {}
        
        common = {}
        for key in outcomes[0].context:
            values = [o.context.get(key) for o in outcomes if key in o.context]
            if len(values) == len(outcomes) and len(set(values)) == 1:
                common[key] = values[0]
        
        return common


class ThresholdOptimizer:
    """Automatically tunes detection and decision thresholds"""
    
    def __init__(self, outcome_tracker: OutcomeTracker):
        self.tracker = outcome_tracker
        self.thresholds: Dict[str, float] = defaultdict(lambda: 0.5)
        self.threshold_history: List[Dict] = []
    
    async def optimize_threshold(
        self,
        subsystem: str,
        metric: str,
        target_success_rate: float = 0.85
    ) -> Optional[HeuristicUpdate]:
        """Optimize a threshold based on outcomes"""
        
        threshold_key = f"{subsystem}.{metric}"
        current_threshold = self.thresholds[threshold_key]
        
        outcomes = await self.tracker.get_outcomes_for_pattern(subsystem)
        if len(outcomes) < 20:
            return None
        
        current_success_rate = sum(1 for o in outcomes if o.success) / len(outcomes)
        
        if abs(current_success_rate - target_success_rate) < 0.05:
            return None
        
        if current_success_rate < target_success_rate:
            new_threshold = current_threshold * 1.1
            justification = f"Increasing threshold from {current_threshold:.3f} to {new_threshold:.3f} to improve success rate from {current_success_rate:.2%} to {target_success_rate:.2%}"
        else:
            new_threshold = current_threshold * 0.95
            justification = f"Decreasing threshold from {current_threshold:.3f} to {new_threshold:.3f} - success rate {current_success_rate:.2%} exceeds target {target_success_rate:.2%}"
        
        new_threshold = max(0.1, min(0.95, new_threshold))
        
        update = HeuristicUpdate(
            update_id=f"update_{datetime.utcnow().timestamp()}",
            subsystem=subsystem,
            parameter=metric,
            old_value=current_threshold,
            new_value=new_threshold,
            justification=justification,
            confidence=0.75
        )
        
        return update
    
    async def apply_threshold_update(self, update: HeuristicUpdate):
        """Apply approved threshold update"""
        threshold_key = f"{update.subsystem}.{update.parameter}"
        self.thresholds[threshold_key] = update.new_value
        update.approved = True
        update.applied_at = datetime.utcnow()
        
        self.threshold_history.append({
            "update_id": update.update_id,
            "threshold": threshold_key,
            "old": update.old_value,
            "new": update.new_value,
            "applied_at": update.applied_at
        })
        
        await immutable_log.append(
            actor="learning_system",
            action="threshold_updated",
            resource=threshold_key,
            subsystem="threshold_optimizer",
            payload={
                "old_value": update.old_value,
                "new_value": update.new_value,
                "justification": update.justification
            },
            result="applied"
        )


class PlaybookSelector:
    """ML-enhanced playbook selection"""
    
    def __init__(self, outcome_tracker: OutcomeTracker):
        self.tracker = outcome_tracker
        self.playbook_performance: Dict[str, Dict] = defaultdict(lambda: {
            "executions": 0,
            "successes": 0,
            "avg_latency": 0.0,
            "success_by_context": defaultdict(lambda: {"total": 0, "success": 0})
        })
    
    async def select_playbook(
        self,
        incident_type: str,
        context: Dict[str, Any],
        candidate_playbooks: List[str]
    ) -> Tuple[str, float]:
        """Select best playbook based on learned performance"""
        
        scores = {}
        
        for playbook_id in candidate_playbooks:
            perf = self.playbook_performance[playbook_id]
            
            if perf["executions"] == 0:
                scores[playbook_id] = 0.5
                continue
            
            base_success_rate = perf["successes"] / perf["executions"]
            
            context_key = self._context_signature(context)
            context_perf = perf["success_by_context"][context_key]
            
            if context_perf["total"] > 0:
                context_success_rate = context_perf["success"] / context_perf["total"]
                confidence = min(context_perf["total"] / 10.0, 1.0)
                final_score = (base_success_rate * (1 - confidence)) + (context_success_rate * confidence)
            else:
                final_score = base_success_rate
            
            latency_penalty = min(perf["avg_latency"] / 100.0, 0.2)
            final_score -= latency_penalty
            
            scores[playbook_id] = final_score
        
        best_playbook = max(scores.items(), key=lambda x: x[1])
        return best_playbook[0], best_playbook[1]
    
    async def record_playbook_outcome(
        self,
        playbook_id: str,
        context: Dict,
        success: bool,
        latency: float
    ):
        """Record playbook execution outcome"""
        
        perf = self.playbook_performance[playbook_id]
        perf["executions"] += 1
        if success:
            perf["successes"] += 1
        
        perf["avg_latency"] = (
            (perf["avg_latency"] * (perf["executions"] - 1) + latency) /
            perf["executions"]
        )
        
        context_key = self._context_signature(context)
        context_perf = perf["success_by_context"][context_key]
        context_perf["total"] += 1
        if success:
            context_perf["success"] += 1
    
    def _context_signature(self, context: Dict) -> str:
        """Create signature from context for matching"""
        relevant_keys = ["incident_type", "severity", "service", "region"]
        sig_parts = []
        for key in relevant_keys:
            if key in context:
                sig_parts.append(f"{key}={context[key]}")
        return "|".join(sig_parts) if sig_parts else "default"


class SelfUpgradeEngine:
    """Autonomously upgrades heuristics when confidence thresholds met"""
    
    def __init__(
        self,
        pattern_analyzer: PatternAnalyzer,
        threshold_optimizer: ThresholdOptimizer
    ):
        self.analyzer = pattern_analyzer
        self.optimizer = threshold_optimizer
        self.upgrade_confidence_threshold = 0.75
        self.pending_upgrades: List[HeuristicUpdate] = []
        self.applied_upgrades: List[HeuristicUpdate] = []
    
    async def evaluate_upgrades(self):
        """Evaluate potential heuristic upgrades"""
        
        insights = await self.analyzer.analyze_patterns()
        
        for insight in insights:
            if insight.confidence >= self.upgrade_confidence_threshold:
                if insight.heuristic_update:
                    await self._propose_upgrade(insight)
    
    async def _propose_upgrade(self, insight: LearningInsight):
        """Propose a heuristic upgrade based on insight"""
        
        heuristic = insight.heuristic_update
        
        if heuristic["type"] == "threshold_adjustment":
            update = await self._create_threshold_update(heuristic, insight)
            if update:
                self.pending_upgrades.append(update)
                
                await trigger_mesh.publish(TriggerEvent(
                    event_type="learning.upgrade_proposed",
                    source="self_upgrade_engine",
                    actor="grace_agent",
                    resource=update.update_id,
                    payload={
                        "subsystem": update.subsystem,
                        "parameter": update.parameter,
                        "old_value": update.old_value,
                        "new_value": update.new_value,
                        "confidence": update.confidence,
                        "justification": update.justification
                    },
                    timestamp=datetime.utcnow()
                ))
    
    async def _create_threshold_update(
        self,
        heuristic: Dict,
        insight: LearningInsight
    ) -> Optional[HeuristicUpdate]:
        """Create threshold update from heuristic"""
        
        parts = heuristic["target"].split("_")
        subsystem = parts[0]
        parameter = "_".join(parts[1:])
        
        current = self.optimizer.thresholds[heuristic["target"]]
        
        if heuristic["adjustment"] == "increase_by_0.1":
            new_value = min(current + 0.1, 0.95)
        elif heuristic["adjustment"] == "decrease_by_0.1":
            new_value = max(current - 0.1, 0.1)
        else:
            return None
        
        return HeuristicUpdate(
            update_id=f"upgrade_{datetime.utcnow().timestamp()}",
            subsystem=subsystem,
            parameter=parameter,
            old_value=current,
            new_value=new_value,
            justification=f"{insight.recommendation} (confidence: {insight.confidence:.2f}, evidence: {insight.evidence_count})",
            confidence=insight.confidence
        )
    
    async def auto_approve_upgrades(self):
        """Auto-approve high-confidence upgrades with audit trail"""
        
        for upgrade in self.pending_upgrades[:]:
            if upgrade.confidence >= 0.85 and not upgrade.approved:
                upgrade.approved = True
                await self.optimizer.apply_threshold_update(upgrade)
                
                self.pending_upgrades.remove(upgrade)
                self.applied_upgrades.append(upgrade)
                
                await immutable_log.append(
                    actor="learning_system",
                    action="heuristic_auto_upgraded",
                    resource=upgrade.update_id,
                    subsystem="self_upgrade_engine",
                    payload={
                        "subsystem": upgrade.subsystem,
                        "parameter": upgrade.parameter,
                        "old_value": upgrade.old_value,
                        "new_value": upgrade.new_value,
                        "confidence": upgrade.confidence,
                        "justification": upgrade.justification
                    },
                    result="applied"
                )
                
                print(f"✓ Auto-upgraded: {upgrade.subsystem}.{upgrade.parameter} = {upgrade.new_value} (was {upgrade.old_value})")


class LearningIntegration:
    """Main learning system coordinator"""
    
    def __init__(self):
        self.outcome_tracker = OutcomeTracker()
        self.pattern_analyzer = PatternAnalyzer(self.outcome_tracker)
        self.threshold_optimizer = ThresholdOptimizer(self.outcome_tracker)
        self.playbook_selector = PlaybookSelector(self.outcome_tracker)
        self.upgrade_engine = SelfUpgradeEngine(self.pattern_analyzer, self.threshold_optimizer)
    
    async def start(self):
        """Start learning integration"""
        asyncio.create_task(self._learning_loop())
        print("✓ Learning Integration started")
    
    async def _learning_loop(self):
        """Background loop for continuous learning"""
        while True:
            await asyncio.sleep(3600)
            
            await self.upgrade_engine.evaluate_upgrades()
            await self.upgrade_engine.auto_approve_upgrades()


learning_integration = LearningIntegration()
