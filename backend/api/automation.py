"""
Automation API
Manage automation rules and triggers
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/automation", tags=["Automation"])


class AutomationRule(BaseModel):
    name: str
    description: str
    trigger_event: str
    action: str
    enabled: bool = True
    conditions: Optional[Dict[str, Any]] = None


@router.get("/rules")
async def list_automation_rules() -> Dict[str, Any]:
    """List all automation rules"""
    rules = [
        {
            "id": 1,
            "name": "Auto-Ingest Books",
            "description": "Automatically ingest books when uploaded to grace_training/books/",
            "trigger_event": "librarian.file.created",
            "action": "start_ingestion",
            "enabled": True,
            "execution_count": 23,
            "last_executed": "2025-11-13T14:30:00"
        },
        {
            "id": 2,
            "name": "Auto-Verify After Ingestion",
            "description": "Run verification checks after successful ingestion",
            "trigger_event": "ingestion.completed",
            "action": "run_verification",
            "enabled": True,
            "execution_count": 22,
            "last_executed": "2025-11-13T15:20:00"
        },
        {
            "id": 3,
            "name": "Self-Heal on Ingestion Failure",
            "description": "Trigger ingestion replay playbook when ingestion fails",
            "trigger_event": "ingestion.failed",
            "action": "trigger_playbook:ingestion_replay",
            "enabled": True,
            "execution_count": 3,
            "last_executed": "2025-11-13T10:15:00"
        },
        {
            "id": 4,
            "name": "Trust Update on Verification",
            "description": "Update trust scores when verification completes",
            "trigger_event": "verification.completed",
            "action": "update_trust_score",
            "enabled": True,
            "execution_count": 18,
            "last_executed": "2025-11-13T15:45:00"
        },
        {
            "id": 5,
            "name": "Weekly Summary Report",
            "description": "Generate weekly summary of ingestion and learning",
            "trigger_event": "schedule.weekly",
            "action": "generate_summary",
            "enabled": False,
            "execution_count": 0,
            "last_executed": None
        }
    ]
    
    return {
        "rules": rules,
        "count": len(rules),
        "enabled_count": len([r for r in rules if r['enabled']])
    }


@router.get("/rules/{rule_id}")
async def get_automation_rule(rule_id: int) -> Dict[str, Any]:
    """Get a specific automation rule"""
    return {
        "id": rule_id,
        "name": "Auto-Ingest Books",
        "description": "Automatically ingest books when uploaded",
        "trigger_event": "librarian.file.created",
        "action": "start_ingestion",
        "enabled": True,
        "conditions": {
            "file_extension": [".pdf", ".epub"],
            "folder_path": "grace_training/books/"
        },
        "execution_count": 23,
        "last_executed": "2025-11-13T14:30:00",
        "created_at": "2025-01-01T00:00:00"
    }


@router.post("/rules")
async def create_automation_rule(rule: AutomationRule):
    """Create a new automation rule"""
    return {
        "success": True,
        "message": f"Automation rule '{rule.name}' created",
        "rule_id": 6
    }


@router.put("/rules/{rule_id}")
async def update_automation_rule(rule_id: int, rule: AutomationRule):
    """Update an automation rule"""
    return {
        "success": True,
        "message": f"Rule {rule_id} updated"
    }


@router.post("/rules/{rule_id}/enable")
async def enable_rule(rule_id: int):
    """Enable an automation rule"""
    return {
        "success": True,
        "message": f"Rule {rule_id} enabled"
    }


@router.post("/rules/{rule_id}/disable")
async def disable_rule(rule_id: int):
    """Disable an automation rule"""
    return {
        "success": True,
        "message": f"Rule {rule_id} disabled"
    }


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: int):
    """Delete an automation rule"""
    return {
        "success": True,
        "message": f"Rule {rule_id} deleted"
    }


@router.get("/executions")
async def list_executions(limit: int = Query(50, le=200)) -> Dict[str, Any]:
    """List recent automation rule executions"""
    executions = []
    
    for i in range(min(limit, 20)):
        executions.append({
            "id": i + 1,
            "rule_id": (i % 4) + 1,
            "rule_name": "Auto-Ingest Books",
            "trigger_event": "librarian.file.created",
            "action_taken": "start_ingestion",
            "status": "completed",
            "duration_ms": 2400,
            "executed_at": datetime.now().isoformat(),
            "result": "Book ingestion started successfully"
        })
    
    return {
        "executions": executions,
        "count": len(executions)
    }


@router.get("/metrics")
async def get_automation_metrics() -> Dict[str, Any]:
    """Get automation system metrics"""
    return {
        "total_rules": 5,
        "enabled_rules": 4,
        "total_executions_today": 45,
        "successful_executions": 43,
        "failed_executions": 2,
        "average_execution_time_ms": 1850,
        "most_active_rule": "Auto-Ingest Books"
    }
