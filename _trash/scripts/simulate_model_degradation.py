"""
Simulate Model Degradation for Demo

Injects degraded performance metrics to trigger rollback detection.
"""

import requests
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/model-registry"


def simulate_degradation(model_id: str, snapshots: int = 5):
    """
    Simulate model degradation
    
    Args:
        model_id: Model to degrade
        snapshots: Number of bad snapshots to record
    """
    print(f"\n🔥 Simulating degradation for: {model_id}")
    print(f"Recording {snapshots} degraded snapshots...\n")
    
    # Get current model info
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/models/{model_id}")
        if response.status_code != 200:
            print(f"❌ Model not found: {model_id}")
            return
        
        model_data = response.json()['model']
        version = model_data['version']
        print(f"📊 Model: {model_data['name']} (v{version})")
        print(f"📊 Current Status: {model_data['deploy_status']}\n")
        
    except Exception as e:
        print(f"❌ Error fetching model: {e}")
        return
    
    # Degraded performance profile
    degraded_snapshot = {
        "model_id": model_id,
        "version": version,
        "latency_p50_ms": 85.0,      # High latency
        "latency_p95_ms": 180.0,     # Very high p95
        "latency_p99_ms": 320.0,     # Very high p99
        "requests_per_second": 95.0,  # Low throughput
        "error_rate": 0.095,          # 9.5% errors - TRIGGERS ROLLBACK
        "ood_rate": 0.26,             # 26% OOD - TRIGGERS ROLLBACK
        "input_drift_score": 0.42,    # High drift - TRIGGERS ROLLBACK
        "accuracy": 0.78              # Degraded accuracy
    }
    
    # Record degraded snapshots
    for i in range(1, snapshots + 1):
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/models/{model_id}/performance",
                json=degraded_snapshot,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"⚠️ Snapshot {i}/{snapshots}: Error rate: {degraded_snapshot['error_rate']:.1%}, "
                      f"OOD: {degraded_snapshot['ood_rate']:.1%}, "
                      f"Drift: {degraded_snapshot['input_drift_score']:.2f}")
            else:
                print(f"❌ Failed to record snapshot {i}")
                
        except Exception as e:
            print(f"❌ Error recording snapshot {i}: {e}")
        
        if i < snapshots:
            time.sleep(1)  # Wait between snapshots
    
    print("\n" + "="*60)
    print("CHECKING ROLLBACK TRIGGERS")
    print("="*60)
    
    # Check rollback triggers
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/models/{model_id}/rollback-check",
            params={
                "window_minutes": 60,
                "auto_remediate": True  # Enable auto-remediation
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n🔍 Rollback Analysis:")
            print(f"   Should Rollback: {'✅ YES' if result['should_rollback'] else '❌ NO'}")
            print(f"   Auto-Remediate: {'✅ ENABLED' if result['auto_remediate'] else '❌ DISABLED'}")
            
            if result['reasons']:
                print(f"\n⚠️ Rollback Reasons:")
                for reason in result['reasons']:
                    print(f"   - {reason}")
            
            if result['should_rollback'] and result['auto_remediate']:
                print(f"\n🔧 Self-healing has been triggered!")
                print(f"   - Incident created")
                print(f"   - Playbook: model_rollback")
                print(f"   - Status will change to ROLLBACK")
        else:
            print(f"❌ Failed to check rollback: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking rollback: {e}")
    
    # Get health status
    print("\n" + "="*60)
    print("HEALTH STATUS")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/models/{model_id}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            health = response.json()
            
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "critical": "🚨",
                "unknown": "❓"
            }
            
            status = health.get('health_status', 'unknown')
            emoji = status_emoji.get(status, "❓")
            
            print(f"\n{emoji} Health Status: {status.upper()}")
            
            if 'metrics' in health:
                metrics = health['metrics']
                if metrics:
                    print(f"\n📊 Recent Metrics:")
                    print(f"   Error Rate: {metrics.get('avg_error_rate', 0):.2%}")
                    print(f"   Latency p95: {metrics.get('avg_latency_p95_ms', 0):.1f}ms")
                    print(f"   OOD Rate: {metrics.get('avg_ood_rate', 0):.2%}")
                    print(f"   Snapshots: {metrics.get('snapshot_count', 0)}")
        else:
            print(f"❌ Failed to get health: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting health: {e}")
    
    # Show next steps
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Check incidents:")
    print(f"   curl {BASE_URL}/api/incidents")
    print("\n2. View model details:")
    print(f"   curl {BASE_URL}{API_PREFIX}/models/{model_id}")
    print("\n3. Monitor production fleet:")
    print(f"   curl {BASE_URL}{API_PREFIX}/monitor/production")
    print("\n4. Execute manual rollback:")
    print(f"   curl -X POST {BASE_URL}{API_PREFIX}/models/{model_id}/rollback?reason=demo")
    print()


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("\n❌ Usage: python simulate_model_degradation.py <model_id> [num_snapshots]")
        print("\nAvailable models:")
        print("  - fraud_detector_v1")
        print("  - sentiment_analyzer_v2")
        print("  - churn_predictor_v3")
        print("  - recommender_system_v4")
        print("  - anomaly_detector_v1")
        print("\nExample:")
        print("  python simulate_model_degradation.py fraud_detector_v1 5")
        sys.exit(1)
    
    model_id = sys.argv[1]
    snapshots = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    simulate_degradation(model_id, snapshots)


if __name__ == "__main__":
    main()
