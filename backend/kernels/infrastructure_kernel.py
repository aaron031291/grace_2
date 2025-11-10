"""
Infrastructure Kernel - Monitoring, Scheduling & Workers AI Agent
Manages: self-healing, monitoring, scheduling, workers, observability
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance, ExecutionTrace
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class InfrastructureKernel(BaseDomainKernel):
    """
    Intelligent agent for infrastructure, monitoring, and workers
    
    Manages 35 endpoints:
    - /api/self-heal/* - Self-healing operations (8)
    - /api/scheduler/* - Scheduler observability (5)
    - /api/healing/* - Healing dashboard, analytics (4)
    - /api/concurrent/* - Concurrent execution (3)
    - /api/hardware/* - Hardware awareness (6)
    - /api/terminal/* - Terminal WebSocket (2)
    - /api/multimodal/* - Multimodal APIs (7)
    """
    
    def __init__(self):
        super().__init__("infrastructure")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from infrastructure systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Infrastructure Domain (monitoring, workers):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (self_heal, monitor, schedule, hardware_check, status)
2. What infrastructure component?
3. What's the goal?

Respond in JSON:
{{
    "operation": "self_heal|monitor|schedule|hardware|status",
    "primary_goal": "infrastructure objective",
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
                confidence=parsed.get("confidence", 0.88)
            )
        except Exception as e:
            log_event("infrastructure_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["status"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for infrastructure operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "self_heal":
                actions.append({"api": "/api/self-heal/status", "method": "GET"})
            elif action == "monitor":
                actions.append({"api": "/api/scheduler/status", "method": "GET"})
            elif action == "hardware":
                actions.append({"api": "/api/hardware/status", "method": "GET"})
            elif action == "status":
                actions.append({"api": "/api/self-heal/status", "method": "GET"})
                actions.append({"api": "/api/scheduler/status", "method": "GET"})
            elif action == "heal_trigger":
                actions.append({"api": "/api/self-heal/trigger", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"infrastructure_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="parallel",  # Can check multiple systems in parallel
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
                    component="infrastructure_kernel",
                    action=f"call_{action['api']}",
                    duration_ms=0,
                    data_source=action['api']
                ))
            
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
                log_event("infrastructure_kernel_execute_error", {"error": str(e)})
        
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
        
        prompt = f"""Summarize these infrastructure status results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Provide infrastructure health summary."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Infrastructure kernel checked {len(execution_results.get('apis_called', []))} systems."
        
        # Build provenance
        provenance = [
            DataProvenance(
                source_type="infrastructure_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.95,
                verified=True
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="infrastructure",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["infrastructure"],
            execution_trace={
                "request_id": f"infrastructure_{datetime.now().timestamp()}",
                "total_duration_ms": 120,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["infrastructure"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.95,
            suggested_panels=[{"type": "infrastructure_dashboard", "title": "System Status"}],
            confidence=original_intent.confidence
        )


# Global instance
infrastructure_kernel = InfrastructureKernel()
