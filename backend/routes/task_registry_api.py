"""
Task Registry API
Unified endpoint for querying task status across all subsystems
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/task-registry", tags=["task-registry"])


class TaskRegistration(BaseModel):
    task_id: str
    task_type: str
    subsystem: str
    title: str
    created_by: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: int = 5
    verification_required: bool = True
    sla_hours: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskCompletion(BaseModel):
    task_id: str
    success: bool = True
    verification_passed: bool = True
    resource_usage: Optional[Dict[str, float]] = None
    ml_metrics: Optional[Dict[str, Any]] = None
    result_metadata: Optional[Dict[str, Any]] = None


@router.post("/register")
async def register_task(req: TaskRegistration):
    """
    Register a new task in the unified registry
    
    Any subsystem can register tasks:
    - Self-healing playbooks
    - Coding agent work orders
    - Learning missions
    - ML/DL training jobs
    - RAG index builds
    """
    from backend.services.task_registry import task_registry
    
    success = await task_registry.register_task(
        task_id=req.task_id,
        task_type=req.task_type,
        subsystem=req.subsystem,
        title=req.title,
        created_by=req.created_by,
        description=req.description,
        assigned_to=req.assigned_to,
        priority=req.priority,
        verification_required=req.verification_required,
        sla_hours=req.sla_hours,
        metadata=req.metadata
    )
    
    if success:
        return {"registered": True, "task_id": req.task_id}
    else:
        raise HTTPException(status_code=409, detail="Task already exists")


@router.post("/start/{task_id}")
async def start_task(task_id: str, metadata: Optional[Dict[str, Any]] = None):
    """Mark task as started and begin resource tracking"""
    from backend.services.task_registry import task_registry
    
    success = await task_registry.start_task(task_id, metadata)
    
    if success:
        return {"started": True, "task_id": task_id}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/complete")
async def complete_task(req: TaskCompletion):
    """
    Mark task as completed with verification and resource metrics
    
    Required:
    - task_id: Task to complete
    - success: Whether task succeeded
    - verification_passed: Whether verification checks passed
    
    Optional:
    - resource_usage: {cpu_seconds, memory_peak_mb, disk_read_mb, etc.}
    - ml_metrics: {dataset_size_mb, vectors_processed, tokens_processed, etc.}
    - result_metadata: Additional result data
    """
    from backend.services.task_registry import task_registry
    
    success = await task_registry.complete_task(
        task_id=req.task_id,
        success=req.success,
        verification_passed=req.verification_passed,
        resource_usage=req.resource_usage,
        ml_metrics=req.ml_metrics,
        result_metadata=req.result_metadata
    )
    
    if success:
        return {"completed": True, "task_id": req.task_id}
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    """Get detailed status of a specific task"""
    from backend.services.task_registry import task_registry
    
    task = await task_registry.get_task_status(task_id)
    
    if task:
        return task
    else:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/tasks")
async def query_tasks(
    subsystem: Optional[str] = None,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    created_by: Optional[str] = None,
    limit: int = 100
):
    """
    Query tasks with filters
    
    Examples:
    - /api/task-registry/tasks?subsystem=healing&status=active
    - /api/task-registry/tasks?task_type=playbook&status=completed
    - /api/task-registry/tasks?created_by=guardian&limit=50
    """
    from backend.services.task_registry import task_registry
    
    tasks = await task_registry.query_tasks(
        subsystem=subsystem,
        status=status,
        task_type=task_type,
        created_by=created_by,
        limit=limit
    )
    
    return {
        "tasks": tasks,
        "count": len(tasks),
        "filters": {
            "subsystem": subsystem,
            "status": status,
            "task_type": task_type,
            "created_by": created_by
        }
    }


@router.get("/subsystems")
async def list_subsystems():
    """List all subsystems with their current task counts"""
    from backend.services.task_registry import task_registry
    from backend.models.base_models import async_session
    from backend.models.task_registry_models import TaskRegistryEntry
    from sqlalchemy import select, func
    
    try:
        async with async_session() as session:
            result = await session.execute(
                select(
                    TaskRegistryEntry.subsystem,
                    TaskRegistryEntry.status,
                    func.count(TaskRegistryEntry.id)
                )
                .group_by(TaskRegistryEntry.subsystem, TaskRegistryEntry.status)
            )
            
            rows = result.all()
            
            # Organize by subsystem
            subsystems = {}
            for subsystem, status, count in rows:
                if subsystem not in subsystems:
                    subsystems[subsystem] = {
                        'subsystem': subsystem,
                        'total': 0,
                        'by_status': {}
                    }
                subsystems[subsystem]['by_status'][status] = count
                subsystems[subsystem]['total'] += count
            
            return {
                "subsystems": list(subsystems.values()),
                "count": len(subsystems)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subsystem/{subsystem}")
async def get_subsystem_status(subsystem: str):
    """
    Get detailed status for a specific subsystem
    
    Shows:
    - Open tasks (pending, active)
    - Historical metrics (avg duration, success rate)
    - Resource usage patterns
    """
    from backend.services.task_registry import task_registry
    
    status = await task_registry.get_subsystem_status(subsystem)
    
    return status


@router.get("/forecast")
async def forecast_task(subsystem: str, task_type: str):
    """
    Forecast duration and resource usage for a task type
    
    Based on historical data, provides:
    - Expected duration (avg, min, max, p95)
    - Resource forecasts
    - Confidence level
    
    Example:
    /api/task-registry/forecast?subsystem=healing&task_type=playbook
    """
    from backend.services.task_registry import task_registry
    
    forecast = await task_registry.forecast_task_duration(subsystem, task_type)
    
    if forecast:
        return {
            "subsystem": subsystem,
            "task_type": task_type,
            "forecast": forecast
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No historical data for {subsystem}/{task_type}"
        )


@router.get("/metrics/anomalies")
async def detect_anomalies(subsystem: Optional[str] = None):
    """
    Detect tasks that took abnormally long or used excessive resources
    
    Compares recent tasks against historical baselines
    """
    from backend.services.task_registry import task_registry
    from backend.models.base_models import async_session
    from backend.models.task_registry_models import TaskRegistryEntry, SubsystemTaskMetrics
    from sqlalchemy import select, and_
    
    try:
        anomalies = []
        
        async with async_session() as session:
            # Get recent completed tasks (last 24 hours)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            
            query = select(TaskRegistryEntry).where(
                and_(
                    TaskRegistryEntry.status.in_(['completed', 'failed']),
                    TaskRegistryEntry.completed_at >= cutoff,
                    TaskRegistryEntry.duration_seconds.isnot(None)
                )
            )
            
            if subsystem:
                query = query.where(TaskRegistryEntry.subsystem == subsystem)
            
            result = await session.execute(query)
            recent_tasks = result.scalars().all()
            
            # Check each task against its baseline
            for task in recent_tasks:
                metrics_result = await session.execute(
                    select(SubsystemTaskMetrics)
                    .where(and_(
                        SubsystemTaskMetrics.subsystem == task.subsystem,
                        SubsystemTaskMetrics.task_type == task.task_type
                    ))
                )
                metrics = metrics_result.scalar_one_or_none()
                
                if metrics and metrics.anomaly_threshold_duration:
                    if task.duration_seconds > metrics.anomaly_threshold_duration:
                        anomalies.append({
                            'task_id': task.task_id,
                            'subsystem': task.subsystem,
                            'task_type': task.task_type,
                            'title': task.title,
                            'duration_seconds': task.duration_seconds,
                            'expected_max_seconds': metrics.anomaly_threshold_duration,
                            'anomaly_type': 'duration',
                            'severity': 'high' if task.duration_seconds > metrics.anomaly_threshold_duration * 2 else 'medium',
                            'completed_at': task.completed_at.isoformat()
                        })
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "subsystem_filter": subsystem,
            "window": "24h"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_registry_stats():
    """Get overall registry statistics"""
    from backend.services.task_registry import task_registry
    from backend.models.base_models import async_session
    from backend.models.task_registry_models import TaskRegistryEntry
    from sqlalchemy import select, func
    
    try:
        async with async_session() as session:
            # Count by status
            result = await session.execute(
                select(
                    TaskRegistryEntry.status,
                    func.count(TaskRegistryEntry.id)
                )
                .group_by(TaskRegistryEntry.status)
            )
            status_counts = {row[0]: row[1] for row in result}
            
            # Total tasks
            total_result = await session.execute(
                select(func.count(TaskRegistryEntry.id))
            )
            total = total_result.scalar()
            
            return {
                **task_registry.get_stats(),
                'total_tasks': total,
                'by_status': status_counts,
                'active_count': status_counts.get('active', 0),
                'pending_count': status_counts.get('pending', 0),
                'completed_count': status_counts.get('completed', 0),
                'failed_count': status_counts.get('failed', 0)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for task registry"""
    from backend.services.task_registry import task_registry
    
    return {
        "status": "healthy" if task_registry.running else "stopped",
        "service": "task_registry",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
