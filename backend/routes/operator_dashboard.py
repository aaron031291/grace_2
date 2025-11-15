"""
Operator Dashboard API
Consolidated visibility into boot progress, kernel health, active fixes

Endpoints:
- GET /operator/dashboard - Full system status
- GET /operator/boot/progress - Current boot progress
- GET /operator/kernels - Kernel health status
- GET /operator/fixes - Active coding agent fixes
- GET /operator/snapshots - Available rollback snapshots
- POST /operator/rollback - Trigger rollback to snapshot
- GET /operator/sbom - Software bill of materials
- GET /operator/vulnerabilities - CVE alerts
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from datetime import datetime

router = APIRouter(prefix="/operator", tags=["Operator Dashboard"])


@router.get("/dashboard")
async def get_dashboard():
    """
    Consolidated operator dashboard
    Shows everything at a glance
    """
    
    from ..core.control_plane import control_plane
    from ..core.boot_orchestrator import boot_orchestrator
    from ..core.production_hardening import (
        rollback_manager,
        secret_attestation,
        sbom_manager,
        boot_rate_limiter
    )
    
    # Get control plane status
    cp_status = control_plane.get_status()
    
    # Get boot orchestrator status
    boot_status = boot_orchestrator.get_status() if hasattr(boot_orchestrator, 'get_status') else {}
    
    # Get production hardening status
    snapshots = [
        {
            'snapshot_id': s.snapshot_id,
            'timestamp': s.timestamp.isoformat(),
            'git_commit': s.git_commit
        }
        for s in rollback_manager.snapshots
    ]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_state": cp_status['system_state'],
        "boot_phase": boot_orchestrator.boot_phase.value if hasattr(boot_orchestrator, 'boot_phase') else "complete",
        
        "kernels": {
            "total": cp_status['total_kernels'],
            "running": cp_status['running_kernels'],
            "failed": cp_status['failed_kernels'],
            "degraded": sum(1 for k in boot_orchestrator.kernel_graph.values() if k.degraded) if hasattr(boot_orchestrator, 'kernel_graph') else 0
        },
        
        "security": {
            "boot_rate_limiting": boot_rate_limiter.boot_mode,
            "attested_secrets": len(secret_attestation.attestations),
            "dependencies_tracked": len(sbom_manager.sbom),
            "vulnerabilities": len(sbom_manager.vulnerabilities)
        },
        
        "rollback": {
            "snapshots_available": len(snapshots),
            "latest_snapshot": snapshots[-1] if snapshots else None
        },
        
        "health": "healthy" if cp_status['failed_kernels'] == 0 else "degraded"
    }


@router.get("/boot/progress")
async def get_boot_progress():
    """Current boot progress with phase breakdown"""
    
    from ..core.boot_orchestrator import boot_orchestrator
    
    return {
        "phase": boot_orchestrator.boot_phase.value if hasattr(boot_orchestrator, 'boot_phase') else "complete",
        "boot_events": len(boot_orchestrator.boot_events) if hasattr(boot_orchestrator, 'boot_events') else 0,
        "recent_events": boot_orchestrator.boot_events[-10:] if hasattr(boot_orchestrator, 'boot_events') else []
    }


@router.get("/kernels")
async def get_kernel_health():
    """Detailed kernel health status"""
    
    from ..core.control_plane import control_plane
    from ..core.boot_orchestrator import boot_orchestrator
    
    cp_status = control_plane.get_status()
    
    kernels = []
    for name, kernel in cp_status['kernels'].items():
        # Get extended info from boot orchestrator if available
        extended_info = {}
        if hasattr(boot_orchestrator, 'kernel_graph'):
            if name in boot_orchestrator.kernel_graph:
                kernel_dep = boot_orchestrator.kernel_graph[name]
                extended_info = {
                    'tier': kernel_dep.tier,
                    'degraded': kernel_dep.degraded,
                    'retry_count': kernel_dep.retry_count,
                    'dependencies': kernel_dep.depends_on,
                    'priority': kernel_dep.priority
                }
        
        kernels.append({
            **kernel,
            **extended_info
        })
    
    return {
        "kernels": kernels,
        "summary": {
            "total": len(kernels),
            "running": sum(1 for k in kernels if k['state'] == 'running'),
            "failed": sum(1 for k in kernels if k['state'] == 'failed'),
            "degraded": sum(1 for k in kernels if k.get('degraded', False))
        }
    }


@router.get("/fixes")
async def get_active_fixes():
    """Active coding agent fix tasks"""
    
    try:
        from ..agents_core.elite_coding_agent import elite_coding_agent
        
        active_tasks = [
            {
                'task_id': task.task_id,
                'task_type': task.task_type.value,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'created_at': task.created_at.isoformat()
            }
            for task in elite_coding_agent.active_tasks.values()
        ]
        
        return {
            "active_fixes": active_tasks,
            "queue_length": len(elite_coding_agent.task_queue),
            "completed_count": len(elite_coding_agent.completed_tasks)
        }
    
    except Exception as e:
        return {
            "active_fixes": [],
            "error": str(e)
        }


@router.get("/snapshots")
async def get_snapshots():
    """Available rollback snapshots"""
    
    from ..core.production_hardening import rollback_manager
    
    snapshots = [
        {
            'snapshot_id': s.snapshot_id,
            'timestamp': s.timestamp.isoformat(),
            'git_commit': s.git_commit,
            'deployment_metadata': s.deployment_metadata,
            'config_files': len(s.config_hashes),
            'model_files': len(s.model_hashes)
        }
        for s in rollback_manager.snapshots
    ]
    
    return {
        "snapshots": snapshots,
        "count": len(snapshots),
        "max_snapshots": rollback_manager.max_snapshots
    }


@router.post("/rollback")
async def trigger_rollback(snapshot_id: str):
    """Trigger rollback to specific snapshot"""
    
    from ..core.production_hardening import rollback_manager
    
    success = await rollback_manager.rollback_to_snapshot(snapshot_id)
    
    if success:
        return {
            "success": True,
            "message": f"Rolled back to {snapshot_id}",
            "action_required": "Restart Grace to apply rollback"
        }
    else:
        raise HTTPException(status_code=500, detail="Rollback failed")


@router.get("/sbom")
async def get_sbom():
    """Software bill of materials"""
    
    from ..core.production_hardening import sbom_manager
    
    return {
        "generated": datetime.utcnow().isoformat(),
        "dependencies": sbom_manager.sbom,
        "count": len(sbom_manager.sbom)
    }


@router.get("/vulnerabilities")
async def get_vulnerabilities():
    """CVE alerts and vulnerabilities"""
    
    from ..core.production_hardening import sbom_manager
    
    vulns = [
        {
            'package': v.package,
            'current_version': v.current_version,
            'vulnerability_id': v.vulnerability_id,
            'severity': v.severity,
            'fixed_version': v.fixed_version,
            'description': v.description
        }
        for v in sbom_manager.vulnerabilities
    ]
    
    return {
        "vulnerabilities": vulns,
        "count": len(vulns),
        "by_severity": {
            'critical': sum(1 for v in vulns if v['severity'] == 'critical'),
            'high': sum(1 for v in vulns if v['severity'] == 'high'),
            'medium': sum(1 for v in vulns if v['severity'] == 'medium'),
            'low': sum(1 for v in vulns if v['severity'] == 'low')
        }
    }


@router.get("/rate-limits")
async def get_rate_limits():
    """Current rate limiting status"""
    
    from ..core.production_hardening import boot_rate_limiter
    
    return {
        "boot_mode": boot_rate_limiter.boot_mode,
        "limits": boot_rate_limiter.rate_limits,
        "current_counts": {
            resource: len(timestamps)
            for resource, timestamps in boot_rate_limiter.request_counts.items()
        }
    }
