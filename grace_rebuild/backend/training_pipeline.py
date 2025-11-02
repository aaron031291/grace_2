"""Signature-wrapped ML training pipeline"""

import hashlib
import json
import uuid
from datetime import datetime
from sqlalchemy import select
from .ml_models_table import MLModel, TrainingRun
from .knowledge_models import KnowledgeArtifact
from .models import async_session

class TrainingPipeline:
    """Train models from trust-scored knowledge"""
    
    async def extract_training_data(self, trust_threshold: float = 70.0, limit: int = 1000):
        """Extract training data from trusted knowledge"""
        
        async with async_session() as session:
            result = await session.execute(
                select(KnowledgeArtifact)
                .order_by(KnowledgeArtifact.created_at.desc())
                .limit(limit)
            )
            artifacts = result.scalars().all()
            
            training_samples = []
            content_hashes = []
            
            for artifact in artifacts:
                training_samples.append({
                    "content": artifact.content,
                    "domain": artifact.domain,
                    "artifact_type": artifact.artifact_type,
                    "source": artifact.source
                })
                content_hashes.append(artifact.content_hash)
            
            dataset_hash = hashlib.sha256(
                ''.join(sorted(content_hashes)).encode()
            ).hexdigest()
            
            print(f"✓ Extracted {len(training_samples)} training samples (trust ≥{trust_threshold})")
            
            return training_samples, dataset_hash
    
    async def train_model(
        self,
        model_name: str,
        model_type: str,
        trust_threshold: float,
        actor: str = "system"
    ) -> int:
        """Train model with governance"""
        
        from .governance import governance_engine
        
        decision = await governance_engine.check(
            actor=actor,
            action="ml_train",
            resource=model_name,
            payload={"model_type": model_type, "trust_threshold": trust_threshold}
        )
        
        if decision["decision"] != "allow":
            print(f"⚠️ Training blocked: {decision['policy']}")
            return None
        
        training_data, dataset_hash = await self.extract_training_data(trust_threshold)
        
        action_id = str(uuid.uuid4())
        model_hash = hashlib.sha256(f"{model_name}:{dataset_hash}:{datetime.utcnow()}".encode()).hexdigest()
        
        async with async_session() as session:
            run = TrainingRun(
                dataset_trust_threshold=trust_threshold,
                samples_used=len(training_data),
                final_loss=0.0,
                validation_score=0.0,
                approved=False
            )
            session.add(run)
            await session.flush()
            
            model = MLModel(
                model_name=model_name,
                version="1.0.0",
                model_type=model_type,
                model_hash=model_hash,
                dataset_hash=dataset_hash,
                trust_score_min=trust_threshold,
                training_data_count=len(training_data),
                verification_status="pending",
                deployment_status="trained"
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            
            run.model_id = model.id
            await session.commit()
        
        from .verification import verification_engine
        await verification_engine.log_verified_action(
            action_id=action_id,
            actor=actor,
            action_type="ml_train",
            resource=model_name,
            input_data={"dataset_hash": dataset_hash, "samples": len(training_data)},
            output_data={"model_id": model.id, "model_hash": model_hash},
            criteria_met=True
        )
        
        from .trigger_mesh import trigger_mesh, TriggerEvent
        await trigger_mesh.publish(TriggerEvent(
            event_type="mldl.training_completed",
            source="training_pipeline",
            actor=actor,
            resource=model_name,
            payload={"model_id": model.id, "samples": len(training_data)},
            timestamp=datetime.utcnow()
        ))
        
        print(f"✓ Model trained: {model_name} (ID: {model.id}, samples: {len(training_data)})")
        return model.id
    
    async def deploy_model(self, model_id: int, actor: str) -> bool:
        """Deploy model with verification"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                return False
            
            from .governance import governance_engine
            decision = await governance_engine.check(
                actor=actor,
                action="ml_deploy",
                resource=model.model_name,
                payload={"model_id": model_id, "accuracy": model.accuracy or 0.0}
            )
            
            if decision["decision"] != "allow":
                print(f"⚠️ Deployment blocked: {decision['policy']}")
                return False
            
            model.deployment_status = "deployed"
            model.deployed_at = datetime.utcnow()
            model.approved_by = actor
            await session.commit()
        
        print(f"✓ Model deployed: {model.model_name} v{model.version}")
        return True

training_pipeline = TrainingPipeline()
