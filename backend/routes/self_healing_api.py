"""
Self-Healing API Routes
Dashboard and management endpoints for the Self-Healing Kernel
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/self-healing", tags=["Self-Healing"])


class ManualHealingRequest(BaseModel):
    """Request to trigger manual self-healing"""
    component: str
    error_details: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_self_healing_status() -> Dict[str, Any]:
    """Get Self-Healing Kernel status"""
    try:
        from backend.unified_grace_orchestrator import orchestrator

        if hasattr(orchestrator, 'domain_kernels') and 'self_healing' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['self_healing']
            return kernel.get_status()
        else:
            return {"status": "not_initialized", "message": "Self-Healing Kernel not found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playbooks")
async def get_playbooks() -> Dict[str, Any]:
    """Get all available self-healing playbooks"""
    try:
        from backend.unified_grace_orchestrator import orchestrator

        if hasattr(orchestrator, 'domain_kernels') and 'self_healing' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['self_healing']
            playbooks = kernel.get_playbook_definitions()

            return {
                "playbooks": list(playbooks.values()),
                "count": len(playbooks)
            }
        else:
            return {"playbooks": [], "count": 0}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playbooks/{playbook_name}")
async def get_playbook_details(playbook_name: str) -> Dict[str, Any]:
    """Get details for a specific playbook"""
    try:
        from backend.unified_grace_orchestrator import orchestrator

        if hasattr(orchestrator, 'domain_kernels') and 'self_healing' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['self_healing']
            playbooks = kernel.get_playbook_definitions()

            if playbook_name in playbooks:
                return playbooks[playbook_name]
            else:
                raise HTTPException(status_code=404, detail=f"Playbook '{playbook_name}' not found")
        else:
            raise HTTPException(status_code=404, detail="Self-Healing Kernel not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-runs")
async def get_active_runs() -> Dict[str, Any]:
    """Get currently active self-healing runs"""
    try:
        from backend.unified_grace_orchestrator import orchestrator

        if hasattr(orchestrator, 'domain_kernels') and 'self_healing' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['self_healing']
            active_runs = kernel.get_active_playbooks()

            return {
                "active_runs": active_runs,
                "count": len(active_runs)
            }
        else:
            return {"active_runs": [], "count": 0}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-manual")
async def trigger_manual_healing(request: ManualHealingRequest) -> Dict[str, Any]:
    """Manually trigger self-healing for a component"""
    try:
        from backend.unified_grace_orchestrator import orchestrator

        if hasattr(orchestrator, 'domain_kernels') and 'self_healing' in orchestrator.domain_kernels:
            kernel = orchestrator.domain_kernels['self_healing']

            await kernel.trigger_manual_healing(
                component=request.component,
                error_details=request.error_details or {}
            )

            return {
                "status": "triggered",
                "message": f"Self-healing triggered for component: {request.component}"
            }
        else:
            raise HTTPException(status_code=404, detail="Self-Healing Kernel not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution-logs")
async def get_execution_logs(limit: int = 50) -> Dict[str, Any]:
    """Get recent self-healing execution logs"""
    try:
        from backend.memory_tables.registry import table_registry

        # Query memory_execution_logs for self-healing related entries
        logs = table_registry.query_rows(
            'memory_execution_logs',
            filters={'playbook_name': {'$ne': None}},  # Not null
            limit=limit,
            order_by='timestamp',
            descending=True
        )

        return {
            "logs": logs,
            "count": len(logs)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_self_healing_metrics() -> Dict[str, Any]:
    """Get self-healing performance metrics"""
    try:
        from backend.memory_tables.registry import table_registry

        # Get playbook statistics
        playbooks = table_registry.query_rows('memory_self_healing_playbooks')

        total_playbooks = len(playbooks)
        active_playbooks = len([p for p in playbooks if p.get('total_runs', 0) > 0])

        # Calculate success rates
        success_rates = []
        for playbook in playbooks:
            total_runs = playbook.get('total_runs', 0)
            successful_runs = playbook.get('successful_runs', 0)
            if total_runs > 0:
                success_rates.append(successful_runs / total_runs)

        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0

        # Get recent activity (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

        recent_logs = table_registry.query_rows(
            'memory_execution_logs',
            filters={
                'timestamp': {'$gte': yesterday},
                'playbook_name': {'$ne': None}
            }
        )

        recent_runs = len(recent_logs)
        recent_successes = len([log for log in recent_logs if log.get('success')])

        return {
            "overview": {
                "total_playbooks": total_playbooks,
                "active_playbooks": active_playbooks,
                "average_success_rate": round(avg_success_rate, 3)
            },
            "recent_activity": {
                "runs_last_24h": recent_runs,
                "successes_last_24h": recent_successes,
                "success_rate_last_24h": recent_successes / recent_runs if recent_runs > 0 else 0
            },
            "performance": {
                "most_successful_playbook": max(playbooks, key=lambda p: p.get('success_rate', 0))['playbook_name'] if playbooks else None,
                "least_successful_playbook": min(playbooks, key=lambda p: p.get('success_rate', 0))['playbook_name'] if playbooks else None
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents")
async def get_incidents(status: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """Get self-healing incidents"""
    try:
        from backend.memory_tables.registry import table_registry

        filters = {}
        if status:
            filters['status'] = status

        incidents = table_registry.query_rows(
            'memory_incidents',
            filters=filters,
            limit=limit,
            order_by='created_at',
            descending=True
        )

        return {
            "incidents": incidents,
            "count": len(incidents)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grace-loops")
async def get_grace_loops(limit: int = 20) -> Dict[str, Any]:
    """Get GraceLoopOutput entries for self-healing"""
    try:
        from backend.memory_tables.registry import table_registry

        loops = table_registry.query_rows(
            'memory_grace_loops',
            filters={'loop_type': 'self_healing'},
            limit=limit,
            order_by='started_at',
            descending=True
        )

        return {
            "loops": loops,
            "count": len(loops)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comprehensive-metrics")
async def get_comprehensive_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics for dashboard"""
    try:
        from backend.memory_tables.registry import table_registry

        # Self-healing metrics
        execution_logs = table_registry.query_rows('memory_execution_logs')
        playbooks = table_registry.query_rows('memory_self_healing_playbooks')

        total_runs = len(execution_logs)
        successful_runs = len([log for log in execution_logs if log.get('status') == 'success'])
        success_rate = successful_runs / total_runs if total_runs > 0 else 0

        execution_times = [log.get('execution_time_ms', 0) for log in execution_logs if log.get('execution_time_ms')]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Mock MTTR calculation (would need incident data)
        mttr_minutes = 15  # Placeholder

        # Ingestion metrics (mock data - would need real ingestion logs)
        ingestion_metrics = {
            "total_ingested": 150,
            "throughput_per_hour": 12,
            "average_processing_time_ms": 2500,
            "success_rate": 0.95
        }

        # Verification metrics (mock data)
        verification_metrics = {
            "total_verifications": 200,
            "passed_verifications": 190,
            "average_trust_score": 0.87,
            "anomalies_detected": 3
        }

        # Trust levels
        trust_levels = {
            "overall_trust": 0.89,
            "librarian_trust": 0.92,
            "verification_trust": 0.85,
            "recent_dips": [
                {
                    "component": "ingestion_pipeline",
                    "old_trust": 0.95,
                    "new_trust": 0.89,
                    "timestamp": "2025-11-13T12:30:00Z"
                }
            ]
        }

        return {
            "self_healing": {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "average_success_rate": success_rate,
                "average_execution_time_ms": avg_execution_time,
                "mttr_minutes": mttr_minutes
            },
            "ingestion": ingestion_metrics,
            "verification": verification_metrics,
            "trust_levels": trust_levels
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))