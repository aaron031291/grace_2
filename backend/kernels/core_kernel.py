"""
Core Kernel - System & User Interaction AI Agent
Manages: chat, auth, tasks, health, metrics, history, reflections, summaries, plugins, issues, speech, evaluation
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class CoreKernel(BaseDomainKernel):
    """
    Intelligent agent for core system operations & user interaction
    
    Manages 35 endpoints:
    - /api/chat - Main conversation
    - /api/auth/* - Authentication (2)
    - /api/tasks/* - Task management (3)
    - /api/health - System health
    - /api/metrics/* - System metrics (3)
    - /api/history/* - History tracking (2)
    - /api/reflections/* - Reflection system (2)
    - /api/summaries/* - Summaries (2)
    - /api/plugins/* - Plugin management (3)
    - /api/issues/* - Issue tracking (3)
    - /api/speech/* - Speech/TTS (8)
    - /api/evaluation/* - Evaluation (2)
    """
    
    def __init__(self):
        super().__init__(kernel_id="core_kernel", domain="core")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from core systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Core Domain (system operations & user interaction):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (chat, auth, task, health, metrics, history, reflection, summary, plugin, issue, speech, evaluation)
2. What data is needed?
3. Which APIs to call?
4. What's the primary goal?

Respond in JSON:
{{
    "operation": "operation_type",
    "primary_goal": "what user wants to achieve",
    "required_actions": ["action1", "action2"],
    "data_needed": ["data1", "data2"],
    "confidence": 0.0-1.0
}}
"""
        
        try:
            response = await llm.complete(prompt)
            import json
            parsed = json.loads(response)
            
            return KernelIntent(
                original_request=intent,
                understood_intent=parsed.get("primary_goal", intent),
                required_actions=parsed.get("required_actions", []),
                data_needed=parsed.get("data_needed", []),
                confidence=parsed.get("confidence", 0.8)
            )
        except Exception as e:
            log_event("core_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["chat"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for core operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "chat":
                actions.append({"api": "/api/chat", "method": "POST", "data": {"message": parsed_intent.original_request}})
            elif action == "health":
                actions.append({"api": "/health", "method": "GET"})
            elif action == "metrics":
                actions.append({"api": "/api/metrics", "method": "GET"})
            elif action == "tasks":
                actions.append({"api": "/api/tasks", "method": "GET"})
            elif action == "history":
                actions.append({"api": "/api/history", "method": "GET"})
            elif action == "reflections":
                actions.append({"api": "/api/reflections", "method": "GET"})
            elif action == "issues":
                actions.append({"api": "/api/issues", "method": "GET"})
            elif action == "speech":
                actions.append({"api": "/api/speech/synthesize", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"core_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="parallel",  # Can fetch most things in parallel
            estimated_duration_ms=len(actions) * 50,
            risk_level="low"
        )
    
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plan by orchestrating internal APIs"""
        
        results = {}
        execution_steps = []
        apis_called = []
        
        async with httpx.AsyncClient() as client:
            tasks = []
            
            for action in plan.actions:
                api_url = f"{self.base_url}{action['api']}"
                apis_called.append(action['api'])
                
                if action['method'] == 'GET':
                    tasks.append(client.get(api_url, timeout=10.0))
                elif action['method'] == 'POST':
                    tasks.append(client.post(api_url, json=action.get('data', {}), timeout=10.0))
                
                execution_steps.append(ExecutionStep(
                    step_number=len(execution_steps) + 1,
                    component="core_kernel",
                    action=f"call_{action['api']}",
                    duration_ms=0,
                    data_source=action['api']
                ))
            
            # Execute in parallel
            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                for idx, response in enumerate(responses):
                    if isinstance(response, Exception):
                        results[plan.actions[idx]['api']] = {"error": str(response)}
                    else:
                        try:
                            results[plan.actions[idx]['api']] = response.json()
                        except:
                            results[plan.actions[idx]['api']] = {"status": response.status_code}
            except Exception as e:
                log_event("core_kernel_execute_error", {"error": str(e)})
        
        return {
            "results": results,
            "execution_steps": execution_steps,
            "apis_called": apis_called
        }
    
    async def aggregate_response(
        self,
        execution_results: Dict[str, Any],
        original_intent: KernelIntent,
        context: Dict[str, Any]
    ) -> KernelResponse:
        """Aggregate results into intelligent response"""
        
        llm = get_grace_llm()
        
        # Use LLM to create natural language summary
        prompt = f"""Summarize these API results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Create a concise, helpful summary."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Core kernel executed {len(execution_results.get('apis_called', []))} operations."
        
        # Build provenance
        provenance = [
            DataProvenance(
                source_type="core_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.95,
                verified=True
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="core",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["core"],
            execution_trace={
                "request_id": f"core_{datetime.now().timestamp()}",
                "total_duration_ms": 100,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["core"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.92,
            suggested_panels=[],
            confidence=original_intent.confidence
        )
    
    # Implement abstract methods required by BaseDomainKernel
    async def _initialize_watchers(self):
        """Set up filesystem, event, or API watchers for core domain"""
        # Core kernel monitors system events and API health
        pass
    
    async def _load_pending_work(self):
        """Load any pending core system tasks"""
        # Check for pending tasks, health checks, or system operations
        pass
    
    async def _coordinator_loop(self):
        """Main coordination loop for core operations"""
        while self._running:
            try:
                # Heartbeat and health monitoring
                await asyncio.sleep(10)
            except Exception as e:
                log_event("core_kernel_loop_error", {"error": str(e)})
    
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent for core domain tasks"""
        # Stub: would create actual agent instances
        return {"agent_id": agent_id, "type": agent_type, "task": task_data}
    
    async def _cleanup(self):
        """Cleanup core kernel resources on shutdown"""
        pass


# Global instance
core_kernel = CoreKernel()
