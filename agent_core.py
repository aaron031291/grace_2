# agent_core.py
"""Core agent loop for Grace.
Implements the think → act → observe → update cycle.
"""
import asyncio
from tool_registry import TOOL_REGISTRY
from reflection import generate_reflection

class GraceAgent:
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory
        self.history = []

    async def run_step(self, goal):
        # 1. Think: generate a plan or next action
        prompt = f"Goal: {goal}\nHistory: {self.history[-5:] if self.history else 'None'}\nWhat is the next action? Respond with a JSON {{\"tool\": <tool_name>, \"args\": {{...}}}}"
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
        await generate_reflection(self.history[-1])
        return result

    async def run(self, goal, max_steps=10):
        for _ in range(max_steps):
            result = await self.run_step(goal)
            if result.get('status') == 'completed':
                break
        return self.history
