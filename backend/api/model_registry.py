"""
Model Registry API
Manage ML/DL models with deployment stages, metrics, and governance
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dataclasses import asdict
from datetime import datetime

router = APIRouter(prefix="/model-registry", tags=["Model Registry"])


class ModelRegistrationRequest(BaseModel):
    model_id: str
    name: str
    version: str
    framework: str
    model_type: str
    owner: str
    team: str
    training_data_hash: str
    training_dataset_size: int
    evaluation_metrics: Dict[str, float]
    description: Optional[str] = None
    tags: List[str] = []


class DeploymentUpdateRequest(BaseModel):
    status: str  # development, sandbox, canary, production
    canary_percentage: float = 0.0


@router.get("/models")
async def list_models(
    stage: Optional[str] = None,
    framework: Optional[str] = None,
    tags: Optional[str] = None
) -> Dict[str, Any]:
    """List all registered models with optional filtering"""
    from backend.services.model_registry import get_registry, DeploymentStage
    
    registry = get_registry()
    
    # Convert filters
    deploy_status = DeploymentStage(stage) if stage else None
    tag_list = tags.split(',') if tags else None
    
    models = registry.list_models(deploy_status, framework, tag_list)
    
    return {
        "models": [asdict(m) for m in models],
        "count": len(models)
    }


@router.get("/models/{model_id}")
async def get_model(model_id: str) -> Dict[str, Any]:
    """Get specific model details"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    entry = registry.get_model(model_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {"model": asdict(entry)}


@router.post("/models")
async def register_model(request: ModelRegistrationRequest):
    """Register a new model"""
    from backend.services.model_registry import get_registry, ModelRegistryEntry, DeploymentStage
    
    registry = get_registry()
    
    entry = ModelRegistryEntry(
        model_id=request.model_id,
        name=request.name,
        version=request.version,
        artifact_path=f"models/{request.model_id}.pkl",
        framework=request.framework,
        model_type=request.model_type,
        owner=request.owner,
        team=request.team,
        training_data_hash=request.training_data_hash,
        training_dataset_size=request.training_dataset_size,
        training_timestamp=datetime.now(),
        evaluation_metrics=request.evaluation_metrics,
        deploy_status=DeploymentStage.DEVELOPMENT,
        tags=request.tags,
        description=request.description or ""
    )
    
    success = registry.register_model(entry)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to register model")
    
    return {
        "status": "registered",
        "model_id": request.model_id,
        "message": f"Model {request.name} v{request.version} registered"
    }


@router.patch("/models/{model_id}/deployment")
async def update_deployment(model_id: str, request: DeploymentUpdateRequest):
    """Update model deployment status"""
    from backend.services.model_registry import get_registry, DeploymentStage
    
    registry = get_registry()
    
    try:
        new_status = DeploymentStage(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid deployment status: {request.status}")
    
    # Check governance before promoting
    if new_status in [DeploymentStage.CANARY, DeploymentStage.PRODUCTION]:
        entry = registry.get_model(model_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Model not found")
        
        if not entry.constitutional_compliance:
            raise HTTPException(
                status_code=403,
                detail="Cannot promote: Model has not passed constitutional compliance checks"
            )
        
        if not entry.bias_check_passed:
            raise HTTPException(
                status_code=403,
                detail="Cannot promote: Model has not passed bias checks"
            )
    
    success = registry.update_deployment_status(
        model_id,
        new_status,
        request.canary_percentage
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Log to immutable log
    try:
        from backend.clarity import get_event_bus, Event
        bus = get_event_bus()
        await bus.publish(Event(
            event_type="model.deployment.updated",
            source="model_registry",
            payload={
                "model_id": model_id,
                "new_status": request.status,
                "canary_percentage": request.canary_percentage
            }
        ))
    except Exception:
        pass
    
    return {
        "status": "updated",
        "model_id": model_id,
        "deployment_status": request.status
    }


@router.post("/models/{model_id}/generate-card")
async def generate_model_card(model_id: str):
    """Generate model card documentation"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    
    try:
        card_path = registry.generate_model_card(model_id)
        return {
            "status": "generated",
            "model_card_path": card_path
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{model_id}/rollback-check")
async def check_rollback(model_id: str, window_minutes: int = 10, auto_remediate: bool = False):
    """Check if model should be rolled back based on performance"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    
    should_rollback, reasons = await registry.check_rollback_triggers(
        model_id, 
        window_minutes,
        auto_remediate=auto_remediate
    )
    
    return {
        "model_id": model_id,
        "should_rollback": should_rollback,
        "reasons": reasons,
        "window_minutes": window_minutes,
        "auto_remediate": auto_remediate
    }


@router.post("/models/{model_id}/rollback")
async def rollback_model(model_id: str, reason: str, target_version: Optional[str] = None):
    """Rollback a model to previous version"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    
    success = await registry.perform_rollback(model_id, target_version)
    
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "status": "rolled_back",
        "model_id": model_id,
        "reason": reason,
        "target_version": target_version or "previous"
    }


@router.get("/stats")
async def get_registry_stats():
    """Get model registry statistics"""
    from backend.services.model_registry import get_registry, DeploymentStage
    
    registry = get_registry()
    
    all_models = list(registry.models.values())
    
    return {
        "total_models": len(all_models),
        "by_stage": {
            "development": len([m for m in all_models if m.deploy_status == DeploymentStage.DEVELOPMENT]),
            "sandbox": len([m for m in all_models if m.deploy_status == DeploymentStage.SANDBOX]),
            "canary": len([m for m in all_models if m.deploy_status == DeploymentStage.CANARY]),
            "production": len([m for m in all_models if m.deploy_status == DeploymentStage.PRODUCTION]),
            "rollback": len([m for m in all_models if m.deploy_status == DeploymentStage.ROLLBACK]),
        },
        "by_framework": {
            "pytorch": len([m for m in all_models if m.framework == "pytorch"]),
            "sklearn": len([m for m in all_models if m.framework == "sklearn"]),
            "tensorflow": len([m for m in all_models if m.framework == "tensorflow"]),
        },
        "governance": {
            "constitutional_passed": len([m for m in all_models if m.constitutional_compliance]),
            "bias_passed": len([m for m in all_models if m.bias_check_passed]),
        }
    }


@router.get("/monitor/production")
async def monitor_production(window_minutes: int = 10):
    """Monitor all production models for health issues"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    results = await registry.monitor_production_models(window_minutes)
    
    return results


@router.get("/models/{model_id}/health")
async def get_model_health(model_id: str):
    """Get comprehensive health summary for a model"""
    from backend.services.model_registry import get_registry
    
    registry = get_registry()
    summary = registry.get_model_health_summary(model_id)
    
    if 'error' in summary:
        raise HTTPException(status_code=404, detail=summary['error'])
    
    return summary


class PerformanceSnapshotRequest(BaseModel):
    model_id: str
    version: str
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    requests_per_second: float
    error_rate: float = 0.0
    ood_rate: float = 0.0
    input_drift_score: Optional[float] = None
    accuracy: Optional[float] = None


@router.post("/models/{model_id}/performance")
async def record_performance(model_id: str, snapshot: PerformanceSnapshotRequest):
    """Record a performance snapshot for a model"""
    from backend.services.model_registry import get_registry, ModelPerformanceSnapshot
    
    registry = get_registry()
    
    perf_snapshot = ModelPerformanceSnapshot(
        model_id=model_id,
        version=snapshot.version,
        timestamp=datetime.now(),
        latency_p50_ms=snapshot.latency_p50_ms,
        latency_p95_ms=snapshot.latency_p95_ms,
        latency_p99_ms=snapshot.latency_p99_ms,
        requests_per_second=snapshot.requests_per_second,
        error_rate=snapshot.error_rate,
        ood_rate=snapshot.ood_rate,
        input_drift_score=snapshot.input_drift_score,
        accuracy=snapshot.accuracy
    )
    
    await registry.record_performance_snapshot(perf_snapshot)
    
    return {
        "status": "recorded",
        "model_id": model_id,
        "timestamp": perf_snapshot.timestamp.isoformat()
    }
