"""
Code Kernel - Code Generation & Execution AI Agent
Manages: coding, sandbox, execution, commits, grace-architect
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio
import httpx

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..schemas import ExecutionStep, DataProvenance
from ..logging_utils import log_event
from ..grace_llm import get_grace_llm


class CodeKernel(BaseDomainKernel):
    """
    Intelligent agent for code generation, execution, and understanding
    
    Manages 30 endpoints:
    - /api/coding/* - Code generation, parsing, context (16)
    - /api/sandbox/* - Sandbox execution (5)
    - /api/execution/* - Code execution (4)
    - /api/commit/* - Commit workflows (2)
    - /api/grace-architect/* - Self-extension (7)
    """
    
    def __init__(self):
        super().__init__(kernel_id="code_kernel", domain="code")
        self.base_url = "http://localhost:8000"
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from code systems"""
        
        llm = get_grace_llm()
        
        prompt = f"""Parse this user request for the Code Domain (code generation & execution):

User: "{intent}"
Context: {context}

Determine:
1. What operation? (generate, execute, understand, commit, extend)
2. What language/framework?
3. What's the goal?
4. Safety requirements?

Respond in JSON:
{{
    "operation": "generate|execute|understand|commit|extend",
    "language": "python|javascript|etc",
    "primary_goal": "what code should do",
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
            log_event("code_kernel_parse_error", {"error": str(e)})
            return KernelIntent(
                original_request=intent,
                understood_intent=intent,
                required_actions=["generate"],
                data_needed=[],
                confidence=0.5
            )
    
    async def create_plan(self, parsed_intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan for code operations"""
        
        actions = []
        
        # Map actions to API calls
        for action in parsed_intent.required_actions:
            if action == "generate":
                actions.append({"api": "/api/coding-agent/generate", "method": "POST", "data": {"prompt": parsed_intent.original_request}})
            elif action == "execute":
                actions.append({"api": "/api/execution/execute", "method": "POST"})
            elif action == "sandbox":
                actions.append({"api": "/api/sandbox/test", "method": "POST"})
            elif action == "understand":
                actions.append({"api": "/api/coding-agent/understand", "method": "POST"})
            elif action == "commit":
                actions.append({"api": "/api/commit/create", "method": "POST"})
        
        return KernelPlan(
            plan_id=f"code_plan_{datetime.now().timestamp()}",
            actions=actions,
            sequence="sequential",  # Code operations usually sequential
            estimated_duration_ms=len(actions) * 200,
            risk_level="medium"  # Code execution has risks
        )
    
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plan by orchestrating internal APIs"""
        
        results = {}
        execution_steps = []
        apis_called = []
        
        async with httpx.AsyncClient() as client:
            # Sequential execution for code operations
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
                    component="code_kernel",
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
        
        prompt = f"""Summarize these code operation results for the user:

User asked: "{original_intent.original_request}"

Results:
{execution_results.get('results', {})}

Create a concise summary with code if generated."""

        try:
            answer = await llm.complete(prompt)
        except:
            answer = f"Code kernel executed {len(execution_results.get('apis_called', []))} operations."
        
        # Build provenance
        provenance = [
            DataProvenance(
                source_type="code_system",
                source_id=api,
                timestamp=datetime.now().isoformat(),
                confidence=0.88,
                verified=True
            )
            for api in execution_results.get('apis_called', [])
        ]
        
        return KernelResponse(
            kernel_name="code",
            answer=answer,
            data=execution_results.get('results'),
            apis_called=execution_results.get('apis_called', []),
            kernels_consulted=["code"],
            execution_trace={
                "request_id": f"code_{datetime.now().timestamp()}",
                "total_duration_ms": 200,
                "steps": execution_results.get('execution_steps', []),
                "agents_involved": ["code"],
                "data_sources_used": execution_results.get('apis_called', [])
            },
            data_provenance=provenance,
            trust_score=0.88,
            suggested_panels=[{"type": "code_editor", "title": "Generated Code"}],
            confidence=original_intent.confidence
        )
    
    # Implement abstract methods required by BaseDomainKernel
    async def _initialize_watchers(self):
        """Set up watchers for code generation requests"""
        pass
    
    async def _load_pending_work(self):
        """Load pending code generation tasks"""
        pass
    
    async def _coordinator_loop(self):
        """Main coordination loop for code operations"""
        while self._running:
            try:
                await asyncio.sleep(10)
            except Exception as e:
                pass
    
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent for code tasks"""
        return {"agent_id": agent_id, "type": agent_type, "task": task_data}
    
    async def _cleanup(self):
        """Cleanup code kernel resources"""
        pass


# Global instance
code_kernel = CodeKernel()
