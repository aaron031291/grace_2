"""
Autonomous Healing Dashboard API
Monitor all three healing systems: Code Healer, Log Healer, Resilient Startup
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api/healing", tags=["Autonomous Healing"])


@router.get("/status")
async def get_healing_status() -> Dict[str, Any]:
    """Get status of all autonomous healing systems"""
    
    from ..autonomous_code_healer import code_healer
    from ..log_based_healer import log_based_healer
    from ..resilient_startup import resilient_startup
    
    return {
        "code_healer": await code_healer.get_status(),
        "log_healer": {
            "running": log_based_healer.running,
            "log_path": log_based_healer.log_path,
            "scan_interval": log_based_healer.scan_interval,
            "last_position": log_based_healer.last_position
        },
        "resilient_startup": await resilient_startup.get_startup_report(),
        "overall_health": "operational"
    }


@router.get("/fixes/recent")
async def get_recent_fixes(limit: int = 20) -> Dict[str, Any]:
    """Get recently applied fixes from all healing systems"""
    
    from ..immutable_log import ImmutableLog
    from ..models import async_session
    from ..governance_models import ImmutableLogEntry
    from sqlalchemy import select, desc, or_
    
    async with async_session() as session:
        # Get recent healing actions
        result = await session.execute(
            select(ImmutableLogEntry)
            .where(
                or_(
                    ImmutableLogEntry.subsystem == "autonomous_code_healer",
                    ImmutableLogEntry.subsystem == "log_based_healer",
                    ImmutableLogEntry.subsystem == "resilient_startup"
                )
            )
            .order_by(desc(ImmutableLogEntry.timestamp))
            .limit(limit)
        )
        
        entries = result.scalars().all()
        
        fixes = []
        for entry in entries:
            fixes.append({
                'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
                'actor': entry.actor,
                'action': entry.action,
                'resource': entry.resource,
                'subsystem': entry.subsystem,
                'result': entry.result
            })
        
        return {
            'fixes': fixes,
            'count': len(fixes)
        }


@router.get("/errors/detected")
async def get_detected_errors(limit: int = 50) -> Dict[str, Any]:
    """Get errors detected by healing systems"""
    
    from ..immutable_log import ImmutableLog
    from ..models import async_session
    from ..governance_models import ImmutableLogEntry
    from sqlalchemy import select, desc
    
    async with async_session() as session:
        # Get error detection events
        result = await session.execute(
            select(ImmutableLogEntry)
            .where(ImmutableLogEntry.action.like('%error%'))
            .order_by(desc(ImmutableLogEntry.timestamp))
            .limit(limit)
        )
        
        entries = result.scalars().all()
        
        errors = []
        for entry in entries:
            errors.append({
                'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
                'actor': entry.actor,
                'action': entry.action,
                'resource': entry.resource,
                'subsystem': entry.subsystem,
                'result': entry.result
            })
        
        return {
            'errors': errors,
            'count': len(errors)
        }


@router.post("/scan-now")
async def trigger_immediate_scan() -> Dict[str, str]:
    """Trigger immediate log scan (instead of waiting for interval)"""
    
    from ..log_based_healer import log_based_healer
    
    if not log_based_healer.running:
        return {
            "status": "error",
            "message": "Log healer not running"
        }
    
    # Trigger immediate scan
    await log_based_healer._scan_logs()
    
    return {
        "status": "success",
        "message": "Log scan triggered"
    }
