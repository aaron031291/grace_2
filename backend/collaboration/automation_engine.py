"""
Automation Engine
Trigger-based automation for workflows and tasks
"""
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    FILE_CHANGED = "file_changed"
    WORKFLOW_APPROVED = "workflow_approved"
    SCHEMA_VALIDATED = "schema_validated"
    INGESTION_COMPLETED = "ingestion_completed"
    QUALITY_THRESHOLD = "quality_threshold"
    TIME_BASED = "time_based"
    USER_ACTION = "user_action"


class ActionType(str, Enum):
    SEND_NOTIFICATION = "send_notification"
    CREATE_WORKFLOW = "create_workflow"
    RUN_INGESTION = "run_ingestion"
    TRIGGER_SYNC = "trigger_sync"
    EXECUTE_SCRIPT = "execute_script"
    UPDATE_STATUS = "update_status"


class AutomationRule:
    """Represents an automation rule"""
    
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        trigger_type: TriggerType,
        trigger_conditions: Dict[str, Any],
        actions: List[Dict[str, Any]],
        enabled: bool = True
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.trigger_type = trigger_type
        self.trigger_conditions = trigger_conditions
        self.actions = actions
        self.enabled = enabled
        
        self.created_at = datetime.utcnow()
        self.last_triggered: Optional[datetime] = None
        self.trigger_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type.value,
            "trigger_conditions": self.trigger_conditions,
            "actions": self.actions,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "trigger_count": self.trigger_count
        }


class AutomationEngine:
    """
    Automation engine for Grace.
    Trigger-based workflows, notifications, and tasks.
    """
    
    def __init__(self):
        self.rules: Dict[str, AutomationRule] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self._running = False
        
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self.register_action_handler("send_notification", self._handle_send_notification)
        self.register_action_handler("create_workflow", self._handle_create_workflow)
        self.register_action_handler("run_ingestion", self._handle_run_ingestion)
        self.register_action_handler("update_status", self._handle_update_status)
    
    async def start(self):
        """Start automation engine"""
        self._running = True
        logger.info("🤖 Automation engine started")
    
    async def stop(self):
        """Stop automation engine"""
        self._running = False
        logger.info("🛑 Automation engine stopped")
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register action handler"""
        self.action_handlers[action_type] = handler
        logger.info(f"✅ Registered action handler: {action_type}")
    
    async def create_rule(
        self,
        name: str,
        description: str,
        trigger_type: TriggerType,
        trigger_conditions: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> AutomationRule:
        """Create automation rule"""
        rule_id = str(uuid.uuid4())
        
        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            description=description,
            trigger_type=trigger_type,
            trigger_conditions=trigger_conditions,
            actions=actions
        )
        
        self.rules[rule_id] = rule
        logger.info(f"📋 Created automation rule: {name}")
        
        return rule
    
    async def trigger_event(
        self,
        trigger_type: TriggerType,
        event_data: Dict[str, Any]
    ):
        """Process trigger event and execute matching rules"""
        matching_rules = [
            rule for rule in self.rules.values()
            if rule.enabled and rule.trigger_type == trigger_type
        ]
        
        for rule in matching_rules:
            if await self._check_conditions(rule.trigger_conditions, event_data):
                await self._execute_rule(rule, event_data)
    
    async def _check_conditions(
        self,
        conditions: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if event data matches rule conditions"""
        for key, expected_value in conditions.items():
            if key not in event_data:
                return False
            
            actual_value = event_data[key]
            
            if isinstance(expected_value, dict):
                operator = expected_value.get("operator", "equals")
                value = expected_value.get("value")
                
                if operator == "equals" and actual_value != value:
                    return False
                elif operator == "contains" and value not in str(actual_value):
                    return False
                elif operator == "greater_than" and actual_value <= value:
                    return False
                elif operator == "less_than" and actual_value >= value:
                    return False
            else:
                if actual_value != expected_value:
                    return False
        
        return True
    
    async def _execute_rule(self, rule: AutomationRule, event_data: Dict[str, Any]):
        """Execute automation rule actions"""
        logger.info(f"🚀 Executing rule: {rule.name}")
        
        rule.last_triggered = datetime.utcnow()
        rule.trigger_count += 1
        
        for action in rule.actions:
            action_type = action.get("type")
            action_params = action.get("params", {})
            
            merged_params = {**event_data, **action_params}
            
            handler = self.action_handlers.get(action_type)
            if handler:
                try:
                    await handler(merged_params)
                except Exception as e:
                    logger.error(f"Action handler failed ({action_type}): {e}")
            else:
                logger.warning(f"No handler for action type: {action_type}")
    
    async def _handle_send_notification(self, params: Dict[str, Any]):
        """Handle send notification action"""
        from backend.collaboration.notification_service import notification_service
        
        user_id = params.get("user_id")
        title = params.get("title", "Automation Notification")
        message = params.get("message", "")
        priority = params.get("priority", "normal")
        
        if user_id:
            await notification_service.create_notification(
                user_id=user_id,
                notification_type="automation",
                title=title,
                message=message,
                priority=priority
            )
    
    async def _handle_create_workflow(self, params: Dict[str, Any]):
        """Handle create workflow action"""
        from backend.collaboration.workflow_engine import workflow_engine, WorkflowType
        
        workflow_type = params.get("workflow_type", "schema_approval")
        title = params.get("title", "Automated Workflow")
        description = params.get("description", "")
        reviewers = params.get("reviewers", [])
        
        await workflow_engine.create_workflow(
            workflow_type=WorkflowType(workflow_type),
            title=title,
            description=description,
            created_by="automation_engine",
            reviewers=reviewers
        )
    
    async def _handle_run_ingestion(self, params: Dict[str, Any]):
        """Handle run ingestion action"""
        logger.info(f"🔄 Triggered ingestion: {params}")
    
    async def _handle_update_status(self, params: Dict[str, Any]):
        """Handle update status action"""
        logger.info(f"📊 Status update: {params}")
    
    async def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get rule by ID"""
        rule = self.rules.get(rule_id)
        return rule.to_dict() if rule else None
    
    async def list_rules(self) -> List[Dict[str, Any]]:
        """List all rules"""
        return [rule.to_dict() for rule in self.rules.values()]
    
    async def enable_rule(self, rule_id: str):
        """Enable rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
    
    async def disable_rule(self, rule_id: str):
        """Disable rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
    
    async def delete_rule(self, rule_id: str):
        """Delete rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]


automation_engine = AutomationEngine()
