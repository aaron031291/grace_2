"""
Intelligence Kernel - ML, Predictions & Causal Reasoning AI Agent
Manages: ML, temporal reasoning, causal analysis, learning, meta-loop, cognition
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance, ExecutionTrace
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class IntelligenceKernel(BaseDomainKernel):
    """
    Intelligent agent for ML, predictions, and advanced reasoning
    
    Manages 45 endpoints:
    - /api/ml/* - Model training, deployment (3)
    - /api/temporal/* - Predictions, simulations, patterns (11)
    - /api/causal/* - Causal graphs, analysis (11)
    - /api/learning/* - Learning aggregates, outcomes (2)
    - /api/meta/* - Meta-loop, analyses, recommendations (8)
    - /api/cognition/* - Intent parsing, execution (10)
    """
    
    def __init__(self):
        super().__init__("intelligence")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from intelligence systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Intelligence Domain (ML, predictions, reasoning):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (predict, analyze, train, causal_analysis, meta_analysis)
2. What data is needed?
3. What's the reasoning goal?
4. Time horizon?

Respond in JSON:
{{
    "operation": "predict|analyze|train|causal|meta",
    "primary_goal": "intelligence objective",
    "required_actions": ["action1", "action2"],
    "data_needed": ["data1", "data2"],
    "time_horizon": "short|medium|long",
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
                confidence=parsed.get("confidence", 0.82)
            )
        except Exception as e:
            log_event("intelligence_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["analyze"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for intelligence operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "predict":
                actions.append({"api": "/api/temporal/predict", "method": "POST"})
            elif action == "causal":
                actions.append({"api": "/api/causal-graph/analyze", "method": "POST"})
            elif action == "train":
                actions.append({"api": "/api/ml/train", "method": "POST"})
            elif action == "meta":
                actions.append({"api": "/api/meta/analyze", "method": "POST"})
            elif action == "cognition":
                actions.append({"api": "/api/cognition/parse", "method": "POST"})
            elif action == "analyze":
                actions.append({"api": "/api/temporal/analyze", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"intelligence_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="sequential",  # Intelligence operations build on each other
            estimated_duration_ms=len(actions) * 300,
            risk_level="low"
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
                        response = await client.get(api_url, timeout=30.0)
                    elif action['method'] == 'POST':
                        response = await client.post(api_url, json=action.get('data', {}), timeout=30.0)
                    
                    try:
                        results[action['api']] = response.json()
                    except:
                        results[action['api']] = {"status": response.status_code}
                except Exception as e:
                    results[action['api']] = {"error": str(e)}
                
                execution_steps.append(ExecutionStep(
                    step_number=len(execution_steps) + 1,
                    component="intelligence_kernel",
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
        
        prompt = f"""Summarize these intelligence analysis results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Provide insights, predictions, and causal explanations."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Intelligence kernel executed {len(execution_results.get('apis_called', []))} analyses."
        
        # Build provenance
        provenance = [
            DataProvenance(
                source_type="intelligence_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.85,
                verified=True
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="intelligence",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["intelligence"],
            execution_trace={
                "request_id": f"intelligence_{datetime.now().timestamp()}",
                "total_duration_ms": 350,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["intelligence"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.87,
            suggested_panels=[
                {"type": "prediction_chart", "title": "Predictions"},
                {"type": "causal_graph", "title": "Causal Analysis"}
            ],
            confidence=original_intent.confidence
        )


# Global instance
intelligence_kernel = IntelligenceKernel()
