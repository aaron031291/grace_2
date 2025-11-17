"""Trust and Decay Scoring Engine for Memory Artifacts

Computes trust scores from multiple signals and applies configurable decay curves.
"""

import math
from dataclasses import dataclass
from enum import Enum

from .GraceLoopOutput import GraceLoopOutput


class DecayCurve(Enum):
    """Decay curve types"""
    HYPERBOLIC = "hyperbolic"  # Slower decay for reasoning
    EXPONENTIAL = "exponential"  # Faster decay for telemetry
    LINEAR = "linear"  # Linear decay for observations


@dataclass
class TrustSignals:
    """Individual trust signal components"""
    provenance: float = 0.5  # Component reputation + model certainty
    consensus: float = 0.5  # Agreement with specialists
    governance: float = 1.0  # Constitutional compliance
    usage: float = 0.0  # Read frequency + successful outcomes


@dataclass
class TrustInit:
    """Initial trust score on write"""
    total_score: float
    signals: TrustSignals
    reason: str


@dataclass
class ReadBoost:
    """Trust boost from successful read"""
    delta: float
    reason: str
    new_score: float


@dataclass
class DecayResult:
    """Result of decay application"""
    original_score: float
    decayed_score: float
    decay_factor: float
    hours_elapsed: float


class MemoryScoreModel:
    """
    Trust and Decay Scoring Engine
    
    Computes trust from:
    - Provenance (component reputation, model certainty)
    - Consensus (agreement with specialists)
    - Governance (constitutional compliance)
    - Usage (read frequency, successful outcomes)
    
    Applies decay curves:
    - Hyperbolic: slower decay for reasoning
    - Exponential: faster decay for telemetry
    - Linear: linear decay for observations
    """
    
    # Component reputation weights
    COMPONENT_REPUTATION = {
        "reflection": 0.85,
        "hunter": 0.90,
        "meta": 0.80,
        "causal": 0.85,
        "temporal": 0.75,
        "specialist": 0.88,
        "quorum": 0.92,
        "governance": 0.95,
        "parliament": 0.93,
        "default": 0.70
    }
    
    # Trust signal weights
    WEIGHTS = {
        "provenance": 0.30,
        "consensus": 0.25,
        "governance": 0.30,
        "usage": 0.15
    }
    
    def __init__(self):
        pass
    
    def score_on_write(self, output: GraceLoopOutput) -> TrustInit:
        """
        Compute initial trust score when memory is written
        
        Args:
            output: GraceLoopOutput to score
            
        Returns:
            TrustInit with initial score and signals
        """
        signals = TrustSignals()
        
        # 1. Provenance: component reputation + confidence
        component_rep = self.COMPONENT_REPUTATION.get(
            output.component.lower(),
            self.COMPONENT_REPUTATION["default"]
        )
        signals.provenance = (component_rep * 0.6 + output.confidence * 0.4)
        
        # 2. Consensus: quality score if available
        if output.quality_score is not None:
            signals.consensus = output.quality_score
        else:
            # Default to confidence if no quality score
            signals.consensus = output.confidence
        
        # 3. Governance: constitutional compliance
        signals.governance = 1.0 if output.constitutional_compliance else 0.3
        if output.requires_approval:
            signals.governance *= 0.8
        
        # Penalize if there are errors
        if output.errors:
            signals.governance *= 0.7
        
        # Penalize if there are violations in policy tags
        for tag in output.policy_tags:
            if tag.status == "violation":
                signals.governance *= 0.5
            elif tag.status == "requires_review":
                signals.governance *= 0.8
        
        # 4. Usage: starts at 0, grows with use
        signals.usage = 0.0
        
        # Compute weighted total
        total_score = (
            signals.provenance * self.WEIGHTS["provenance"] +
            signals.consensus * self.WEIGHTS["consensus"] +
            signals.governance * self.WEIGHTS["governance"] +
            signals.usage * self.WEIGHTS["usage"]
        )
        
        # Clamp to [0, 1]
        total_score = max(0.0, min(1.0, total_score))
        
        reason = f"Initial trust: prov={signals.provenance:.2f}, cons={signals.consensus:.2f}, gov={signals.governance:.2f}"
        
        return TrustInit(
            total_score=total_score,
            signals=signals,
            reason=reason
        )
    
    def score_on_read(
        self,
        current_trust: float,
        access_count: int,
        success_count: int,
        failure_count: int,
        outcome: str = "success"  # success, failure, neutral
    ) -> ReadBoost:
        """
        Update trust score based on read outcome
        
        Args:
            current_trust: Current trust score
            access_count: Total access count
            success_count: Successful use count
            failure_count: Failed use count
            outcome: Outcome of this read
            
        Returns:
            ReadBoost with delta and new score
        """
        delta = 0.0
        reason_parts = []
        
        # Boost for successful use
        if outcome == "success":
            # Diminishing returns: first success is worth more
            boost = 0.05 / (1 + success_count * 0.1)
            delta += boost
            reason_parts.append(f"success_boost={boost:.3f}")
        
        # Penalty for failure
        elif outcome == "failure":
            # Failures hurt more early on
            penalty = -0.08 / (1 + failure_count * 0.05)
            delta += penalty
            reason_parts.append(f"failure_penalty={penalty:.3f}")
        
        # Bonus for consistent success rate
        if access_count > 5:
            success_rate = success_count / access_count
            if success_rate > 0.8:
                consistency_bonus = 0.02
                delta += consistency_bonus
                reason_parts.append(f"consistency_bonus={consistency_bonus:.3f}")
        
        # Apply delta
        new_score = current_trust + delta
        new_score = max(0.0, min(1.0, new_score))
        
        reason = ", ".join(reason_parts) if reason_parts else "neutral_read"
        
        return ReadBoost(
            delta=delta,
            reason=reason,
            new_score=new_score
        )
    
    def apply_decay(
        self,
        trust_score: float,
        curve: DecayCurve,
        half_life_hours: float,
        hours_elapsed: float
    ) -> DecayResult:
        """
        Apply decay curve to trust score
        
        Args:
            trust_score: Current trust score
            curve: Type of decay curve
            half_life_hours: Half-life in hours
            hours_elapsed: Time elapsed since last access
            
        Returns:
            DecayResult with decayed score
        """
        if hours_elapsed <= 0:
            return DecayResult(
                original_score=trust_score,
                decayed_score=trust_score,
                decay_factor=1.0,
                hours_elapsed=0.0
            )
        
        decay_factor = 1.0
        
        if curve == DecayCurve.HYPERBOLIC:
            # Hyperbolic decay: 1 / (1 + kt)
            # Slower decay, good for reasoning
            k = 1.0 / half_life_hours
            decay_factor = 1.0 / (1.0 + k * hours_elapsed)
        
        elif curve == DecayCurve.EXPONENTIAL:
            # Exponential decay: e^(-λt)
            # Faster decay, good for telemetry
            lambda_val = math.log(2) / half_life_hours
            decay_factor = math.exp(-lambda_val * hours_elapsed)
        
        elif curve == DecayCurve.LINEAR:
            # Linear decay: 1 - (t / T)
            # Uniform decay, good for observations
            total_lifetime = half_life_hours * 2  # Linear to zero at 2x half-life
            decay_factor = max(0.0, 1.0 - (hours_elapsed / total_lifetime))
        
        decayed_score = trust_score * decay_factor
        
        return DecayResult(
            original_score=trust_score,
            decayed_score=decayed_score,
            decay_factor=decay_factor,
            hours_elapsed=hours_elapsed
        )
    
    def compute_memory_rank(
        self,
        trust_score: float,
        relevance_score: float,
        recency_score: float,
        importance: float = 0.5
    ) -> float:
        """
        Compute final memory ranking score
        
        Args:
            trust_score: Trust score (after decay)
            relevance_score: Semantic relevance to query
            recency_score: Recency score (0-1)
            importance: Importance hint from output
            
        Returns:
            Final ranking score
        """
        # Weighted combination
        rank = (
            trust_score * 0.40 +
            relevance_score * 0.35 +
            recency_score * 0.15 +
            importance * 0.10
        )
        
        return max(0.0, min(1.0, rank))
    
    def recommend_decay_curve(self, output_type: str) -> tuple[DecayCurve, float]:
        """
        Recommend decay curve and half-life based on output type
        
        Args:
            output_type: Type of output (reasoning, observation, etc.)
            
        Returns:
            Tuple of (DecayCurve, half_life_hours)
        """
        recommendations = {
            "reasoning": (DecayCurve.HYPERBOLIC, 168.0),  # 1 week, slow decay
            "decision": (DecayCurve.HYPERBOLIC, 120.0),  # 5 days
            "reflection": (DecayCurve.HYPERBOLIC, 240.0),  # 10 days
            "observation": (DecayCurve.LINEAR, 48.0),  # 2 days
            "action": (DecayCurve.EXPONENTIAL, 72.0),  # 3 days
            "prediction": (DecayCurve.EXPONENTIAL, 96.0),  # 4 days
            "generation": (DecayCurve.LINEAR, 24.0),  # 1 day
        }
        
        return recommendations.get(
            output_type.lower(),
            (DecayCurve.HYPERBOLIC, 168.0)  # Default
        )
    
    def update_usage_signal(
        self,
        current_usage_score: float,
        access_count: int,
        success_count: int,
        failure_count: int
    ) -> float:
        """
        Compute usage signal from access patterns
        
        Args:
            current_usage_score: Current usage signal
            access_count: Total accesses
            success_count: Successful uses
            failure_count: Failed uses
            
        Returns:
            New usage signal score
        """
        if access_count == 0:
            return 0.0
        
        # Success rate
        success_rate = success_count / access_count
        
        # Access frequency component (diminishing returns)
        frequency_score = min(1.0, access_count / 20.0)
        
        # Combine: success rate is more important
        usage_score = success_rate * 0.7 + frequency_score * 0.3
        
        return max(0.0, min(1.0, usage_score))
