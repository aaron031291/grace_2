"""Coding orchestrator that coordinates multi-agent development workflows.

The orchestrator decomposes user requests, spawns specialised subagents, and
merges their outputs while honouring Grace's governance and security layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..code_understanding import code_understanding
from ..dev_workflow import dev_workflow
from ..governance import governance_engine
from ..hunter import hunter
from ..trigger_mesh import trigger_mesh, TriggerEvent
from ..meta_loop import meta_loop_engine
from ..task_executor import task_executor

from .subagents import (
    AnalysisAgent,
    ImplementationAgent,
    ReviewAgent,
    SubAgentResult,
)
from .tools import Toolbelt


@dataclass
class OrchestrationContext:
    """Normalized context passed to every subagent."""

    description: str
    user: str
    intent: Optional[Dict[str, Any]] = None
    code_context: Optional[Dict[str, Any]] = None
    working_dir: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationPlan:
    """Structured plan produced before execution."""

    steps: List[Dict[str, Any]]
    intent: Dict[str, Any]
    code_context: Dict[str, Any]
    rationale: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class CodingOrchestrator:
    """High-level coordinator for Grace's agentic coding workflows."""

    def __init__(self):
        self.toolbelt = Toolbelt()
        self._subagent_registry = {
            "analysis": AnalysisAgent,
            "implementation": ImplementationAgent,
            "review": ReviewAgent,
        }

    async def plan(self, *, description: str, user: str, context: Optional[Dict[str, Any]] = None) -> OrchestrationPlan:
        """Create a multi-step plan for a natural language request."""

        context = context or {}

        # Step 1: understand high-level intent
        intent = await code_understanding.understand_intent(description, context)

        # Step 2: pull deep code context for the primary file if provided
        code_ctx: Dict[str, Any] = {}
        target_file = context.get("file_path")
        if target_file:
            code_ctx = await code_understanding.analyze_current_context(
                file_path=target_file,
                cursor_position=context.get("cursor_position"),
                file_content=context.get("file_content"),
                session_id=context.get("session_id", "default"),
            )

        # Step 3: derive plan steps using dev workflow heuristics
        task_outline = await dev_workflow.parse_task(description, context)
        plan_steps = await dev_workflow.plan_implementation(task_outline)

        rationale = (
            "Plan derived from intent classification, current code context, and "
            "dev workflow heuristics. Each step will be executed by a dedicated subagent."
        )

        return OrchestrationPlan(
            steps=plan_steps,
            intent=intent,
            code_context=code_ctx,
            rationale=rationale,
        )

    async def execute(self, plan: OrchestrationPlan, *, description: str, user: str) -> Dict[str, Any]:
        """Execute a plan by instantiating specialised subagents."""

        orchestration_ctx = OrchestrationContext(
            description=description,
            user=user,
            intent=plan.intent,
            code_context=plan.code_context,
        )

        await self._publish_event(
            event_type="coding.plan.started",
            actor=user,
            resource=plan.intent.get("entities", []) if plan.intent else [],
            payload={"steps": plan.steps},
        )

        results: List[SubAgentResult] = []

        for step in plan.steps:
            subagent_type = step.get("agent", "implementation")
            agent_cls = self._subagent_registry.get(subagent_type)
            if not agent_cls:
                continue

            agent = agent_cls(
                toolbelt=self.toolbelt,
                intent=plan.intent,
                code_context=plan.code_context,
                step=step,
            )

            result = await agent.run(orchestration_ctx)
            results.append(result)

            await self._publish_event(
                event_type="coding.subagent.completed",
                actor=user,
                resource=step.get("description", ""),
                payload=result.to_payload(),
            )

        merged = await self._merge_results(results, user=user)

        await self._publish_event(
            event_type="coding.plan.completed",
            actor=user,
            resource=[r.step_id for r in results],
            payload={"summary": merged.get("summary"), "diffs": merged.get("diffs")},
        )

        # Meta-loop learns from outcome
        await meta_loop_engine.analyze_and_optimize()

        return merged

    async def quick_execute(self, *, description: str, user: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Shortcut helper that plans and executes in a single call."""

        plan = await self.plan(description=description, user=user, context=context)
        return await self.execute(plan, description=description, user=user)

    async def _merge_results(self, results: List[SubAgentResult], *, user: str) -> Dict[str, Any]:
        """Merge diffs, run governance & security checks, and schedule validations."""

        if not results:
            return {"summary": "No subagent results", "diffs": []}

        diffs: List[Dict[str, Any]] = []
        for result in results:
            if not result.diff:
                continue

            approval = await governance_engine.check(
                actor=user,
                action="code_write",
                resource=result.diff.get("file_path", ""),
                payload={"summary": result.summary},
            )

            if approval.get("decision") == "block":
                result.status = "blocked"
                result.notes.append(f"Governance blocked change: {approval.get('policy')}")
                continue

            alerts = await hunter.inspect(
                actor=user,
                action="code_change",
                resource=result.diff.get("file_path", ""),
                payload={"diff_preview": result.diff.get("patch")},
            )

            if alerts:
                result.status = "requires_review"
                result.notes.append("Security alerts raised; manual review required")

            diffs.append(result.diff)

        if diffs:
            await task_executor.submit_task(
                user=user,
                task_type="verification",
                description="Run unit tests for orchestrator changes",
                task_func=self.toolbelt.run_validation_suite,
            )

        summary = {
            "summary": "Processed diffs with governance and security checks",
            "diffs": diffs,
            "results": [r.to_payload() for r in results],
        }

        return summary

    async def _publish_event(self, *, event_type: str, actor: str, resource: Any, payload: Dict[str, Any]):
        """Publish events through the trigger mesh and immutable log."""

        await trigger_mesh.publish(
            TriggerEvent(
                event_type=event_type,
                source="coding_orchestrator",
                actor=actor,
                resource=str(resource),
                payload=payload,
                timestamp=datetime.utcnow(),
            )
        )


__all__ = ["CodingOrchestrator", "OrchestrationPlan"]
