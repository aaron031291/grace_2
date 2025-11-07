"""
Capability Registry - Safe Actions for LLM Tool Use

Defines every capability Grace can perform.
This manifest feeds into LLM prompts as available tools.
LLM can only request actions in this registry.
"""

from typing import Dict, Any, Callable, Optional, List


class CapabilityRegistry:
    """
    Central registry of all Grace capabilities.
    Used by both CLI and LLM tool orchestration.
    """
    
    def __init__(self):
        self.capabilities: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
        self._register_builtin_capabilities()
        self._load_handlers()
    
    def _load_handlers(self):
        """Load handlers from capability_handlers module"""
        try:
            from . import capability_handlers
            
            self.handlers["task.list"] = capability_handlers.handle_task_list
            self.handlers["task.create"] = capability_handlers.handle_task_create
            self.handlers["knowledge.search"] = capability_handlers.handle_knowledge_search
            self.handlers["chat.respond"] = capability_handlers.handle_chat_respond
            self.handlers["verification.status"] = capability_handlers.handle_verification_status
            self.handlers["benchmark.run"] = capability_handlers.handle_benchmark_run
        except ImportError:
            pass  # Handlers optional
    
    def register_capability(
        self,
        intent_type: str,
        description: str,
        parameters_schema: Dict[str, Any],
        steps: List[Dict[str, Any]],
        handler: Optional[Callable] = None,
        requires_approval: bool = False,
        tier: str = "tier_1",
        risk_level: str = "low",
        estimated_duration: float = 1.0
    ):
        """Register a capability"""
        
        self.capabilities[intent_type] = {
            "intent_type": intent_type,
            "description": description,
            "parameters_schema": parameters_schema,
            "steps": steps,
            "requires_approval": requires_approval,
            "tier": tier,
            "risk_level": risk_level,
            "estimated_duration": estimated_duration
        }
        
        if handler:
            self.handlers[intent_type] = handler
    
    def get_capability(self, intent_type: str) -> Optional[Dict[str, Any]]:
        """Get capability definition"""
        return self.capabilities.get(intent_type)
    
    def get_handler(self, intent_type: str) -> Optional[Callable]:
        """Get handler function for capability"""
        return self.handlers.get(intent_type)
    
    def get_all_capabilities(self) -> List[Dict[str, Any]]:
        """Get all registered capabilities (for LLM tool manifest)"""
        return list(self.capabilities.values())
    
    def to_llm_tools(self) -> List[Dict[str, Any]]:
        """Export capabilities as LLM tool definitions"""
        tools = []
        for cap in self.capabilities.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": cap["intent_type"].replace(".", "_"),
                    "description": cap["description"],
                    "parameters": cap["parameters_schema"]
                }
            })
        return tools
    
    def _register_builtin_capabilities(self):
        """Register all built-in Grace capabilities"""
        
        # Task Management
        self.register_capability(
            intent_type="task.list",
            description="List user tasks with optional filtering",
            parameters_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "in-progress", "completed"]}
                }
            },
            steps=[{"action": "task.list", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        self.register_capability(
            intent_type="task.create",
            description="Create a new task",
            parameters_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            },
            steps=[{"action": "task.create", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # Knowledge Operations
        self.register_capability(
            intent_type="knowledge.search",
            description="Search knowledge base",
            parameters_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            },
            steps=[{"action": "knowledge.search", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # Chat
        self.register_capability(
            intent_type="chat.respond",
            description="General conversational response",
            parameters_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            },
            steps=[{"action": "chat.respond", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # System Operations
        self.register_capability(
            intent_type="system.benchmark",
            description="Run system benchmarks",
            parameters_schema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["smoke", "regression"]}
                }
            },
            steps=[{"action": "benchmark.run", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # Verification
        self.register_capability(
            intent_type="verification.status",
            description="Check verification system status",
            parameters_schema={
                "type": "object",
                "properties": {}
            },
            steps=[{"action": "verification.status", "tier": "tier_1"}],
            tier="tier_1"
        )


# Singleton
capability_registry = CapabilityRegistry()
