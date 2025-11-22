"""
Dynamic Mission Planner for High-End Agentic Behavior

This module provides the data structures for representing missions not as
static playbooks, but as dynamic, goal-oriented plans that Grace can
decompose, adapt, and reason about in real-time.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from backend.core.intent_api import Intent

class MissionStatus(str, Enum):
    """Status of a mission or goal."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ADAPTING = "adapting" # When in-mission replanning occurs

@dataclass
class MissionGoal:
    """A high-level or intermediate goal within a mission."""
    goal_id: str
    description: str
    status: MissionStatus = MissionStatus.PENDING
    parent_goal_id: Optional[str] = None
    sub_steps: List[Union[MissionGoal, Intent]] = field(default_factory=list)
    outcome: Optional[str] = None
    rationale: Optional[str] = None # Why this goal was formulated

@dataclass
class DynamicMissionPlan:
    """A full, hierarchical mission plan composed of nested goals and intents."""
    mission_id: str
    root_goal: MissionGoal
    status: MissionStatus = MissionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def find_step(self, step_id: str) -> Optional[Union[MissionGoal, Intent]]:
        """Find a goal or intent within the plan by its ID."""
        queue = [self.root_goal]
        while queue:
            current_step = queue.pop(0)
            if isinstance(current_step, MissionGoal):
                if current_step.goal_id == step_id:
                    return current_step
                queue.extend(current_step.sub_steps)
            elif isinstance(current_step, Intent):
                if current_step.intent_id == step_id:
                    return current_step
        return None

def create_mission_plan(description: str, context: Optional[Dict] = None) -> DynamicMissionPlan:
    """Create a new dynamic mission plan from a high-level description."""
    mission_id = f"mission_{uuid.uuid4().hex}"
    root_goal = MissionGoal(
        goal_id=f"goal_{uuid.uuid4().hex}",
        description=description,
    )
    return DynamicMissionPlan(
        mission_id=mission_id,
        root_goal=root_goal,
        context=context or {}
    )

__all__ = [
    "MissionStatus",
    "MissionGoal",
    "DynamicMissionPlan",
    "create_mission_plan",
]
