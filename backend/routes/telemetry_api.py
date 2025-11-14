"""
Telemetry API - Unified data source for all dashboard views
Provides real-time metrics for Layer 1-4 dashboards
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from backend.core.database import get_session
from backend.kernels.kernel_registry import KernelRegistry
from backend.memory_services.htm_queue import HTMQueue
from backend.learning_systems.learning_loop import LearningLoop
from backend.crypto.crypto_health import CryptoHealthMonitor
import asyncio

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])


# ========== LAYER 1: OPS CONSOLE ==========

@router.get("/kernels/status")
async def get_kernel_status():
    """Real-time kernel status, boot metrics, stress test results"""
    try:
        registry = KernelRegistry()
        kernels = await registry.get_all_kernels()
        
        kernel_statuses = []
        for kernel in kernels:
            status_data = {
                "kernel_id": kernel.kernel_id,
                "name": kernel.name,
                "status": kernel.status,  # active, idle, booting, error
                "boot_time_ms": getattr(kernel, "boot_time_ms", 0),
                "uptime_seconds": getattr(kernel, "uptime_seconds", 0),
                "last_heartbeat": getattr(kernel, "last_heartbeat", None),
                "health": kernel.health if hasattr(kernel, "health") else "unknown",
                "stress_score": getattr(kernel, "stress_score", 0),
                "task_count": getattr(kernel, "task_count", 0),
                "error_count": getattr(kernel, "error_count", 0),
            }
            kernel_statuses.append(status_data)
        
        return {
            "total_kernels": len(kernel_statuses),
            "active": sum(1 for k in kernel_statuses if k["status"] == "active"),
            "idle": sum(1 for k in kernel_statuses if k["status"] == "idle"),
            "errors": sum(1 for k in kernel_statuses if k["status"] == "error"),
            "avg_boot_time_ms": sum(k["boot_time_ms"] for k in kernel_statuses) / len(kernel_statuses) if kernel_statuses else 0,
            "kernels": kernel_statuses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch kernel status: {str(e)}")


@router.get("/crypto/health")
async def get_crypto_health():
    """Cryptographic health: signature validation, key rotation status"""
    try:
        monitor = CryptoHealthMonitor()
        health_data = await monitor.get_health_status()
        
        return {
            "overall_health": health_data.get("status", "unknown"),
            "signatures_validated": health_data.get("signatures_validated", 0),
            "signature_failures": health_data.get("signature_failures", 0),
            "key_rotation_due": health_data.get("key_rotation_due", False),
            "last_key_rotation": health_data.get("last_key_rotation"),
            "encrypted_items": health_data.get("encrypted_items", 0),
            "components": health_data.get("components", {})
        }
    except Exception as e:
        return {
            "overall_health": "unknown",
            "error": str(e)
        }


@router.get("/ingestion/throughput")
async def get_ingestion_throughput(hours: int = Query(default=24, ge=1, le=168)):
    """Ingestion throughput metrics: files processed, MB ingested, avg time"""
    try:
        async with get_session() as session:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            # Query ingestion jobs from last N hours
            from backend.models import IngestionJob
            result = await session.execute(
                select(
                    func.count(IngestionJob.id).label("total_jobs"),
                    func.sum(IngestionJob.size_bytes).label("total_bytes"),
                    func.avg(IngestionJob.duration_seconds).label("avg_duration"),
                    func.max(IngestionJob.duration_seconds).label("max_duration")
                ).where(
                    IngestionJob.created_at >= since
                )
            )
            stats = result.first()
            
            return {
                "time_window_hours": hours,
                "total_jobs": stats.total_jobs or 0,
                "total_mb": round((stats.total_bytes or 0) / 1024 / 1024, 2),
                "avg_duration_seconds": round(stats.avg_duration or 0, 2),
                "max_duration_seconds": round(stats.max_duration or 0, 2),
                "throughput_mb_per_hour": round((stats.total_bytes or 0) / 1024 / 1024 / hours, 2)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingestion throughput: {str(e)}")


@router.post("/kernels/{kernel_id}/control")
async def control_kernel(kernel_id: str, action: str):
    """Control kernel: start, stop, restart, view logs"""
    try:
        registry = KernelRegistry()
        
        if action == "start":
            await registry.start_kernel(kernel_id)
        elif action == "stop":
            await registry.stop_kernel(kernel_id)
        elif action == "restart":
            await registry.restart_kernel(kernel_id)
        elif action == "stress":
            await registry.run_stress_test(kernel_id)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")
        
        return {"kernel_id": kernel_id, "action": action, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kernel control failed: {str(e)}")


@router.get("/kernels/{kernel_id}/logs")
async def get_kernel_logs(kernel_id: str, lines: int = Query(default=100, ge=1, le=1000)):
    """Fetch recent kernel logs"""
    try:
        registry = KernelRegistry()
        logs = await registry.get_kernel_logs(kernel_id, lines=lines)
        return {"kernel_id": kernel_id, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch logs: {str(e)}")


# ========== LAYER 2: HTM CONSOLE ==========

@router.get("/htm/queue")
async def get_htm_queue_status():
    """HTM task queue status: depth, timing, size, SLA metrics"""
    try:
        htm_queue = HTMQueue()
        queue_stats = await htm_queue.get_queue_metrics()
        
        return {
            "queue_depth": queue_stats.get("depth", 0),
            "pending_tasks": queue_stats.get("pending", 0),
            "active_tasks": queue_stats.get("active", 0),
            "completed_today": queue_stats.get("completed_today", 0),
            "failed_today": queue_stats.get("failed_today", 0),
            "avg_wait_time_seconds": queue_stats.get("avg_wait_time", 0),
            "p95_duration_seconds": queue_stats.get("p95_duration", 0),
            "avg_task_size_mb": queue_stats.get("avg_size_mb", 0),
            "sla_breaches": queue_stats.get("sla_breaches", 0),
            "tasks": queue_stats.get("tasks", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch HTM queue: {str(e)}")


@router.get("/htm/tasks")
async def get_htm_tasks(
    origin: Optional[str] = Query(default=None, description="Filter by origin: filesystem, remote, hunter"),
    status: Optional[str] = Query(default=None, description="Filter by status: pending, active, completed, failed"),
    limit: int = Query(default=50, ge=1, le=500)
):
    """Retrieve HTM tasks with filters by origin and status"""
    try:
        async with get_session() as session:
            from backend.models import HTMTask
            
            query = select(HTMTask).order_by(HTMTask.created_at.desc()).limit(limit)
            
            if origin:
                query = query.where(HTMTask.origin == origin)
            if status:
                query = query.where(HTMTask.status == status)
            
            result = await session.execute(query)
            tasks = result.scalars().all()
            
            task_list = [{
                "task_id": t.id,
                "origin": t.origin,
                "status": t.status,
                "size_mb": round(t.size_bytes / 1024 / 1024, 2) if t.size_bytes else 0,
                "duration_seconds": t.duration_seconds,
                "priority": t.priority,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            } for t in tasks]
            
            return {"total": len(task_list), "tasks": task_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch HTM tasks: {str(e)}")


@router.get("/htm/workload")
async def get_htm_workload_perception():
    """Workload perception: active agents, auto-escalations, capacity"""
    try:
        async with get_session() as session:
            from backend.models import Agent, HTMTask
            
            # Count active agents
            active_agents_result = await session.execute(
                select(func.count(Agent.id)).where(Agent.status == "active")
            )
            active_agents = active_agents_result.scalar() or 0
            
            # Count auto-escalations today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            escalations_result = await session.execute(
                select(func.count(HTMTask.id)).where(
                    and_(
                        HTMTask.created_at >= today_start,
                        HTMTask.priority == "high"
                    )
                )
            )
            escalations_today = escalations_result.scalar() or 0
            
            return {
                "active_agents": active_agents,
                "auto_escalations_today": escalations_today,
                "capacity_utilization_percent": min(100, int((active_agents / 10) * 100)),
                "workload_status": "normal" if active_agents < 8 else "high"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workload perception: {str(e)}")


# ========== LAYER 3: INTENT & LEARNING ==========

@router.get("/intent/active")
async def get_active_intents():
    """Active intents, completion status, linked HTM tasks"""
    try:
        async with get_session() as session:
            from backend.models import Intent
            
            result = await session.execute(
                select(Intent).where(Intent.status.in_(["active", "pending"])).order_by(Intent.created_at.desc())
            )
            intents = result.scalars().all()
            
            intent_list = [{
                "intent_id": i.id,
                "goal": i.goal,
                "status": i.status,
                "completion_percent": getattr(i, "completion_percent", 0),
                "created_at": i.created_at.isoformat() if i.created_at else None,
                "htm_tasks_generated": getattr(i, "htm_tasks_count", 0),
                "estimated_completion": getattr(i, "estimated_completion", None)
            } for i in intents]
            
            return {"total": len(intent_list), "intents": intent_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch intents: {str(e)}")


@router.get("/learning/retrospectives")
async def get_retrospectives(limit: int = Query(default=20, ge=1, le=100)):
    """Learning retrospectives: completed cycles, insights"""
    try:
        loop = LearningLoop()
        retrospectives = await loop.get_recent_retrospectives(limit=limit)
        
        return {
            "total": len(retrospectives),
            "retrospectives": retrospectives
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospectives: {str(e)}")


@router.get("/learning/playbooks")
async def get_playbook_success_rates():
    """Playbook success rates and usage stats"""
    try:
        async with get_session() as session:
            from backend.models import PlaybookExecution
            
            result = await session.execute(
                select(
                    PlaybookExecution.playbook_name,
                    func.count(PlaybookExecution.id).label("total_runs"),
                    func.sum(func.cast(PlaybookExecution.success, int)).label("successful_runs")
                ).group_by(PlaybookExecution.playbook_name)
            )
            
            playbooks = result.all()
            playbook_stats = [{
                "playbook_name": p.playbook_name,
                "total_runs": p.total_runs,
                "success_rate_percent": round((p.successful_runs / p.total_runs * 100), 1) if p.total_runs else 0
            } for p in playbooks]
            
            return {"playbooks": playbook_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch playbook stats: {str(e)}")


@router.get("/learning/policy_suggestions")
async def get_policy_suggestions():
    """AI-generated policy suggestions from learning loops"""
    try:
        async with get_session() as session:
            from backend.models import PolicySuggestion
            
            result = await session.execute(
                select(PolicySuggestion).where(PolicySuggestion.status == "pending").order_by(PolicySuggestion.confidence.desc())
            )
            suggestions = result.scalars().all()
            
            suggestion_list = [{
                "suggestion_id": s.id,
                "policy_area": s.policy_area,
                "suggestion": s.suggestion,
                "confidence": s.confidence,
                "supporting_evidence": s.evidence,
                "created_at": s.created_at.isoformat() if s.created_at else None
            } for s in suggestions]
            
            return {"suggestions": suggestion_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch policy suggestions: {str(e)}")


# ========== LAYER 4: DEV/OS VIEW ==========

@router.get("/secrets/status")
async def get_secrets_status():
    """Secrets vault status: stored keys, encryption health"""
    try:
        async with get_session() as session:
            from backend.models import SecretVault
            
            result = await session.execute(
                select(
                    func.count(SecretVault.id).label("total_secrets"),
                    func.sum(func.cast(SecretVault.is_encrypted, int)).label("encrypted_count")
                )
            )
            stats = result.first()
            
            return {
                "total_secrets": stats.total_secrets or 0,
                "encrypted": stats.encrypted_count or 0,
                "vault_health": "healthy" if stats.encrypted_count == stats.total_secrets else "degraded"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch secrets status: {str(e)}")


@router.get("/recordings/pending")
async def get_pending_recordings():
    """Recordings awaiting ingestion"""
    try:
        async with get_session() as session:
            from backend.models import Recording
            
            result = await session.execute(
                select(Recording).where(Recording.ingestion_status == "pending").order_by(Recording.created_at.desc())
            )
            recordings = result.scalars().all()
            
            recording_list = [{
                "recording_id": r.id,
                "type": r.recording_type,
                "filename": r.filename,
                "size_mb": round(r.size_bytes / 1024 / 1024, 2) if r.size_bytes else 0,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in recordings]
            
            return {"total": len(recording_list), "recordings": recording_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending recordings: {str(e)}")


@router.get("/remote_access/sessions")
async def get_remote_access_sessions(active_only: bool = Query(default=True)):
    """Remote access session logs"""
    try:
        async with get_session() as session:
            from backend.models import RemoteAccessSession
            
            query = select(RemoteAccessSession).order_by(RemoteAccessSession.started_at.desc())
            if active_only:
                query = query.where(RemoteAccessSession.status == "active")
            
            result = await session.execute(query.limit(50))
            sessions = result.scalars().all()
            
            session_list = [{
                "session_id": s.id,
                "user": s.user_id,
                "status": s.status,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "duration_minutes": getattr(s, "duration_minutes", 0)
            } for s in sessions]
            
            return {"total": len(session_list), "sessions": session_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch remote access sessions: {str(e)}")


@router.get("/deployment/status")
async def get_deployment_status():
    """Code and deployment status"""
    try:
        # This would integrate with CI/CD systems
        return {
            "last_deployment": "2025-11-14T10:30:00Z",
            "environment": "production",
            "version": "4.2.1",
            "health_check": "passing",
            "pending_tests": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch deployment status: {str(e)}")


# ========== REAL-TIME STREAM ENDPOINT ==========

@router.get("/stream/metrics")
async def stream_metrics():
    """WebSocket-compatible endpoint for real-time metric streaming"""
    # This would be implemented as a WebSocket endpoint for live updates
    return {"message": "Use WebSocket connection at /ws/telemetry for real-time updates"}
