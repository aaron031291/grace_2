"""
Self-Reflection Loop
Grace's ability to look inward, analyze her own performance, and propose self-improvements.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.services.rag_service import rag_service
from backend.model_orchestrator import model_orchestrator
from backend.core.message_bus import message_bus

logger = logging.getLogger(__name__)

class SelfReflectionLoop:
    """
    The Mirror: Grace's self-reflection mechanism.
    
    Cycle:
    1. Observe: Read memory/logs for errors, gaps, and user feedback.
    2. Orient: Analyze patterns using LLM reasoning.
    3. Decide: Propose a "Growth Plan" (code changes, new skills).
    4. Act: (Currently manual) Save plan for user review.
    """
    
    def __init__(self):
        self.running = False
        self.reflection_interval = 3600  # Reflect every hour
        self.brain_dir = Path("brain")
        self.brain_dir.mkdir(exist_ok=True)
        
    async def start(self):
        """Start the reflection loop"""
        self.running = True
        logger.info("[REFLECTION] Mirror active - Grace is watching herself")
        asyncio.create_task(self._loop())
        
    async def stop(self):
        self.running = False
        
    async def _loop(self):
        while self.running:
            try:
                await self.reflect()
                await asyncio.sleep(self.reflection_interval)
            except Exception as e:
                logger.error(f"[REFLECTION] Error in loop: {e}")
                await asyncio.sleep(60)
                
    async def reflect(self):
        """Perform a single reflection cycle"""
        logger.info("[REFLECTION] Starting self-reflection cycle...")
        
        # 1. Gather Data (The "Self")
        # Query RAG for recent failures or gaps
        rag_result = await rag_service.retrieve(
            query="system error failure bug missing capability",
            top_k=10,
            source_types=["log", "memory", "user_feedback"]
        )
        
        context_text = "\n".join([r.get('text_content', '') for r in rag_result['results']])
        
        if not context_text:
            logger.info("[REFLECTION] No significant issues found to reflect on.")
            return

        # 2. Analyze (The "Reasoning")
        prompt = f"""
        You are Grace, an advanced AI system. 
        Analyze the following logs and memory fragments to identify:
        1. Recurring errors.
        2. Missing capabilities (things I tried to do but failed).
        3. User frustrations.
        
        Logs:
        {context_text}
        
        Output a JSON object with:
        - analysis: Summary of issues.
        - proposed_improvements: List of specific code changes or new features needed.
        - priority: High/Medium/Low.
        """
        
        response = await model_orchestrator.chat_with_learning(
            message=prompt,
            # Use MoE powerhouse for deep analysis
            user_preference="deepseek-v2.5:236b" # MoE reasoning powerhouse
        )
        
        analysis = response.get('text', '')
        
        # 3. Propose Growth (The "Plan")
        await self._save_growth_plan(analysis)
        
    async def _save_growth_plan(self, analysis: str):
        """Save the analysis as a Growth Plan artifact"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = self.brain_dir / f"GROWTH_PLAN_{timestamp}.md"
        
        content = f"""# Grace Growth Plan ({timestamp})

## Self-Reflection Analysis
{analysis}

## Action Items
- [ ] User to review proposed changes.
- [ ] Guardian to validate safety.
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"[REFLECTION] Generated Growth Plan: {filename}")
        
        # Notify via bus
        await message_bus.publish(
            source="self_reflection_loop",
            topic="agent.growth_plan",
            payload={"path": str(filename), "summary": analysis[:100] + "..."}
        )

# Global instance
self_reflection_loop = SelfReflectionLoop()
