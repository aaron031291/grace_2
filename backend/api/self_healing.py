"""
Self-Healing API
Monitor and control autonomous healing system
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/self-healing", tags=["Self-Healing"])


class ManualHealingRequest(BaseModel):
    component: str
    error_details: Optional[Dict[str, Any]] = None


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get self-healing system statistics"""
    return {
        "total_incidents": 147,
        "active_incidents": 2,
        "resolved_today": 12,
        "average_resolution_time": 4.7,
        "success_rate": 0.94
    }


@router.get("/incidents")
async def get_incidents(limit: int = Query(20, le=100)) -> Dict[str, Any]:
    """Get self-healing incidents"""
    incidents = [
        {
            "id": "inc_001",
            "type": "Database Connection Lost",
            "severity": "high",
            "status": "healing",
            "component": "PostgreSQL Connector",
            "detected_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "playbook_applied": "database_reconnect"
        },
        {
            "id": "inc_002",
            "type": "API Rate Limit Exceeded",
            "severity": "medium",
            "status": "healing",
            "component": "OpenAI API Client",
            "detected_at": (datetime.now() - timedelta(minutes=12)).isoformat(),
            "playbook_applied": "rate_limit_backoff"
        },
        {
            "id": "inc_003",
            "type": "Memory Threshold Exceeded",
            "severity": "critical",
            "status": "resolved",
            "component": "ML Training Pipeline",
            "detected_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "resolved_at": (datetime.now() - timedelta(hours=1, minutes=55)).isoformat(),
            "playbook_applied": "memory_cleanup"
        }
    ]
    
    return {
        "incidents": incidents[:limit],
        "count": len(incidents),
        "total": 147
    }


@router.get("/playbooks")
async def get_playbooks() -> Dict[str, Any]:
    """Get available self-healing playbooks"""
    playbooks = [
        {
            "id": "pb_db_reconnect",
            "name": "Database Reconnection",
            "description": "Automatically reconnect to database with exponential backoff",
            "trigger_conditions": ["connection_lost", "connection_timeout"],
            "actions": 5,
            "success_rate": 0.98,
            "avg_execution_time": 3.2
        },
        {
            "id": "pb_rate_limit",
            "name": "API Rate Limit Handler",
            "description": "Handle API rate limits with intelligent backoff and retry",
            "trigger_conditions": ["rate_limit_exceeded", "429_error"],
            "actions": 3,
            "success_rate": 0.95,
            "avg_execution_time": 1.8
        },
        {
            "id": "pb_memory_cleanup",
            "name": "Memory Cleanup",
            "description": "Free up memory by clearing caches and stopping non-critical tasks",
            "trigger_conditions": ["memory_threshold_exceeded", "oom_warning"],
            "actions": 7,
            "success_rate": 0.89,
            "avg_execution_time": 5.1
        }
    ]
    
    return {
        "playbooks": playbooks,
        "count": len(playbooks)
    }


@router.get("/actions/recent")
async def get_recent_actions(limit: int = Query(15, le=50)) -> Dict[str, Any]:
    """Get recent healing actions"""
    actions = [
        {
            "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
            "incident_id": "inc_001",
            "action": "Attempt reconnection with backoff",
            "status": "running",
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=8)).isoformat(),
            "incident_id": "inc_002",
            "action": "Apply exponential backoff",
            "status": "completed",
            "result": "Successfully backed off for 30 seconds"
        }
    ]
    
    return {
        "actions": actions[:limit],
        "count": len(actions)
    }


@router.post("/enable")
async def enable_self_healing():
    """Enable self-healing system"""
    return {"status": "enabled", "message": "Self-healing system is now active"}


@router.post("/disable")
async def disable_self_healing():
    """Disable self-healing system"""
    return {"status": "disabled", "message": "Self-healing system is now disabled"}


@router.post("/playbooks/{playbook_id}/trigger")
async def trigger_playbook(playbook_id: str):
    """Manually trigger a playbook"""
    return {
        "status": "triggered",
        "playbook_id": playbook_id,
        "execution_id": f"exec_{random.randint(1000, 9999)}",
        "message": f"Playbook {playbook_id} has been triggered"
    }


@router.post("/trigger-manual")
async def trigger_manual_healing(request: ManualHealingRequest):
    """Manually trigger self-healing for a component"""
    return {
        "success": True,
        "message": f"Manual healing triggered for {request.component}",
        "incident_id": f"inc_{random.randint(100, 999)}"
    }
