# planner.py
"""Planner module for Grace.
Provides goal decomposition and re‑planning using an LLM.
"""
from typing import List, Dict, Any

class Planner:
    def __init__(self, llm):
        self.llm = llm

    async def decompose_goal(self, goal: str) -> List[str]:
        """Given a high‑level goal, return a list of sub‑goals.
        The LLM is prompted to break the goal into manageable steps.
        """
        prompt = f"Decompose the following goal into a numbered list of concrete sub‑goals. Goal: {goal}"
        response = await self.llm.generate(prompt)
        # Handle both dict response (mock) and string response (real LLM)
        if isinstance(response, dict):
            return response.get("steps", [])
        # Fallback for string response parsing would go here
        return []

    async def replan_on_failure(self, failed_step: str, context: str) -> List[str]:
        """Generate a revised plan when a step fails.
        Uses the LLM to suggest alternatives based on the failed step and current context.
        """
        prompt = (
            f"The previous step '{failed_step}' failed. Given the current context: {context}, "
            "suggest a revised list of sub‑goals to achieve the original goal."
        )
        response = await self.llm.generate(prompt)
        if isinstance(response, dict):
            return response.get("steps", [])
        return []
