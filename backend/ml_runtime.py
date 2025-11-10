"""ML Runtime for model storage, loading, and deployment"""

import os
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from .ml_models_table import MLModel
from .models import async_session

class ModelRegistry:
    """Registry for storing and loading trained models"""
    
    def __init__(self, storage_path: str = "ml_artifacts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self._loaded_models: Dict[str, Any] = {}
    
    def _get_model_path(self, model_id: int) -> Path:
        """Get file path for model artifact"""
        return self.storage_path / f"model_{model_id}.pkl"
    
    def _get_metadata_path(self, model_id: int) -> Path:
        """Get file path for model metadata"""
        return self.storage_path / f"model_{model_id}_meta.json"
    
    async def save_model(self, model_id: int, model_artifact: Any, metadata: Dict = None) -> str:
        """Save trained model to disk"""
        
        model_path = self._get_model_path(model_id)
        meta_path = self._get_metadata_path(model_id)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_artifact, f)
        
        metadata = metadata or {}
        metadata['saved_at'] = datetime.utcnow().isoformat()
        metadata['model_id'] = model_id
        
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if model:
                model.signature = str(model_path)
                await session.commit()
        
        print(f"✓ Model artifact saved: {model_path}")
        return str(model_path)
    
    async def load_model(self, model_id: int) -> Optional[Any]:
        """Load model artifact from disk"""
        
        model_path = self._get_model_path(model_id)
        
        if not model_path.exists():
            print(f"⚠️ Model artifact not found: {model_path}")
            return None
        
        with open(model_path, 'rb') as f:
            model_artifact = pickle.load(f)
        
        self._loaded_models[f"model_{model_id}"] = model_artifact
        print(f"✓ Model loaded: {model_id}")
        return model_artifact
    
    async def load_latest_model(self, model_type: str) -> Optional[tuple]:
        """Load latest deployed model of given type"""
        
        async with async_session() as session:
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model_type)
                .where(MLModel.deployment_status == "deployed")
                .order_by(MLModel.deployed_at.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()
            
            if not model:
                print(f"⚠️ No deployed model found for type: {model_type}")
                return None
            
            artifact = await self.load_model(model.id)
            if not artifact:
                return None
            
            return model, artifact
    
    async def deploy_model(self, model_id: int, actor: str = "system") -> bool:
        """Deploy model with verification checks"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                print(f"⚠️ Model not found: {model_id}")
                return False
            
            model_path = self._get_model_path(model_id)
            if not model_path.exists():
                print(f"⚠️ Model artifact missing: {model_path}")
                return False
            
            if model.accuracy is None:
                print(f"⚠️ Model accuracy not evaluated")
                return False
            
            if model.accuracy < 0.6:
                print(f"⚠️ Model accuracy too low: {model.accuracy}")
                return False
            
            if model.training_data_count < 10:
                print(f"⚠️ Insufficient training samples: {model.training_data_count}")
                return False
            
            from .governance import governance_engine
            decision = await governance_engine.check(
                actor=actor,
                action="ml_deploy",
                resource=model.model_name,
                payload={"model_id": model_id, "accuracy": model.accuracy}
            )
            
            if decision["decision"] != "allow":
                print(f"⚠️ Deployment blocked by governance: {decision['policy']}")
                return False
            
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model.model_type)
                .where(MLModel.deployment_status == "deployed")
            )
            currently_deployed = result.scalars().all()
            
            for prev_model in currently_deployed:
                prev_model.deployment_status = "deprecated"
                prev_model.deprecated_at = datetime.utcnow()
            
            model.deployment_status = "deployed"
            model.deployed_at = datetime.utcnow()
            model.approved_by = actor
            model.verification_status = "verified"
            
            await session.commit()
        
        from .mldl import mldl_manager
        await mldl_manager.log_training_event(
            model_name=model.model_name,
            event_type="model_deployed",
            accuracy=model.accuracy,
            actor=actor
        )
        
        print(f"✓ Model deployed: {model.model_name} v{model.version} (ID: {model_id})")
        return True
    
    async def rollback_model(self, model_type: str, actor: str = "system") -> bool:
        """Rollback to previous deployed version"""
        
        async with async_session() as session:
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model_type)
                .where(MLModel.deployment_status == "deployed")
            )
            current = result.scalar_one_or_none()
            
            if not current:
                print(f"⚠️ No deployed model to rollback: {model_type}")
                return False
            
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model_type)
                .where(MLModel.deployment_status == "deprecated")
                .order_by(MLModel.deprecated_at.desc())
                .limit(1)
            )
            previous = result.scalar_one_or_none()
            
            if not previous:
                print(f"⚠️ No previous version to rollback to: {model_type}")
                return False
            
            from .governance import governance_engine
            decision = await governance_engine.check(
                actor=actor,
                action="ml_rollback",
                resource=model_type,
                payload={"from_id": current.id, "to_id": previous.id}
            )
            
            if decision["decision"] != "allow":
                print(f"⚠️ Rollback blocked by governance: {decision['policy']}")
                return False
            
            current.deployment_status = "deprecated"
            current.deprecated_at = datetime.utcnow()
            
            previous.deployment_status = "deployed"
            previous.deployed_at = datetime.utcnow()
            previous.approved_by = actor
            
            await session.commit()
        
        from .mldl import mldl_manager
        await mldl_manager.log_training_event(
            model_name=previous.model_name,
            event_type="model_rollback",
            accuracy=previous.accuracy,
            actor=actor
        )
        
        print(f"✓ Rolled back: {model_type} to v{previous.version} (ID: {previous.id})")
        return True

model_registry = ModelRegistry()
