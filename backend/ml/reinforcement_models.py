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
        policy[experience.chosen_playbook] = (
            policy.get(experience.chosen_playbook, 0.0) * weight
            + reward * (1 - weight)
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

        ranked = sorted(
            candidates,
            key=lambda c: policy.get(c, 0.0),
            reverse=True,
        )

        # If policy lacks data for some candidates, append them at the end in original order.
        unseen = [c for c in candidates if c not in ranked]
        return ranked + unseen

    async def summarise_policy(self) -> Dict[str, Dict[str, float]]:
        """
        Export the current policy state for inspection or persistence.
        """

        return {
            f"{service}:{diagnosis}": policy
            for (service, diagnosis), policy in self._policy_state.items()
        }


__all__ = [
    "CausalPlaybookReinforcementAgent",
    "PlaybookExperience",
]
