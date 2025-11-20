"""
Learning Health API
Health monitoring endpoints for Grace's autonomous learning systems
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/api/learning",
    tags=["Learning Health"]
)


@router.get("/health")
async def get_learning_health() -> Dict[str, Any]:
    """
    Get health status of autonomous learning system
    
    Returns:
        Health status including running state, last activity, errors
    """
    try:
        from backend.learning_systems.advanced_learning import advanced_learning_supervisor
        
        if not advanced_learning_supervisor:
            return {
                "status": "unavailable",
                "message": "Advanced learning supervisor not initialized",
                "running": False
            }
        
        is_running = advanced_learning_supervisor.is_running
        task_count = len(advanced_learning_supervisor.tasks)
        
        from backend.services.google_search_service import google_search_service
        search_health = await google_search_service.get_health()
        
        if not is_running:
            status = "stopped"
            message = "Learning supervisor is not running"
        elif search_health.get("offline_mode"):
            status = "degraded"
            message = "OFFLINE MODE - Using local sources only"
        elif search_health.get("status") == "degraded":
            status = "degraded"
            message = f"Search degraded: {search_health.get('message')}"
        else:
            status = "healthy"
            message = "Learning system operational"
        
        return {
            "status": status,
            "message": message,
            "running": is_running,
            "active_tasks": task_count,
            "search_status": search_health.get("status"),
            "offline_mode": search_health.get("offline_mode", False),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get learning health: {e}",
            "running": False
        }


@router.get("/metrics")
async def get_learning_metrics() -> Dict[str, Any]:
    """
    Get detailed metrics for learning system
    
    Returns:
        Metrics including ingestion counts, success rates, etc.
    """
    try:
        from backend.agents.real_data_ingestion import real_data_ingestion
        ingestion_metrics = await real_data_ingestion.get_metrics()
        
        from backend.services.google_search_service import google_search_service
        search_metrics = await google_search_service.get_metrics()
        
        return {
            "ingestion": ingestion_metrics,
            "search": search_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": f"Failed to get learning metrics: {e}",
            "ingestion": {},
            "search": {}
        }
