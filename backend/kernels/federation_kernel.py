"""
Federation Kernel - External Integrations AI Agent
Manages: web learning, external APIs, GitHub, Slack, AWS, third-party integrations
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance, ExecutionTrace
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class FederationKernel(BaseDomainKernel):
    """
    Intelligent agent for external integrations and federation
    
    Manages 35 endpoints:
    - /api/web-learning/* - Web learning, Amp API, verification (12)
    - /api/external-api/* - External API integration (8)
    - /api/agentic/* - Agentic insights (5)
    - /api/chunked-upload/* - File uploads (3)
    - /api/websocket/* - WebSocket connections (2)
    - Plus: GitHub, Slack, AWS integrations (5)
    """
    
    def __init__(self):
        super().__init__("federation")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from federation systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Federation Domain (external integrations):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (web_learn, external_api, integrate, upload, connect)
2. What external system?
3. What data to fetch/send?
4. Authentication needed?

Respond in JSON:
{{
    "operation": "web_learn|external_api|integrate|upload|connect",
    "primary_goal": "federation objective",
    "required_actions": ["action1", "action2"],
    "data_needed": ["data1", "data2"],
    "external_systems": ["system1", "system2"],
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
                confidence=parsed.get("confidence", 0.85)
            )
        except Exception as e:
            log_event("federation_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["web_learn"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for federation operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "web_learn":
                actions.append({"api": "/api/web-learning/learn", "method": "POST"})
            elif action == "amp_query":
                actions.append({"api": "/api/web-learning/amp/query", "method": "POST"})
            elif action == "verify_source":
                actions.append({"api": "/api/web-learning/verify/source", "method": "POST"})
            elif action == "external_api":
                actions.append({"api": "/api/external-api/call", "method": "POST"})
            elif action == "integrations":
                actions.append({"api": "/api/web-learning/ingestions", "method": "GET"})
            elif action == "upload":
                actions.append({"api": "/api/chunked-upload/start", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"federation_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="sequential",  # External calls usually sequential
            estimated_duration_ms=len(actions) * 500,  # External APIs can be slow
            risk_level="medium"  # External systems have risks
        )
    
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plan by orchestrating internal APIs"""
        
        results = {}
        execution_steps = []
        apis_called = []
        
        async with httpx.AsyncClient() as client:
            for action in plan.actions:
                api_url = f"{self.base_url}{action['api']}"
                apis_called.append(action['api'])
                
                try:
                    if action['method'] == 'GET':
                        response = await client.get(api_url, timeout=60.0)  # Longer timeout for external
                    elif action['method'] == 'POST':
                        response = await client.post(api_url, json=action.get('data', {}), timeout=60.0)
                    
                    try:
                        results[action['api']] = response.json()
                    except:
                        results[action['api']] = {"status": response.status_code}
                except Exception as e:
                    results[action['api']] = {"error": str(e)}
                
                execution_steps.append(ExecutionStep(
                    step_number=len(execution_steps) + 1,
                    component="federation_kernel",
                    action=f"call_{action['api']}",
                    duration_ms=0,
                    data_source=action['api']
                ))
        
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
        
        prompt = f"""Summarize these external integration results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Provide summary of data fetched and any integrations made."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Federation kernel executed {len(execution_results.get('apis_called', []))} external operations."
        
        # Build provenance - mark as external sources
        provenance = [
            DataProvenance(
                source_type="external_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.80,  # Lower confidence for external
                verified=False  # Needs verification
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="federation",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["federation"],
            execution_trace={
                "request_id": f"federation_{datetime.now().timestamp()}",
                "total_duration_ms": 600,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["federation"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.80,  # Lower trust for external
            suggested_panels=[
                {"type": "web_learning", "title": "Learning Results"},
                {"type": "external_data", "title": "External Data"}
            ],
            confidence=original_intent.confidence
        )


# Global instance
federation_kernel = FederationKernel()
