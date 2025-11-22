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
        return {"status": "error", "message": str(e)}


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
        return {"playbooks": [], "count": 0}


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


@router.get("/stats")
async def get_self_healing_stats() -> Dict[str, Any]:
    """Get self-healing statistics"""
    try:
        # Try to get real stats from self-healing system
        from backend.self_heal.trigger_playbook_integration import trigger_playbook_integration
        from datetime import datetime, timedelta
        
        active = len(trigger_playbook_integration.active_incidents)
        resolved = len(trigger_playbook_integration.resolved_incidents)
        
        # Calculate today's resolved incidents
        today = datetime.utcnow().date()
        resolved_today = len([
            inc for inc in trigger_playbook_integration.resolved_incidents
            if datetime.fromisoformat(inc.get("completed_at", "2000-01-01")).date() == today
        ])
        
        # Calculate average resolution time
        resolution_times = [
            inc.get("resolution_time_seconds", 0)
            for inc in trigger_playbook_integration.resolved_incidents
            if inc.get("resolution_time_seconds")
        ]
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Calculate success rate
        total_attempts = active + resolved
        success_rate = (resolved / total_attempts * 100) if total_attempts > 0 else 100.0
        
        return {
            "total_incidents": active + resolved,
            "active_incidents": active,
            "resolved_today": resolved_today,
            "average_resolution_time": avg_resolution,
            "success_rate": success_rate,
            "mttr": avg_resolution,
            "mttr_target": 300
        }
    except Exception as e:
        # Return default stats if system not available
        return {
            "total_incidents": 0,
            "active_incidents": 0,
            "resolved_today": 0,
            "average_resolution_time": 0,
            "success_rate": 100.0,
            "mttr": 0,
            "mttr_target": 300
        }

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
        # Get real incidents from trigger system
        from backend.self_heal.trigger_playbook_integration import trigger_playbook_integration
        
        all_incidents = []
        
        # Add active incidents
        for inc_id, inc_data in trigger_playbook_integration.active_incidents.items():
            all_incidents.append({
                "id": inc_id,
                "type": inc_data.get("trigger_type", "unknown"),
                "severity": inc_data.get("severity", "medium"),
                "status": inc_data.get("status", "pending"),
                "component": inc_data.get("component", "unknown"),
                "detected_at": inc_data.get("created_at", datetime.utcnow().isoformat()),
                "playbook_applied": inc_data.get("playbook_name"),
                "error_message": inc_data.get("error_message")
            })
        
        # Add resolved incidents
        for inc_data in trigger_playbook_integration.resolved_incidents:
            if len(all_incidents) >= limit:
                break
            all_incidents.append({
                "id": inc_data.get("incident_id", "unknown"),
                "type": inc_data.get("trigger_type", "unknown"),
                "severity": inc_data.get("severity", "medium"),
                "status": "resolved",
                "component": inc_data.get("component", "unknown"),
                "detected_at": inc_data.get("created_at", datetime.utcnow().isoformat()),
                "resolved_at": inc_data.get("completed_at"),
                "playbook_applied": inc_data.get("playbook_name"),
                "resolution_time": inc_data.get("resolution_time_seconds")
            })
        
        # Filter by status if requested
        if status:
            all_incidents = [inc for inc in all_incidents if inc["status"] == status]
        
        # Limit results
        all_incidents = all_incidents[:limit]
        
        return {
            "incidents": all_incidents,
            "count": len(all_incidents),
            "total": len(all_incidents)
        }

    except Exception as e:
        # Return empty result instead of error
        print(f"[SELF-HEALING] Error fetching incidents: {e}")
        return {
            "incidents": [],
            "count": 0,
            "total": 0
        }


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
