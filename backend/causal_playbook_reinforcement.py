"""
Causal reinforcement learning for playbook selection.

The CausalPlaybookReinforcementAgent observes incidents, playbook choices,
and resulting KPIs to improve Grace's recovery strategies over time.

This scaffold outlines the control surface; concrete reward shaping and
policy updates will be implemented once live incident outcomes are recorded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from .immutable_log import immutable_log
from .grace_training_storage import training_storage

logger = logging.getLogger(__name__)


@dataclass
class PlaybookExperience:
    """One step of experience collected from an incident response."""

    incident_id: str
    service: str
    diagnosis_code: str
    candidate_playbooks: List[str]
    chosen_playbook: str
    reward: float
    kpi_deltas: Dict[str, float]
    trust_score_delta: float
    metadata: Optional[Dict[str, str]] = None


class CausalPlaybookReinforcementAgent:
    """
    Cross-playbook policy optimizer with causal attribution.

    Core responsibilities:
    - Maintain a policy over candidate playbooks conditioned on incident context.
    - Estimate causal impact of a playbook on key KPIs (latency, rollback rate, trust).
    - Recommend playbooks in ranked order for the agentic spine.
    """

    def __init__(self) -> None:
        self._policy_state: Dict[Tuple[str, str], Dict[str, float]] = {}
        self._experience_buffer: List[PlaybookExperience] = []
        logger.info("[CAUSAL-RL] Causal Playbook Reinforcement Agent initialized")

    async def record_experience(self, experience: PlaybookExperience) -> None:
        """
        Append a new experience tuple resulting from an executed playbook.
        """

        self._experience_buffer.append(experience)

        key = (experience.service, experience.diagnosis_code)
        policy = self._policy_state.setdefault(key, {})

        # Placeholder policy update: simple exponential moving average.
        weight = 0.7
        reward = experience.reward
        old_score = policy.get(experience.chosen_playbook, 0.0)
        new_score = old_score * weight + reward * (1 - weight)
        policy[experience.chosen_playbook] = new_score
        
        logger.info(
            f"[CAUSAL-RL] Updated policy for {experience.service}/{experience.diagnosis_code}: "
            f"{experience.chosen_playbook} reward={reward:.2f} score={new_score:.2f}"
        )
        print(
            f"[CAUSAL-RL]  Learned: {experience.chosen_playbook}  reward={reward:.2f} "
            f"(trust_delta={experience.trust_score_delta:+.2f})"
        )
        
        # Log to immutable log
        await immutable_log.append(
            actor="causal_rl_agent",
            action="experience_recorded",
            resource=experience.incident_id,
            subsystem="causal_reinforcement",
            payload={
                "service": experience.service,
                "diagnosis": experience.diagnosis_code,
                "playbook": experience.chosen_playbook,
                "reward": reward,
                "kpi_deltas": experience.kpi_deltas,
                "trust_delta": experience.trust_score_delta
            },
            result="success"
        )
        
        # Save to training storage
        await training_storage.save_knowledge(
            category="errors_fixed",
            item_id=experience.incident_id,
            content={
                "service": experience.service,
                "diagnosis": experience.diagnosis_code,
                "playbook_chosen": experience.chosen_playbook,
                "candidates": experience.candidate_playbooks,
                "reward": reward,
                "kpi_deltas": experience.kpi_deltas,
                "trust_score_delta": experience.trust_score_delta,
                "policy_score": new_score,
                "metadata": experience.metadata or {}
            },
            source=f"incident_{experience.incident_id}",
            tags=["causal_rl", "playbook_learning", experience.diagnosis_code]
        )

    async def recommend(
        self,
        service: str,
        diagnosis_code: str,
        candidates: List[str],
    ) -> List[str]:
        """
        Return a list of playbook codes ranked by expected reward.
        """

        key = (service, diagnosis_code)
        policy = self._policy_state.get(key, {})

        # Rank candidates by learned policy scores
        ranked = sorted(
            [c for c in candidates if c in policy],
            key=lambda c: policy[c],
            reverse=True,
        )

        # If policy lacks data for some candidates, append them at the end in original order.
        unseen = [c for c in candidates if c not in policy]
        
        result = ranked + unseen
        
        logger.info(
            f"[CAUSAL-RL] Recommended playbooks for {service}/{diagnosis_code}: "
            f"{result[:3]} (top 3 of {len(result)})"
        )
        
        return result

    async def summarise_policy(self) -> Dict[str, Dict[str, float]]:
        """
        Export the current policy state for inspection or persistence.
        """

        return {
            f"{service}:{diagnosis}": policy
            for (service, diagnosis), policy in self._policy_state.items()
        }
    
    def get_statistics(self) -> Dict:
        """Get statistics about learned policies"""
        return {
            "total_policies": len(self._policy_state),
            "total_experiences": len(self._experience_buffer),
            "policies": {
                f"{s}:{d}": {
                    "playbooks_learned": len(p),
                    "best_playbook": max(p.items(), key=lambda x: x[1])[0] if p else None,
                    "best_score": max(p.values()) if p else 0.0
                }
                for (s, d), p in self._policy_state.items()
            }
        }


# Global singleton
causal_rl_agent = CausalPlaybookReinforcementAgent()


__all__ = [
    "CausalPlaybookReinforcementAgent",
    "PlaybookExperience",
    "causal_rl_agent",
]
