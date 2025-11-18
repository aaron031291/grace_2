"""
Search Health API
Health monitoring endpoints for Grace's web search and learning systems
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(
    prefix="/api/search",
    tags=["Search Health"]
)


@router.get("/health")
async def get_search_health() -> Dict[str, Any]:
    """
    Get health status of web search system
    
    Returns:
        Health status including provider, backoff state, offline mode
    """
    from backend.services.google_search_service import google_search_service
    
    try:
        health = await google_search_service.get_health()
        return health
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get search health: {e}",
            "provider": "unknown",
            "offline_mode": True
        }


@router.get("/metrics")
async def get_search_metrics() -> Dict[str, Any]:
    """
    Get detailed metrics for web search system
    
    Returns:
        Detailed metrics including success rates, trust scores, etc.
    """
    from backend.services.google_search_service import google_search_service
    
    try:
        metrics = await google_search_service.get_metrics()
        return metrics
    except Exception as e:
        return {
            "error": f"Failed to get search metrics: {e}",
            "total_searches": 0,
            "success_rate_pct": 0.0
        }
