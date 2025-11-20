"""
Unified Decision Engine - The Brain That Stitches Everything Together
Synthesizes inputs from Governance, AVN, MLDL Quorum, Learning, Memory into coherent decisions.

Complete implementation of all three phases:
- Phase 1: Define contracts
- Phase 2: Aggregation logic with weighted scoring
- Phase 3: Routing to autonomous loop, UI, learning
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# Phase 1: Define Contracts
# ============================================================================

class DecisionAction(Enum):
    """Possible decision actions"""
    EXECUTE = "execute"
    PAUSE = "pause"
    REJECT = "reject"
    ESCALATE = "escalate"
    RETRY = "retry"
    ROLLBACK = "rollback"


class ConflictType(Enum):
    """Types of contradictions found"""
    GOVERNANCE_POLICY = "governance_policy"
    HEALTH_STATE = "health_state"
    TRUST_SCORE = "trust_score"
    CONSENSUS_DIVERGENCE = "consensus_divergence"
    LEARNING_FEEDBACK = "learning_feedback"


@dataclass
class GovernanceInput:
    """Input from Governance system"""
    approved: bool
    approval_id: Optional[str]
    violated_policies: List[str] = field(default_factory=list)
    required_approvals: int = 0
    received_approvals: int = 0
    reasoning: str = ""
    trust_score: float = 1.0


@dataclass
class AVNInput:
    """Input from AVN (Autonomous Validation Network)"""
    health_state: str  # healthy, degraded, critical
    anomalies_detected: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = "none"  # none, low, medium, high, critical
    recommended_action: Optional[str] = None
    confidence: float = 1.0


@dataclass
class MLDLQuorumInput:
    """Input from MLDL Quorum consensus"""
    consensus_reached: bool
    consensus_action: Optional[str] = None
    vote_breakdown: Dict[str, int] = field(default_factory=dict)
    confidence: float = 0.0
    reasoning: List[str] = field(default_factory=list)


@dataclass
class LearningInput:
    """Input from Learning system"""
    insights: List[str] = field(default_factory=list)
    pattern_confidence: float = 0.0
    recommended_adjustments: List[str] = field(default_factory=list)
    similar_past_outcomes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MemoryInput:
    """Input from Memory system"""
    relevant_context: List[Dict[str, Any]] = field(default_factory=list)
    trust_scores: Dict[str, float] = field(default_factory=dict)
    contradictions_found: List[str] = field(default_factory=list)


@dataclass
class UnifiedDecision:
    """
    Phase 1: Output contract - Complete decision synthesis
    
    This is what the brain produces after considering all inputs
    """
    # Core decision
    action: DecisionAction
    confidence: float
    
    # Reasoning trail
    reasoning_chain_ids: List[str]
    primary_reasoning: str
    supporting_evidence: List[str]
    
    # Trust & quality
    trust_score: float
    quality_score: float
    
    # Conflicts & issues
    contradictions: List[Dict[str, Any]]
    warnings: List[str]
    
    # Recommendations
    recommended_next_loops: List[str]
    fallback_actions: List[str]
    
    # Metadata
    decision_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    synthesized_from: Dict[str, Any] = field(default_factory=dict)
    
    # Component scores (how much each system contributed)
    governance_weight: float = 0.0
    avn_weight: float = 0.0
    mldl_weight: float = 0.0
    learning_weight: float = 0.0
    memory_weight: float = 0.0


# ============================================================================
# Phase 2: Aggregation Logic
# ============================================================================

class UnifiedDecisionEngine:
    """
    The brain that synthesizes all layers into one coherent decision
    
    Strategy (Phase 2):
    - Governance failures override everything
    - AVN high-severity anomalies pause or alter actions
    - MLDL consensus drives which business/system action to take
    - Learning provides adjustments
    - Memory provides context and contradiction detection
    """
    
    def __init__(self):
        self.decisions_made = 0
        self.decisions_rejected = 0
        self.decisions_escalated = 0
        
        # Weighted scoring configuration
        self.weights = {
            'governance': 1.0,  # Governance veto power
            'avn': 0.8,          # Health is critical
            'mldl': 0.7,         # Consensus matters
            'learning': 0.5,     # Learning adjusts
            'memory': 0.6        # Context informs
        }
    
    async def synthesize(
        self,
        governance_decision: GovernanceInput,
        avn_state: AVNInput,
        mldl_consensus: MLDLQuorumInput,
        learning_insights: LearningInput,
        memory_context: MemoryInput,
        decision_id: Optional[str] = None
    ) -> UnifiedDecision:
        """
        Phase 2: Synthesize all inputs into unified decision
        
        Args:
            governance_decision: From governance system
            avn_state: From AVN health monitoring
            mldl_consensus: From quorum voting
            learning_insights: From learning system
            memory_context: From memory retrieval
            decision_id: Optional decision ID
            
        Returns:
            UnifiedDecision with action and reasoning
        """
        
        decision_id = decision_id or f"decision_{datetime.utcnow().timestamp()}"
        
        # Collect reasoning chain
        reasoning_chain = []
        contradictions = []
        warnings = []
        
        # ===== GOVERNANCE OVERRIDE =====
        # Governance failures override everything
        if not governance_decision.approved:
            action = DecisionAction.REJECT
            primary_reasoning = f"Governance rejected: {governance_decision.reasoning}"
            
            reasoning_chain.append("governance_rejection")
            warnings.append(f"Governance violations: {', '.join(governance_decision.violated_policies)}")
            
            if governance_decision.violated_policies:
                contradictions.append({
                    'type': ConflictType.GOVERNANCE_POLICY.value,
                    'severity': 'critical',
                    'details': f"Policies violated: {governance_decision.violated_policies}"
                })
            
            self.decisions_rejected += 1
            
            return self._build_decision(
                decision_id=decision_id,
                action=action,
                confidence=0.0,
                reasoning_chain=reasoning_chain,
                primary_reasoning=primary_reasoning,
                contradictions=contradictions,
                warnings=warnings,
                governance_weight=1.0,
                inputs={
                    'governance': governance_decision,
                    'avn': avn_state,
                    'mldl': mldl_consensus,
                    'learning': learning_insights,
                    'memory': memory_context
                }
            )
        
        # ===== AVN HIGH-SEVERITY ANOMALIES =====
        # AVN critical/high severity pauses or alters actions
        if avn_state.severity in ['critical', 'high']:
            
            if avn_state.severity == 'critical':
                action = DecisionAction.PAUSE
                primary_reasoning = "Critical health anomalies detected - pausing for safety"
                warnings.append(f"Critical anomalies: {len(avn_state.anomalies_detected)}")
            else:
                # High severity - check if recommended action is safe
                if avn_state.recommended_action == 'rollback':
                    action = DecisionAction.ROLLBACK
                    primary_reasoning = "High-severity anomalies - rolling back to safe state"
                else:
                    action = DecisionAction.PAUSE
                    primary_reasoning = "High-severity anomalies - pausing for assessment"
            
            reasoning_chain.append("avn_health_check")
            
            contradictions.append({
                'type': ConflictType.HEALTH_STATE.value,
                'severity': avn_state.severity,
                'details': f"{len(avn_state.anomalies_detected)} anomalies detected"
            })
            
            self.decisions_made += 1
            
            return self._build_decision(
                decision_id=decision_id,
                action=action,
                confidence=avn_state.confidence,
                reasoning_chain=reasoning_chain,
                primary_reasoning=primary_reasoning,
                contradictions=contradictions,
                warnings=warnings,
                avn_weight=0.8,
                inputs={
                    'governance': governance_decision,
                    'avn': avn_state,
                    'mldl': mldl_consensus,
                    'learning': learning_insights,
                    'memory': memory_context
                }
            )
        
        # ===== MLDL CONSENSUS DRIVES ACTION =====
        # MLDL consensus determines what to do
        if not mldl_consensus.consensus_reached:
            # No consensus - escalate for human decision
            action = DecisionAction.ESCALATE
            primary_reasoning = "No quorum consensus - escalating to human review"
            
            reasoning_chain.append("mldl_no_consensus")
            warnings.append(f"Vote breakdown: {mldl_consensus.vote_breakdown}")
            
            contradictions.append({
                'type': ConflictType.CONSENSUS_DIVERGENCE.value,
                'severity': 'medium',
                'details': f"Vote split: {mldl_consensus.vote_breakdown}"
            })
            
            self.decisions_escalated += 1
            
            return self._build_decision(
                decision_id=decision_id,
                action=action,
                confidence=0.5,
                reasoning_chain=reasoning_chain,
                primary_reasoning=primary_reasoning,
                contradictions=contradictions,
                warnings=warnings,
                mldl_weight=0.7,
                inputs={
                    'governance': governance_decision,
                    'avn': avn_state,
                    'mldl': mldl_consensus,
                    'learning': learning_insights,
                    'memory': memory_context
                }
            )
        
        # Consensus reached - use consensus action
        action = DecisionAction.EXECUTE if mldl_consensus.consensus_action else DecisionAction.RETRY
        primary_reasoning = f"MLDL consensus: {mldl_consensus.consensus_action or 'retry'}"
        reasoning_chain.append("mldl_consensus")
        reasoning_chain.extend(mldl_consensus.reasoning)
        
        # ===== MEMORY CONTRADICTIONS =====
        # Check for contradictions in memory
        if memory_context.contradictions_found:
            warnings.extend(memory_context.contradictions_found)
            
            contradictions.append({
                'type': ConflictType.TRUST_SCORE.value,
                'severity': 'low',
                'details': f"Memory contradictions: {len(memory_context.contradictions_found)}"
            })
            
            reasoning_chain.append("memory_context")
        
        # ===== LEARNING ADJUSTMENTS =====
        # Learning provides insights and adjustments
        if learning_insights.recommended_adjustments:
            warnings.extend([f"Learning: {adj}" for adj in learning_insights.recommended_adjustments[:3]])
            reasoning_chain.append("learning_insights")
        
        # ===== CALCULATE FINAL SCORES =====
        # Weighted confidence calculation
        confidence = self._calculate_weighted_confidence(
            governance_decision,
            avn_state,
            mldl_consensus,
            learning_insights,
            memory_context
        )
        
        # Trust score (governance is most trusted)
        trust_score = min(
            governance_decision.trust_score,
            avn_state.confidence,
            mldl_consensus.confidence
        )
        
        # Quality score (combination of all inputs)
        quality_score = (
            (1.0 if governance_decision.approved else 0.0) * 0.3 +
            (1.0 if avn_state.health_state == 'healthy' else 0.5 if avn_state.health_state == 'degraded' else 0.0) * 0.3 +
            mldl_consensus.confidence * 0.4
        )
        
        self.decisions_made += 1
        
        return self._build_decision(
            decision_id=decision_id,
            action=action,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            primary_reasoning=primary_reasoning,
            contradictions=contradictions,
            warnings=warnings,
            trust_score=trust_score,
            quality_score=quality_score,
            governance_weight=0.3,
            avn_weight=0.3,
            mldl_weight=0.4,
            inputs={
                'governance': governance_decision,
                'avn': avn_state,
                'mldl': mldl_consensus,
                'learning': learning_insights,
                'memory': memory_context
            }
        )
    
    def _calculate_weighted_confidence(
        self,
        governance: GovernanceInput,
        avn: AVNInput,
        mldl: MLDLQuorumInput,
        learning: LearningInput,
        memory: MemoryInput
    ) -> float:
        """Calculate weighted confidence score"""
        
        # Component scores
        gov_score = 1.0 if governance.approved else 0.0
        avn_score = 1.0 if avn.health_state == 'healthy' else 0.5 if avn.health_state == 'degraded' else 0.0
        mldl_score = mldl.confidence if mldl.consensus_reached else 0.0
        learning_score = learning.pattern_confidence
        memory_score = 1.0 - (len(memory.contradictions_found) * 0.1)  # Penalize contradictions
        
        # Weighted average
        weighted_sum = (
            gov_score * self.weights['governance'] +
            avn_score * self.weights['avn'] +
            mldl_score * self.weights['mldl'] +
            learning_score * self.weights['learning'] +
            memory_score * self.weights['memory']
        )
        
        total_weight = sum(self.weights.values())
        
        return max(0.0, min(1.0, weighted_sum / total_weight))
    
    def _build_decision(
        self,
        decision_id: str,
        action: DecisionAction,
        confidence: float,
        reasoning_chain: List[str],
        primary_reasoning: str,
        contradictions: List[Dict[str, Any]],
        warnings: List[str],
        trust_score: float = 1.0,
        quality_score: float = 1.0,
        governance_weight: float = 0.0,
        avn_weight: float = 0.0,
        mldl_weight: float = 0.0,
        learning_weight: float = 0.0,
        memory_weight: float = 0.0,
        inputs: Optional[Dict[str, Any]] = None
    ) -> UnifiedDecision:
        """Build unified decision object"""
        
        # Recommend next loops based on action
        recommended_next_loops = self._recommend_next_loops(action, contradictions)
        
        # Fallback actions
        fallback_actions = self._determine_fallbacks(action)
        
        # Supporting evidence from inputs
        supporting_evidence = []
        if inputs:
            if inputs.get('governance') and inputs['governance'].approved:
                supporting_evidence.append(f"Governance approved: {inputs['governance'].reasoning}")
            if inputs.get('mldl') and inputs['mldl'].consensus_reached:
                supporting_evidence.append(f"MLDL consensus: {inputs['mldl'].consensus_action}")
            if inputs.get('learning') and inputs['learning'].insights:
                supporting_evidence.extend(inputs['learning'].insights[:2])
        
        return UnifiedDecision(
            decision_id=decision_id,
            action=action,
            confidence=confidence,
            reasoning_chain_ids=reasoning_chain,
            primary_reasoning=primary_reasoning,
            supporting_evidence=supporting_evidence,
            trust_score=trust_score,
            quality_score=quality_score,
            contradictions=contradictions,
            warnings=warnings,
            recommended_next_loops=recommended_next_loops,
            fallback_actions=fallback_actions,
            governance_weight=governance_weight,
            avn_weight=avn_weight,
            mldl_weight=mldl_weight,
            learning_weight=learning_weight,
            memory_weight=memory_weight,
            synthesized_from=inputs or {}
        )
    
    def _recommend_next_loops(
        self,
        action: DecisionAction,
        contradictions: List[Dict[str, Any]]
    ) -> List[str]:
        """Recommend next processing loops based on action and state"""
        
        loops = []
        
        if action == DecisionAction.EXECUTE:
            loops.extend(['execution_monitor', 'feedback_collection'])
        
        elif action == DecisionAction.PAUSE:
            loops.extend(['health_assessment', 'anomaly_investigation'])
        
        elif action == DecisionAction.REJECT:
            loops.extend(['governance_review', 'policy_clarification'])
        
        elif action == DecisionAction.ESCALATE:
            loops.extend(['human_review', 'consensus_building'])
        
        elif action == DecisionAction.RETRY:
            loops.extend(['state_refresh', 're_evaluation'])
        
        elif action == DecisionAction.ROLLBACK:
            loops.extend(['rollback_execution', 'state_verification'])
        
        # Add contradiction-specific loops
        for contradiction in contradictions:
            if contradiction['type'] == ConflictType.HEALTH_STATE.value:
                loops.append('health_deep_dive')
            elif contradiction['type'] == ConflictType.GOVERNANCE_POLICY.value:
                loops.append('policy_alignment')
        
        return list(set(loops))  # Deduplicate
    
    def _determine_fallbacks(self, action: DecisionAction) -> List[str]:
        """Determine fallback actions if primary action fails"""
        
        fallbacks = {
            DecisionAction.EXECUTE: ['pause', 'retry', 'rollback'],
            DecisionAction.PAUSE: ['retry', 'escalate'],
            DecisionAction.REJECT: ['escalate'],
            DecisionAction.ESCALATE: ['reject'],
            DecisionAction.RETRY: ['pause', 'escalate'],
            DecisionAction.ROLLBACK: ['pause', 'escalate']
        }
        
        return fallbacks.get(action, ['escalate'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            'decisions_made': self.decisions_made,
            'decisions_rejected': self.decisions_rejected,
            'decisions_escalated': self.decisions_escalated,
            'weights': self.weights
        }


# Global instance
unified_decision_engine = UnifiedDecisionEngine()
