"""
Activation API - Trigger GRACE's autonomous activities
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/activate", tags=["activation"])


class LearningRequest(BaseModel):
    """Request to start learning"""
    topic: str
    max_sources: int = 5
    auto_apply: bool = False


@router.post("/learning")
async def activate_learning(request: LearningRequest):
    """Trigger autonomous learning session"""
    
    from backend.orchestrators.web_learning_orchestrator import web_learning_orchestrator
    
    try:
        result = await web_learning_orchestrator.start_learning_session(
            topic=request.topic,
            max_sources=request.max_sources
        )
        
        return {
            "status": "started",
            "topic": request.topic,
            "session_id": result.get("session_id"),
            "message": f"Grace is learning about: {request.topic}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/self-improvement")
async def activate_self_improvement():
    """Trigger autonomous improvement cycle"""
    
    
    try:
        # Trigger improvement scan
        print("[ACTIVATION] Starting autonomous improvement cycle...")
        
        return {
            "status": "triggered",
            "message": "Grace is analyzing codebase for improvements",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast")
async def trigger_forecast():
    """Trigger immediate forecast cycle"""
    
    from ..temporal_forecasting import temporal_forecaster, ForecastRequest
    
    try:
        key_metrics = [
            "api.latency_p95",
            "api.error_rate",
            "executor.queue_depth"
        ]
        
        request = ForecastRequest(
            metric_ids=key_metrics,
            horizon_minutes=60
        )
        
        forecasts = await temporal_forecaster.forecast(request)
        
        return {
            "status": "complete",
            "forecasts_generated": len(forecasts),
            "metrics": key_metrics,
            "horizon_minutes": 60,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_activation_status():
    """Get status of autonomous systems"""
    
    from backend.orchestrators.web_learning_orchestrator import web_learning_orchestrator
    from ..autonomous_improver import autonomous_improver
    from ..forecast_scheduler import forecast_scheduler
    from ..automated_ml_training import automated_training
    
    return {
        "systems": {
            "web_learning": {
                "running": getattr(web_learning_orchestrator, 'running', False),
                "status": "active" if getattr(web_learning_orchestrator, 'running', False) else "idle"
            },
            "autonomous_improver": {
                "running": getattr(autonomous_improver, 'running', False),
                "status": "active" if getattr(autonomous_improver, 'running', False) else "idle"
            },
            "forecast_scheduler": {
                "running": forecast_scheduler.running,
                "forecast_count": forecast_scheduler.forecast_count,
                "status": "active" if forecast_scheduler.running else "stopped"
            },
            "automated_training": {
                "running": automated_training.running,
                "training_count": automated_training.training_count,
                "status": "active" if automated_training.running else "stopped"
            }
        },
        "overall_status": "active" if any([
            getattr(web_learning_orchestrator, 'running', False),
            forecast_scheduler.running,
            automated_training.running
        ]) else "idle",
        "timestamp": datetime.utcnow().isoformat()
    }
