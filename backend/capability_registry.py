"""
Capability Registry - Safe Actions for LLM Tool Use

Defines every capability Grace can perform:
- Authentication
- Task management
- Knowledge operations
- Code editing
- Security checks
- Governance actions
- Verification queries

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
        self._register_builtin_handlers()
    
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
        """
        Export capabilities as LLM tool definitions.
        Compatible with OpenAI function calling format.
        """
        
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
        
        # ============= Authentication =============
        
        self.register_capability(
            intent_type="auth.login",
            description="Authenticate user and obtain access token",
            parameters_schema={
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["username", "password"]
            },
            steps=[{"action": "auth.login", "tier": "tier_1"}],
            tier="tier_1",
            requires_approval=False
        )
        
        # ============= Task Management =============
        
        self.register_capability(
            intent_type="task.list",
            description="List user tasks with optional filtering",
            parameters_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "in-progress", "completed"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
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
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["title"]
            },
            steps=[{"action": "task.create", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # ============= Knowledge Operations =============
        
        self.register_capability(
            intent_type="knowledge.search",
            description="Search knowledge base for information",
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
        
        self.register_capability(
            intent_type="knowledge.ingest",
            description="Ingest new knowledge into the system",
            parameters_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "source": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["content"]
            },
            steps=[{"action": "knowledge.ingest", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # ============= Code Operations =============
        
        self.register_capability(
            intent_type="code.edit",
            description="Edit code files with verification",
            parameters_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "changes": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["file_path", "changes"]
            },
            steps=[{"action": "code.edit", "tier": "tier_2", "timeout": 60}],
            tier="tier_2",
            requires_approval=True,
            risk_level="medium"
        )
        
        self.register_capability(
            intent_type="code.review",
            description="Review code changes and run tests",
            parameters_schema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "run_tests": {"type": "boolean", "default": True}
                }
            },
            steps=[
                {"action": "code.review", "tier": "tier_1"},
                {"action": "code.test", "tier": "tier_1"}
            ],
            tier="tier_1"
        )
        
        # ============= Security/Hunter =============
        
        self.register_capability(
            intent_type="hunter.check",
            description="Check for security threats and alerts",
            parameters_schema={
                "type": "object",
                "properties": {
                    "scope": {"type": "string", "enum": ["recent", "all", "critical"]},
                    "alert_type": {"type": "string"}
                }
            },
            steps=[{"action": "hunter.scan", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # ============= Governance =============
        
        self.register_capability(
            intent_type="governance.review",
            description="Review pending governance approvals",
            parameters_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected"]}
                }
            },
            steps=[{"action": "governance.list_approvals", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        self.register_capability(
            intent_type="governance.approve",
            description="Approve or reject a governance action",
            parameters_schema={
                "type": "object",
                "properties": {
                    "approval_id": {"type": "string"},
                    "approved": {"type": "boolean"},
                    "reason": {"type": "string"}
                },
                "required": ["approval_id", "approved"]
            },
            steps=[{"action": "governance.approve", "tier": "tier_2"}],
            tier="tier_2",
            requires_approval=False  # This IS the approval action
        )
        
        # ============= Verification =============
        
        self.register_capability(
            intent_type="verification.status",
            description="Check verification system status",
            parameters_schema={
                "type": "object",
                "properties": {
                    "include_contracts": {"type": "boolean", "default": False},
                    "include_snapshots": {"type": "boolean", "default": False}
                }
            },
            steps=[{"action": "verification.status", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # ============= Chat/Conversation =============
        
        self.register_capability(
            intent_type="chat.respond",
            description="General conversational response",
            parameters_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "context": {"type": "object"}
                },
                "required": ["message"]
            },
            steps=[{"action": "chat.respond", "tier": "tier_1"}],
            tier="tier_1"
        )
        
        # ============= System Operations =============
        
        self.register_capability(
            intent_type="system.restart",
            description="Restart system service",
            parameters_schema={
                "type": "object",
                "properties": {
                    "service": {"type": "string"},
                    "graceful": {"type": "boolean", "default": True}
                }
            },
            steps=[{"action": "restart_service", "tier": "tier_2", "timeout": 90}],
            tier="tier_2",
            requires_approval=True,
            risk_level="medium"
        )
        
        self.register_capability(
            intent_type="system.benchmark",
            description="Run system benchmarks",
            parameters_schema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["smoke", "regression", "full"]}
                }
            },
            steps=[{"action": "benchmark.run", "tier": "tier_1"}],
            tier="tier_1"
        )


# Singleton
capability_registry = CapabilityRegistry()
 
