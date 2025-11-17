"""
Autonomous Healing Dashboard API
Monitor all three healing systems: Code Healer, Log Healer, Resilient Startup
"""

from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/healing", tags=["Autonomous Healing"])


class AutonomyTierRequest(BaseModel):
    """Request to change autonomy tier"""
    tier: int  # 0-3


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
    
    from ..models import async_session
    from ..base_models import ImmutableLogEntry
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
    
    from ..models import async_session
    from ..base_models import ImmutableLogEntry
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


@router.get("/ml/insights")
async def get_ml_insights() -> Dict[str, Any]:
    """Get ML/DL learning insights about error patterns and fixes"""
    
    from ..ml_healing import ml_healing, dl_healing
    
    ml_insights = await ml_healing.get_insights()
    dl_insights = await dl_healing.get_insights()
    
    return {
        "machine_learning": ml_insights,
        "deep_learning": dl_insights,
        "combined_patterns": ml_insights.get('total_patterns_learned', 0)
    }


@router.get("/ml/predictions")
async def get_error_predictions() -> Dict[str, Any]:
    """Get ML predictions of likely errors"""
    
    from ..ml_healing import ml_healing
    
    # Get predictions for common error types
    error_types = ['incorrect_await', 'missing_attribute', 'json_serialization', 'missing_module']
    
    predictions = {}
    for error_type in error_types:
        likelihood = await ml_healing.predict_error_likelihood(error_type)
        predictions[error_type] = {
            'likelihood': likelihood,
            'confidence': 'high' if likelihood > 0.7 else 'medium' if likelihood > 0.3 else 'low'
        }
    
    return {
        "predictions": predictions,
        "model_info": ml_healing.prediction_model if ml_healing.prediction_model else "Not yet trained"
    }


@router.get("/ml/recommendations/{error_type}")
async def get_fix_recommendations(error_type: str) -> Dict[str, Any]:
    """Get ML-recommended fix strategy for error type"""
    
    from ..ml_healing import ml_healing
    
    recommendation = await ml_healing.recommend_fix_strategy(error_type)
    
    if not recommendation:
        return {
            "error_type": error_type,
            "recommendation": None,
            "message": "No historical data for this error type"
        }
    
    return {
        "error_type": error_type,
        "recommendation": recommendation
    }


@router.get("/autonomy/status")
async def get_autonomy_status() -> Dict[str, Any]:
    """Get full autonomy mode status"""
    
    from ..full_autonomy import full_autonomy
    
    return full_autonomy.get_status()


@router.post("/autonomy/enable")
async def enable_autonomy(request: AutonomyTierRequest) -> Dict[str, Any]:
    """Enable full autonomy mode"""
    
    from ..full_autonomy import full_autonomy
    
    success = await full_autonomy.enable(tier=request.tier)
    
    return {
        "enabled": success,
        "tier": request.tier,
        "status": full_autonomy.get_status()
    }


@router.post("/autonomy/disable")
async def disable_autonomy() -> Dict[str, str]:
    """Disable full autonomy mode"""
    
    from ..full_autonomy import full_autonomy
    
    await full_autonomy.disable()
    
    return {
        "status": "disabled",
        "message": "Full autonomy mode disabled"
    }


@router.get("/analytics/summary")
async def get_healing_analytics(hours: int = 24) -> Dict[str, Any]:
    """Get comprehensive healing analytics"""
    
    from ..healing_analytics import healing_analytics
    
    summary = await healing_analytics.get_healing_summary(hours)
    ml_stats = await healing_analytics.get_ml_learning_stats(hours)
    
    return {
        "healing": summary,
        "ml_learning": ml_stats,
        "period_hours": hours
    }


@router.get("/analytics/cube")
async def get_cube_analytics(
    dimension: str = "subsystem",
    metric: str = "count",
    hours: int = 24
) -> Dict[str, Any]:
    """Get data cube analytics"""
    
    from ..healing_analytics import healing_analytics
    
    return await healing_analytics.get_data_cube_analytics(dimension, metric, hours)


@router.get("/crypto/verify")
async def verify_crypto_chains() -> Dict[str, Any]:
    """Verify cryptographic chain integrity across all tables"""
    
    from ..healing_analytics import healing_analytics
    
    return await healing_analytics.get_crypto_verification_report()
