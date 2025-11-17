"""
Guardian API - Stats and monitoring for healing playbooks
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/guardian", tags=["guardian"])

@router.get("/stats")
async def get_guardian_stats() -> Dict[str, Any]:
    """
    Get comprehensive Guardian statistics
    
    Returns:
    - Playbook execution counts
    - Success rates
    - MTTR metrics
    - Recent healing actions
    """
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        from backend.self_heal.network_healing_playbooks import NetworkPlaybookRegistry
        
        # Get MTTR stats
        tracker = get_mttr_tracker()
        mttr_stats = tracker.get_stats()
        
        # Get network playbook stats
        try:
            network_registry = NetworkPlaybookRegistry()
            network_stats = network_registry.get_playbook_stats()
        except Exception as e:
            network_stats = {"error": str(e)}
        
        # Get auto-healing playbook stats
        auto_healing_stats = {}
        try:
            from backend.self_heal.auto_healing_playbooks import (
                RestartKernelPlaybook,
                RestartServicePlaybook,
                PerformanceOptimizationPlaybook,
                ResourceCleanupPlaybook
            )
            
            # Sample playbooks (would normally load from registry)
            playbooks = {
                "restart_kernel": RestartKernelPlaybook(),
                "restart_service": RestartServicePlaybook(),
                "performance_optimization": PerformanceOptimizationPlaybook(),
                "resource_cleanup": ResourceCleanupPlaybook()
            }
            
            for name, pb in playbooks.items():
                auto_healing_stats[name] = {
                    "executions": getattr(pb, 'execution_count', 0),
                    "successes": getattr(pb, 'success_count', 0),
                    "failures": getattr(pb, 'failure_count', 0),
                    "success_rate": 0
                }
        except Exception as e:
            auto_healing_stats = {"error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mttr": mttr_stats,
            "network_playbooks": network_stats,
            "auto_healing_playbooks": auto_healing_stats,
            "overall_health": {
                "status": "healthy" if mttr_stats.get("success_rate_percent", 0) >= 90 else "degraded",
                "mttr_target_seconds": 120,
                "mttr_actual_seconds": mttr_stats.get("mttr_seconds"),
                "target_met": mttr_stats.get("mttr_seconds", 999) < 120 if mttr_stats.get("mttr_seconds") else False
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Guardian stats: {str(e)}")

@router.get("/healer/stats")
async def get_healer_stats() -> Dict[str, Any]:
    """
    Get last 5 healing runs and current status
    
    Returns:
    - Recent healing actions
    - Success/failure counts
    - Average recovery time
    """
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        
        tracker = get_mttr_tracker()
        stats = tracker.get_stats()
        
        recent_actions = stats.get("recent_actions", [])[-5:]
        
        return {
            "last_5_runs": recent_actions,
            "summary": {
                "total_healing_actions": stats.get("total_actions", 0),
                "successful": stats.get("successful", 0),
                "failed": stats.get("failed", 0),
                "success_rate": stats.get("success_rate_percent", 0),
                "average_recovery_time_seconds": stats.get("mttr_seconds"),
                "active_healing_actions": stats.get("active_actions_count", 0)
            },
            "mttr_targets": {
                "target_seconds": 120,
                "current_seconds": stats.get("mttr_seconds"),
                "target_met": stats.get("mttr_seconds", 999) < 120 if stats.get("mttr_seconds") else False
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get healer stats: {str(e)}")

@router.get("/playbooks")
async def list_playbooks() -> Dict[str, Any]:
    """
    List all available Guardian playbooks
    
    Returns:
    - Playbook names
    - Descriptions
    - Success rates
    - Average execution times
    """
    try:
        from backend.self_heal.network_healing_playbooks import NetworkPlaybookRegistry
        
        network_registry = NetworkPlaybookRegistry()
        
        playbooks = []
        
        for name, playbook in network_registry.playbooks.items():
            playbooks.append({
                "name": name,
                "type": "network_healing",
                "class": playbook.__class__.__name__,
                "description": playbook.__class__.__doc__ or "No description",
                "executions": getattr(playbook, 'execution_count', 0),
                "successes": getattr(playbook, 'success_count', 0),
                "failures": getattr(playbook, 'failure_count', 0),
                "success_rate": (
                    getattr(playbook, 'success_count', 0) / getattr(playbook, 'execution_count', 1) * 100
                    if getattr(playbook, 'execution_count', 0) > 0 else 0
                )
            })
        
        # Add auto-healing playbooks
        try:
            from backend.self_heal.auto_healing_playbooks import (
                RestartKernelPlaybook,
                RestartServicePlaybook,
                PerformanceOptimizationPlaybook,
                ResourceCleanupPlaybook,
                RollbackDeploymentPlaybook,
                QuarantineArtifactsPlaybook,
                RunDiagnosticsPlaybook,
                DailyHealthCheckPlaybook,
                RotateSecretsPlaybook
            )
            
            auto_playbooks = [
                ("restart_kernel", RestartKernelPlaybook()),
                ("restart_service", RestartServicePlaybook()),
                ("performance_optimization", PerformanceOptimizationPlaybook()),
                ("resource_cleanup", ResourceCleanupPlaybook()),
                ("rollback_deployment", RollbackDeploymentPlaybook()),
                ("quarantine_artifacts", QuarantineArtifactsPlaybook()),
                ("run_diagnostics", RunDiagnosticsPlaybook()),
                ("daily_health_check", DailyHealthCheckPlaybook()),
                ("rotate_secrets", RotateSecretsPlaybook())
            ]
            
            for name, pb in auto_playbooks:
                playbooks.append({
                    "name": name,
                    "type": "auto_healing",
                    "class": pb.__class__.__name__,
                    "description": pb.__class__.__doc__ or "No description",
                    "executions": getattr(pb, 'execution_count', 0),
                    "successes": getattr(pb, 'success_count', 0),
                    "failures": getattr(pb, 'failure_count', 0),
                    "success_rate": 0
                })
        except Exception:
            pass
        
        return {
            "total_playbooks": len(playbooks),
            "playbooks": playbooks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list playbooks: {str(e)}")

@router.get("/mttr/by-issue-type")
async def get_mttr_by_issue_type() -> Dict[str, Any]:
    """Get MTTR broken down by issue type"""
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        
        tracker = get_mttr_tracker()
        stats = tracker.get_stats()
        
        return {
            "mttr_by_issue_type": stats.get("mttr_by_issue_type", {}),
            "target_seconds": 120
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MTTR by issue type: {str(e)}")

@router.get("/mttr/by-playbook")
async def get_mttr_by_playbook() -> Dict[str, Any]:
    """Get MTTR broken down by playbook"""
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        
        tracker = get_mttr_tracker()
        stats = tracker.get_stats()
        
        return {
            "mttr_by_playbook": stats.get("mttr_by_playbook", {}),
            "target_seconds": 120
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MTTR by playbook: {str(e)}")

@router.get("/failures/recent")
async def get_recent_failures(limit: int = 10) -> Dict[str, Any]:
    """Get recent healing failures for investigation"""
    try:
        from backend.monitoring.mttr_tracker import get_mttr_tracker
        
        tracker = get_mttr_tracker()
        failures = tracker.get_recent_failures(limit)
        
        return {
            "total_failures": len(failures),
            "failures": [f.to_dict() for f in failures]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent failures: {str(e)}")
