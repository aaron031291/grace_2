"""
Populate Model Registry with Realistic ML Models

Creates a diverse set of production-ready models to showcase the registry.
"""

import requests
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/model-registry"


def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("\n⚠️ Make sure the backend server is running:")
        print("   python serve.py")
        return False


MODELS = [
    {
        "model_id": "fraud_detector_v1",
        "name": "Fraud Detection Model",
        "version": "1.2.3",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "data_science",
        "team": "ml_platform",
        "training_data_hash": "abc123def456",
        "training_dataset_size": 500000,
        "evaluation_metrics": {
            "accuracy": 0.94,
            "precision": 0.92,
            "recall": 0.91,
            "f1_score": 0.915,
            "auc_roc": 0.96
        },
        "description": "Production fraud detection model using ensemble methods (Random Forest + XGBoost)",
        "tags": ["fraud", "production", "ensemble", "sklearn"]
    },
    {
        "model_id": "sentiment_analyzer_v2",
        "name": "Sentiment Analysis",
        "version": "2.0.1",
        "framework": "pytorch",
        "model_type": "classification",
        "owner": "nlp_team",
        "team": "ai_research",
        "training_data_hash": "xyz789abc012",
        "training_dataset_size": 1000000,
        "evaluation_metrics": {
            "accuracy": 0.89,
            "precision": 0.87,
            "recall": 0.88,
            "f1_score": 0.875,
            "perplexity": 12.3
        },
        "description": "BERT-based sentiment classifier fine-tuned on customer reviews and social media",
        "tags": ["nlp", "sentiment", "bert", "production", "pytorch"]
    },
    {
        "model_id": "churn_predictor_v3",
        "name": "Customer Churn Prediction",
        "version": "3.1.0",
        "framework": "sklearn",
        "model_type": "classification",
        "owner": "analytics",
        "team": "data_science",
        "training_data_hash": "churn456xyz",
        "training_dataset_size": 250000,
        "evaluation_metrics": {
            "accuracy": 0.86,
            "precision": 0.84,
            "recall": 0.85,
            "f1_score": 0.845,
            "auc_roc": 0.90
        },
        "description": "Random forest model for predicting customer churn with feature importance analysis",
        "tags": ["churn", "customer", "production", "sklearn"]
    },
    {
        "model_id": "recommender_system_v4",
        "name": "Product Recommendation Engine",
        "version": "4.0.2",
        "framework": "pytorch",
        "model_type": "recommendation",
        "owner": "recommendations",
        "team": "personalization",
        "training_data_hash": "rec789ghi012",
        "training_dataset_size": 2000000,
        "evaluation_metrics": {
            "ndcg_at_10": 0.72,
            "precision_at_10": 0.45,
            "recall_at_10": 0.38,
            "map": 0.68
        },
        "description": "Neural collaborative filtering with attention mechanisms for personalized recommendations",
        "tags": ["recommendations", "collaborative_filtering", "pytorch", "production"]
    },
    {
        "model_id": "anomaly_detector_v1",
        "name": "Anomaly Detection System",
        "version": "1.0.5",
        "framework": "sklearn",
        "model_type": "anomaly_detection",
        "owner": "security",
        "team": "infra_security",
        "training_data_hash": "anom123sec456",
        "training_dataset_size": 750000,
        "evaluation_metrics": {
            "precision": 0.88,
            "recall": 0.82,
            "f1_score": 0.85,
            "false_positive_rate": 0.02
        },
        "description": "Isolation Forest for detecting anomalous behavior in system logs and user activities",
        "tags": ["anomaly_detection", "security", "sklearn", "production"]
    }
]


def register_models():
    """Register all models"""
    print("\n" + "="*60)
    print("POPULATING MODEL REGISTRY")
    print("="*60)
    
    registered = []
    
    for model in MODELS:
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/models",
                json=model,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Registered: {model['name']} (v{model['version']})")
                registered.append(model['model_id'])
            else:
                print(f"❌ Failed to register {model['name']}: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error registering {model['name']}: {e}")
    
    return registered


def promote_to_production(model_ids):
    """Promote models to production"""
    print("\n" + "="*60)
    print("PROMOTING MODELS TO PRODUCTION")
    print("="*60)
    
    promoted = []
    
    for model_id in model_ids:
        try:
            response = requests.patch(
                f"{BASE_URL}{API_PREFIX}/models/{model_id}/deployment",
                json={"status": "production", "canary_percentage": 0.0},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"🚀 Promoted to production: {model_id}")
                promoted.append(model_id)
            else:
                print(f"❌ Failed to promote {model_id}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error promoting {model_id}: {e}")
    
    return promoted


def simulate_healthy_performance(model_ids):
    """Record healthy performance snapshots"""
    print("\n" + "="*60)
    print("RECORDING HEALTHY PERFORMANCE")
    print("="*60)
    
    model_configs = {
        "fraud_detector_v1": {
            "version": "1.2.3",
            "latency_p50_ms": 42.5,
            "latency_p95_ms": 85.3,
            "latency_p99_ms": 120.7,
            "requests_per_second": 250.0,
            "error_rate": 0.002,
            "ood_rate": 0.04,
            "input_drift_score": 0.08,
            "accuracy": 0.94
        },
        "sentiment_analyzer_v2": {
            "version": "2.0.1",
            "latency_p50_ms": 120.5,
            "latency_p95_ms": 245.8,
            "latency_p99_ms": 380.2,
            "requests_per_second": 180.0,
            "error_rate": 0.005,
            "ood_rate": 0.06,
            "input_drift_score": 0.12,
            "accuracy": 0.89
        },
        "churn_predictor_v3": {
            "version": "3.1.0",
            "latency_p50_ms": 35.2,
            "latency_p95_ms": 68.5,
            "latency_p99_ms": 95.3,
            "requests_per_second": 300.0,
            "error_rate": 0.001,
            "ood_rate": 0.03,
            "input_drift_score": 0.05,
            "accuracy": 0.86
        },
        "recommender_system_v4": {
            "version": "4.0.2",
            "latency_p50_ms": 85.0,
            "latency_p95_ms": 165.5,
            "latency_p99_ms": 250.0,
            "requests_per_second": 500.0,
            "error_rate": 0.003,
            "ood_rate": 0.08,
            "input_drift_score": 0.15,
            "accuracy": 0.72
        },
        "anomaly_detector_v1": {
            "version": "1.0.5",
            "latency_p50_ms": 28.5,
            "latency_p95_ms": 55.8,
            "latency_p99_ms": 82.3,
            "requests_per_second": 400.0,
            "error_rate": 0.004,
            "ood_rate": 0.10,
            "input_drift_score": 0.18,
            "accuracy": 0.85
        }
    }
    
    for model_id in model_ids:
        if model_id not in model_configs:
            continue
        
        config = model_configs[model_id]
        config["model_id"] = model_id
        
        # Record 3 healthy snapshots with slight variance
        for i in range(3):
            # Add slight random variance
            snapshot = config.copy()
            snapshot["latency_p50_ms"] *= random.uniform(0.95, 1.05)
            snapshot["latency_p95_ms"] *= random.uniform(0.95, 1.05)
            snapshot["error_rate"] *= random.uniform(0.8, 1.2)
            
            try:
                response = requests.post(
                    f"{BASE_URL}{API_PREFIX}/models/{model_id}/performance",
                    json=snapshot,
                    timeout=10
                )
                
                if response.status_code == 200:
                    if i == 0:  # Only print once per model
                        print(f"📊 Recorded performance: {model_id}")
                else:
                    print(f"❌ Failed to record performance for {model_id}")
            except Exception as e:
                print(f"❌ Error recording performance: {e}")


def generate_model_cards(model_ids):
    """Generate model cards"""
    print("\n" + "="*60)
    print("GENERATING MODEL CARDS")
    print("="*60)
    
    for model_id in model_ids:
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/models/{model_id}/generate-card",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"📄 Generated model card: {model_id}")
                print(f"   Path: {result.get('model_card_path')}")
            else:
                print(f"❌ Failed to generate card for {model_id}")
        except Exception as e:
            print(f"❌ Error generating card: {e}")


def show_registry_stats():
    """Display registry statistics"""
    print("\n" + "="*60)
    print("REGISTRY STATISTICS")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Total Models: {stats['total_models']}")
            print(f"\n📈 By Stage:")
            for stage, count in stats['by_stage'].items():
                if count > 0:
                    print(f"   {stage}: {count}")
            
            print(f"\n🔧 By Framework:")
            for framework, count in stats['by_framework'].items():
                if count > 0:
                    print(f"   {framework}: {count}")
            
            print(f"\n✅ Governance:")
            print(f"   Constitutional Compliance: {stats['governance']['constitutional_passed']}")
            print(f"   Bias Checks Passed: {stats['governance']['bias_passed']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")


def main():
    """Main execution"""
    print("\n🤖 Model Registry Population Script")
    print("This will populate the registry with 5 realistic ML models\n")
    
    # Check server
    if not check_server():
        sys.exit(1)
    
    # Register models
    registered = register_models()
    
    if not registered:
        print("\n❌ No models were registered. Exiting.")
        sys.exit(1)
    
    # Promote to production
    promoted = promote_to_production(registered)
    
    # Record performance
    simulate_healthy_performance(promoted)
    
    # Generate model cards
    generate_model_cards(registered)
    
    # Show stats
    show_registry_stats()
    
    print("\n" + "="*60)
    print("✅ MODEL REGISTRY POPULATED SUCCESSFULLY!")
    print("="*60)
    print("\nNext steps:")
    print("1. View models: http://localhost:8000/api/model-registry/models")
    print("2. Monitor health: http://localhost:8000/api/model-registry/monitor/production")
    print("3. Check a model: http://localhost:8000/api/model-registry/models/fraud_detector_v1/health")
    print("\nTo simulate degradation:")
    print("  python scripts/simulate_model_degradation.py fraud_detector_v1")
    print()


if __name__ == "__main__":
    main()
