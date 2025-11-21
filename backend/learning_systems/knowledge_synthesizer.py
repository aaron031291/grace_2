"""
Knowledge Synthesizer
Standardizes raw information into high-quality ML/DL ready knowledge.
Extracts concepts, code, Q&A, and summaries from raw content.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from backend.llm.unified_llm import unified_llm
except ImportError:
    unified_llm = None

logger = logging.getLogger(__name__)

class KnowledgeSynthesizer:
    """
    Synthesizes raw content into standardized knowledge artifacts.
    """

    def __init__(self):
        self.llm = unified_llm

    async def synthesize(self, content: str, source_url: str, topic: str) -> Dict[str, Any]:
        """
        Synthesize raw content into structured knowledge.
        
        Args:
            content: Raw text/HTML content
            source_url: Source URL
            topic: Topic being learned
            
        Returns:
            Dict containing synthesized knowledge (concepts, code, qa, summary)
        """
        if not self.llm:
            logger.warning("[SYNTHESIZER] Unified LLM not available, returning raw content wrapper")
            return {
                "summary": content[:500] + "...",
                "concepts": [],
                "code_snippets": [],
                "qa_pairs": [],
                "raw_content": content
            }

        # Truncate content if too long for context window (simple heuristic)
        # In production, use token counting
        max_chars = 15000
        if len(content) > max_chars:
            content = content[:max_chars] + "...(truncated)"

        prompt = f"""
        You are an Expert Knowledge Engineer. Your task is to synthesize the following raw content into high-quality, standardized knowledge for an AI system's memory.
        
        Topic: {topic}
        Source: {source_url}
        
        Raw Content:
        {content}
        
        Output a JSON object with the following structure:
        {{
            "summary": "Concise high-level summary of the content (max 3 sentences)",
            "concepts": [
                {{ "term": "Concept Name", "definition": "Clear, technical definition" }}
            ],
            "code_snippets": [
                {{ "language": "python/js/etc", "code": "The code", "description": "What it does" }}
            ],
            "qa_pairs": [
                {{ "question": "Technical question based on content", "answer": "Precise answer" }}
            ],
            "key_takeaways": ["Point 1", "Point 2"]
        }}
        
        Ensure all extracted information is accurate, technical, and free of fluff.
        If no code is present, return empty list for code_snippets.
        """

        try:
            response = await self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                json_mode=True
            )
            
            # Parse JSON response
            # Assuming the LLM returns a string that might need parsing
            # If unified_llm handles JSON mode natively and returns dict, adapt accordingly
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown blocks if present
                    import re
                    match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    if match:
                        data = json.loads(match.group(1))
                    else:
                        raise ValueError("Could not parse JSON from LLM response")
            else:
                data = response

            # Add metadata
            data['synthesized_at'] = datetime.utcnow().isoformat()
            data['source_url'] = source_url
            data['topic'] = topic
            
            return data

        except Exception as e:
            logger.error(f"[SYNTHESIZER] Error synthesizing content: {e}")
            return {
                "summary": "Error during synthesis",
                "error": str(e),
                "raw_content": content[:500]
            }

# Global instance
knowledge_synthesizer = KnowledgeSynthesizer()
