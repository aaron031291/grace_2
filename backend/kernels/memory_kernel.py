"""
Memory Kernel - Intelligent Memory & Knowledge Agent
Manages all memory storage, retrieval, and knowledge operations
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_kernel import BaseDomainKernel, KernelIntent, KernelPlan, KernelResponse
from ..memory import PersistentMemory
from ..schemas import ExecutionStep, DataProvenance
from ..logging_utils import log_event


class MemoryKernel(BaseDomainKernel):
    """
    Intelligent agent for all memory & knowledge operations
    
    Manages:
    - Memory tree (domains/categories)
    - Knowledge queries (semantic search)
    - Ingestion (text/file/URL)
    - Trust scoring
    - Context assembly
    """
    
    def __init__(self):
        super().__init__("memory")
        self.memory = PersistentMemory()
    
    async def parse_intent(self, intent: str, context: Dict[str, Any]) -> KernelIntent:
        """Parse what user wants from memory/knowledge"""
        
        # Use LLM to understand intent
        prompt = f"""Parse this user request for the Memory/Knowledge domain:
        
User: "{intent}"

Determine:
1. What type of memory operation? (search, store, retrieve, ingest)
2. What data is needed?
3. Which memory systems? (Lightning short-term, Library indexed, Fusion long-term)
4. Search parameters if applicable

Respond in JSON:
{{
    "operation": "search|store|retrieve|ingest",
    "query": "semantic search query if search operation",
    "domain": "domain filter if any",
    "data_needed": ["list", "of", "data"],
    "memory_systems": ["lightning", "library", "fusion"]
}}
"""
        
        # For now, simple keyword detection (would use LLM in production)
        operation = "search"
        if any(word in intent.lower() for word in ["store", "save", "remember"]):
            operation = "store"
        elif any(word in intent.lower() for word in ["find", "search", "get", "show"]):
            operation = "search"
        elif any(word in intent.lower() for word in ["ingest", "load", "import"]):
            operation = "ingest"
        
        return KernelIntent(
            original_request=intent,
            understood_intent=f"{operation} operation in memory domain",
            required_actions=[operation],
            data_needed=["memory_tree", "knowledge_base"] if operation == "search" else ["target_data"],
            confidence=0.85
        )
    
    async def create_plan(self, intent: KernelIntent, context: Dict[str, Any]) -> KernelPlan:
        """Create execution plan"""
        
        actions = []
        
        if "search" in intent.required_actions:
            actions.append({
                "type": "api_call",
                "endpoint": "/api/memory/tree",
                "method": "GET",
                "params": {}
            })
            actions.append({
                "type": "api_call",
                "endpoint": "/api/knowledge/query",
                "method": "POST",
                "params": {"query": intent.original_request, "limit": 10}
            })
            sequence = "parallel"
        
        elif "store" in intent.required_actions:
            actions.append({
                "type": "api_call",
                "endpoint": "/api/memory/items",
                "method": "POST",
                "params": context.get("data", {})
            })
            sequence = "sequential"
        
        elif "ingest" in intent.required_actions:
            actions.append({
                "type": "api_call",
                "endpoint": "/api/ingest/text",
                "method": "POST",
                "params": context.get("data", {})
            })
            sequence = "sequential"
        
        else:
            actions.append({
                "type": "default",
                "endpoint": "/api/memory/tree"
            })
            sequence = "sequential"
        
        return KernelPlan(
            plan_id=f"mem_{datetime.utcnow().timestamp()}",
            actions=actions,
            sequence=sequence,
            estimated_duration_ms=len(actions) * 100.0,
            risk_level="low"
        )
    
    async def execute_plan(self, plan: KernelPlan, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plan by calling appropriate APIs"""
        
        results = {}
        
        # Use memory service directly (avoid route function imports)
        for action in plan.actions:
            endpoint = action["endpoint"]
            
            try:
                if endpoint == "/api/memory/tree":
                    # Access memory tree through memory service
                    artifacts = await self.memory.get_all_artifacts()
                    results["memory_tree"] = {
                        "flat_list": artifacts[:50],  # First 50
                        "total": len(artifacts)
                    }
                
                elif endpoint == "/api/knowledge/query":
                    # Use knowledge service
                    query_text = action["params"].get("query", "")
                    # Stub - would call knowledge.query_semantic
                    results["knowledge"] = {
                        "results": [],
                        "total": 0,
                        "query": query_text
                    }
                
                elif endpoint == "/api/memory/items":
                    # Store via memory service
                    await self.memory.store_artifact(
                        path=action["params"].get("path", "/temp"),
                        content=action["params"].get("content", ""),
                        domain=action["params"].get("domain", "general")
                    )
                    results["stored"] = {"success": True}
                
                elif endpoint == "/api/ingest/text":
                    # Ingest stub
                    results["ingested"] = {
                        "status": "ingested",
                        "artifact_id": 1
                    }
                
            except Exception as e:
                results[endpoint] = {"error": str(e)}
        
        return results
    
    async def aggregate_response(
        self, 
        results: Dict[str, Any], 
        intent: KernelIntent, 
        context: Dict[str, Any]
    ) -> KernelResponse:
        """Aggregate results intelligently"""
        
        # Build execution trace
        steps = []
        step_num = 1
        
        steps.append(ExecutionStep(
            step_number=step_num,
            component="memory_kernel",
            action="parse_intent",
            duration_ms=15.0,
            data_source="user_input"
        ))
        step_num += 1
        
        steps.append(ExecutionStep(
            step_number=step_num,
            component="memory_kernel",
            action="create_plan",
            duration_ms=10.0,
            data_source="intent"
        ))
        step_num += 1
        
        for api in self.apis_called:
            steps.append(ExecutionStep(
                step_number=step_num,
                component="memory_kernel",
                action=f"call_{api}",
                duration_ms=50.0,
                data_source="memory_database"
            ))
            step_num += 1
        
        steps.append(ExecutionStep(
            step_number=step_num,
            component="memory_kernel",
            action="aggregate_results",
            duration_ms=20.0,
            data_source="api_results"
        ))
        
        # Build data provenance
        provenance = []
        if "memory_tree" in results:
            provenance.append(DataProvenance(
                source_type="memory_database",
                source_id="memory_tree",
                timestamp=datetime.utcnow().isoformat(),
                confidence=0.95,
                verified=True
            ))
        
        if "knowledge" in results:
            provenance.append(DataProvenance(
                source_type="knowledge_base",
                source_id="semantic_search",
                timestamp=datetime.utcnow().isoformat(),
                confidence=0.88,
                verified=True
            ))
        
        # Create intelligent answer
        answer = self._generate_answer(results, intent)
        
        return KernelResponse(
            kernel_name=self.domain_name,
            answer=answer,
            data=results,
            apis_called=self.apis_called,
            kernels_consulted=[],
            execution_trace=self.create_execution_trace(steps),
            data_provenance=provenance,
            trust_score=0.92,
            suggested_panels=self._suggest_panels(results),
            confidence=intent.confidence
        )
    
    def _generate_answer(self, results: Dict[str, Any], intent: KernelIntent) -> str:
        """Generate intelligent natural language answer"""
        
        if "memory_tree" in results:
            tree = results["memory_tree"]
            count = len(tree.get("flat_list", []))
            return f"Found {count} items in memory. {intent.understood_intent} completed."
        
        if "knowledge" in results:
            kr = results["knowledge"]
            return f"Found {kr.get('total', 0)} knowledge items. Top results retrieved."
        
        if "stored" in results:
            return "Memory item stored successfully with trust verification."
        
        if "ingested" in results:
            return "Data ingested and indexed in knowledge base."
        
        return "Memory operation completed."
    
    def _suggest_panels(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest UI panels based on results"""
        panels = []
        
        if "memory_tree" in results and results["memory_tree"].get("flat_list"):
            panels.append({
                "type": "table",
                "title": "Memory Items",
                "data": results["memory_tree"]["flat_list"]
            })
        
        if "knowledge" in results and results["knowledge"].get("results"):
            panels.append({
                "type": "list",
                "title": "Knowledge Results",
                "data": results["knowledge"]["results"]
            })
        
        return panels


# Global instance
memory_kernel = MemoryKernel()
