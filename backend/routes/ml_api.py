from fastapi import APIRouter, Depends
from sqlalchemy import select
from ..auth import get_current_user
from ..ml_models_table import MLModel
from ..models import async_session
from ..training_pipeline import training_pipeline
from ..verification_middleware import verify_action
router = APIRouter(prefix="/api/ml", tags=["machine_learning"])

@router.post("/train")
@verify_action("ml_train", lambda data: data.get("model_name", "unknown"))
async def train_model(
    model_name: str,
    model_type: str = "classifier",
    trust_threshold: float = 70.0,
    current_user: str = Depends(get_current_user)
):
    """Train model from trusted knowledge"""
    model_id = await training_pipeline.train_model(
        model_name,
        model_type,
        trust_threshold,
        current_user
    )
    
    if model_id:
        return {"status": "trained", "model_id": model_id}
    else:
        return {"status": "blocked", "message": "Training blocked by governance"}

@router.post("/deploy/{model_id}")
@verify_action("ml_deploy", lambda data: f"model_{data.get('model_id', 'unknown')}")
async def deploy_model(
    model_id: int,
    current_user: str = Depends(get_current_user)
):
    """Deploy trained model"""
    success = await training_pipeline.deploy_model(model_id, current_user)
    return {"status": "deployed" if success else "blocked"}

@router.get("/models")
async def list_models():
    """List all trained models"""
    async with async_session() as session:
        result = await session.execute(
            select(MLModel).order_by(MLModel.created_at.desc())
        )
        return [
            {
                "id": m.id,
                "name": m.model_name,
                "version": m.version,
                "type": m.model_type,
                "accuracy": m.accuracy,
                "deployment_status": m.deployment_status,
                "created_at": m.created_at
            }
            for m in result.scalars().all()
        ]
        return MLModelsListResponse(
            models=models,
            count=len(models),
            execution_trace=None,
            data_provenance=[]
        )
