# agent_core.py
"""Core agent loop for Grace.
Implements the think → act → observe → update cycle.
"""
import asyncio
from tool_registry import TOOL_REGISTRY
from reflection import Reflector
from planner import Planner

class GraceAgent:
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
        self.planner = Planner(llm)
        self.reflector = Reflector(llm)
        self.history = []
        self.current_plan = []

    async def run_step(self, goal):
        # 1. Think: generate a plan or next action
        prompt = f"Current Sub-Goal: {goal}\nHistory: {self.history[-5:] if self.history else 'None'}\nWhat is the next action? Respond with a JSON {{\"tool\": <tool_name>, \"args\": {{...}}}}"
        response = await self.llm.generate(prompt)
        # Assume response is dict with tool and args
        tool_name = response.get('tool')
        args = response.get('args', {})
        # 2. Act: dispatch tool
        result = await TOOL_REGISTRY.dispatch(tool_name, **args)
        # 3. Observe: record result
        self.history.append({"action": tool_name, "args": args, "result": result})
        # 4. Update memory
        await self.memory.store_observation(self.history[-1])
        # 5. Reflection (optional)
        await self.reflector.generate_reflection(self.history[-1])
        return result

    async def run(self, goal, max_steps=10):
        # 1. Plan: Decompose goal
        self.current_plan = await self.planner.decompose_goal(goal)
        if not self.current_plan:
            # Fallback if planner returns nothing
            self.current_plan = [goal]
        
        results = []
        for sub_goal in self.current_plan:
            # Execute each sub-goal
            # For simplicity, we assume one step per sub-goal for now, 
            # but in reality this might be a loop until sub-goal is satisfied.
            step_result = await self.run_step(sub_goal)
            results.append(step_result)
            
            # Check for failure and replan if needed
            if step_result.get('status') == 'error':
                new_plan = await self.planner.replan_on_failure(sub_goal, str(step_result))
                if new_plan:
                    # Append new steps to current plan (simplified)
                    # In a real system we'd replace the remaining plan
                    self.current_plan.extend(new_plan)
        
        return self.history
