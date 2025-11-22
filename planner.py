# planner.py
"""Planner module for Grace.
Provides goal decomposition and re‑planning using an LLM.
"""
import asyncio
from typing import List, Dict, Any

# Placeholder LLM interface – replace with actual LLM client
class LLMClient:
    async def generate(self, prompt: str) -> Dict[str, Any]:
        # Simulate a simple planner response
        await asyncio.sleep(0.1)
        # Expected format: {'steps': ['step1', 'step2', ...]}
        return {"steps": ["Analyze goal", "Create sub‑goals", "Execute sub‑goals"]}

llm = LLMClient()

async def decompose_goal(goal: str) -> List[str]:
    """Given a high‑level goal, return a list of sub‑goals.
    The LLM is prompted to break the goal into manageable steps.
    """
    prompt = f"Decompose the following goal into a numbered list of concrete sub‑goals. Goal: {goal}"
    response = await llm.generate(prompt)
    return response.get("steps", [])

async def replan_on_failure(failed_step: str, context: str) -> List[str]:
    """Generate a revised plan when a step fails.
    Uses the LLM to suggest alternatives based on the failed step and current context.
    """
    prompt = (
        f"The previous step '{failed_step}' failed. Given the current context: {context}, "
        "suggest a revised list of sub‑goals to achieve the original goal."
    )
    response = await llm.generate(prompt)
    return response.get("steps", [])
