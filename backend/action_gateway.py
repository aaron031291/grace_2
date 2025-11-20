"""
Action Gateway - Governance enforcement for all agent actions
Every action goes through this gateway with ExecutionTrace and DataProvenance
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from backend.event_bus import event_bus, Event, EventType
from backend.core.unified_event_publisher import publish_event_obj

class GovernanceTier(Enum):
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"

class ActionGateway:
    """
    Unified Action Gateway for Grace's agentic organism
    Enforces governance, logs ExecutionTrace, attaches DataProvenance
    """
    
    def __init__(self):
        self.governance_rules = self._load_default_rules()
        self.action_log = []
        
    def _load_default_rules(self) -> Dict[str, GovernanceTier]:
        """Load default governance rules"""
        return {
            "read_memory": GovernanceTier.AUTONOMOUS,
            "write_memory": GovernanceTier.SUPERVISED,
            "execute_code": GovernanceTier.APPROVAL_REQUIRED,
            "modify_schema": GovernanceTier.APPROVAL_REQUIRED,
            "deploy_service": GovernanceTier.APPROVAL_REQUIRED,
            "delete_data": GovernanceTier.BLOCKED,
            "external_api_call": GovernanceTier.SUPERVISED,
            "self_healing": GovernanceTier.AUTONOMOUS,
            "learning_update": GovernanceTier.AUTONOMOUS,
        }
    
    async def request_action(
        self,
        action_type: str,
        agent: str,
        params: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request action through governance gateway
        Returns: {approved: bool, reason: str, trace_id: str}
        """
        
        trace_id = trace_id or f"trace_{datetime.now().timestamp()}"
        
        governance_tier = self.governance_rules.get(action_type, GovernanceTier.SUPERVISED)
        
        execution_trace = {
            "trace_id": trace_id,
            "action_type": action_type,
            "agent": agent,
            "params": params,
            "governance_tier": governance_tier.value,
            "timestamp": datetime.now().isoformat(),
            "approved": False,
            "reason": ""
        }
        
        if governance_tier == GovernanceTier.BLOCKED:
            execution_trace["approved"] = False
            execution_trace["reason"] = f"Action '{action_type}' is blocked by governance"
            
        elif governance_tier == GovernanceTier.APPROVAL_REQUIRED:
            execution_trace["approved"] = False
            execution_trace["reason"] = f"Action '{action_type}' requires human approval"
            
        elif governance_tier == GovernanceTier.SUPERVISED:
            execution_trace["approved"] = True
            execution_trace["reason"] = f"Action '{action_type}' approved with supervision"
            
        elif governance_tier == GovernanceTier.AUTONOMOUS:
            execution_trace["approved"] = True
            execution_trace["reason"] = f"Action '{action_type}' approved autonomously"
        
        self.action_log.append(execution_trace)
        
        await publish_event_obj(Event(
            event_type=EventType.GOVERNANCE_CHECK,
            source="action_gateway",
            data=execution_trace,
            trace_id=trace_id
        ))
        
        print(f"[ActionGateway] {agent} requested {action_type}: {execution_trace['approved']}")
        
        return execution_trace
    
    async def record_outcome(
        self,
        trace_id: str,
        success: bool,
        result: Any,
        error: Optional[str] = None
    ) -> None:
        """Record action outcome for learning"""
        
        outcome = {
            "trace_id": trace_id,
            "success": success,
            "result": result,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        await publish_event_obj(Event(
            event_type=EventType.LEARNING_OUTCOME,
            source="action_gateway",
            data=outcome,
            trace_id=trace_id
        ))
        
        print(f"[ActionGateway] Recorded outcome for {trace_id}: success={success}")
    
    def get_action_log(self, limit: int = 100) -> list:
        """Get recent action log"""
        return self.action_log[-limit:]
    
    def update_governance_rule(self, action_type: str, tier: GovernanceTier) -> None:
        """Update governance rule for action type"""
        self.governance_rules[action_type] = tier
        print(f"[ActionGateway] Updated rule: {action_type} -> {tier.value}")

action_gateway = ActionGateway()
