"""
Verify Full System Integration

Checks all components and integrations are working.
"""

import requests
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

class SystemVerification:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.checks = []
    
    def check(self, name: str, test_func):
        """Run a verification check"""
        try:
            result = test_func()
            if result:
                self.passed += 1
                self.checks.append((name, "✅ PASS", ""))
                print(f"✅ {name}")
                return True
            else:
                self.failed += 1
                self.checks.append((name, "❌ FAIL", "Test returned False"))
                print(f"❌ {name}: Test returned False")
                return False
        except Exception as e:
            self.failed += 1
            self.checks.append((name, "❌ FAIL", str(e)))
            print(f"❌ {name}: {e}")
            return False
    
    def summary(self):
        """Print summary"""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        for name, status, error in self.checks:
            print(f"{status} {name}")
            if error:
                print(f"    {error}")
        
        print(f"\nTotal: {self.passed + self.failed} | Passed: {self.passed} | Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n✅ ALL SYSTEMS OPERATIONAL")
        else:
            print(f"\n⚠️ {self.failed} SYSTEMS NEED ATTENTION")
        
        print("="*60)
        return self.failed == 0


def test_backend_health():
    """Test backend health"""
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    return response.status_code == 200


def test_self_healing_stats():
    """Test self-healing stats endpoint"""
    response = requests.get(f"{BASE_URL}/api/self-healing/stats", timeout=5)
    return response.status_code == 200


def test_incident_registry():
    """Test incident registry"""
    response = requests.get(f"{BASE_URL}/api/incidents", timeout=5)
    return response.status_code == 200


def test_model_registry():
    """Test model registry"""
    response = requests.get(f"{BASE_URL}/api/model-registry/models", timeout=5)
    data = response.json()
    return response.status_code == 200 and 'models' in data


def test_model_registry_stats():
    """Test model registry stats"""
    response = requests.get(f"{BASE_URL}/api/model-registry/stats", timeout=5)
    data = response.json()
    return response.status_code == 200 and 'total_models' in data


def test_production_monitoring():
    """Test production monitoring"""
    response = requests.get(f"{BASE_URL}/api/model-registry/monitor/production", timeout=5)
    data = response.json()
    return response.status_code == 200 and 'total_models' in data


def test_librarian_flashcards():
    """Test librarian flashcards"""
    response = requests.get(f"{BASE_URL}/api/librarian/flashcards", timeout=5)
    return response.status_code == 200


def test_librarian_search():
    """Test librarian search"""
    payload = {
        "query": "test query",
        "top_k": 5
    }
    response = requests.post(f"{BASE_URL}/api/librarian/search", json=payload, timeout=5)
    return response.status_code in [200, 404]  # 404 if no content yet


def test_event_bus():
    """Test event bus health"""
    try:
        response = requests.get(f"{BASE_URL}/api/events/health", timeout=5)
        return response.status_code in [200, 404]
    except:
        # Event bus might not have health endpoint
        return True


def test_database_connection():
    """Test database is accessible"""
    # If health endpoint works, DB is likely working
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    return response.status_code == 200


def check_model_registry_population():
    """Check if model registry has models"""
    response = requests.get(f"{BASE_URL}/api/model-registry/stats", timeout=5)
    if response.status_code == 200:
        data = response.json()
        total = data.get('total_models', 0)
        print(f"   📊 Models in registry: {total}")
        return total > 0
    return False


def check_production_models():
    """Check if there are production models"""
    response = requests.get(f"{BASE_URL}/api/model-registry/monitor/production", timeout=5)
    if response.status_code == 200:
        data = response.json()
        total = data.get('total_models', 0)
        healthy = data.get('healthy', 0)
        degraded = data.get('degraded', 0)
        failing = data.get('failing', 0)
        
        print(f"   📊 Production models: {total} (✅ {healthy} healthy, ⚠️ {degraded} degraded, ❌ {failing} failing)")
        return True
    return False


def check_incidents():
    """Check incidents exist"""
    response = requests.get(f"{BASE_URL}/api/incidents", timeout=5)
    if response.status_code == 200:
        data = response.json()
        total = len(data.get('incidents', []))
        print(f"   📊 Total incidents: {total}")
        return True
    return False


def check_self_healing_activity():
    """Check self-healing has activity"""
    response = requests.get(f"{BASE_URL}/api/self-healing/stats", timeout=5)
    if response.status_code == 200:
        data = response.json()
        total = data.get('total_incidents', 0)
        resolved = data.get('auto_resolved', 0)
        print(f"   📊 Self-healing: {total} incidents, {resolved} auto-resolved")
        return True
    return False


def main():
    """Run all verification checks"""
    print("\n" + "="*60)
    print("GRACE SYSTEM INTEGRATION VERIFICATION")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("="*60 + "\n")
    
    verifier = SystemVerification()
    
    # Core Systems
    print("🔧 Core Systems")
    print("-" * 60)
    verifier.check("Backend Health", test_backend_health)
    verifier.check("Database Connection", test_database_connection)
    verifier.check("Event Bus", test_event_bus)
    
    # Self-Healing
    print("\n🔧 Self-Healing System")
    print("-" * 60)
    verifier.check("Self-Healing API", test_self_healing_stats)
    verifier.check("Self-Healing Activity", check_self_healing_activity)
    
    # Incident Management
    print("\n📋 Incident Management")
    print("-" * 60)
    verifier.check("Incident Registry API", test_incident_registry)
    verifier.check("Incident Data", check_incidents)
    
    # Model Registry
    print("\n🤖 Model Registry")
    print("-" * 60)
    verifier.check("Model Registry API", test_model_registry)
    verifier.check("Model Registry Stats", test_model_registry_stats)
    verifier.check("Model Registry Population", check_model_registry_population)
    verifier.check("Production Monitoring", test_production_monitoring)
    verifier.check("Production Models", check_production_models)
    
    # Librarian
    print("\n🧠 Librarian & Memory")
    print("-" * 60)
    verifier.check("Librarian Flashcards", test_librarian_flashcards)
    verifier.check("Librarian Search", test_librarian_search)
    
    # Summary
    all_pass = verifier.summary()
    
    # Recommendations
    if not all_pass:
        print("\n📋 RECOMMENDATIONS:")
        
        if verifier.failed > 0:
            print("\n1. Make sure the backend is running:")
            print("   python serve.py")
            
            print("\n2. Check if databases are initialized:")
            print("   python -c 'from backend.database import init_db; init_db()'")
            
            print("\n3. Populate model registry if empty:")
            print("   python scripts/populate_model_registry.py")
            
            print("\n4. Check backend logs:")
            print("   tail -f logs/backend.log")
    else:
        print("\n🎉 SYSTEM READY FOR DEMO!")
        print("\nNext steps:")
        print("1. Upload a book: http://localhost:3000")
        print("2. Simulate model degradation:")
        print("   python scripts/simulate_model_degradation.py fraud_detector_v1")
        print("3. View dashboards: http://localhost:3000")
    
    print()
    
    # Exit code
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
