"""
Minimal planner scaffolding for Grace's agentic capabilities.
- Provides Plan/PlanStep dataclasses
- Planner.build()/replan() stubs with simple deterministic heuristic ordering

This module is read-only (computes plans) and does not execute steps.
Wire from orchestrator after verification.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterable, Tuple


@dataclass
class PlanStep:
    id: str
    description: str
    goal_id: Optional[int] = None
    requires: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_duration_s: float = 0.0
    risk: float = 0.0
    policy_flags: List[str] = field(default_factory=list)


@dataclass
class Plan:
    steps: List[PlanStep]
    ordering: List[str]
    objective: str
    expected_value: float
    risk: float
    confidence: float

    def step_map(self) -> Dict[str, PlanStep]:
        return {s.id: s for s in self.steps}


class Planner:
    """
    Minimal planner with deterministic ordering:
    - Topological sort by dependencies (requires)
    - Within the same level, sort by (priority desc -> value_score desc -> risk asc -> id)

    Inputs to build(): context dict (no schema requirement). If provided, it may include:
        goals: List[dict] with keys id, priority, value_score, risk_score, status
        deps: Iterable[Tuple[int, int]] of (depends_on_id, goal_id)
        extra_steps: Optional[List[PlanStep]] for ad-hoc actions
        objective: Optional[str]
    """

    PRIORITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}

    async def build(self, context: Dict) -> Plan:
        goals: List[dict] = context.get("goals", [])
        deps_pairs: Iterable[Tuple[int, int]] = context.get("deps", [])
        extra_steps: List[PlanStep] = context.get("extra_steps", [])
        objective: str = context.get("objective", "Execute prioritized goals safely")

        # Create one step per goal (placeholder). Orchestrator can expand later.
        steps: List[PlanStep] = [
            PlanStep(
                id=f"goal:{g['id']}",
                description=g.get("goal_text", f"Goal {g['id']}")[:140],
                goal_id=g["id"],
                requires=[f"goal:{a}" for a in _prereqs_for(g["id"], deps_pairs)],
                estimated_cost=0.0,
                estimated_duration_s=0.0,
                risk=float(g.get("risk_score") or 0.0),
                policy_flags=[],
            )
            for g in goals
        ] + list(extra_steps)

        # Compute topological sort with tie-breaks by priority/value/risk
        priority_map = {g["id"]: self.PRIORITY_ORDER.get(str(g.get("priority", "medium")).lower(), 2) for g in goals}
        value_map = {g["id"]: float(g.get("value_score") or 0.0) for g in goals}
        risk_map = {g["id"]: float(g.get("risk_score") or 0.0) for g in goals}

        ordering = _toposort_with_tiebreaks(
            steps,
            key=lambda s: (
                -priority_map.get(s.goal_id, 2),
                -value_map.get(s.goal_id, 0.0),
                risk_map.get(s.goal_id, 0.0),
                s.id,
            ),
        )

        expected_value = sum(value_map.values())
        total_risk = sum(risk_map.values())
        confidence = max(0.3, 1.0 - min(1.0, total_risk / (len(risk_map) or 1)))

        return Plan(
            steps=steps,
            ordering=ordering,
            objective=objective,
            expected_value=expected_value,
            risk=total_risk,
            confidence=confidence,
        )

    async def replan(self, context: Dict, previous: Plan) -> Plan:
        # For now, just rebuild; later diff against previous and keep stable prefixes
        return await self.build(context)


def _prereqs_for(goal_id: int, deps_pairs: Iterable[Tuple[int, int]]) -> List[int]:
    return [a for (a, b) in deps_pairs if b == goal_id]


def _toposort_with_tiebreaks(steps: List[PlanStep], key) -> List[str]:
    # Kahn's algorithm with custom tie-break ordering of ready nodes
    incoming_count: Dict[str, int] = {s.id: 0 for s in steps}
    outgoing: Dict[str, List[str]] = {s.id: [] for s in steps}
    by_id: Dict[str, PlanStep] = {s.id: s for s in steps}

    for s in steps:
        for r in s.requires:
            incoming_count[s.id] = incoming_count.get(s.id, 0) + 1
            outgoing.setdefault(r, []).append(s.id)

    ready = [sid for sid, cnt in incoming_count.items() if cnt == 0]
    # Sort ready nodes by tie-break key computed from PlanStep
    ready.sort(key=lambda sid: key(by_id[sid]))

    result: List[str] = []
    while ready:
        current = ready.pop(0)
        result.append(current)
        for nb in outgoing.get(current, []):
            incoming_count[nb] -= 1
            if incoming_count[nb] == 0:
                ready.append(nb)
        ready.sort(key=lambda sid: key(by_id[sid]))

    # If cycle, append remaining in deterministic order to avoid crash
    if len(result) < len(steps):
        remaining = [sid for sid in by_id.keys() if sid not in result]
        remaining.sort()
        result += remaining

    return result
