"""
HTM Dashboard API - Real-Time Task Execution Metrics

Provides:
- Live SLA compliance stats
- Task timing distributions (p50, p95, p99)
- Queue depths and wait times
- Worker utilization
- Violation alerts
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from backend.models.htm_models import HTMTask, HTMTaskAttempt, HTMMetrics
from backend.models.base_models import async_session
from backend.core.htm_sla_enforcer import htm_sla_enforcer
from backend.core.htm_size_metrics import htm_size_metrics
from backend.core.htm_size_tracker import format_bytes
from sqlalchemy import select, func, and_, or_
from collections import defaultdict
import statistics


router = APIRouter(prefix="/api/htm/dashboard", tags=["htm_dashboard"])


class HTMDashboardStats(BaseModel):
    """Real-time HTM dashboard statistics"""
    # Overall metrics
    total_tasks: int
    active_tasks: int
    queued_tasks: int
    completed_tasks: int
    failed_tasks: int
    
    # SLA metrics
    sla_compliance_rate: float
    active_violations: int
    total_violations: int
    avg_buffer_ms: float
    
    # Timing metrics
    avg_queue_time_ms: float
    avg_execution_time_ms: float
    avg_total_time_ms: float
    p50_execution_ms: float
    p95_execution_ms: float
    p99_execution_ms: float
    
    # Data volume metrics
    total_bytes_processed: int
    total_bytes_processed_human: str
    total_items_processed: int
    avg_task_size_bytes: float
    avg_task_size_human: str
    p95_task_size_bytes: int
    p95_task_size_human: str
    
    # Throughput metrics
    avg_throughput_bytes_per_sec: float
    avg_throughput_human: str
    p95_throughput_bytes_per_sec: float
    p95_throughput_human: str
    
    # Queue health
    queue_depths: Dict[str, int]
    longest_queued_ms: Optional[float]
    
    # Worker stats
    active_workers: int
    worker_utilization: Dict[str, int]
    
    # Escalation stats
    warnings_issued: int
    escalations_triggered: int
    sub_agents_spawned: int


class TaskTimingDetail(BaseModel):
    """Detailed timing for a specific task"""
    task_id: str
    task_type: str
    domain: str
    status: str
    priority: str
    
    # Timing
    created_at: datetime
    queue_time_ms: Optional[float]
    execution_time_ms: Optional[float]
    total_time_ms: Optional[float]
    
    # SLA
    sla_ms: Optional[int]
    sla_met: Optional[bool]
    sla_buffer_ms: Optional[float]
    
    # Execution
    assigned_worker: Optional[str]
    attempt_number: int
    success: Optional[bool]


@router.get("/stats", response_model=HTMDashboardStats)
async def get_dashboard_stats():
    """
    Get real-time HTM dashboard statistics
    
    Returns comprehensive metrics for monitoring:
    - Task counts and states
    - SLA compliance and violations
    - Timing distributions
    - Queue health
    - Worker utilization
    """
    now = datetime.now(timezone.utc)
    
    async with async_session() as session:
        # Task counts by status
        result = await session.execute(
            select(HTMTask.status, func.count(HTMTask.id))
            .group_by(HTMTask.status)
        )
        status_counts = dict(result.all())
        
        # Queue depths by priority
        result = await session.execute(
            select(HTMTask.priority, func.count(HTMTask.id))
            .where(HTMTask.status == 'queued')
            .group_by(HTMTask.priority)
        )
        queue_depths = dict(result.all())
        
        # Longest queued task
        result = await session.execute(
            select(HTMTask)
            .where(HTMTask.status == 'queued')
            .order_by(HTMTask.queued_at.asc())
            .limit(1)
        )
        longest_queued = result.scalar_one_or_none()
        longest_queued_ms = None
        if longest_queued:
            longest_queued_ms = (now - longest_queued.queued_at).total_seconds() * 1000
        
        # Worker utilization
        result = await session.execute(
            select(HTMTask.assigned_worker, func.count(HTMTask.id))
            .where(HTMTask.status.in_(['assigned', 'running']))
            .where(HTMTask.assigned_worker.isnot(None))
            .group_by(HTMTask.assigned_worker)
        )
        worker_utilization = dict(result.all())
        
        # Timing metrics from completed tasks (last hour)
        one_hour_ago = now - timedelta(hours=1)
        result = await session.execute(
            select(HTMTask)
            .where(HTMTask.status == 'completed')
            .where(HTMTask.finished_at >= one_hour_ago)
            .where(HTMTask.execution_time_ms.isnot(None))
        )
        recent_completed = result.scalars().all()
        
        # Calculate percentiles
        if recent_completed:
            queue_times = [t.queue_time_ms for t in recent_completed if t.queue_time_ms]
            execution_times = [t.execution_time_ms for t in recent_completed if t.execution_time_ms]
            total_times = [t.total_time_ms for t in recent_completed if t.total_time_ms]
            
            avg_queue_time_ms = statistics.mean(queue_times) if queue_times else 0
            avg_execution_time_ms = statistics.mean(execution_times) if execution_times else 0
            avg_total_time_ms = statistics.mean(total_times) if total_times else 0
            
            if execution_times:
                sorted_exec = sorted(execution_times)
                p50_execution_ms = sorted_exec[len(sorted_exec) // 2]
                p95_execution_ms = sorted_exec[int(len(sorted_exec) * 0.95)]
                p99_execution_ms = sorted_exec[int(len(sorted_exec) * 0.99)]
            else:
                p50_execution_ms = p95_execution_ms = p99_execution_ms = 0
        else:
            avg_queue_time_ms = avg_execution_time_ms = avg_total_time_ms = 0
            p50_execution_ms = p95_execution_ms = p99_execution_ms = 0
        
        # SLA metrics
        sla_stats = await htm_sla_enforcer.get_statistics()
        
        # Size metrics
        size_stats = htm_size_metrics.stats
    
    return HTMDashboardStats(
        total_tasks=sum(status_counts.values()),
        active_tasks=status_counts.get('running', 0) + status_counts.get('assigned', 0),
        queued_tasks=status_counts.get('queued', 0),
        completed_tasks=status_counts.get('completed', 0),
        failed_tasks=status_counts.get('failed', 0) + status_counts.get('timeout', 0),
        
        sla_compliance_rate=sla_stats['sla_compliance_rate'],
        active_violations=sla_stats['active_violations'],
        total_violations=sla_stats['total_violations'],
        avg_buffer_ms=sla_stats['avg_buffer_ms'],
        
        avg_queue_time_ms=avg_queue_time_ms,
        avg_execution_time_ms=avg_execution_time_ms,
        avg_total_time_ms=avg_total_time_ms,
        p50_execution_ms=p50_execution_ms,
        p95_execution_ms=p95_execution_ms,
        p99_execution_ms=p99_execution_ms,
        
        total_bytes_processed=size_stats.get("total_bytes_processed", 0),
        total_bytes_processed_human=size_stats.get("total_data_processed_human", "0 B"),
        total_items_processed=size_stats.get("total_items_processed", 0),
        avg_task_size_bytes=size_stats.get("avg_task_size_bytes", 0),
        avg_task_size_human=size_stats.get("avg_task_size_human", "0 B"),
        p95_task_size_bytes=size_stats.get("p95_task_size_bytes", 0),
        p95_task_size_human=size_stats.get("p95_task_size_human", "0 B"),
        
        avg_throughput_bytes_per_sec=size_stats.get("avg_throughput_bytes_per_sec", 0),
        avg_throughput_human=format_bytes(int(size_stats.get("avg_throughput_bytes_per_sec", 0))) + "/s",
        p95_throughput_bytes_per_sec=size_stats.get("p95_throughput_bytes_per_sec", 0),
        p95_throughput_human=format_bytes(int(size_stats.get("p95_throughput_bytes_per_sec", 0))) + "/s",
        
        queue_depths=queue_depths,
        longest_queued_ms=longest_queued_ms,
        
        active_workers=len(worker_utilization),
        worker_utilization=worker_utilization,
        
        warnings_issued=sla_stats['warnings_issued'],
        escalations_triggered=sla_stats['escalations_triggered'],
        sub_agents_spawned=sla_stats['sub_agents_spawned']
    )


@router.get("/violations", response_model=List[Dict[str, Any]])
async def get_active_violations():
    """
    Get all active SLA violations
    
    Returns tasks that have exceeded their SLA deadlines
    """
    sla_stats = await htm_sla_enforcer.get_statistics()
    return sla_stats['violations_detail']


@router.get("/tasks/slow", response_model=List[TaskTimingDetail])
async def get_slow_tasks(limit: int = 20):
    """
    Get slowest running tasks
    
    Returns tasks sorted by execution time (slowest first)
    Useful for identifying performance bottlenecks
    """
    async with async_session() as session:
        result = await session.execute(
            select(HTMTask)
            .where(HTMTask.status.in_(['running', 'completed']))
            .where(HTMTask.execution_time_ms.isnot(None))
            .order_by(HTMTask.execution_time_ms.desc())
            .limit(limit)
        )
        slow_tasks = result.scalars().all()
    
    return [
        TaskTimingDetail(
            task_id=t.task_id,
            task_type=t.task_type,
            domain=t.domain,
            status=t.status,
            priority=t.priority,
            created_at=t.created_at,
            queue_time_ms=t.queue_time_ms,
            execution_time_ms=t.execution_time_ms,
            total_time_ms=t.total_time_ms,
            sla_ms=t.sla_ms,
            sla_met=t.sla_met,
            sla_buffer_ms=t.sla_buffer_ms,
            assigned_worker=t.assigned_worker,
            attempt_number=t.attempt_number,
            success=t.success
        )
        for t in slow_tasks
    ]


@router.get("/tasks/queued", response_model=List[TaskTimingDetail])
async def get_queued_tasks(priority: Optional[str] = None):
    """
    Get all queued tasks, optionally filtered by priority
    
    Shows current queue state with wait times
    """
    now = datetime.now(timezone.utc)
    
    async with async_session() as session:
        query = select(HTMTask).where(HTMTask.status == 'queued')
        
        if priority:
            query = query.where(HTMTask.priority == priority)
        
        query = query.order_by(HTMTask.queued_at.asc())
        
        result = await session.execute(query)
        queued_tasks = result.scalars().all()
    
    # Calculate wait times
    tasks_with_wait = []
    for t in queued_tasks:
        wait_time_ms = (now - t.queued_at).total_seconds() * 1000
        tasks_with_wait.append(
            TaskTimingDetail(
                task_id=t.task_id,
                task_type=t.task_type,
                domain=t.domain,
                status=t.status,
                priority=t.priority,
                created_at=t.created_at,
                queue_time_ms=wait_time_ms,  # Current wait time
                execution_time_ms=None,
                total_time_ms=None,
                sla_ms=t.sla_ms,
                sla_met=None,
                sla_buffer_ms=(t.sla_ms - wait_time_ms) if t.sla_ms else None,
                assigned_worker=None,
                attempt_number=t.attempt_number,
                success=None
            )
        )
    
    return tasks_with_wait


@router.get("/metrics/hourly", response_model=List[Dict[str, Any]])
async def get_hourly_metrics(hours: int = 24):
    """
    Get aggregated hourly metrics
    
    Returns historical performance data for trending
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    async with async_session() as session:
        result = await session.execute(
            select(HTMMetrics)
            .where(HTMMetrics.bucket == 'hourly')
            .where(HTMMetrics.bucket_start >= cutoff)
            .order_by(HTMMetrics.bucket_start.desc())
        )
        metrics = result.scalars().all()
    
    return [
        {
            "bucket_start": m.bucket_start.isoformat(),
            "task_type": m.task_type,
            "domain": m.domain,
            "total_tasks": m.total_tasks,
            "completed_tasks": m.completed_tasks,
            "failed_tasks": m.failed_tasks,
            "avg_execution_time_ms": m.avg_execution_time_ms,
            "p95_execution_ms": m.p95_execution_ms,
            "sla_compliance_rate": m.sla_compliance_rate,
            "success_rate": m.success_rate
        }
        for m in metrics
    ]


@router.get("/size/analysis")
async def get_size_analysis(
    task_type: Optional[str] = None,
    hours: int = 24
):
    """
    Get detailed data volume analysis
    
    Returns comprehensive size statistics, throughput, and recommendations
    """
    return await htm_size_metrics.get_size_analysis(task_type, hours)


@router.get("/size/heavy")
async def get_heavy_tasks(
    min_size_mb: Optional[int] = None,
    limit: int = 20
):
    """
    Get heaviest tasks by data volume
    
    Query Parameters:
    - min_size_mb: Minimum size in MB (optional)
    - limit: Max results (default 20)
    """
    min_size_bytes = min_size_mb * 1024 * 1024 if min_size_mb else None
    return await htm_size_metrics.get_heavy_tasks(min_size_bytes, limit)


@router.get("/size/distribution")
async def get_size_distribution():
    """
    Get distribution of task sizes
    
    Returns count by size class (tiny, small, medium, large, huge, massive)
    """
    size_stats = htm_size_metrics.stats
    return {
        "distribution": size_stats.get("size_distribution", {}),
        "by_task_type": size_stats.get("by_task_type", {})
    }


@router.get("/health")
async def get_htm_health():
    """
    Get overall HTM health status
    
    Returns health indicators and alerts
    """
    stats = await get_dashboard_stats()
    sla_stats = await htm_sla_enforcer.get_statistics()
    
    # Determine health status
    health = "healthy"
    alerts = []
    
    if stats.sla_compliance_rate < 0.9:
        health = "degraded"
        alerts.append(f"SLA compliance low: {stats.sla_compliance_rate:.1%}")
    
    if stats.active_violations > 10:
        health = "degraded"
        alerts.append(f"{stats.active_violations} active SLA violations")
    
    if stats.longest_queued_ms and stats.longest_queued_ms > 300000:  # 5 min
        health = "warning"
        alerts.append(f"Task queued for {stats.longest_queued_ms / 1000:.1f}s")
    
    if stats.failed_tasks > stats.completed_tasks * 0.1:  # >10% failure rate
        health = "critical"
        alerts.append(f"High failure rate: {stats.failed_tasks} failures")
    
    # Check throughput
    if stats.avg_throughput_bytes_per_sec < 1024 * 1024:  # < 1 MB/s
        health = "warning"
        alerts.append(f"Low throughput: {stats.avg_throughput_human}")
    
    return {
        "status": health,
        "sla_compliance_rate": stats.sla_compliance_rate,
        "active_tasks": stats.active_tasks,
        "queued_tasks": stats.queued_tasks,
        "active_violations": stats.active_violations,
        "total_data_processed": stats.total_bytes_processed_human,
        "avg_throughput": stats.avg_throughput_human,
        "alerts": alerts,
        "uptime_seconds": sla_stats.get("uptime_seconds", 0),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
