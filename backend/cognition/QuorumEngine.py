"""QuorumEngine - Trust-Weighted Specialist Consensus

Coordinates multiple specialists (reflection, hunter, meta, causal, MLDL)
and reaches consensus through trust-weighted voting.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import math
import logging

from .models import (
    DecisionTask, ConsensusDecision, SpecialistProposal,
    DecisionStrategy, RiskLevel
)
from .GraceLoopOutput import GraceLoopOutput

logger = logging.getLogger(__name__)

class QuorumEngine:
    """
    Trust-weighted specialist consensus engine.
    
    Collects proposals from multiple specialists and uses
    trust scoring + governance constraints to reach decisions.
    """
    
    def __init__(self):
        self.decision_history: List[ConsensusDecision] = []
        self.specialist_trust: Dict[str, float] = {
            'reflection': 0.85,
            'hunter': 0.90,
            'meta': 0.88,
            'causal': 0.82,
            'mldl': 0.80,
            'temporal': 0.78,
            'code_understanding': 0.75
        }
        self.track_records: Dict[str, List[float]] = {}
    
    def deliberate(self, task: DecisionTask) -> ConsensusDecision:
        """
        Main deliberation method - reaches consensus on task.
        
        Args:
            task: DecisionTask with proposals and constraints
            
        Returns:
            ConsensusDecision with chosen proposal and rationale
        """
        logger.info(f"QuorumEngine deliberating on task: {task.task_id}")
        
        if not task.specialist_proposals:
            raise ValueError("No specialist proposals to deliberate on")
        
        # Score all proposals
        scored_proposals = self._score_proposals(task)
        
        # Apply decision strategy
        if task.strategy == DecisionStrategy.MAJORITY:
            decision = self._majority_vote(task, scored_proposals)
        elif task.strategy == DecisionStrategy.SOFTMAX_WEIGHTED:
            decision = self._softmax_weighted_vote(task, scored_proposals)
        elif task.strategy == DecisionStrategy.MIN_RISK:
            decision = self._min_risk_vote(task, scored_proposals)
        elif task.strategy == DecisionStrategy.UNANIMOUS:
            decision = self._unanimous_vote(task, scored_proposals)
        else:
            decision = self._softmax_weighted_vote(task, scored_proposals)
        
        # Record decision
        self.decision_history.append(decision)
        
        logger.info(f"Decision reached: {decision.rationale[:100]}...")
        return decision
    
    def _score_proposals(
        self, 
        task: DecisionTask
    ) -> List[Tuple[SpecialistProposal, float]]:
        """
        Score each proposal based on trust, track record, and recency.
        
        Returns:
            List of (proposal, score) tuples
        """
        scored = []
        
        for proposal in task.specialist_proposals:
            # Base trust score
            trust = self.specialist_trust.get(proposal.specialist_name, 0.5)
            
            # Track record (historical accuracy)
            track_record = proposal.track_record
            
            # Recency weight (recent wins count more)
            recency = proposal.recency_weight
            
            # Governance compliance bonus
            governance_bonus = 1.0
            if proposal.output.constitutional_compliance:
                governance_bonus = 1.1
            if proposal.output.policy_tags:
                compliant_tags = sum(
                    1 for tag in proposal.output.policy_tags 
                    if tag.status == 'compliant'
                )
                governance_bonus *= (1.0 + 0.05 * compliant_tags)
            
            # Confidence in output
            confidence_weight = proposal.output.confidence
            
            # Combined score
            score = (
                trust * 0.3 +
                track_record * 0.25 +
                recency * 0.15 +
                confidence_weight * 0.2
            ) * governance_bonus
            
            # Risk adjustment - lower risk levels favor higher confidence
            if task.risk_level == RiskLevel.CRITICAL:
                if proposal.output.confidence < 0.9:
                    score *= 0.8
            elif task.risk_level == RiskLevel.HIGH:
                if proposal.output.confidence < 0.8:
                    score *= 0.9
            
            scored.append((proposal, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _majority_vote(
        self, 
        task: DecisionTask, 
        scored_proposals: List[Tuple[SpecialistProposal, float]]
    ) -> ConsensusDecision:
        """Simple majority voting - highest score wins"""
        winner_proposal, winner_score = scored_proposals[0]
        
        weights = {
            p.specialist_name: score 
            for p, score in scored_proposals
        }
        
        dissent = [
            p.output for p, _ in scored_proposals[1:]
        ]
        
        rationale = (
            f"Majority vote: {winner_proposal.specialist_name} "
            f"won with score {winner_score:.3f}. "
            f"Beat {len(dissent)} other proposals."
        )
        
        return ConsensusDecision(
            task_id=task.task_id,
            chosen_proposal=winner_proposal.output,
            rationale=rationale,
            weights=weights,
            dissent=dissent,
            confidence=winner_score,
            strategy_used=DecisionStrategy.MAJORITY,
            voting_summary={
                'winner': winner_proposal.specialist_name,
                'winner_score': winner_score,
                'total_proposals': len(scored_proposals)
            }
        )
    
    def _softmax_weighted_vote(
        self, 
        task: DecisionTask, 
        scored_proposals: List[Tuple[SpecialistProposal, float]]
    ) -> ConsensusDecision:
        """
        Softmax-weighted voting - blend proposals with temperature.
        Gives smooth distribution favoring highest scores.
        """
        # Extract scores
        scores = [score for _, score in scored_proposals]
        
        # Apply softmax with temperature
        temperature = 0.5  # Lower = more decisive
        exp_scores = [math.exp(s / temperature) for s in scores]
        total = sum(exp_scores)
        probabilities = [e / total for e in exp_scores]
        
        # Winner is highest probability
        winner_idx = probabilities.index(max(probabilities))
        winner_proposal, winner_score = scored_proposals[winner_idx]
        winner_prob = probabilities[winner_idx]
        
        weights = {
            p.specialist_name: prob 
            for (p, _), prob in zip(scored_proposals, probabilities)
        }
        
        dissent = [
            p.output for i, (p, _) in enumerate(scored_proposals) 
            if i != winner_idx
        ]
        
        rationale = (
            f"Softmax-weighted consensus: {winner_proposal.specialist_name} "
            f"selected with probability {winner_prob:.3f}. "
            f"Weighted by trust ({winner_proposal.trust_score:.2f}), "
            f"track record ({winner_proposal.track_record:.2f}), "
            f"and governance compliance."
        )
        
        return ConsensusDecision(
            task_id=task.task_id,
            chosen_proposal=winner_proposal.output,
            rationale=rationale,
            weights=weights,
            dissent=dissent,
            confidence=winner_prob,
            strategy_used=DecisionStrategy.SOFTMAX_WEIGHTED,
            voting_summary={
                'winner': winner_proposal.specialist_name,
                'probability': winner_prob,
                'temperature': temperature,
                'score_distribution': dict(zip(
                    [p.specialist_name for p, _ in scored_proposals],
                    probabilities
                ))
            }
        )
    
    def _min_risk_vote(
        self, 
        task: DecisionTask, 
        scored_proposals: List[Tuple[SpecialistProposal, float]]
    ) -> ConsensusDecision:
        """
        Minimum risk strategy - choose safest option under constraints.
        Favors proposals with high governance compliance and conservative actions.
        """
        # Filter by governance constraints
        valid_proposals = []
        for proposal, score in scored_proposals:
            if proposal.output.constitutional_compliance:
                # Check constraints
                meets_constraints = True
                for constraint in task.constraints:
                    # Check if proposal violates constraint
                    if any(tag.policy_name == constraint and tag.status != 'compliant' 
                           for tag in proposal.output.policy_tags):
                        meets_constraints = False
                        break
                
                if meets_constraints:
                    # Risk-adjusted score: penalize low confidence
                    risk_adjusted = score * proposal.output.confidence
                    valid_proposals.append((proposal, risk_adjusted))
        
        if not valid_proposals:
            # Fall back to highest governance compliance
            valid_proposals = [
                (p, s * (1.0 if p.output.constitutional_compliance else 0.5))
                for p, s in scored_proposals
            ]
        
        # Sort by risk-adjusted score
        valid_proposals.sort(key=lambda x: x[1], reverse=True)
        winner_proposal, winner_score = valid_proposals[0]
        
        weights = {
            p.specialist_name: score 
            for p, score in valid_proposals
        }
        
        dissent = [
            p.output for p, _ in valid_proposals[1:]
        ]
        
        rationale = (
            f"Minimum risk strategy: {winner_proposal.specialist_name} "
            f"chosen as safest option (risk-adjusted score {winner_score:.3f}). "
            f"Constitutional compliance: {winner_proposal.output.constitutional_compliance}, "
            f"Confidence: {winner_proposal.output.confidence:.2f}, "
            f"Met {len(task.constraints)} governance constraints."
        )
        
        return ConsensusDecision(
            task_id=task.task_id,
            chosen_proposal=winner_proposal.output,
            rationale=rationale,
            weights=weights,
            dissent=dissent,
            confidence=winner_proposal.output.confidence,
            governance_validated=True,
            strategy_used=DecisionStrategy.MIN_RISK,
            voting_summary={
                'winner': winner_proposal.specialist_name,
                'risk_adjusted_score': winner_score,
                'constraints_checked': len(task.constraints),
                'valid_candidates': len(valid_proposals)
            }
        )
    
    def _unanimous_vote(
        self, 
        task: DecisionTask, 
        scored_proposals: List[Tuple[SpecialistProposal, float]]
    ) -> ConsensusDecision:
        """
        Unanimous consensus - all specialists must agree.
        If no consensus, escalate to Parliament.
        """
        # Check if all proposals agree (same result)
        results = [p.output.result for p, _ in scored_proposals]
        
        if len(set(str(r) for r in results)) == 1:
            # Unanimous agreement
            winner_proposal, winner_score = scored_proposals[0]
            
            weights = {
                p.specialist_name: 1.0 
                for p, _ in scored_proposals
            }
            
            rationale = (
                f"Unanimous consensus: All {len(scored_proposals)} specialists "
                f"agree on outcome. High confidence decision."
            )
            
            return ConsensusDecision(
                task_id=task.task_id,
                chosen_proposal=winner_proposal.output,
                rationale=rationale,
                weights=weights,
                dissent=[],
                confidence=1.0,
                governance_validated=True,
                strategy_used=DecisionStrategy.UNANIMOUS,
                voting_summary={
                    'unanimous': True,
                    'specialist_count': len(scored_proposals)
                }
            )
        else:
            # No unanimous agreement - escalate
            winner_proposal, winner_score = scored_proposals[0]
            
            weights = {
                p.specialist_name: score 
                for p, score in scored_proposals
            }
            
            dissent = [
                p.output for p, _ in scored_proposals[1:]
            ]
            
            rationale = (
                f"No unanimous consensus reached among {len(scored_proposals)} "
                f"specialists. Escalating to Parliament for tie-breaking. "
                f"Top proposal from {winner_proposal.specialist_name}."
            )
            
            decision = ConsensusDecision(
                task_id=task.task_id,
                chosen_proposal=winner_proposal.output,
                rationale=rationale,
                weights=weights,
                dissent=dissent,
                confidence=0.5,
                strategy_used=DecisionStrategy.UNANIMOUS,
                voting_summary={
                    'unanimous': False,
                    'requires_escalation': True,
                    'specialist_count': len(scored_proposals)
                }
            )
            decision.chosen_proposal.requires_approval = True
            return decision
    
    def update_specialist_trust(self, specialist: str, outcome_success: bool):
        """Update specialist trust based on outcome"""
        if specialist not in self.specialist_trust:
            self.specialist_trust[specialist] = 0.5
        
        current = self.specialist_trust[specialist]
        
        # Exponential moving average
        alpha = 0.1
        new_value = 1.0 if outcome_success else 0.0
        self.specialist_trust[specialist] = alpha * new_value + (1 - alpha) * current
        
        # Track record
        if specialist not in self.track_records:
            self.track_records[specialist] = []
        self.track_records[specialist].append(1.0 if outcome_success else 0.0)
        
        # Keep last 100 outcomes
        if len(self.track_records[specialist]) > 100:
            self.track_records[specialist].pop(0)
    
    def get_specialist_track_record(self, specialist: str) -> float:
        """Get historical accuracy for specialist"""
        if specialist not in self.track_records or not self.track_records[specialist]:
            return 0.5
        return sum(self.track_records[specialist]) / len(self.track_records[specialist])
    
    def explain(self, consensus: ConsensusDecision) -> Dict[str, any]:
        """
        Explain consensus decision with auditable math.
        
        Returns detailed breakdown of voting process.
        """
        return {
            'task_id': consensus.task_id,
            'strategy': consensus.strategy_used.value,
            'winner': {
                'component': consensus.chosen_proposal.component,
                'confidence': consensus.chosen_proposal.confidence,
                'constitutional_compliance': consensus.chosen_proposal.constitutional_compliance
            },
            'weights': consensus.weights,
            'rationale': consensus.rationale,
            'voting_summary': consensus.voting_summary,
            'dissent_count': len(consensus.dissent),
            'overall_confidence': consensus.confidence,
            'governance_validated': consensus.governance_validated,
            'timestamp': consensus.created_at.isoformat()
        }
