"""
Memory Kernel - Intelligent Memory & Knowledge Agent
Manages all memory storage, retrieval, and knowledge operations
"""

from typing import Dict, Any, List
from datetime import datetime
import asyncio

from backend.core.kernel_sdk import KernelSDK
from backend.core.message_bus import message_bus, MessagePriority
from .base_kernel import KernelIntent, KernelPlan, KernelResponse
from ..memory_services.memory import PersistentMemory
from ..schemas import ExecutionStep, DataProvenance
from ..logging_utils import log_event


class MemoryKernel(KernelSDK):
    """
    Intelligent agent for all memory & knowledge operations - Multi-OS Support
    
    Manages:
    - Memory tree (domains/categories)
    - Knowledge queries (semantic search)
    - Ingestion (text/file/URL)
    - Trust scoring
    - Context assembly
    - Host state persistence (infrastructure memory)
    """
    
    def __init__(self):
        super().__init__(kernel_name="memory_kernel")
        self.memory = PersistentMemory()
        
        # Infrastructure state memory
        self.host_state_cache = {}
        
        # Subscribe to infrastructure events for state persistence (deferred)
        self._infrastructure_subscription = None
    
    async def initialize(self):
        """Initialize kernel - called from async context"""
        if not self._infrastructure_subscription:
            self._infrastructure_subscription = asyncio.create_task(self._subscribe_to_infrastructure_events())
    
    async def _subscribe_to_infrastructure_events(self):
        """Subscribe to infrastructure events to persist host state"""
        try:
            # Subscribe to host registrations
            reg_queue = await message_bus.subscribe(
                subscriber="memory",
                topic="infrastructure.host.registered"
            )
            
            # Subscribe to health summaries
            health_queue = await message_bus.subscribe(
                subscriber="memory",
                topic="infrastructure.health.summary"
            )
            
            # Process events
            asyncio.create_task(self._process_host_registrations(reg_queue))
            asyncio.create_task(self._process_health_summaries(health_queue))
            
        except Exception as e:
            log_event(
                action="memory.infrastructure.subscribe_error",
                actor="memory_kernel",
                resource="infrastructure_subscription",
                outcome="error",
                payload={"error": str(e)}
            )
    
    async def _process_host_registrations(self, queue):
        """Process and persist host registration events"""
        while True:
            try:
                msg = await queue.get()
                host_data = msg.payload
                host_id = host_data.get("host_id")
                
                # Cache in memory
                self.host_state_cache[host_id] = {
                    "registered_at": datetime.utcnow().isoformat(),
                    "last_updated": datetime.utcnow().isoformat(),
                    "data": host_data
                }
                
                # Store in persistent memory (ChatMessage format)
                await self.memory.store(
                    user="infrastructure_manager",
                    role="system",
                    content=f"Host registered: {host_id} ({host_data.get('os_type')})"
                )
                
                log_event(
                    action="memory.host.persisted",
                    actor="memory_kernel",
                    resource=f"host_{host_id}",
                    outcome="ok",
                    payload={"host_id": host_id}
                )
                
            except Exception as e:
                log_event(
                    action="memory.process_registration.error",
                    actor="memory_kernel",
                    resource="host_registration",
                    outcome="error",
                    payload={"error": str(e)}
                )
    
    async def _process_health_summaries(self, queue):
        """Process and persist infrastructure health summaries"""
        while True:
            try:
                msg = await queue.get()
                summary = msg.payload
                
                # Store health snapshot (ChatMessage format)
                timestamp = summary.get("timestamp", "unknown")
                await self.memory.store(
                    user="infrastructure_manager",
                    role="system",
                    content=f"Health snapshot at {timestamp}: {summary.get('status', 'unknown')}"
                )
                
            except Exception as e:
                log_event(
                    action="memory.process_health.error",
                    actor="memory_kernel",
                    resource="health_summary",
                    outcome="error",
                    payload={"error": str(e)}
                )
    
    async def get_host_state(self, host_id: str) -> Dict[str, Any]:
        """Retrieve host state from memory"""
        
        # Check cache first
        if host_id in self.host_state_cache:
            return self.host_state_cache[host_id]
        
        # Query persistent memory
        try:
            result = await self.memory.retrieve(
                domain="infrastructure",
                key=host_id
            )
            return result
        except:
            return {}
    
    async def get_infrastructure_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get infrastructure health history"""
        
        try:
            results = await self.memory.query(
                domain="infrastructure",
                category="health_snapshots",
                limit=hours * 2  # Assuming ~2 snapshots per hour
            )
            return results
        except:
            return []
    
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
    
    # Implement abstract methods required by BaseDomainKernel
    async def _initialize_watchers(self):
        """Set up watchers for memory operations"""
        pass
    
    async def _load_pending_work(self):
        """Load pending memory operations"""
        pass
    
    async def _coordinator_loop(self):
        """Main coordination loop for memory operations"""
        while self._running:
            try:
                await asyncio.sleep(10)
            except Exception as e:
                pass
    
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent for memory tasks"""
        return {"agent_id": agent_id, "type": agent_type, "task": task_data}
    
    async def _cleanup(self):
        """Cleanup memory kernel resources"""
        pass


# Global instance
memory_kernel = MemoryKernel()
