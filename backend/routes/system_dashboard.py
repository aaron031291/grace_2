"""
System Dashboard API
Complete overview of all Grace systems in one endpoint
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/system", tags=["System Dashboard"])


@router.get("/dashboard")
async def get_complete_dashboard() -> Dict[str, Any]:
    """Get complete system dashboard with all metrics"""
    
    from ..grace_log_reader import grace_log_reader
    from ..healing_analytics import healing_analytics
    from ..full_autonomy import full_autonomy
    from ..governance_framework import governance_framework
    from ..autonomous_code_healer import code_healer
    from ..log_based_healer import log_based_healer
    from ..ml_healing import ml_healing, dl_healing
    from ..auto_commit import auto_commit
    
    # Gather all data
    activity = await grace_log_reader.get_my_recent_activity(hours=24)
    healing_summary = await healing_analytics.get_healing_summary(hours=24)
    ml_stats = await healing_analytics.get_ml_learning_stats(hours=24)
    learning_progress = await grace_log_reader.get_my_learning_progress()
    autonomy_status = full_autonomy.get_status()
    governance_summary = governance_framework.get_summary()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "OPERATIONAL",
        
        "autonomy": autonomy_status,
        
        "governance": governance_summary,
        
        "healing": {
            "code_healer": await code_healer.get_status(),
            "log_healer": {
                "running": log_based_healer.running,
                "scan_interval": log_based_healer.scan_interval
            },
            "summary": healing_summary
        },
        
        "ml_dl": {
            "ml": await ml_healing.get_insights(),
            "dl": await dl_healing.get_insights(),
            "stats": ml_stats,
            "learning_progress": learning_progress
        },
        
        "activity_24h": activity,
        
        "auto_commit": auto_commit.get_status(),
        
        "recent_errors": await grace_log_reader.get_my_errors(hours=24, limit=5),
        "recent_successes": await grace_log_reader.get_my_successes(hours=24, limit=5)
    }


@router.get("/health/detailed")
async def get_detailed_health() -> Dict[str, Any]:
    """Detailed health check of all systems"""
    
    from ..autonomous_code_healer import code_healer
    from ..log_based_healer import log_based_healer
    from ..ml_healing import ml_healing, dl_healing
    from ..full_autonomy import full_autonomy
    
    systems = {
        "trigger_mesh": {"status": "operational", "component": "event_bus"},
        "code_healer": {"status": "operational" if code_healer.running else "stopped", "fixes": code_healer.fixes_applied},
        "log_healer": {"status": "operational" if log_based_healer.running else "stopped"},
        "ml_healing": {"status": "operational" if ml_healing.running else "stopped"},
        "dl_healing": {"status": "operational" if dl_healing.running else "stopped"},
        "autonomy": {"status": "enabled" if full_autonomy.enabled else "disabled", "tier": full_autonomy.autonomy_tier}
    }
    
    all_operational = all(s.get("status") in ["operational", "enabled"] for s in systems.values())
    
    return {
        "overall_status": "HEALTHY" if all_operational else "DEGRADED",
        "timestamp": datetime.utcnow().isoformat(),
        "systems": systems,
        "operational_count": sum(1 for s in systems.values() if s.get("status") in ["operational", "enabled"]),
        "total_count": len(systems)
    }


@router.get("/metrics/realtime")
async def get_realtime_metrics() -> Dict[str, Any]:
    """Get real-time metrics for monitoring"""
    
    from ..models import async_session
    from ..healing_models import DataCubeEntry
    from sqlalchemy import select, func
    from datetime import timedelta
    
    # Last 1 hour metrics
    since = datetime.utcnow() - timedelta(hours=1)
    
    async with async_session() as session:
        # Activity count
        result = await session.execute(
            select(func.count(DataCubeEntry.id))
            .where(DataCubeEntry.dimension_time >= since)
        )
        activity_count = result.scalar() or 0
        
        # Error count
        result = await session.execute(
            select(func.count(DataCubeEntry.id))
            .where(DataCubeEntry.dimension_time >= since)
            .where(DataCubeEntry.metric_error_count > 0)
        )
        error_count = result.scalar() or 0
        
        # Fix count
        result = await session.execute(
            select(func.count(DataCubeEntry.id))
            .where(DataCubeEntry.dimension_time >= since)
            .where(DataCubeEntry.metric_fix_count > 0)
        )
        fix_count = result.scalar() or 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "period_minutes": 60,
        "metrics": {
            "total_activity": activity_count,
            "errors_detected": error_count,
            "fixes_applied": fix_count,
            "activity_rate": activity_count / 60,  # per minute
            "fix_rate": fix_count / 60 if error_count > 0 else 0
        }
    }


@router.post("/export/all")
async def export_all_data(format: str = "json") -> Dict[str, str]:
    """Export all Grace data for backup"""
    
    from ..data_export import data_exporter
    
    export_path = await data_exporter.export_all(format=format)
    
    return {
        "status": "success",
        "export_path": export_path,
        "format": format
    }


@router.post("/export/learning")
async def export_learning_data() -> Dict[str, str]:
    """Export ML/DL learning data only"""
    
    from ..data_export import data_exporter
    
    export_path = await data_exporter.export_learning_only()
    
    return {
        "status": "success",
        "export_path": export_path
    }


@router.post("/backup/crypto")
async def backup_crypto_chains() -> Dict[str, str]:
    """Backup cryptographic chains"""
    
    from ..data_export import data_exporter
    
    backup_path = await data_exporter.backup_crypto_chains()
    
    return {
        "status": "success",
        "backup_path": backup_path
    }
