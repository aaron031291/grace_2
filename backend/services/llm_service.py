# backend/services/llm_service.py
import json
import re
from typing import Dict, Any, Optional
from backend.unified_llm import unified_llm

class LLMService:
    """
    Adapter service to connect GraceAgent with UnifiedLLM.
    Handles prompt formatting and JSON parsing.
    """
    def __init__(self):
        self.llm = unified_llm

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a structured response from the LLM.
        Expects the LLM to return JSON text.
        """
        # Call UnifiedLLM
        # We use 'use_agentic=False' to avoid recursive loops if the agent is calling this
        response = await self.llm.chat(
            message=prompt,
            use_memory=True,
            use_agentic=False
        )
        
        text = response.get("text", "")
        
        # Attempt to parse JSON from the response
        try:
            # Find JSON-like structure in the text (in case of extra conversational text)
            # Look for { ... }
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback if no JSON found, return text wrapped in a dict
                # This might break strict tool expectations, but useful for debugging
                return {"text": text, "error": "No JSON found"}
        except json.JSONDecodeError:
            return {"text": text, "error": "Invalid JSON"}
        except Exception as e:
            return {"error": str(e)}

# Singleton instance
llm_service = LLMService()
