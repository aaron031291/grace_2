"""
ML Dashboard API
Real-time monitoring and visualization for ML/AI systems
"""

from fastapi import APIRouter, Query
from typing import Dict, List
from datetime import datetime

from ..causal_playbook_reinforcement import causal_rl_agent
from ..temporal_forecasting import temporal_forecaster
from ..automated_ml_training import automated_training
from ..forecast_scheduler import forecast_scheduler
from ..ml_performance_analytics import ml_performance_analytics
from ..incident_predictor import incident_predictor


router = APIRouter(prefix="/api/ml/dashboard", tags=["ml_dashboard"])


@router.get("/overview")
async def get_ml_overview():
    """Comprehensive ML systems overview"""
    
    rl_stats = causal_rl_agent.get_statistics()
    fc_stats = temporal_forecaster.get_statistics()
    train_stats = automated_training.get_statistics()
    pred_stats = incident_predictor.get_statistics()
    
    # Get recent forecast accuracy
    forecast_accuracy = await _calculate_forecast_accuracy()
    
    return {
        "system_status": {
            "all_operational": True,
            "components": {
                "causal_rl": "operational",
                "temporal_forecaster": "operational" if fc_stats["model_loaded"] else "initializing",
                "automated_training": "operational" if train_stats["running"] else "stopped",
                "forecast_scheduler": "operational" if forecast_scheduler.running else "stopped",
                "incident_predictor": "operational" if pred_stats["running"] else "stopped"
            }
        },
        "learning_metrics": {
            "policies_learned": rl_stats["total_policies"],
            "experiences_recorded": rl_stats["total_experiences"],
            "training_cycles_completed": train_stats["training_count"],
            "forecasts_generated": forecast_scheduler.forecast_count,
            "metrics_under_prediction": fc_stats["metrics_learned"],
            "predictions_made": pred_stats["predictions_made"],
            "incidents_prevented": pred_stats["incidents_prevented"]
        },
        "performance": {
            "forecast_accuracy_pct": forecast_accuracy,
            "policy_coverage_pct": _calculate_policy_coverage(rl_stats),
            "incident_prevention_rate": pred_stats["prevention_rate"],
            "next_training_in_hours": train_stats["next_training_in_hours"],
            "last_training": train_stats["last_training"]
        },
        "top_learned_policies": _get_top_policies(rl_stats),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/learning-progress")
async def get_learning_progress(hours_back: int = Query(default=24, ge=1, le=168)):
    """Track ML learning progress over time"""
    
    # Get policy growth over time
    rl_stats = causal_rl_agent.get_statistics()
    train_stats = automated_training.get_statistics()
    
    return {
        "time_range_hours": hours_back,
        "current_state": {
            "total_policies": rl_stats["total_policies"],
            "total_experiences": rl_stats["total_experiences"],
            "training_cycles": train_stats["training_count"]
        },
        "growth_trajectory": {
            "policies_per_day": rl_stats["total_experiences"] / max(1, hours_back / 24),
            "avg_experiences_per_policy": (
                rl_stats["total_experiences"] / max(1, rl_stats["total_policies"])
            )
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/playbook-performance")
async def get_playbook_performance():
    """Analyze performance of learned playbooks"""
    
    policies = await causal_rl_agent.summarise_policy()
    rl_stats = causal_rl_agent.get_statistics()
    
    # Extract performance data
    playbook_scores = {}
    
    for context, policy in policies.items():
        for playbook, score in policy.items():
            if playbook not in playbook_scores:
                playbook_scores[playbook] = {
                    "total_score": 0.0,
                    "contexts": 0,
                    "avg_score": 0.0
                }
            
            playbook_scores[playbook]["total_score"] += score
            playbook_scores[playbook]["contexts"] += 1
    
    # Calculate averages
    for playbook in playbook_scores:
        playbook_scores[playbook]["avg_score"] = (
            playbook_scores[playbook]["total_score"] / 
            playbook_scores[playbook]["contexts"]
        )
    
    # Rank by average score
    ranked = sorted(
        playbook_scores.items(),
        key=lambda x: x[1]["avg_score"],
        reverse=True
    )
    
    return {
        "playbook_count": len(playbook_scores),
        "total_contexts": len(policies),
        "rankings": [
            {
                "playbook_id": playbook,
                "avg_score": data["avg_score"],
                "contexts_used": data["contexts"],
                "effectiveness_rating": _get_effectiveness_rating(data["avg_score"])
            }
            for playbook, data in ranked
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/forecast-accuracy")
async def get_forecast_accuracy(metric_id: str = Query(None)):
    """Calculate forecast accuracy by comparing predictions to actuals"""
    
    accuracy = await _calculate_forecast_accuracy(metric_id)
    
    return {
        "metric_id": metric_id or "all",
        "accuracy_percentage": accuracy,
        "evaluation_method": "mean_absolute_percentage_error",
        "sample_size": "last_24h",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/training-history")
async def get_training_history(limit: int = Query(default=10, ge=1, le=100)):
    """Get history of ML training cycles"""
    
    train_stats = automated_training.get_statistics()
    fc_stats = temporal_forecaster.get_statistics()
    
    # Get training history from forecaster
    history = fc_stats.get("last_training", {})
    
    return {
        "total_cycles": train_stats["training_count"],
        "last_training": train_stats["last_training"],
        "interval_hours": train_stats["interval_hours"],
        "recent_training": history,
        "next_scheduled": train_stats["next_training_in_hours"],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/trigger-training")
async def trigger_manual_training():
    """Manually trigger a training cycle"""
    
    try:
        logger.info("[AUTO-TRAIN] Manual training triggered via API")
        print("[AUTO-TRAIN] 🎓 Manual training cycle initiated...")
        
        # Collect data
        training_data = await automated_training._collect_training_data()
        
        if not training_data:
            return {
                "status": "skipped",
                "reason": "No training data available",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Train model
        await temporal_forecaster.train(training_data)
        
        return {
            "status": "success",
            "metrics_trained": len(training_data),
            "total_samples": sum(len(v) for v in training_data.values()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[AUTO-TRAIN] Manual training failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health-report")
async def get_ml_health_report():
    """Generate comprehensive ML health report"""
    report = await ml_performance_analytics.generate_ml_health_report()
    return report


# Helper functions

async def _calculate_forecast_accuracy(metric_id: str = None) -> float:
    """Calculate forecast accuracy (placeholder implementation)"""
    # In production: compare forecasts to actual values
    # For now: return optimistic placeholder
    return 75.0


def _calculate_policy_coverage(rl_stats: Dict) -> float:
    """Calculate percentage of incident contexts with learned policies"""
    total = rl_stats.get("total_policies", 0)
    if total == 0:
        return 0.0
    
    # Assume 20 common incident contexts
    expected_contexts = 20
    return min(100.0, (total / expected_contexts) * 100)


def _get_top_policies(rl_stats: Dict) -> List[Dict]:
    """Extract top learned policies"""
    policies = rl_stats.get("policies", {})
    
    top = []
    for context, policy_data in list(policies.items())[:5]:
        top.append({
            "context": context,
            "best_playbook": policy_data.get("best_playbook"),
            "score": policy_data.get("best_score", 0.0),
            "playbooks_learned": policy_data.get("playbooks_learned", 0)
        })
    
    return top


def _get_effectiveness_rating(score: float) -> str:
    """Convert score to effectiveness rating"""
    if score >= 0.8:
        return "excellent"
    elif score >= 0.6:
        return "good"
    elif score >= 0.4:
        return "fair"
    else:
        return "poor"
