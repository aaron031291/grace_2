"""Train the alert severity prediction model"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import init_db
from backend.training_pipeline import training_pipeline
from backend.ml_classifiers import alert_severity_predictor


async def train_model():
    """Train the alert severity predictor"""
    
    print("=" * 60)
    print("Alert Severity Predictor Training")
    print("=" * 60)
    
    await init_db()
    print("[OK] Database initialized\n")
    
    print("Training model...")
    result = await training_pipeline.train_alert_predictor(actor="admin")
    
    if result['success']:
        print("\n" + "=" * 60)
        print("Training Results")
        print("=" * 60)
        print(f"Training samples: {result['training_samples']}")
        print(f"Test samples: {result['test_samples']}")
        print(f"Accuracy: {result['accuracy']:.2%}")
        print(f"Model ID: {result.get('model_id', 'N/A')}")
        print()
        
        print("Classification Report:")
        print("-" * 60)
        for label, metrics in result['classification_report'].items():
            if isinstance(metrics, dict):
                print(f"\n{label}:")
                print(f"  Precision: {metrics.get('precision', 0):.2%}")
                print(f"  Recall: {metrics.get('recall', 0):.2%}")
                print(f"  F1-Score: {metrics.get('f1-score', 0):.2%}")
                print(f"  Support: {metrics.get('support', 0)}")
        
        print("\n" + "-" * 60)
        print("Feature Importance:")
        print("-" * 60)
        for feature, importance in sorted(
            result['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"{feature:25s}: {importance:.4f} {'█' * int(importance * 50)}")
        
        print("\n" + "=" * 60)
        print("[OK] Model training complete!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Training failed!")
        print("=" * 60)
        print(f"Reason: {result.get('reason', 'unknown')}")
        print(f"Message: {result.get('message', 'No details available')}")


async def test_prediction():
    """Test the trained model with sample alerts"""
    
    print("\n" + "=" * 60)
    print("Testing Predictions")
    print("=" * 60)
    
    test_alerts = [
        {
            'actor': 'admin',
            'action': 'file_access',
            'resource': '/etc/passwd',
            'expected': 'critical'
        },
        {
            'actor': 'user_1',
            'action': 'api_query',
            'resource': '/api/search',
            'expected': 'low'
        },
        {
            'actor': 'admin',
            'action': 'config_change',
            'resource': '/config/security.yaml',
            'expected': 'high'
        },
        {
            'actor': 'unknown',
            'action': 'login_attempt',
            'resource': '/auth/login',
            'expected': 'medium'
        }
    ]
    
    print()
    for i, alert in enumerate(test_alerts, 1):
        predicted_severity, confidence = await alert_severity_predictor.predict_severity(alert)
        explanation = alert_severity_predictor.explain_prediction()
        
        match = "[OK]" if predicted_severity == alert['expected'] else "[FAIL]"
        
        print(f"{i}. {alert['action']} on {alert['resource']} by {alert['actor']}")
        print(f"   Expected: {alert['expected']:8s} | Predicted: {predicted_severity:8s} (confidence: {confidence:.2%}) {match}")
        print(f"   All probabilities: {explanation['all_probabilities']}")
        print()


if __name__ == "__main__":
    asyncio.run(train_model())
    asyncio.run(test_prediction())
