"""Train and deploy trust score classifier"""

import asyncio
import sys
from training_pipeline import training_pipeline
from ml_classifiers import trust_classifier_manager
from sqlalchemy import select
from models import async_session
from ml_models_table import MLModel

async def evaluate_test_urls():
    """Test the deployed model on sample URLs"""
    test_urls = [
        ("https://python.org/docs", "High Trust (Official)"),
        ("https://github.com/user/repo", "Medium Trust (Repository)"),
        ("https://stackoverflow.com/questions/123", "Medium Trust (Community)"),
        ("https://arxiv.org/abs/1234.5678", "High Trust (Research)"),
        ("https://wikipedia.org/wiki/ML", "High Trust (Reference)"),
        ("https://example.edu/course", "High Trust (.edu)"),
        ("https://government.gov/data", "High Trust (.gov)"),
        ("http://suspicious-site.temp/phishing", "Low Trust (Suspicious)"),
        ("http://bit.ly/shortened", "Low Trust (URL Shortener)"),
        ("https://random-blog.com/article", "Medium Trust (Unknown)"),
    ]
    
    print("\n" + "="*80)
    print("Testing Deployed Model on Sample URLs")
    print("="*80 + "\n")
    
    for url, expected in test_urls:
        score, method = await trust_classifier_manager.predict_with_fallback(url)
        explanation = await trust_classifier_manager.explain_prediction(url)
        
        print(f"URL: {url}")
        print(f"  Expected: {expected}")
        print(f"  Predicted Score: {score} ({method})")
        
        if 'feature_contributions' in explanation:
            print(f"  Top Features:")
            for feat in explanation['feature_contributions'][:3]:
                print(f"    - {feat['feature']}: {feat['value']:.2f} (importance: {feat['importance']:.3f})")
        
        print()

async def train_and_evaluate():
    """Main training and evaluation workflow"""
    
    print("="*80)
    print("GRACE Trust Score Classifier Training")
    print("="*80 + "\n")
    
    print("Step 1: Training Random Forest Classifier")
    print("-" * 80)
    
    model_id = await training_pipeline.train_trust_classifier(
        model_type="random_forest",
        actor="admin",
        auto_deploy=True
    )
    
    if not model_id:
        print("[FAIL] Training failed")
        return False
    
    print(f"\n[OK] Training completed (Model ID: {model_id})")
    
    async with async_session() as session:
        model = await session.get(MLModel, model_id)
        
        print("\nModel Metrics:")
        print(f"  Accuracy:  {model.accuracy:.3f}")
        print(f"  Precision: {model.precision:.3f}")
        print(f"  Recall:    {model.recall:.3f}")
        print(f"  F1 Score:  {model.f1_score:.3f}")
        print(f"  Status:    {model.deployment_status}")
        print(f"  Verified:  {model.verification_status}")
        
        deployment_threshold = 0.85
        meets_threshold = model.accuracy >= deployment_threshold
        
        print(f"\n{'[OK]' if meets_threshold else '[FAIL]'} Accuracy threshold: {deployment_threshold}")
        
        if model.deployment_status == "deployed":
            print("\n[OK] Model already auto-deployed")
        elif meets_threshold:
            print("\nStep 2: Deploying Model")
            print("-" * 80)
            
            deployed = await training_pipeline.deploy_model(model_id, "admin")
            
            if deployed:
                print("[OK] Model deployed successfully")
            else:
                print("[FAIL] Deployment failed")
                return False
        else:
            print(f"\n[WARN] Model accuracy ({model.accuracy:.3f}) below threshold ({deployment_threshold})")
            print("   Model not deployed")
            return False
    
    await evaluate_test_urls()
    
    print("\n" + "="*80)
    print("Training and Deployment Complete")
    print("="*80)
    
    return True

async def check_model_status():
    """Check current model deployment status"""
    
    print("\n" + "="*80)
    print("Current Model Status")
    print("="*80 + "\n")
    
    async with async_session() as session:
        result = await session.execute(
            select(MLModel)
            .where(MLModel.model_name == "trust_score_classifier")
            .order_by(MLModel.created_at.desc())
        )
        models = result.scalars().all()
        
        if not models:
            print("No trust score classifiers found.")
            return
        
        for i, model in enumerate(models, 1):
            print(f"Model {i} (ID: {model.id})")
            print(f"  Version: {model.version}")
            print(f"  Type: {model.model_type}")
            print(f"  Accuracy: {model.accuracy:.3f if model.accuracy else 'N/A'}")
            print(f"  Status: {model.deployment_status}")
            print(f"  Created: {model.created_at}")
            print(f"  Deployed: {model.deployed_at or 'Not deployed'}")
            print()

async def main():
    """Main entry point"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        await check_model_status()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await evaluate_test_urls()
        return
    
    success = await train_and_evaluate()
    
    if success:
        print("\n[OK] All steps completed successfully")
        sys.exit(0)
    else:
        print("\n[FAIL] Training or deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
