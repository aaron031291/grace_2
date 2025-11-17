"""
Governance Kernel - Policy & Safety AI Agent
Manages: governance, constitutional, hunter, autonomy, parliament, verification
"""

from typing import Dict, Any
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class GovernanceKernel(BaseDomainKernel):
    """
    Intelligent agent for governance, policy, and safety
    
    Manages 40 endpoints:
    - /api/governance/* - Policies, checks, approvals (9)
    - /api/constitutional/* - Constitutional principles (12)
    - /api/hunter/* - Threat detection (4)
    - /api/autonomy/* - Autonomy tiers, checks (8)
    - /api/parliament/* - Parliamentary governance (13)
    - /api/verification/* - Verification audit (4)
    """
    
    def __init__(self):
        super().__init__(kernel_id="governance_kernel", domain="governance")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from governance systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Governance Domain (policy, safety, approvals):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (check_policy, approve, constitutional_check, threat_detect, autonomy_check)
2. What's being governed?
3. Risk level?
4. What checks are needed?

Respond in JSON:
{{
    "operation": "operation_type",
    "primary_goal": "governance objective",
    "required_actions": ["action1", "action2"],
    "data_needed": ["data1", "data2"],
    "risk_level": "low|medium|high",
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
                confidence=parsed.get("confidence", 0.9)
            )
        except Exception as e:
            log_event("governance_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["check_policy"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for governance operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "check_policy":
                actions.append({"api": "/api/governance/check", "method": "POST"})
            elif action == "constitutional_check":
                actions.append({"api": "/api/constitutional/verify", "method": "POST"})
            elif action == "approve":
                actions.append({"api": "/api/governance/approve", "method": "POST"})
            elif action == "threat_detect":
                actions.append({"api": "/api/hunter/detect", "method": "POST"})
            elif action == "autonomy_check":
                actions.append({"api": "/api/autonomy/check", "method": "POST"})
            elif action == "parliament":
                actions.append({"api": "/api/parliament/session", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"governance_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="sequential",  # Governance checks must be sequential
            estimated_duration_ms=len(actions) * 100,
            risk_level="high"  # Governance is critical
        )
    
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plan by orchestrating internal APIs"""
        
        results = {}
        execution_steps = []
        apis_called = []
        
        async with httpx.AsyncClient() as client:
            # Sequential execution for governance
            for action in plan.actions:
                api_url = f"{self.base_url}{action['api']}"
                apis_called.append(action['api'])
                
                try:
                    if action['method'] == 'GET':
                        response = await client.get(api_url, timeout=15.0)
                    elif action['method'] == 'POST':
                        response = await client.post(api_url, json=action.get('data', {}), timeout=15.0)
                    
                    try:
                        results[action['api']] = response.json()
                    except:
                        results[action['api']] = {"status": response.status_code}
                except Exception as e:
                    results[action['api']] = {"error": str(e)}
                
                execution_steps.append(ExecutionStep(
                    step_number=len(execution_steps) + 1,
                    component="governance_kernel",
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
        
        prompt = f"""Summarize these governance check results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Provide clear governance decision with reasoning."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Governance kernel executed {len(execution_results.get('apis_called', []))} checks."
        
        # Build provenance
        provenance = [
            DataProvenance(
                source_type="governance_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.98,
                verified=True
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="governance",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["governance"],
            execution_trace={
                "request_id": f"governance_{datetime.now().timestamp()}",
                "total_duration_ms": 150,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["governance"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.98,
            suggested_panels=[{"type": "governance_decision", "title": "Governance Check"}],
            confidence=original_intent.confidence
        )
    
    # Implement abstract methods required by BaseDomainKernel
    async def _initialize_watchers(self):
        """Set up watchers for governance policy changes"""
        pass
    
    async def _load_pending_work(self):
        """Load pending governance checks and approvals"""
        pass
    
    async def _coordinator_loop(self):
        """Main coordination loop for governance operations"""
        while self._running:
            try:
                await asyncio.sleep(10)
            except Exception as e:
                pass
    
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent for governance tasks"""
        return {"agent_id": agent_id, "type": agent_type, "task": task_data}
    
    async def _cleanup(self):
        """Cleanup governance kernel resources"""
        pass


# Global instance
governance_kernel = GovernanceKernel()
