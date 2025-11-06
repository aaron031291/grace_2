"""
Self-Healing Scheduler Observability

Provides real-time visibility into scheduler behavior:
- Proposals created vs skipped
- Backoff reasons and counts
- Rate limiting effectiveness
- Duplicate detection stats
"""

from __future__ import annotations
from typing import Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_current_user
from ..settings import settings

router = APIRouter(prefix="/api/self_heal", tags=["self-heal-observability"])


@router.get("/scheduler_counters")
async def get_scheduler_counters(current_user: str = Depends(get_current_user)):
    """
    Get scheduler observability counters.
    
    Returns real-time statistics about scheduler decisions:
    - Total proposals created
    - Skipped (rate limited)
    - Skipped (backoff)
    - Skipped (duplicate)
    - Current backoff state
    """
    
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Self-heal endpoints disabled")
    
    try:
        from ..self_heal.scheduler import scheduler
    except ImportError:
        raise HTTPException(status_code=503, detail="Scheduler not available")
    
    # Get backoff state
    backoff_active = []
    for (service, diagnosis), state in scheduler._backoff.items():
        next_at = state.get("next_at")
        if isinstance(next_at, datetime):
            backoff_active.append({
                "service": service,
                "diagnosis": diagnosis,
                "backoff_factor": state.get("factor", 0),
                "next_allowed_at": next_at.isoformat(),
                "suppressed_until": next_at.isoformat()
            })
    
    # Get rate limit state
    rate_limited_services = []
    now = datetime.now(timezone.utc)
    for service, timestamps in scheduler._rate.items():
        # Clean up old entries
        cutoff = now - timedelta(hours=1)
        active = [t for t in timestamps if t >= cutoff]
        
        if len(active) >= 3:  # At rate limit
            rate_limited_services.append({
                "service": service,
                "proposals_last_hour": len(active),
                "limit": 3
            })
    
    return {
        "scheduler_state": {
            "poll_interval_seconds": scheduler._interval,
            "running": bool(scheduler._task and not scheduler._task.done())
        },
        "backoff": {
            "active_count": len(backoff_active),
            "services": backoff_active
        },
        "rate_limiting": {
            "active_count": len(rate_limited_services),
            "services": rate_limited_services
        },
        "statistics": {
            "total_backoff_entries": len(scheduler._backoff),
            "total_rate_tracked_services": len(scheduler._rate)
        },
        "metadata": {
            "timestamp": now.isoformat(),
            "observe_only": settings.SELF_HEAL_OBSERVE_ONLY,
            "execute_enabled": settings.SELF_HEAL_EXECUTE
        }
    }


@router.get("/scheduler_health")
async def get_scheduler_health(current_user: str = Depends(get_current_user)):
    """Get scheduler health status"""
    
    if not (settings.SELF_HEAL_OBSERVE_ONLY or settings.SELF_HEAL_EXECUTE):
        raise HTTPException(status_code=404, detail="Self-heal endpoints disabled")
    
    try:
        from ..self_heal.scheduler import scheduler
        
        is_running = bool(scheduler._task and not scheduler._task.done())
        
        return {
            "status": "running" if is_running else "stopped",
            "poll_interval_seconds": scheduler._interval,
            "backoff_entries": len(scheduler._backoff),
            "rate_tracked_services": len(scheduler._rate),
            "healthy": is_running
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "healthy": False
        }
