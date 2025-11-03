from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from ..models import async_session
from ..temporal_reasoning import temporal_reasoner
from ..simulation_engine import simulation_engine
from ..temporal_models import EventPattern, Simulation, DurationEstimate, TemporalAnomaly

router = APIRouter(prefix="/api/temporal", tags=["temporal"])

class PredictRequest(BaseModel):
    current_state: Dict[str, Any]
    lookback_hours: Optional[int] = 24

class SimulateRequest(BaseModel):
    action: Dict[str, Any]
    iterations: Optional[int] = 1000

class PlanRequest(BaseModel):
    goal: str
    max_steps: Optional[int] = 5

class ScenarioComparisonRequest(BaseModel):
    scenarios: List[Dict[str, Any]]

@router.post("/predict")
async def predict_next_events(request: PredictRequest):
    """Predict what events are likely to happen next"""
    try:
        await temporal_reasoner.initialize()
        
        predictions = await temporal_reasoner.predict_next_event(request.current_state)
        
        patterns = await temporal_reasoner.analyze_sequences(request.lookback_hours)
        
        return {
            "predictions": [
                {"event_type": event, "probability": prob}
                for event, prob in predictions
            ],
            "discovered_patterns": patterns[:5],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
async def simulate_action(request: SimulateRequest):
    """Run Monte Carlo simulation of proposed action"""
    try:
        result = await simulation_engine.simulate_action(
            request.action,
            request.iterations
        )
        
        return {
            "simulation_result": result,
            "action": request.action,
            "iterations": request.iterations,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patterns")
async def get_recurring_patterns(period: str = "daily"):
    """Get recurring temporal patterns"""
    try:
        await temporal_reasoner.initialize()
        
        patterns = await temporal_reasoner.find_recurring_patterns(period)
        
        async with async_session() as session:
            result = await session.execute(
                select(EventPattern).order_by(EventPattern.frequency.desc()).limit(10)
            )
            stored_patterns = result.scalars().all()
        
        return {
            "period": period,
            "active_patterns": patterns,
            "historical_patterns": [
                {
                    "id": p.id,
                    "pattern_type": p.pattern_type,
                    "sequence": p.sequence,
                    "frequency": p.frequency,
                    "confidence": p.confidence,
                    "avg_duration": p.avg_duration
                }
                for p in stored_patterns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plan")
async def plan_for_goal(request: PlanRequest):
    """Find action sequence to achieve goal"""
    try:
        plan = await simulation_engine.run_planning_simulation(
            request.goal,
            request.max_steps
        )
        
        return {
            "plan": plan,
            "goal": request.goal,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/durations")
async def get_duration_estimates(task_type: Optional[str] = None):
    """Get task duration estimates"""
    try:
        async with async_session() as session:
            if task_type:
                result = await session.execute(
                    select(DurationEstimate).where(DurationEstimate.task_type == task_type)
                )
                estimate = result.scalar_one_or_none()
                
                if not estimate:
                    default = await temporal_reasoner.estimate_duration(task_type)
                    return {
                        "task_type": task_type,
                        "estimate": default,
                        "source": "default"
                    }
                
                return {
                    "task_type": task_type,
                    "estimate": {
                        "avg_duration": estimate.avg_duration,
                        "std_deviation": estimate.std_deviation,
                        "min": estimate.min_duration,
                        "max": estimate.max_duration,
                        "confidence_interval": [
                            estimate.confidence_interval_lower,
                            estimate.confidence_interval_upper
                        ],
                        "sample_count": estimate.sample_count
                    },
                    "source": "historical"
                }
            else:
                result = await session.execute(select(DurationEstimate))
                estimates = result.scalars().all()
                
                return {
                    "estimates": [
                        {
                            "task_type": e.task_type,
                            "avg_duration": e.avg_duration,
                            "sample_count": e.sample_count
                        }
                        for e in estimates
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
async def get_timing_anomalies(hours: int = 24):
    """Detect anomalous timing events"""
    try:
        await temporal_reasoner.initialize()
        
        anomalies = await temporal_reasoner.detect_anomalous_timing(hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(TemporalAnomaly)
                .order_by(TemporalAnomaly.detected_at.desc())
                .limit(50)
            )
            stored_anomalies = result.scalars().all()
        
        return {
            "recent_anomalies": anomalies,
            "historical_anomalies": [
                {
                    "id": a.id,
                    "event_type": a.event_type,
                    "event_id": a.event_id,
                    "expected_duration": a.expected_duration,
                    "actual_duration": a.actual_duration,
                    "deviation_sigma": a.deviation_sigma,
                    "severity": a.severity,
                    "detected_at": a.detected_at.isoformat()
                }
                for a in stored_anomalies
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peak-load")
async def predict_peak_load():
    """Predict when system will be busiest"""
    try:
        await temporal_reasoner.initialize()
        
        prediction = await temporal_reasoner.predict_peak_load()
        
        return {
            "next_peak": prediction["next_peak_time"].isoformat() if prediction["next_peak_time"] else None,
            "patterns": prediction["patterns"],
            "recommendation": prediction["recommendation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preventive-actions")
async def get_preventive_actions():
    """Get suggested preventive actions based on patterns"""
    try:
        await temporal_reasoner.initialize()
        
        actions = await temporal_reasoner.suggest_preventive_actions()
        
        return {
            "suggestions": actions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-scenarios")
async def compare_scenarios(request: ScenarioComparisonRequest):
    """Compare multiple scenarios and recommend best"""
    try:
        comparison = await simulation_engine.simulate_scenarios(request.scenarios)
        
        return {
            "comparison": comparison,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulations/{simulation_id}")
async def get_simulation(simulation_id: int):
    """Get a specific simulation result"""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Simulation).where(Simulation.id == simulation_id)
            )
            sim = result.scalar_one_or_none()
            
            if not sim:
                raise HTTPException(status_code=404, detail="Simulation not found")
            
            return {
                "id": sim.id,
                "scenario": sim.scenario,
                "parameters": sim.parameters,
                "predicted_outcome": sim.predicted_outcome,
                "actual_outcome": sim.actual_outcome,
                "accuracy_score": sim.accuracy_score,
                "created_at": sim.created_at.isoformat()
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulations/{simulation_id}/actual")
async def record_actual_outcome(simulation_id: int, actual_outcome: Dict[str, Any]):
    """Record actual outcome and compare with prediction"""
    try:
        comparison = await simulation_engine.compare_prediction_vs_actual(
            simulation_id,
            actual_outcome
        )
        
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
