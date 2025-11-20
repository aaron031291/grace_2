"""
Domain Policy Engine - Governance for specific domains
Implements domain-specific policies with conditions for actions, time windows, risk levels, etc.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)

@dataclass
class DomainPolicy:
    """
    Domain policy with conditions for governance checks
    """
    policy_id: str
    domain: str
    allowed_actions: List[str]
    disallowed_actions: List[str]
    time_windows: List[Dict[str, Any]]  # [{"start": "09:00", "end": "17:00", "days": ["mon", "tue", ...]}]
    risk_levels: List[str]  # ["low", "medium", "high", "critical"]
    max_frequency_per_hour: Optional[int] = None
    requires_approval: bool = False
    approval_threshold: str = "medium"  # low, medium, high, critical
    trust_required: float = 0.5  # Minimum trust score required
    active: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class DomainPolicyEngine:
    """
    Engine for checking domain-specific policies
    """

    def __init__(self):
        self.policies: Dict[str, DomainPolicy] = {}
        self.action_frequency: Dict[str, List[datetime]] = {}  # Track action frequencies

    def add_policy(self, policy: DomainPolicy):
        """Add a domain policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Added domain policy: {policy.policy_id} for domain {policy.domain}")

    def get_policies_for_domain(self, domain: str) -> List[DomainPolicy]:
        """Get all active policies for a domain"""
        return [p for p in self.policies.values() if p.domain == domain and p.active]

    def check_domain_policy(
        self,
        action: str,
        domain: str,
        risk_level: str = "medium",
        trust_score: float = 1.0,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if an action is allowed by domain policies

        Args:
            action: The action to check
            domain: The domain the action belongs to
            risk_level: Risk level of the action
            trust_score: Current trust score
            context: Additional context

        Returns:
            Dict with 'allowed', 'reason', 'requires_approval', etc.
        """

        if context is None:
            context = {}

        # Get applicable policies
        policies = self.get_policies_for_domain(domain)

        if not policies:
            # No policies defined, allow by default
            return {
                'allowed': True,
                'reason': f'No policies defined for domain {domain}',
                'requires_approval': False,
                'policy_id': None
            }

        # Check each policy
        for policy in policies:
            result = self._check_single_policy(action, risk_level, trust_score, context, policy)
            if not result['allowed']:
                return result

        # All policies passed
        return {
            'allowed': True,
            'reason': f'Action {action} allowed by all domain policies',
            'requires_approval': any(p.requires_approval for p in policies),
            'policy_id': policies[0].policy_id if policies else None
        }

    def _check_single_policy(
        self,
        action: str,
        risk_level: str,
        trust_score: float,
        context: Dict[str, Any],
        policy: DomainPolicy
    ) -> Dict[str, Any]:
        """Check a single policy"""

        # Check if action is explicitly disallowed
        if action in policy.disallowed_actions:
            return {
                'allowed': False,
                'reason': f'Action {action} is explicitly disallowed by policy {policy.policy_id}',
                'requires_approval': False,
                'policy_id': policy.policy_id
            }

        # Check if action is allowed (if allowed_actions is specified)
        if policy.allowed_actions and action not in policy.allowed_actions:
            return {
                'allowed': False,
                'reason': f'Action {action} is not in allowed actions for policy {policy.policy_id}',
                'requires_approval': False,
                'policy_id': policy.policy_id
            }

        # Check risk level
        if risk_level not in policy.risk_levels:
            return {
                'allowed': False,
                'reason': f'Risk level {risk_level} not allowed by policy {policy.policy_id}',
                'requires_approval': False,
                'policy_id': policy.policy_id
            }

        # Check trust score
        if trust_score < policy.trust_required:
            return {
                'allowed': False,
                'reason': f'Trust score {trust_score:.2f} below required {policy.trust_required} for policy {policy.policy_id}',
                'requires_approval': False,
                'policy_id': policy.policy_id
            }

        # Check time windows
        if not self._check_time_windows(policy.time_windows):
            return {
                'allowed': False,
                'reason': f'Action not allowed outside time windows for policy {policy.policy_id}',
                'requires_approval': False,
                'policy_id': policy.policy_id
            }

        # Check frequency limits
        if policy.max_frequency_per_hour:
            if not self._check_frequency_limit(action, policy.max_frequency_per_hour):
                return {
                    'allowed': False,
                    'reason': f'Action frequency limit exceeded for policy {policy.policy_id}',
                    'requires_approval': False,
                    'policy_id': policy.policy_id
                }

        # All checks passed
        return {
            'allowed': True,
            'reason': f'Action {action} passed policy {policy.policy_id}',
            'requires_approval': policy.requires_approval,
            'policy_id': policy.policy_id
        }

    def _check_time_windows(self, time_windows: List[Dict[str, Any]]) -> bool:
        """Check if current time is within allowed windows"""

        if not time_windows:
            return True  # No restrictions

        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%a').lower()

        for window in time_windows:
            days = [d.lower() for d in window.get('days', [])]
            if days and current_day not in days:
                continue

            start_str = window.get('start', '00:00')
            end_str = window.get('end', '23:59')

            try:
                start_time = datetime.strptime(start_str, '%H:%M').time()
                end_time = datetime.strptime(end_str, '%H:%M').time()

                if start_time <= current_time <= end_time:
                    return True
            except ValueError:
                logger.warning(f"Invalid time format in policy: {start_str} - {end_str}")
                continue

        return False

    def _check_frequency_limit(self, action: str, max_per_hour: int) -> bool:
        """Check if action frequency is within limits"""

        if action not in self.action_frequency:
            self.action_frequency[action] = []

        # Clean old entries (older than 1 hour)
        cutoff = datetime.now().replace(hour=datetime.now().hour - 1)
        self.action_frequency[action] = [
            ts for ts in self.action_frequency[action] if ts > cutoff
        ]

        # Check current count
        if len(self.action_frequency[action]) >= max_per_hour:
            return False

        # Record this action
        self.action_frequency[action].append(datetime.now())
        return True

# Global instance
domain_policy_engine = DomainPolicyEngine()

# Convenience function as requested
def _check_domain_policy(action: str, policy: DomainPolicy) -> bool:
    """
    Check if an action is allowed by a specific domain policy

    Args:
        action: The action to check
        policy: The domain policy to check against

    Returns:
        True if allowed, False if blocked
    """
    result = domain_policy_engine._check_single_policy(
        action=action,
        risk_level="medium",  # Default
        trust_score=1.0,     # Default
        context={},
        policy=policy
    )
    return result['allowed']