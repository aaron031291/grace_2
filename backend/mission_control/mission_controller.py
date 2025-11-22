"""
Mission Controller - The Engine for Dynamic, Manifest-Driven Missions

This controller takes a declarative MissionManifest, uses agentic kernels
to decompose the high-level objective into a hierarchical plan, and then
oversees the execution of that plan.
"""

from __future__ import annotations
import asyncio
import uuid
from typing import Dict, Optional

from .mission_manifest import MissionManifest
from .mission_planner import DynamicMissionPlan, MissionGoal, MissionStatus, create_mission_plan
from backend.core.intent_api import Intent, IntentPriority
from backend.agents_core.elite_coding_agent import elite_coding_agent, CodingTask, CodingTaskType, ExecutionMode
from backend.model_orchestrator import model_orchestrator
from backend.core.intent_api import IntentPriority

class MissionController:
    """Orchestrates the entire lifecycle of a manifest-driven mission."""
    def __init__(self):
        self.active_missions: Dict[str, DynamicMissionPlan] = {}
        # Simple tracking for dispatched intents to avoid re-execution
        self.dispatched_intent_ids: set[str] = set()

    async def start_mission_from_manifest(self, manifest: MissionManifest) -> DynamicMissionPlan:
        """
        Begins a new mission, starting with goal decomposition.
        """
        plan = create_mission_plan(
            description=manifest.objective,
            context={"manifest_id": manifest.manifest_id, **manifest.initial_context}
        )
        self.active_missions[plan.mission_id] = plan

        # Immediately start the planning phase by decomposing the root goal
        asyncio.create_task(self.decompose_and_plan(plan.root_goal, manifest))

        return plan

    async def decompose_and_plan(self, goal: MissionGoal, manifest: MissionManifest):
        """
        Uses the coding_agent to break a goal into smaller, actionable sub-goals or intents.
        """
        goal.status = MissionStatus.PLANNING

        # Prepare a task for the coding agent to perform goal decomposition
        decomposition_prompt = f"""
        Given the high-level mission objective: "{manifest.objective}"
        And the current goal: "{goal.description}"
        Decompose this goal into a short, ordered list of smaller, verifiable sub-goals.
        Each sub-goal should directly contribute to achieving the parent goal.
        The final sub-goal should align with one of the mission's success criteria.

        Constraints to respect: {manifest.constraints}
        Success Criteria to achieve: {manifest.success_criteria}

        Respond ONLY with a JSON list of strings, where each string is a clear sub-goal description.
        Example response:
        [
            "Analyze current API latency metrics to establish a baseline.",
            "Identify the top 3 slowest API endpoints.",
            "Generate optimization suggestions for the slowest endpoint.",
            "Apply the most promising optimization as a code patch.",
            "Verify p95 latency is reduced by at least 10% post-deployment."
        ]
        """

        try:
            # Let the orchestrator pick the best model for this reasoning task
            selected_model = await model_orchestrator.select_best_model(decomposition_prompt)
            
            task = CodingTask(
                task_id=f"decompose_{goal.goal_id}",
                task_type=CodingTaskType.GENERATE_CODE, # Using this for structured text generation
                description=decomposition_prompt,
                execution_mode=ExecutionMode.AUTO,
                priority=9,
                preferred_model=selected_model # Pass the selected model
            )
            # This is a simplified interaction; a real implementation would use a callback
            # or poll for the result. For now, we assume a direct 'get_result' method.
            # In a real scenario, this would be an async, event-driven process.
            sub_goal_descriptions = await elite_coding_agent.execute_and_get_result(task)

            if sub_goal_descriptions:
                for desc in sub_goal_descriptions:
                    new_goal = MissionGoal(
                        goal_id=f"goal_{uuid.uuid4().hex}",
                        description=desc,
                        parent_goal_id=goal.goal_id
                    )
                    goal.sub_steps.append(new_goal)
                goal.status = MissionStatus.EXECUTING
                # Start executing the first sub-step
                await self.execute_next_step(goal, manifest)
            else:
                raise ValueError("Decomposition failed to produce sub-goals.")

        except Exception as e:
            goal.status = MissionStatus.FAILED
            goal.outcome = f"Decomposition failed: {e}"

    async def execute_next_step(self, parent_goal: MissionGoal, manifest: MissionManifest):
        """
        Executes the next pending step in a goal's sub-step list.
        This method is the core of the recursive execution engine.
        """
        next_step = next((s for s in parent_goal.sub_steps if s.status == MissionStatus.PENDING), None)

        if not next_step:
            # If no more steps, the parent goal is likely complete, pending verification.
            is_complete = all(s.status == MissionStatus.COMPLETED for s in parent_goal.sub_steps)
            if is_complete:
                parent_goal.status = MissionStatus.COMPLETED
            # Potentially trigger execution of the next goal at the parent level, or verify success
            return

        if isinstance(next_step, MissionGoal):
            is_actionable = await self._is_goal_actionable(next_step)
            if is_actionable:
                # Convert the low-level goal to an Intent and dispatch it
                intent = await self._create_intent_from_goal(next_step, manifest)
                next_step.sub_steps.append(intent) # Link intent to the goal
                await submit_intent(intent)
                self.dispatched_intent_ids.add(intent.intent_id)
                next_step.status = MissionStatus.EXECUTING # Mark as in-flight
            else:
                # If the goal is still too high-level, decompose it further
                await self.decompose_and_plan(next_step, manifest)

        # After handling a step, recursively call to continue execution
        # This creates a depth-first execution flow.
        await self.execute_next_step(parent_goal, manifest)

    async def _is_goal_actionable(self, goal: MissionGoal) -> bool:
        """
        Uses the coding_agent to determine if a goal is low-level enough to be
        converted directly into an Intent, or if it needs further decomposition.
        """
        prompt = f"""
        Analyze the following goal description: "{goal.description}"
        Is this goal a single, concrete, actionable command that can be executed now?
        Or is it a high-level objective that requires further decomposition into smaller steps?

        Respond ONLY with "actionable" or "decomposition".
        """
        try:
            # Reusing the existing 'select_best_model' which seems to have a typo in my previous version.
            # Assuming it should be `model_orchestrator.select_best_model`.
            selected_model = await model_orchestrator.select_best_model(prompt) 

            task = CodingTask(
                task_id=f"check_actionable_{goal.goal_id}",
                task_type=CodingTaskType.GENERATE_CODE,
                description=prompt,
                execution_mode=ExecutionMode.AUTO,
                priority=8,
                preferred_model=selected_model
            )
            result = await elite_coding_agent.execute_and_get_result(task)
            return "actionable" in result.lower()
        except Exception:
            return False # Default to decomposition if check fails

    async def _create_intent_from_goal(self, goal: MissionGoal, manifest: MissionManifest) -> Intent:
        """
        Uses the coding_agent to formulate a structured Intent from a low-level goal description.
        """
        prompt = f"""
        Given the mission objective: "{manifest.objective}"
        And the actionable goal: "{goal.description}"

        Formulate a structured JSON Intent object to execute this goal.
        The Intent should have 'domain', 'verb', 'target', and 'parameters'.

        Available domains: {', '.join([d.value for d in IntentDomain])}.

        Respond ONLY with the JSON object for the Intent.
        Example for a goal "Apply the most promising optimization as a code patch.":
        {{
            "domain": "coding",
            "goal": "Apply code patch opt-123 to slow_endpoint.py",
            "expected_outcome": "p95 latency reduced by 10%",
            "context": {{
                "file_path": "backend/slow_endpoint.py",
                "patch_id": "opt-123"
            }}
        }}
        """
        selected_model = await model_orchestrator.select_best_model(prompt)

        task = CodingTask(
            task_id=f"formulate_intent_{goal.goal_id}",
            task_type=CodingTaskType.GENERATE_CODE,
            description=prompt,
            execution_mode=ExecutionMode.AUTO,
            priority=8,
            preferred_model=selected_model
        )
        intent_data = await elite_coding_agent.execute_and_get_result(task) or {}

        # Use the correct Intent data model from intent_api.py
        return Intent(
            intent_id=f"intent_{uuid.uuid4().hex}",
            goal=intent_data.get("goal", goal.description),
            expected_outcome=intent_data.get("expected_outcome", "Goal completed"),
            sla_ms=60000, # 1 minute default SLA
            priority=IntentPriority.NORMAL, # Default priority
            domain=intent_data.get("domain", "system"),
            context={
                "mission_id": manifest.manifest_id,
                "goal_id": goal.goal_id,
                "parameters": intent_data.get("context", {}) # The 'context' from the LLM is the 'parameters' for the intent
            },
        )

    def get_mission_status(self, mission_id: str) -> Optional[DynamicMissionPlan]:
        """Returns the current state of a mission."""
        return self.active_missions.get(mission_id)

mission_controller = MissionController()

__all__ = ["mission_controller", "MissionController"]
