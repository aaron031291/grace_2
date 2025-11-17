"""
ML Systems API
Endpoints for monitoring and controlling ML/AI systems
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime

from ..causal_playbook_reinforcement import causal_rl_agent
from ..temporal_forecasting import temporal_forecaster, ForecastRequest

router = APIRouter(prefix="/api/ml", tags=["ml_systems"])


class TrainingRequest(BaseModel):
    """Request to train forecasting model"""
    metric_data: Dict[str, List[float]]


class ForecastRequestModel(BaseModel):
    """Request for temporal forecast"""
    metric_ids: List[str]
    horizon_minutes: int = 60
    include_trust_signals: bool = True
    include_learning_signals: bool = True


@router.get("/causal-rl/statistics")
async def get_causal_rl_stats():
    """Get statistics about causal RL agent"""
    stats = causal_rl_agent.get_statistics()
    return {
        "status": "operational",
        "statistics": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/causal-rl/policies")
async def get_learned_policies():
    """Get all learned playbook policies"""
    policies = await causal_rl_agent.summarise_policy()
    return {
        "policies": policies,
        "total_contexts": len(policies),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/causal-rl/recommend")
async def recommend_playbook(
    service: str = Query(..., description="Service name"),
    diagnosis: str = Query(..., description="Diagnosis code"),
    candidates: str = Query(..., description="Comma-separated playbook IDs")
):
    """Get playbook recommendations based on learned policy"""
    candidate_list = [c.strip() for c in candidates.split(",")]
    
    recommendations = await causal_rl_agent.recommend(
        service=service,
        diagnosis_code=diagnosis,
        candidates=candidate_list
    )
    
    return {
        "service": service,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
        "total_candidates": len(candidate_list),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/forecaster/statistics")
async def get_forecaster_stats():
    """Get statistics about temporal forecaster"""
    stats = temporal_forecaster.get_statistics()
    return {
        "status": "operational",
        "statistics": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/forecaster/train")
async def train_forecaster(request: TrainingRequest):
    """Train the temporal forecaster on metric data"""
    try:
        await temporal_forecaster.train(request.metric_data)
        
        stats = temporal_forecaster.get_statistics()
        
        return {
            "status": "success",
            "message": f"Trained on {len(request.metric_data)} metrics",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/forecaster/predict")
async def forecast_metrics(request: ForecastRequestModel):
    """Generate temporal forecasts for metrics"""
    try:
        forecast_request = ForecastRequest(
            metric_ids=request.metric_ids,
            horizon_minutes=request.horizon_minutes,
            include_trust_signals=request.include_trust_signals,
            include_learning_signals=request.include_learning_signals
        )
        
        results = await temporal_forecaster.forecast(forecast_request)
        
        return {
            "status": "success",
            "forecasts": [
                {
                    "metric_id": r.metric_id,
                    "horizon_minutes": request.horizon_minutes,
                    "predicted_values": r.predicted_values,
                    "confidence": r.confidence,
                    "lower_bound": r.lower_bound,
                    "upper_bound": r.upper_bound,
                    "feature_importance": r.feature_importance
                }
                for r in results
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("/dashboard")
async def get_ml_dashboard():
    """Get comprehensive ML systems dashboard data"""
    rl_stats = causal_rl_agent.get_statistics()
    fc_stats = temporal_forecaster.get_statistics()
    policies = await causal_rl_agent.summarise_policy()
    
    return {
        "causal_rl": {
            "statistics": rl_stats,
            "policy_count": len(policies),
            "top_policies": {
                k: v for k, v in list(policies.items())[:5]
            } if policies else {}
        },
        "temporal_forecaster": {
            "statistics": fc_stats,
            "model_status": "trained" if fc_stats.get("model_trained") else "untrained"
        },
        "system_status": {
            "causal_rl_operational": rl_stats["total_policies"] >= 0,
            "forecaster_operational": fc_stats["model_loaded"],
            "total_learned_experiences": rl_stats["total_experiences"],
            "total_forecasting_metrics": fc_stats["metrics_learned"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health")
async def ml_systems_health():
    """Health check for ML systems"""
    try:
        rl_stats = causal_rl_agent.get_statistics()
        fc_stats = temporal_forecaster.get_statistics()
        
        return {
            "status": "healthy",
            "components": {
                "causal_rl": "operational",
                "temporal_forecaster": "operational" if fc_stats["model_loaded"] else "initializing"
            },
            "metrics": {
                "policies_learned": rl_stats["total_policies"],
                "experiences_recorded": rl_stats["total_experiences"],
                "metrics_trained": fc_stats["metrics_learned"]
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
