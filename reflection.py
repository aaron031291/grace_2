# reflection.py
"""Reflection utilities for Grace.
After each action the agent can generate a short reflection that is stored in memory.
"""
from typing import Dict, Any

class Reflector:
    def __init__(self, llm):
        self.llm = llm

    async def generate_reflection(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a reflection based on the latest observation.
        Returns a dict with a 'reflection' string.
        """
        prompt = (
            "You are a reflective AI. Summarize what you learned from the following observation in a concise sentence."
            f" Observation: {observation}"
        )
        result = await self.llm.generate(prompt)
        # In a real system you would store this reflection in memory; here we just return it.
        # Handle both dict and string response
        if isinstance(result, dict):
            return result
        return {"reflection": str(result)}
