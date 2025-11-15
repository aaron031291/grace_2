"""
Mission Manifest - Declarative Goal Definition for Grace

A Mission is the Manifest. This module defines the structure for a
declarative mission document. It specifies the high-level objective,
success criteria, constraints, and governance policies, allowing Grace to
reason about and plan the mission dynamically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class SuccessCriterion:
    """A single, verifiable condition for mission success."""
    description: str
    # The check can be an API endpoint, a data query, or a kernel state verification
    check_type: str  # e.g., "api_endpoint", "database_query", "kernel_state"
    check_parameters: Dict[str, Any]
    expected_result: Any

@dataclass
class Constraint:
    """A rule or limitation the mission must operate within."""
    description: str
    constraint_type: str  # e.g., "max_budget", "time_limit", "resource_limit"
    value: Any

@dataclass
class MissionManifest:
    """
    A declarative manifest defining a high-level mission for Grace.
    This is the input to the dynamic mission planner.
    """
    manifest_id: str
    mission_name: str
    description: str
    objective: str  # The high-level goal, e.g., "Reduce API p95 latency by 10%".
    success_criteria: List[SuccessCriterion]
    constraints: List[Constraint] = field(default_factory=list)
    initial_context: Dict[str, Any] = field(default_factory=dict)
    governance_policy: Dict[str, Any] = field(default_factory=dict) # e.g., max_risk_level, required_approvals
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the manifest to a dictionary."""
        return {
            "manifest_id": self.manifest_id,
            "mission_name": self.mission_name,
            "description": self.description,
            "objective": self.objective,
            "success_criteria": [vars(sc) for sc in self.success_criteria],
            "constraints": [vars(c) for c in self.constraints],
            "initial_context": self.initial_context,
            "governance_policy": self.governance_policy,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }

__all__ = ["MissionManifest", "SuccessCriterion", "Constraint"]