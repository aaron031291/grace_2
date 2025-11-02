"""Automatic retraining based on new trusted knowledge"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, func
from .knowledge_models import KnowledgeArtifact
from .ml_models_table import MLModel
from .models import async_session

class AutoRetrainEngine:
    """Automatically retrain models when new trusted data arrives"""
    
    def __init__(self, check_interval: int = 3600):
        self.check_interval = check_interval
        self._task = None
        self._running = False
        self.retrain_threshold = 100
    
    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
            print(f"✓ Auto-retrain engine started (interval: {self.check_interval}s)")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("✓ Auto-retrain engine stopped")
    
    async def _loop(self):
        try:
            while self._running:
                await self.check_and_retrain()
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            pass
    
    async def check_and_retrain(self):
        """Check if retraining is needed"""
        
        async with async_session() as session:
            latest_model = await session.execute(
                select(MLModel)
                .where(MLModel.deployment_status == "deployed")
                .order_by(MLModel.created_at.desc())
                .limit(1)
            )
            model = latest_model.scalar_one_or_none()
            
            if not model:
                print("ℹ️ No deployed model - skipping retrain check")
                return
            
            new_knowledge_count = await session.scalar(
                select(func.count(KnowledgeArtifact.id))
                .where(KnowledgeArtifact.created_at > model.created_at)
            )
            
            if new_knowledge_count >= self.retrain_threshold:
                print(f"🔄 Auto-retrain triggered: {new_knowledge_count} new knowledge items")
                
                from .training_pipeline import training_pipeline
                new_model_id = await training_pipeline.train_model(
                    model_name=model.model_name,
                    model_type=model.model_type,
                    trust_threshold=model.trust_score_min or 70.0,
                    actor="auto_retrain"
                )
                
                if new_model_id:
                    print(f"✓ Auto-retrained model: {model.model_name} → ID {new_model_id}")

auto_retrain_engine = AutoRetrainEngine(check_interval=3600)
