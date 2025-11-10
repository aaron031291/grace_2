"""Model deployment pipeline with governance and verification"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from .ml_models_table import MLModel
from .models import async_session
from .governance import governance_engine
from .mldl import mldl_manager, MLEvent

class ModelDeploymentPipeline:
    """End-to-end deployment: train -> verify -> approve -> deploy"""
    
    def __init__(self):
        self.min_accuracy_threshold = 0.6
        self.min_test_samples = 10
        self.improvement_threshold = 0.05
    
    async def verify_model_metrics(self, model_id: int) -> tuple[bool, str]:
        """Verify model meets deployment criteria"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                return False, "Model not found"
            
            if model.accuracy is None:
                return False, "Model accuracy not evaluated"
            
            if model.accuracy < self.min_accuracy_threshold:
                return False, f"Accuracy {model.accuracy:.2f} below threshold {self.min_accuracy_threshold}"
            
            if model.training_data_count < self.min_test_samples:
                return False, f"Only {model.training_data_count} samples, need {self.min_test_samples}"
            
            from .ml_runtime import model_registry
            model_path = model_registry._get_model_path(model_id)
            if not model_path.exists():
                return False, "Model artifact file missing"
            
            return True, "All verification checks passed"
    
    async def request_governance_approval(
        self,
        model_id: int,
        actor: str,
        reason: str = "deployment"
    ) -> tuple[bool, str]:
        """Request governance approval for production deployment"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                return False, "Model not found"
            
            decision = await governance_engine.check(
                actor=actor,
                action="ml_deploy",
                resource=model.model_name,
                payload={
                    "model_id": model_id,
                    "accuracy": model.accuracy or 0.0,
                    "reason": reason
                }
            )
            
            if decision["decision"] != "allow":
                return False, f"Governance denied: {decision['policy']}"
            
            return True, f"Approved by policy: {decision['policy']}"
    
    async def log_deployment_event(
        self,
        model_id: int,
        event_type: str,
        actor: str,
        metadata: dict = None
    ):
        """Record deployment event in MLEvent table"""
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            if not model:
                return
            
            event = MLEvent(
                event_type=event_type,
                model_name=model.model_name,
                version=model.version,
                accuracy=model.accuracy,
                validation_score=model.f1_score,
                deployment_status=model.deployment_status,
                event_metadata=str(metadata or {}),
                actor=actor
            )
            session.add(event)
            await session.commit()
    
    async def deploy_with_pipeline(
        self,
        model_id: int,
        actor: str = "system"
    ) -> tuple[bool, str]:
        """Full deployment pipeline: verify -> approve -> deploy"""
        
        await self.log_deployment_event(
            model_id,
            "deployment_initiated",
            actor,
            {"step": "start"}
        )
        
        verified, msg = await self.verify_model_metrics(model_id)
        if not verified:
            await self.log_deployment_event(
                model_id,
                "deployment_failed",
                actor,
                {"step": "verification", "reason": msg}
            )
            return False, f"Verification failed: {msg}"
        
        print(f"✓ Verification passed: {msg}")
        await self.log_deployment_event(
            model_id,
            "deployment_verified",
            actor,
            {"step": "verification"}
        )
        
        approved, approval_msg = await self.request_governance_approval(
            model_id,
            actor,
            reason="production deployment"
        )
        if not approved:
            await self.log_deployment_event(
                model_id,
                "deployment_denied",
                actor,
                {"step": "governance", "reason": approval_msg}
            )
            return False, f"Approval denied: {approval_msg}"
        
        print(f"✓ Governance approved: {approval_msg}")
        await self.log_deployment_event(
            model_id,
            "deployment_approved",
            actor,
            {"step": "governance"}
        )
        
        from .ml_runtime import model_registry
        deployed = await model_registry.deploy_model(model_id, actor)
        
        if not deployed:
            await self.log_deployment_event(
                model_id,
                "deployment_failed",
                actor,
                {"step": "deploy", "reason": "deployment execution failed"}
            )
            return False, "Deployment execution failed"
        
        await self.log_deployment_event(
            model_id,
            "deployment_completed",
            actor,
            {"step": "complete"}
        )
        
        return True, "Deployment successful"
    
    async def check_auto_deploy_criteria(
        self,
        new_model_id: int,
        model_type: str
    ) -> tuple[bool, str]:
        """Check if new model qualifies for auto-deployment"""
        
        async with async_session() as session:
            new_model = await session.get(MLModel, new_model_id)
            if not new_model or new_model.accuracy is None:
                return False, "New model has no accuracy score"
            
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model_type)
                .where(MLModel.deployment_status == "deployed")
                .limit(1)
            )
            current_model = result.scalar_one_or_none()
            
            if not current_model:
                if new_model.accuracy >= self.min_accuracy_threshold:
                    return True, f"First model with acceptable accuracy: {new_model.accuracy:.2f}"
                return False, f"Accuracy {new_model.accuracy:.2f} below threshold"
            
            if current_model.accuracy is None:
                current_accuracy = 0.0
            else:
                current_accuracy = current_model.accuracy
            
            improvement = new_model.accuracy - current_accuracy
            
            if improvement >= self.improvement_threshold:
                return True, f"Improvement: {improvement:.2%} (≥{self.improvement_threshold:.2%})"
            
            return False, f"Improvement {improvement:.2%} below {self.improvement_threshold:.2%}"

deployment_pipeline = ModelDeploymentPipeline()
