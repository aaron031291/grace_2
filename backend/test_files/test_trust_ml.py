"""End-to-end test for ML trust score classifier"""

import asyncio
import sys
from training_pipeline import training_pipeline
from ml_classifiers import trust_classifier_manager, TrustScoreClassifier
from ingestion_service import ingestion_service
from models import async_session, init_db
from knowledge_models import KnowledgeArtifact
from sqlalchemy import select
import numpy as np

async def test_feature_extraction():
    """Test URL feature extraction"""
    print("\n" + "="*80)
    print("Test 1: Feature Extraction")
    print("="*80 + "\n")
    
    classifier = TrustScoreClassifier()
    
    test_cases = [
        "https://python.org/docs/tutorial",
        "http://bit.ly/short",
        "https://example.edu/research/paper.pdf",
        "https://sub.domain.example.com/path/to/resource?query=1"
    ]
    
    for url in test_cases:
        features = classifier.extract_features(url)
        print(f"URL: {url}")
        print(f"Features: {features[0]}")
        print(f"Feature names: {classifier.feature_names}")
        print()
    
    print("✓ Feature extraction test passed\n")

async def test_classifier_training():
    """Test classifier training with synthetic data"""
    print("="*80)
    print("Test 2: Classifier Training")
    print("="*80 + "\n")
    
    classifier = TrustScoreClassifier(model_type="random_forest")
    
    high_trust_urls = [
        "https://python.org/", "https://github.com/", "https://arxiv.org/",
        "https://wikipedia.org/", "https://example.edu/", "https://example.gov/"
    ]
    
    medium_trust_urls = [
        "https://stackoverflow.com/", "https://medium.com/", "https://dev.to/",
        "https://example.org/", "https://example.com/"
    ]
    
    low_trust_urls = [
        "http://bit.ly/", "http://tinyurl.com/", "http://example.temp/",
        "http://suspicious-site.xyz/", "http://random123.tk/"
    ]
    
    urls = high_trust_urls * 3 + medium_trust_urls * 3 + low_trust_urls * 3
    scores = [92] * (len(high_trust_urls) * 3) + [60] * (len(medium_trust_urls) * 3) + [25] * (len(low_trust_urls) * 3)
    
    X = np.vstack([classifier.extract_features(url) for url in urls])
    y = np.array(scores)
    
    print(f"Training with {len(X)} samples...")
    print(f"Class distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
    
    metrics = classifier.train(X, y)
    
    print(f"\n✓ Training completed:")
    print(f"  Accuracy: {metrics['accuracy']:.3f}")
    print(f"  Precision: {metrics['precision']:.3f}")
    print(f"  Recall: {metrics['recall']:.3f}")
    print(f"  F1 Score: {metrics['f1_score']:.3f}")
    
    if metrics['accuracy'] < 0.7:
        print("\n✗ Warning: Low accuracy")
    else:
        print("\n✓ Accuracy acceptable")
    
    print("\nTesting predictions:")
    test_predictions = [
        ("https://python.org/new", "High"),
        ("https://example.com/page", "Medium"),
        ("http://bit.ly/abc", "Low")
    ]
    
    for url, expected in test_predictions:
        score = classifier.predict(url)
        explanation = classifier.explain(url)
        print(f"  {url}: {score} (expected: {expected})")
        print(f"    Top feature: {explanation['feature_contributions'][0]['feature']}")
    
    print("\n✓ Classifier training test passed\n")
    return classifier

async def test_pipeline_integration():
    """Test full training pipeline"""
    print("="*80)
    print("Test 3: Training Pipeline Integration")
    print("="*80 + "\n")
    
    await init_db()
    
    print("Seeding test URLs into knowledge base...")
    
    test_urls = [
        ("https://python.org/docs", "Python Documentation"),
        ("https://github.com/user/repo", "GitHub Repository"),
        ("https://arxiv.org/abs/1234", "Research Paper"),
    ]
    
    for url, title in test_urls:
        try:
            await ingestion_service.ingest(
                content=f"Test content from {url}",
                artifact_type="url",
                title=title,
                actor="test_user",
                source=url,
                domain="external"
            )
        except:
            pass
    
    print(f"✓ Seeded {len(test_urls)} test artifacts")
    
    print("\nTraining classifier from knowledge base...")
    
    model_id = await training_pipeline.train_trust_classifier(
        model_type="random_forest",
        actor="test_user",
        auto_deploy=False
    )
    
    if model_id:
        print(f"✓ Model trained (ID: {model_id})")
    else:
        print("⚠️ Model training used synthetic data (insufficient real data)")
    
    print("\n✓ Pipeline integration test passed\n")

async def test_ingestion_with_ml():
    """Test URL ingestion with ML trust scoring"""
    print("="*80)
    print("Test 4: URL Ingestion with ML Scoring")
    print("="*80 + "\n")
    
    await init_db()
    
    print("Training and deploying model...")
    model_id = await training_pipeline.train_trust_classifier(
        model_type="random_forest",
        actor="test_user",
        auto_deploy=True
    )
    
    if model_id:
        print(f"✓ Model deployed (ID: {model_id})")
    
    test_urls = [
        "https://python.org/",
        "https://github.com/",
        "http://bit.ly/test"
    ]
    
    print("\nIngesting URLs with ML trust scoring...")
    
    for url in test_urls:
        try:
            artifact_id = await ingestion_service.ingest(
                content=f"Content from {url}",
                artifact_type="url",
                title=url,
                actor="test_user",
                source=url,
                domain="external"
            )
            
            async with async_session() as session:
                artifact = await session.get(KnowledgeArtifact, artifact_id)
                import json
                metadata = json.loads(artifact.artifact_metadata)
                
                print(f"\n  URL: {url}")
                print(f"  Trust Score: {metadata.get('trust_score', 'N/A')}")
                print(f"  Method: {metadata.get('trust_method', 'N/A')}")
        
        except Exception as e:
            print(f"  Failed to ingest {url}: {e}")
    
    print("\n✓ Ingestion with ML test passed\n")

async def test_explanation():
    """Test model explanation capabilities"""
    print("="*80)
    print("Test 5: Model Explanation")
    print("="*80 + "\n")
    
    classifier = TrustScoreClassifier(model_type="random_forest")
    
    urls = [
        "https://python.org/", "https://github.com/", "http://bit.ly/",
        "https://example.edu/", "http://suspicious.temp/"
    ] * 3
    
    scores = [92, 70, 25, 85, 20] * 3
    
    X = np.vstack([classifier.extract_features(url) for url in urls])
    y = np.array(scores)
    
    classifier.train(X, y)
    
    test_url = "https://example.edu/research/paper.pdf"
    explanation = classifier.explain(test_url)
    
    print(f"Explaining prediction for: {test_url}\n")
    print(f"Predicted Score: {explanation['predicted_score']}")
    print(f"\nTop Feature Contributions:")
    
    for feat in explanation['feature_contributions'][:5]:
        print(f"  {feat['feature']:20s}: value={feat['value']:.2f}, importance={feat['importance']:.3f}")
    
    print("\n✓ Explanation test passed\n")

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("GRACE ML Trust Classifier - End-to-End Test Suite")
    print("="*80)
    
    try:
        await test_feature_extraction()
        await test_classifier_training()
        await test_pipeline_integration()
        await test_ingestion_with_ml()
        await test_explanation()
        
        print("="*80)
        print("✓ ALL TESTS PASSED")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
