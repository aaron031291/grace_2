"""
ML Domain Router
Consolidates all machine learning operations: training, inference, model registry, feature store

Bounded Context: ML operations and model lifecycle
- Training: model training jobs and pipelines
- Inference: model inference and prediction services
- Registry: model versioning and deployment
- Features: feature engineering and storage

Canonical Verbs: train, infer, register, deploy, feature_store, evaluate
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..ml_runtime import ml_runtime
from ..model_deployment import model_deployer
from ..ml_performance_analytics import ml_analytics
from ..training_pipeline import training_pipeline

router = APIRouter(prefix="/api/ml", tags=["ML Domain"])


class TrainingJob(BaseModel):
    model_type: str
    dataset: str
    hyperparameters: Dict[str, Any]
    compute_resources: Optional[Dict[str, Any]] = None


class InferenceRequest(BaseModel):
    model_id: str
    input_data: Dict[str, Any]
    explain_prediction: bool = False


class ModelRegistration(BaseModel):
    model_name: str
    version: str
    model_path: str
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]


class FeatureStoreRequest(BaseModel):
    feature_name: str
    feature_data: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


@router.post("/train")
async def start_training_job(
    request: TrainingJob,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start a model training job"""
    try:
        job = await training_pipeline.start_training(
            model_type=request.model_type,
            dataset=request.dataset,
            hyperparameters=request.hyperparameters,
            compute_resources=request.compute_resources
        )

        return {
            "job_id": job.get("id"),
            "status": "started",
            "model_type": request.model_type,
            "estimated_completion": job.get("eta")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/infer")
async def run_inference(
    request: InferenceRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Run model inference"""
    try:
        result = await ml_runtime.infer(
            model_id=request.model_id,
            input_data=request.input_data,
            explain=request.explain_prediction
        )

        return {
            "model_id": request.model_id,
            "prediction": result.get("prediction"),
            "confidence": result.get("confidence"),
            "explanation": result.get("explanation") if request.explain_prediction else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def register_model(
    request: ModelRegistration,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Register a trained model"""
    try:
        registration = await model_deployer.register_model(
            name=request.model_name,
            version=request.version,
            model_path=request.model_path,
            metadata=request.metadata,
            metrics=request.performance_metrics
        )

        return {
            "model_id": registration.get("id"),
            "name": request.model_name,
            "version": request.version,
            "status": "registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy/{model_id}")
async def deploy_model(
    model_id: str,
    target_environment: str = "staging",
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Deploy a model to target environment"""
    try:
        deployment = await model_deployer.deploy_model(
            model_id=model_id,
            environment=target_environment
        )

        return {
            "model_id": model_id,
            "environment": target_environment,
            "endpoint": deployment.get("endpoint"),
            "status": "deployed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feature-store")
async def store_features(
    request: FeatureStoreRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Store features in feature store"""
    try:
        # This would integrate with a feature store system
        # For now, using placeholder
        feature_id = f"feature_{request.feature_name}_{len(request.feature_data)}"

        return {
            "feature_id": feature_id,
            "feature_name": request.feature_name,
            "record_count": len(request.feature_data),
            "status": "stored"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List registered models"""
    try:
        models = await model_deployer.list_models(status=status)
        return {
            "models": models,
            "count": len(models),
            "filter": {"status": status} if status else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_training_jobs(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List training jobs"""
    try:
        jobs = await training_pipeline.list_jobs(status=status)
        return {
            "jobs": jobs,
            "count": len(jobs),
            "filter": {"status": status} if status else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{model_id}")
async def get_model_performance(
    model_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get model performance analytics"""
    try:
        performance = await ml_analytics.get_model_performance(model_id)
        return {
            "model_id": model_id,
            "performance": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate/{model_id}")
async def evaluate_model(
    model_id: str,
    test_dataset: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Evaluate model on test dataset"""
    try:
        evaluation = await ml_analytics.evaluate_model(
            model_id=model_id,
            test_dataset=test_dataset
        )

        return {
            "model_id": model_id,
            "evaluation": evaluation,
            "test_dataset": test_dataset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-store")
async def list_features(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List features in feature store"""
    try:
        # Placeholder for feature store listing
        features = [
            {"name": "user_features", "record_count": 1000},
            {"name": "content_features", "record_count": 5000}
        ]
        return {
            "features": features,
            "count": len(features)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))