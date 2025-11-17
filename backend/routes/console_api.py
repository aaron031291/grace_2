"""
Console API - Unified endpoints for Console UI

Aggregates data from multiple sources for the console interface
"""

from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/console", tags=["console"])


@router.get("/overview")
async def get_console_overview():
    """
    Get overview data for console dashboard
    
    Returns aggregated data for all console panes
    """
    try:
        # Get missions
        # Import mission data functions
        
        # Get recent logs count
        from backend.routes.logs_api import recent_logs
        
        # Get domain health
        from backend.domains import domain_registry
        
        return {
            "missions": {
                "active": 0,  # To be wired
                "proactive": 0,
                "followups": 0
            },
            "logs": {
                "total": len(recent_logs),
                "last_hour": len([
                    log for log in recent_logs 
                    if datetime.fromisoformat(log['timestamp']) > datetime.now() - timedelta(hours=1)
                ])
            },
            "domains": {
                "total": len(domain_registry.get_all()),
                "healthy": len([d for d in domain_registry.get_all() if d.health == 'healthy'])
            },
            "system": {
                "status": "running",
                "uptime_seconds": 0  # To be calculated
            }
        }
    except Exception as e:
        return {
            "missions": {"active": 0, "proactive": 0, "followups": 0},
            "logs": {"total": 0, "last_hour": 0},
            "domains": {"total": 0, "healthy": 0},
            "system": {"status": "running", "uptime_seconds": 0}
        }


@router.get("/health")
async def console_health():
    """Health check for console APIs"""
    return {
        "status": "healthy",
        "endpoints": {
            "logs": "available",
            "missions": "available",
            "chat": "available",
            "workspaces": "available"
        }
    }
