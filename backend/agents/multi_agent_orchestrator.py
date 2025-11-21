"""
Multi-Agent Build Orchestrator
Manages parallel build tasks with up to 10 concurrent agents.
Automatically detects knowledge gaps and triggers learning.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from backend.core.message_bus import message_bus
from backend.core.agent_protocol import AgentProtocol, AgentRequest, AgentResponse
from backend.agents.builder_agent import BuilderAgent

logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """
    Orchestrates multiple builder agents working in parallel.
    
    Features:
    - Spawn up to 10 concurrent builder agents
    - Load balancing across agents
    - Knowledge gap detection
    - Automatic learning loop integration
    - Progress aggregation
    """
    
    def __init__(self, max_agents: int = 10):
        self.max_agents = max_agents
        self.active_agents: Dict[str, BuilderAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.knowledge_gaps: List[str] = []
        
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        asyncio.create_task(self._process_queue())
        logger.info(f"[ORCHESTRATOR] Multi-agent orchestrator started (max {self.max_agents} agents)")
        
    async def stop(self):
        """Stop all agents"""
        self.running = False
        for agent_id, agent in self.active_agents.items():
            await agent.stop()
        self.active_agents.clear()
        
    async def submit_build_task(self, request: AgentRequest) -> str:
        """Submit a build task to the queue"""
        task_id = str(uuid.uuid4())
        await self.task_queue.put((task_id, request))
        logger.info(f"[ORCHESTRATOR] Task {task_id} queued")
        return task_id
        
    async def _process_queue(self):
        """Process build tasks from queue"""
        while self.running:
            try:
                # Wait for task
                task_id, request = await self.task_queue.get()
                
                # Wait for available agent slot
                while len(self.active_agents) >= self.max_agents:
                    await asyncio.sleep(0.5)
                
                # Spawn new agent
                agent = BuilderAgent()
                self.active_agents[task_id] = agent
                await agent.start()
                
                # Execute task
                asyncio.create_task(self._execute_with_learning(task_id, agent, request))
                
            except Exception as e:
                logger.error(f"[ORCHESTRATOR] Queue processing error: {e}")
                await asyncio.sleep(1)
                
    async def _execute_with_learning(self, task_id: str, agent: BuilderAgent, request: AgentRequest):
        """Execute build task with automatic learning on knowledge gaps"""
        try:
            logger.info(f"[ORCHESTRATOR] Starting task {task_id}")
            
            # Subscribe to agent responses
            response_queue = await message_bus.subscribe(f"orchestrator_{task_id}", AgentProtocol.TOPIC_RESPONSE)
            
            # Trigger build
            await message_bus.publish(
                source="multi_agent_orchestrator",
                topic=AgentProtocol.TOPIC_REQUEST,
                payload=request.to_dict()
            )
            
            # Wait for response with timeout
            try:
                response_msg = await asyncio.wait_for(response_queue.get(), timeout=300)  # 5 min timeout
                response = AgentResponse(**response_msg.payload)
                
                # Check for knowledge gaps
                if response.status == "failure":
                    await self._handle_knowledge_gap(request, response)
                    
            except asyncio.TimeoutError:
                logger.error(f"[ORCHESTRATOR] Task {task_id} timed out")
                
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Task {task_id} failed: {e}")
            
        finally:
            # Cleanup
            await agent.stop()
            if task_id in self.active_agents:
                del self.active_agents[task_id]
            logger.info(f"[ORCHESTRATOR] Task {task_id} completed. Active agents: {len(self.active_agents)}")
            
    async def _handle_knowledge_gap(self, original_request: AgentRequest, failed_response: AgentResponse):
        """Detect knowledge gap and trigger learning"""
        error_content = failed_response.content.lower()
        
        # Detect what knowledge is missing
        gap_detected = None
        if "not found" in error_content or "unknown" in error_content:
            gap_detected = self._extract_missing_concept(original_request.query, error_content)
        
        if gap_detected:
            logger.info(f"[ORCHESTRATOR] Knowledge gap detected: {gap_detected}")
            self.knowledge_gaps.append(gap_detected)
            
            # Trigger ProactiveLearningAgent to research this topic
            learning_request = AgentProtocol.create_request(
                source="multi_agent_orchestrator",
                capability="research",
                query=f"Learn about {gap_detected} for software development",
                context={"reason": "knowledge_gap", "original_task": original_request.query}
            )
            
            await message_bus.publish(
                source="multi_agent_orchestrator",
                topic=AgentProtocol.TOPIC_REQUEST,
                payload=learning_request.to_dict()
            )
            
            logger.info(f"[ORCHESTRATOR] Triggered learning for: {gap_detected}")
            
    def _extract_missing_concept(self, query: str, error: str) -> Optional[str]:
        """Extract the missing concept from error message"""
        # Simple heuristic: look for quoted terms or capitalized words in error
        import re
        
        # Try to find quoted terms
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", error)
        if quoted:
            return quoted[0]
        
        # Try to find capitalized terms (likely library/framework names)
        capitalized = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b', error)
        if capitalized:
            return capitalized[0]
        
        # Fallback: extract key terms from original query
        keywords = ["framework", "library", "api", "database", "tool"]
        for keyword in keywords:
            if keyword in query.lower():
                # Extract the word before the keyword
                match = re.search(rf'(\w+)\s+{keyword}', query.lower())
                if match:
                    return match.group(1)
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self.running,
            "active_agents": len(self.active_agents),
            "max_agents": self.max_agents,
            "queue_size": self.task_queue.qsize(),
            "knowledge_gaps_detected": len(self.knowledge_gaps),
            "recent_gaps": self.knowledge_gaps[-5:] if self.knowledge_gaps else []
        }

# Global instance
multi_agent_orchestrator = MultiAgentOrchestrator(max_agents=10)
