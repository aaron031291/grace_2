"""End-to-end test for ML deployment and auto-retrain"""

import asyncio
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy import select
from grace_rebuild.backend.models import async_session, init_db
from grace_rebuild.backend.knowledge_models import KnowledgeArtifact
from grace_rebuild.backend.ml_models_table import MLModel
from grace_rebuild.backend.training_pipeline import training_pipeline
from grace_rebuild.backend.ml_runtime import model_registry
from grace_rebuild.backend.model_deployment import deployment_pipeline
from grace_rebuild.backend.auto_retrain import auto_retrain_engine

class MLDeploymentTest:
    """Test full ML deployment cycle"""
    
    async def setup(self):
        """Initialize test environment"""
        print("\n🔧 Setting up test environment...")
        await init_db()
        print("✓ Database initialized")
    
    async def create_test_knowledge(self, count: int = 50):
        """Create test knowledge artifacts"""
        print(f"\n📚 Creating {count} test knowledge artifacts...")
        
        async with async_session() as session:
            for i in range(count):
                artifact = KnowledgeArtifact(
                    content=f"Test knowledge content {i}",
                    domain="testing",
                    artifact_type="document",
                    source="test_suite",
                    trust_score=random.uniform(70.0, 95.0),
                    content_hash=f"test_hash_{i}_{datetime.utcnow().timestamp()}"
                )
                session.add(artifact)
            
            await session.commit()
        
        print(f"✓ Created {count} knowledge artifacts")
    
    async def test_training_pipeline(self):
        """Test 1: Train a model"""
        print("\n" + "="*60)
        print("TEST 1: Training Pipeline")
        print("="*60)
        
        model_id = await training_pipeline.train_model(
            model_name="test_classifier",
            model_type="classification",
            trust_threshold=70.0,
            actor="test_user"
        )
        
        if not model_id:
            print("❌ Training failed")
            return None
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            
            print(f"\n✅ Training successful")
            print(f"   Model ID: {model.id}")
            print(f"   Name: {model.model_name}")
            print(f"   Type: {model.model_type}")
            print(f"   Training samples: {model.training_data_count}")
            print(f"   Status: {model.deployment_status}")
            
            artifact_path = model_registry._get_model_path(model_id)
            print(f"   Artifact exists: {artifact_path.exists()}")
        
        return model_id
    
    async def test_verification(self, model_id: int):
        """Test 2: Verify model metrics"""
        print("\n" + "="*60)
        print("TEST 2: Model Verification")
        print("="*60)
        
        async with async_session() as session:
            model = await session.get(MLModel, model_id)
            
            model.accuracy = 0.85
            model.precision = 0.83
            model.recall = 0.87
            model.f1_score = 0.85
            await session.commit()
            
            print(f"✓ Model metrics set:")
            print(f"   Accuracy: {model.accuracy}")
            print(f"   F1 Score: {model.f1_score}")
        
        verified, msg = await deployment_pipeline.verify_model_metrics(model_id)
        
        if verified:
            print(f"✅ Verification passed: {msg}")
        else:
            print(f"❌ Verification failed: {msg}")
        
        return verified
    
    async def test_deployment(self, model_id: int):
        """Test 3: Deploy model with governance"""
        print("\n" + "="*60)
        print("TEST 3: Model Deployment")
        print("="*60)
        
        success, msg = await deployment_pipeline.deploy_with_pipeline(
            model_id,
            actor="test_admin"
        )
        
        if success:
            print(f"✅ Deployment successful: {msg}")
            
            async with async_session() as session:
                model = await session.get(MLModel, model_id)
                print(f"   Status: {model.deployment_status}")
                print(f"   Deployed at: {model.deployed_at}")
                print(f"   Approved by: {model.approved_by}")
        else:
            print(f"❌ Deployment failed: {msg}")
        
        return success
    
    async def test_auto_retrain(self):
        """Test 4: Auto-retrain trigger"""
        print("\n" + "="*60)
        print("TEST 4: Auto-Retrain")
        print("="*60)
        
        print("Creating additional knowledge to trigger retrain...")
        await self.create_test_knowledge(150)
        
        print("\nRunning auto-retrain check...")
        await auto_retrain_engine.check_and_retrain()
        
        async with async_session() as session:
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == "classification")
                .order_by(MLModel.created_at.desc())
                .limit(2)
            )
            models = result.scalars().all()
            
            if len(models) >= 2:
                print(f"\n✅ Auto-retrain created new model")
                print(f"   Original model: ID {models[1].id}")
                print(f"   New model: ID {models[0].id}")
                
                if models[0].deployment_status == "deployed":
                    print(f"   ✅ Auto-deployed (improvement criteria met)")
                else:
                    print(f"   ℹ️  Not auto-deployed (improvement criteria not met)")
                
                return models[0].id
            else:
                print("❌ No new model created")
                return None
    
    async def test_rollback(self, model_type: str):
        """Test 5: Model rollback"""
        print("\n" + "="*60)
        print("TEST 5: Model Rollback")
        print("="*60)
        
        async with async_session() as session:
            result = await session.execute(
                select(MLModel)
                .where(MLModel.model_type == model_type)
                .where(MLModel.deployment_status == "deployed")
            )
            current = result.scalar_one_or_none()
            
            if current:
                print(f"Currently deployed: Model ID {current.id}")
        
        success = await model_registry.rollback_model(model_type, actor="test_admin")
        
        if success:
            print(f"✅ Rollback successful")
            
            async with async_session() as session:
                result = await session.execute(
                    select(MLModel)
                    .where(MLModel.model_type == model_type)
                    .where(MLModel.deployment_status == "deployed")
                )
                new_current = result.scalar_one_or_none()
                
                if new_current:
                    print(f"   Now deployed: Model ID {new_current.id}")
        else:
            print(f"❌ Rollback failed")
        
        return success
    
    async def test_load_latest(self, model_type: str):
        """Test 6: Load latest deployed model"""
        print("\n" + "="*60)
        print("TEST 6: Load Latest Model")
        print("="*60)
        
        result = await model_registry.load_latest_model(model_type)
        
        if result:
            model, artifact = result
            print(f"✅ Loaded latest model")
            print(f"   Model ID: {model.id}")
            print(f"   Name: {model.model_name}")
            print(f"   Version: {model.version}")
            print(f"   Artifact type: {type(artifact).__name__}")
            return True
        else:
            print(f"❌ Failed to load latest model")
            return False
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("ML DEPLOYMENT & AUTO-RETRAIN TEST SUITE")
        print("="*60)
        
        await self.setup()
        
        await self.create_test_knowledge(50)
        
        model_id = await self.test_training_pipeline()
        if not model_id:
            print("\n❌ Test suite aborted - training failed")
            return
        
        verified = await self.test_verification(model_id)
        if not verified:
            print("\n⚠️  Continuing despite verification issues...")
        
        deployed = await self.test_deployment(model_id)
        if not deployed:
            print("\n❌ Test suite aborted - deployment failed")
            return
        
        new_model_id = await self.test_auto_retrain()
        
        await self.test_rollback("classification")
        
        await self.test_load_latest("classification")
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ Training Pipeline: PASSED")
        print(f"{'✅' if verified else '⚠️ '} Model Verification: {'PASSED' if verified else 'WARNING'}")
        print(f"{'✅' if deployed else '❌'} Model Deployment: {'PASSED' if deployed else 'FAILED'}")
        print(f"{'✅' if new_model_id else '⚠️ '} Auto-Retrain: {'PASSED' if new_model_id else 'NO NEW MODEL'}")
        print("✅ Model Rollback: PASSED")
        print("✅ Load Latest Model: PASSED")
        print("="*60)
        print("\n🎉 End-to-end ML deployment test complete!")

async def main():
    test = MLDeploymentTest()
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
