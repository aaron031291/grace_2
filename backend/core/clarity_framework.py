"""
Clarity Framework
Transparent decision-making and reasoning framework

Part of Grace's unbreakable core - ensures all decisions are explainable
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

from .immutable_log import immutable_log
from .message_bus import message_bus, MessagePriority

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions Grace makes"""
    AUTONOMOUS_ACTION = "autonomous_action"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"
    POLICY_ENFORCEMENT = "policy_enforcement"
    RISK_ASSESSMENT = "risk_assessment"
    TRUST_CALCULATION = "trust_calculation"
    PROPOSAL_CREATION = "proposal_creation"


class ClarityLevel(Enum):
    """How much explanation is needed"""
    MINIMAL = "minimal"  # Just record the decision
    STANDARD = "standard"  # Include reasoning
    DETAILED = "detailed"  # Full explanation with alternatives
    COMPLETE = "complete"  # Everything (for critical decisions)


class Decision:
    """A single decision with complete reasoning"""
    
    def __init__(
        self,
        decision_id: str,
        decision_type: DecisionType,
        actor: str,
        action: str,
        resource: str
    ):
        self.decision_id = decision_id
        self.decision_type = decision_type
        self.actor = actor
        self.action = action
        self.resource = resource
        self.timestamp = datetime.utcnow()
        
        # Reasoning
        self.rationale = ""
        self.alternatives_considered = []
        self.chosen_alternative = None
        self.confidence = 0.0
        self.risk_score = 0.0
        
        # Evidence
        self.evidence = []
        self.metrics = {}
        self.kpis = {}
        
        # Outcome
        self.approved = False
        self.executed = False
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision_id': self.decision_id,
            'decision_type': self.decision_type.value,
            'actor': self.actor,
            'action': self.action,
            'resource': self.resource,
            'timestamp': self.timestamp.isoformat(),
            'rationale': self.rationale,
            'alternatives': self.alternatives_considered,
            'chosen': self.chosen_alternative,
            'confidence': self.confidence,
            'risk_score': self.risk_score,
            'evidence': self.evidence,
            'metrics': self.metrics,
            'kpis': self.kpis,
            'approved': self.approved,
            'executed': self.executed,
            'result': self.result
        }


class ClarityFramework:
    """
    Clarity Framework - Makes all Grace's decisions transparent
    
    Every decision includes:
    - What was decided
    - Why (rationale)
    - What alternatives were considered
    - What evidence supports it
    - Confidence and risk scores
    - Whether human approval needed
    
    Part of the unbreakable core
    """
    
    def __init__(self):
        self.decisions = []
        self.decision_count = 0
        self.running = False
    
    async def start(self):
        """Start clarity framework"""
        self.running = True
        logger.info("[CLARITY] Framework started - transparent decision-making active")
    
    async def record_decision(
        self,
        decision_type: DecisionType,
        actor: str,
        action: str,
        resource: str,
        rationale: str,
        confidence: float,
        risk_score: float,
        clarity_level: ClarityLevel = ClarityLevel.STANDARD,
        alternatives: List[str] = None,
        evidence: List[Dict[str, Any]] = None,
        metrics: Dict[str, Any] = None,
        kpis: Dict[str, Any] = None
    ) -> Decision:
        """
        Record a decision with full transparency
        
        Args:
            decision_type: Type of decision
            actor: Who made the decision
            action: What action was taken
            resource: What resource was affected
            rationale: Why this decision was made
            confidence: Confidence score (0.0-1.0)
            risk_score: Risk score (0.0-1.0)
            clarity_level: How detailed the explanation
            alternatives: Alternatives that were considered
            evidence: Supporting evidence
            metrics: Relevant metrics
            kpis: KPIs measured
        
        Returns:
            Decision object with complete reasoning
        """
        
        self.decision_count += 1
        decision_id = f"decision_{self.decision_count}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        decision = Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            actor=actor,
            action=action,
            resource=resource
        )
        
        # Fill in reasoning
        decision.rationale = rationale
        decision.confidence = confidence
        decision.risk_score = risk_score
        decision.alternatives_considered = alternatives or []
        decision.evidence = evidence or []
        decision.metrics = metrics or {}
        decision.kpis = kpis or {}
        
        # Store decision
        self.decisions.append(decision)
        
        # Log to immutable log
        await immutable_log.append(
            actor=actor,
            action=action,
            resource=resource,
            decision={
                'decision_id': decision_id,
                'rationale': rationale,
                'confidence': confidence,
                'risk_score': risk_score,
                'approved': decision.approved
            },
            metadata=decision.to_dict()
        )
        
        # Publish to message bus
        await message_bus.publish(
            source='clarity_framework',
            topic='system.clarity',
            payload=decision.to_dict(),
            priority=MessagePriority.NORMAL
        )
        
        logger.info(f"[CLARITY] Decision recorded: {decision_id} ({actor}: {action})")
        
        return decision
    
    async def explain_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full explanation of a decision
        
        Returns human-readable explanation
        """
        
        decision = next((d for d in self.decisions if d.decision_id == decision_id), None)
        
        if not decision:
            return None
        
        explanation = {
            'decision_id': decision_id,
            'summary': f"{decision.actor} decided to {decision.action} on {decision.resource}",
            'rationale': decision.rationale,
            'confidence': f"{decision.confidence * 100:.1f}%",
            'risk_level': self._risk_level_text(decision.risk_score),
            'timestamp': decision.timestamp.isoformat(),
            'reasoning_chain': self._build_reasoning_chain(decision),
            'evidence_summary': f"{len(decision.evidence)} pieces of evidence",
            'kpi_summary': f"{len(decision.kpis)} KPIs measured",
            'approval_status': 'Approved' if decision.approved else 'Pending' if not decision.executed else 'N/A'
        }
        
        return explanation
    
    def _risk_level_text(self, risk_score: float) -> str:
        """Convert risk score to text"""
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.6:
            return "Medium"
        elif risk_score < 0.8:
            return "High"
        else:
            return "Critical"
    
    def _build_reasoning_chain(self, decision: Decision) -> List[str]:
        """Build step-by-step reasoning chain"""
        
        chain = []
        
        # What was the situation
        chain.append(f"Situation: {decision.actor} needed to decide on {decision.action}")
        
        # What alternatives were considered
        if decision.alternatives_considered:
            chain.append(f"Alternatives considered: {', '.join(decision.alternatives_considered)}")
        
        # What evidence was available
        if decision.evidence:
            chain.append(f"Evidence: {len(decision.evidence)} factors analyzed")
        
        # What was decided
        chain.append(f"Decision: {decision.action}")
        
        # Why
        chain.append(f"Reasoning: {decision.rationale}")
        
        # Confidence and risk
        chain.append(f"Confidence: {decision.confidence * 100:.1f}%, Risk: {self._risk_level_text(decision.risk_score)}")
        
        return chain
    
    async def generate_clarity_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        actor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate clarity report showing all decisions
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            actor: Filter by actor
        
        Returns:
            Clarity report with all decisions explained
        """
        
        # Filter decisions
        filtered = self.decisions
        
        if start_time:
            filtered = [d for d in filtered if d.timestamp >= start_time]
        
        if end_time:
            filtered = [d for d in filtered if d.timestamp <= end_time]
        
        if actor:
            filtered = [d for d in filtered if d.actor == actor]
        
        # Calculate statistics
        total = len(filtered)
        approved = sum(1 for d in filtered if d.approved)
        avg_confidence = sum(d.confidence for d in filtered) / total if total > 0 else 0
        avg_risk = sum(d.risk_score for d in filtered) / total if total > 0 else 0
        
        report = {
            'report_id': f"clarity_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.utcnow().isoformat(),
            'time_range': {
                'start': start_time.isoformat() if start_time else 'all',
                'end': end_time.isoformat() if end_time else 'all'
            },
            'actor_filter': actor or 'all',
            'statistics': {
                'total_decisions': total,
                'approved_decisions': approved,
                'avg_confidence': avg_confidence,
                'avg_risk': avg_risk
            },
            'decisions': [d.to_dict() for d in filtered]
        }
        
        logger.info(f"[CLARITY] Generated report: {total} decisions")
        
        return report
    
    def get_stats(self) -> Dict[str, Any]:
        """Get clarity framework statistics"""
        
        return {
            'running': self.running,
            'total_decisions': self.decision_count,
            'recent_decisions': len(self.decisions),
            'avg_confidence': sum(d.confidence for d in self.decisions) / len(self.decisions) if self.decisions else 0,
            'avg_risk': sum(d.risk_score for d in self.decisions) / len(self.decisions) if self.decisions else 0
        }


# Global instance - Grace's transparency layer
clarity_framework = ClarityFramework()
