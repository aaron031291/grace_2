"""
Book Automation Rules - Automated workflows for book ingestion
Handles: auto-detection, pipeline triggering, monitoring
"""

from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json

from backend.clarity import BaseComponent, ComponentStatus, Event, get_event_bus
from backend.core.unified_event_publisher import publish_event_obj
from backend.database import get_db


class BookAutomationRules(BaseComponent):
    """
    Automation rules specific to book ingestion workflow
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "book_automation_rules"
        self.event_bus = get_event_bus()
        self.rules = []
        
        # Register default rules
        self._register_default_rules()
        
    async def activate(self) -> bool:
        """Activate automation rules"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        # Subscribe to events
        await self.event_bus.subscribe("file.created", self._handle_file_created)
        await self.event_bus.subscribe("book.ingestion.completed", self._handle_ingestion_completed)
        await self.event_bus.subscribe("verification.book.completed", self._handle_verification_completed)
        
        return True
    
    def _register_default_rules(self):
        """Register built-in automation rules"""
        
        # Rule 1: Auto-trigger book pipeline for PDFs/EPUBs in books folder
        self.rules.append({
            "id": "auto_book_ingestion",
            "name": "Auto-trigger book ingestion",
            "trigger": "file.created",
            "conditions": [
                {"field": "path", "contains": "books"},
                {"field": "file_type", "in": [".pdf", ".epub"]}
            ],
            "actions": [
                {"type": "trigger_pipeline", "pipeline": "book_ingestion"},
                {"type": "notify", "message": "New book detected, starting ingestion"}
            ],
            "enabled": True
        })
        
        # Rule 2: Auto-verify after ingestion
        self.rules.append({
            "id": "auto_verify_books",
            "name": "Auto-verify ingested books",
            "trigger": "book.ingestion.completed",
            "conditions": [
                {"field": "status", "equals": "completed"}
            ],
            "actions": [
                {"type": "trigger_verification", "verification_type": "book_comprehensive"},
                {"type": "log", "message": "Book ingestion complete, starting verification"}
            ],
            "enabled": True
        })
        
        # Rule 3: Update dashboard after verification
        self.rules.append({
            "id": "update_dashboard_on_verify",
            "name": "Update dashboard after verification",
            "trigger": "verification.book.completed",
            "conditions": [],
            "actions": [
                {"type": "update_dashboard"},
                {"type": "send_notification", "level": "info"}
            ],
            "enabled": True
        })
        
        # Rule 4: Flag low trust scores
        self.rules.append({
            "id": "flag_low_trust",
            "name": "Flag books with low trust scores",
            "trigger": "verification.book.completed",
            "conditions": [
                {"field": "trust_score", "less_than": 0.7}
            ],
            "actions": [
                {"type": "create_review_task"},
                {"type": "send_notification", "level": "warning", "message": "Book requires manual review"}
            ],
            "enabled": True
        })
        
        # Rule 5: Extract metadata sidecars
        self.rules.append({
            "id": "check_metadata_sidecar",
            "name": "Check for metadata sidecar files",
            "trigger": "file.created",
            "conditions": [
                {"field": "path", "contains": "books"},
                {"field": "file_type", "in": [".pdf", ".epub"]}
            ],
            "actions": [
                {"type": "check_sidecar"},
                {"type": "merge_metadata"}
            ],
            "enabled": True
        })
    
    async def _handle_file_created(self, event: Event):
        """Handle file creation events"""
        
        # Find matching rules
        matching_rules = self._find_matching_rules("file.created", event.payload)
        
        for rule in matching_rules:
            await self._execute_rule(rule, event)
    
    async def _handle_ingestion_completed(self, event: Event):
        """Handle ingestion completion events"""
        
        matching_rules = self._find_matching_rules("book.ingestion.completed", event.payload)
        
        for rule in matching_rules:
            await self._execute_rule(rule, event)
    
    async def _handle_verification_completed(self, event: Event):
        """Handle verification completion events"""
        
        matching_rules = self._find_matching_rules("verification.book.completed", event.payload)
        
        for rule in matching_rules:
            await self._execute_rule(rule, event)
    
    def _find_matching_rules(self, trigger: str, payload: Dict) -> List[Dict]:
        """Find rules that match the event"""
        
        matching = []
        
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            
            if rule["trigger"] != trigger:
                continue
            
            # Check conditions
            conditions_met = True
            for condition in rule.get("conditions", []):
                if not self._check_condition(condition, payload):
                    conditions_met = False
                    break
            
            if conditions_met:
                matching.append(rule)
        
        return matching
    
    def _check_condition(self, condition: Dict, payload: Dict) -> bool:
        """Check if a condition is met"""
        
        field = condition.get("field")
        value = payload.get(field)
        
        if "equals" in condition:
            return value == condition["equals"]
        
        if "contains" in condition:
            return condition["contains"] in str(value)
        
        if "in" in condition:
            return value in condition["in"]
        
        if "less_than" in condition:
            return float(value) < condition["less_than"]
        
        if "greater_than" in condition:
            return float(value) > condition["greater_than"]
        
        return True
    
    async def _execute_rule(self, rule: Dict, event: Event):
        """Execute a rule's actions"""
        
        for action in rule.get("actions", []):
            await self._execute_action(action, event, rule)
    
    async def _execute_action(self, action: Dict, event: Event, rule: Dict):
        """Execute a single action"""
        
        action_type = action.get("type")
        
        if action_type == "trigger_pipeline":
            await self._trigger_pipeline(action, event)
        
        elif action_type == "trigger_verification":
            await self._trigger_verification(action, event)
        
        elif action_type == "log":
            await self._log_action(action, event, rule)
        
        elif action_type == "notify":
            await self._send_notification(action, event, rule)
        
        elif action_type == "update_dashboard":
            await self._update_dashboard(event)
        
        elif action_type == "create_review_task":
            await self._create_review_task(event)
        
        elif action_type == "check_sidecar":
            await self._check_metadata_sidecar(event)
    
    async def _trigger_pipeline(self, action: Dict, event: Event):
        """Trigger an ingestion pipeline"""
        
        await publish_event_obj(Event(
            event_type="pipeline.trigger.requested",
            source=self.component_id,
            payload={
                "pipeline": action.get("pipeline"),
                "file_path": event.payload.get("path"),
                "priority": "high",
                "triggered_by": "automation_rule"
            }
        ))
    
    async def _trigger_verification(self, action: Dict, event: Event):
        """Trigger verification"""
        
        await publish_event_obj(Event(
            event_type="verification.trigger.requested",
            source=self.component_id,
            payload={
                "document_id": event.payload.get("document_id"),
                "verification_type": action.get("verification_type"),
                "triggered_by": "automation_rule"
            }
        ))
    
    async def _log_action(self, action: Dict, event: Event, rule: Dict):
        """Log an action"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_librarian_log
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                "automation_rule_executed",
                rule.get("id"),
                json.dumps({
                    "rule": rule["name"],
                    "action": action,
                    "event": event.payload
                })
            )
        )
        
        await db.commit()
    
    async def _send_notification(self, action: Dict, event: Event, rule: Dict):
        """Send a notification"""
        
        await publish_event_obj(Event(
            event_type="notification.send",
            source=self.component_id,
            payload={
                "level": action.get("level", "info"),
                "message": action.get("message", f"Rule triggered: {rule['name']}"),
                "context": event.payload
            }
        ))
    
    async def _update_dashboard(self, event: Event):
        """Update dashboard metrics"""
        
        await publish_event_obj(Event(
            event_type="dashboard.update.requested",
            source=self.component_id,
            payload={
                "metric": "book_verification_completed",
                "value": event.payload
            }
        ))
    
    async def _create_review_task(self, event: Event):
        """Create a manual review task"""
        
        await publish_event_obj(Event(
            event_type="review.task.created",
            source=self.component_id,
            payload={
                "document_id": event.payload.get("document_id"),
                "reason": "Low trust score after verification",
                "priority": "medium"
            }
        ))
    
    async def _check_metadata_sidecar(self, event: Event):
        """Check for metadata sidecar file"""
        
        file_path = Path(event.payload.get("path"))
        sidecar_path = file_path.with_suffix('.meta.json')
        
        if sidecar_path.exists():
            await publish_event_obj(Event(
                event_type="metadata.sidecar.found",
                source=self.component_id,
                payload={
                    "file_path": str(file_path),
                    "sidecar_path": str(sidecar_path)
                }
            ))


# Singleton instance
_automation_rules = None

def get_book_automation_rules() -> BookAutomationRules:
    global _automation_rules
    if _automation_rules is None:
        _automation_rules = BookAutomationRules()
    return _automation_rules
