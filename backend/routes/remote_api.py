"""
Remote API - Remote cockpit and monitoring endpoints

Provides:
- Remote access to Grace console
- System metrics and telemetry
- Task monitoring
- Log streaming
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.world_model.world_model_service import world_model_service
from backend.services.log_service import log_service
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop

router = APIRouter()


class SystemMetrics(BaseModel):
    """System metrics for remote monitoring"""
    timestamp: str
    health: str
    trust_score: float
    confidence: float
    active_tasks: int
    active_missions: int
    pending_approvals: int
    learning_jobs: int
    incidents: int
    memory_usage_mb: float
    uptime_seconds: float


class TaskInfo(BaseModel):
    """Task information"""
    task_id: str
    status: str
    progress: float
    started_at: str
    updated_at: str
    description: str
    metadata: Dict[str, Any]


@router.get("/remote/status", response_model=SystemMetrics)
async def get_system_status():
    """Get current system status and metrics"""
    
    import psutil
    import time
    
    context = await world_model_service.query_context(limit=10)
    
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    uptime = time.time() - process.create_time()
    
    return SystemMetrics(
        timestamp=datetime.utcnow().isoformat(),
        health=context["system_health"].get("status", "unknown"),
        trust_score=context["system_health"].get("trust_score", 0.0),
        confidence=context["system_health"].get("confidence", 0.0),
        active_tasks=len(context.get("active_missions", [])),
        active_missions=len(context.get("active_missions", [])),
        pending_approvals=len(context.get("pending_approvals", [])),
        learning_jobs=len(context.get("learning_jobs", [])),
        incidents=0,
        memory_usage_mb=memory_mb,
        uptime_seconds=uptime,
    )


@router.get("/remote/tasks", response_model=List[TaskInfo])
async def get_active_tasks():
    """Get all active tasks"""
    context = await world_model_service.query_context()
    missions = context.get("active_missions", [])
    
    tasks = []
    for mission in missions:
        tasks.append(TaskInfo(
            task_id=mission.get("mission_id", "unknown"),
            status=mission.get("status", "unknown"),
            progress=mission.get("progress", 0.0),
            started_at=mission.get("started_at", datetime.utcnow().isoformat()),
            updated_at=mission.get("updated_at", datetime.utcnow().isoformat()),
            description=mission.get("description", ""),
            metadata=mission.get("metadata", {}),
        ))
    
    return tasks


@router.get("/remote/logs")
async def get_recent_logs(
    limit: int = 50,
    log_type: Optional[str] = None,
    severity: Optional[str] = None,
):
    """Get recent logs with filters"""
    logs = log_service.get_recent_logs(
        limit=limit,
        log_type=log_type,
        severity=severity,
    )
    return {"logs": logs}


@router.get("/remote/approvals")
async def get_pending_approvals():
    """Get pending approval requests"""
    context = await world_model_service.query_context()
    return {"approvals": context.get("pending_approvals", [])}


@router.post("/remote/approve/{approval_id}")
async def approve_action(approval_id: str):
    """Approve a pending action"""
    try:
        from backend.governance import governance_core
        result = await governance_core.approve_action(approval_id)
        return {"status": "approved", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remote/reject/{approval_id}")
async def reject_action(approval_id: str, reason: str = "User rejected"):
    """Reject a pending action"""
    try:
        from backend.governance import governance_core
        result = await governance_core.reject_action(approval_id, reason)
        return {"status": "rejected", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remote/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.2.0",
    }
