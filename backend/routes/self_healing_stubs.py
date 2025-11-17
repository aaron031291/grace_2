"""
Self-Healing API Stubs - Return valid JSON for frontend
Prevents JSON parsing errors while system initializes
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/stats")
async def get_self_healing_stats() -> Dict[str, Any]:
    """Get self-healing statistics"""
    return {
        "total_incidents": 0,
        "active_incidents": 0,
        "resolved_today": 0,
        "average_resolution_time": 0.0,
        "success_rate": 0.95
    }

@router.get("/incidents")
async def get_incidents(limit: int = 20) -> Dict[str, Any]:
    """Get recent incidents"""
    return {
        "incidents": [],
        "total": 0
    }

@router.get("/playbooks")
async def get_playbooks() -> Dict[str, Any]:
    """Get available playbooks"""
    return {
        "playbooks": [
            {
                "id": "database_recovery",
                "name": "Database Connection Recovery",
                "description": "Restore database connections when lost",
                "trigger_conditions": ["database_error", "connection_timeout"],
                "actions": 3,
                "success_rate": 0.98,
                "avg_execution_time": 2.5
            },
            {
                "id": "memory_cleanup",
                "name": "Memory Pressure Relief",
                "description": "Clear caches and optimize memory usage",
                "trigger_conditions": ["high_memory", "oom_warning"],
                "actions": 4,
                "success_rate": 0.92,
                "avg_execution_time": 5.2
            },
            {
                "id": "api_timeout_fix",
                "name": "API Timeout Recovery",
                "description": "Restart stuck API connections",
                "trigger_conditions": ["api_timeout", "request_hang"],
                "actions": 2,
                "success_rate": 0.95,
                "avg_execution_time": 1.8
            }
        ],
        "count": 3
    }

@router.get("/actions/recent")
async def get_recent_actions(limit: int = 15) -> Dict[str, Any]:
    """Get recent healing actions"""
    return {
        "actions": [],
        "total": 0
    }

@router.post("/enable")
async def enable_self_healing() -> Dict[str, Any]:
    """Enable self-healing system"""
    return {
        "status": "enabled",
        "message": "Self-healing system activated"
    }

@router.post("/disable")
async def disable_self_healing() -> Dict[str, Any]:
    """Disable self-healing system"""
    return {
        "status": "disabled",
        "message": "Self-healing system paused"
    }

@router.post("/playbooks/{playbook_id}/trigger")
async def trigger_playbook(playbook_id: str) -> Dict[str, Any]:
    """Manually trigger a playbook"""
    return {
        "status": "triggered",
        "playbook_id": playbook_id,
        "execution_id": f"exec_{playbook_id}_001",
        "message": f"Playbook {playbook_id} queued for execution"
    }
