"""
End-to-End API Test for Model Registry

Tests all API endpoints with realistic scenarios
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Base URL - adjust if needed
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/model-registry"


class APITestResults:
    """Track API test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name: str, status_code: int):
        self.passed += 1
        self.tests.append((test_name, f"✅ PASSED ({status_code})"))
        print(f"✅ {test_name} - {status_code}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.tests.append((test_name, f"❌ FAILED: {error}"))
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        print("\n" + "="*60)
        print("API TEST SUMMARY")
        print("="*60)
        for name, result in self.tests:
            print(f"{result}")
        print(f"\nTotal: {self.passed + self.failed} | Passed: {self.passed} | Failed: {self.failed}")
        print("="*60)


async def test_register_model(client: httpx.AsyncClient, results: APITestResults):
    """Test POST /models - Register new model"""
    print("\n🧪 API Test 1: Register Model")
    
    try:
        payload = {
            "model_id": "api_test_fraud_v1",
            "name": "API Test Fraud Detector",
            "version": "1.0.0",
            "framework": "sklearn",
            "model_type": "classification",
            "owner": "api_tester",
            "team": "data_science",
            "training_data_hash": "abc123def456",
            "training_dataset_size": 25000,
            "evaluation_metrics": {
                "accuracy": 0.94,
                "precision": 0.92,
                "recall": 0.91,
                "f1_score": 0.915
            },
            "description": "Test fraud detector for API E2E testing",
            "tags": ["fraud", "api_test", "sklearn"]
        }
        
        response = await client.post(f"{API_PREFIX}/models", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "registered" and data.get("model_id") == "api_test_fraud_v1":
                results.add_pass("Register Model", response.status_code)
            else:
                results.add_fail("Register Model", f"Unexpected response: {data}")
        else:
            results.add_fail("Register Model", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.add_fail("Register Model", str(e))


async def test_get_model(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /models/{model_id} - Get model details"""
    print("\n🧪 API Test 2: Get Model")
    
    try:
        response = await client.get(f"{API_PREFIX}/models/api_test_fraud_v1")
        
        if response.status_code == 200:
            data = response.json()
            model = data.get("model")
            if model and model.get("model_id") == "api_test_fraud_v1":
                print(f"  📊 Model: {model['name']} v{model['version']}")
                results.add_pass("Get Model", response.status_code)
            else:
                results.add_fail("Get Model", f"Invalid model data: {data}")
        else:
            results.add_fail("Get Model", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Get Model", str(e))


async def test_list_models(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /models - List all models"""
    print("\n🧪 API Test 3: List Models")
    
    try:
        response = await client.get(f"{API_PREFIX}/models")
        
        if response.status_code == 200:
            data = response.json()
            if "models" in data and "count" in data:
                print(f"  📊 Found {data['count']} models")
                results.add_pass("List Models", response.status_code)
            else:
                results.add_fail("List Models", f"Invalid response: {data}")
        else:
            results.add_fail("List Models", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("List Models", str(e))


async def test_update_deployment(client: httpx.AsyncClient, results: APITestResults):
    """Test PATCH /models/{model_id}/deployment - Update deployment status"""
    print("\n🧪 API Test 4: Update Deployment Status")
    
    try:
        # Move to sandbox
        payload = {
            "status": "sandbox",
            "canary_percentage": 0.0
        }
        
        response = await client.patch(
            f"{API_PREFIX}/models/api_test_fraud_v1/deployment",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("deployment_status") == "sandbox":
                print(f"  ✅ Promoted to SANDBOX")
                results.add_pass("Update Deployment", response.status_code)
            else:
                results.add_fail("Update Deployment", f"Unexpected status: {data}")
        else:
            results.add_fail("Update Deployment", f"Status {response.status_code}: {response.text}")
            
    except Exception as e:
        results.add_fail("Update Deployment", str(e))


async def test_record_performance(client: httpx.AsyncClient, results: APITestResults):
    """Test POST /models/{model_id}/performance - Record performance snapshot"""
    print("\n🧪 API Test 5: Record Performance Snapshot")
    
    try:
        payload = {
            "model_id": "api_test_fraud_v1",
            "version": "1.0.0",
            "latency_p50_ms": 42.5,
            "latency_p95_ms": 85.3,
            "latency_p99_ms": 120.7,
            "requests_per_second": 180.0,
            "error_rate": 0.002,
            "ood_rate": 0.04,
            "input_drift_score": 0.08,
            "accuracy": 0.94
        }
        
        response = await client.post(
            f"{API_PREFIX}/models/api_test_fraud_v1/performance",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "recorded":
                print(f"  📊 Snapshot recorded at {data.get('timestamp')}")
                results.add_pass("Record Performance", response.status_code)
            else:
                results.add_fail("Record Performance", f"Unexpected response: {data}")
        else:
            results.add_fail("Record Performance", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Record Performance", str(e))


async def test_record_degraded_performance(client: httpx.AsyncClient, results: APITestResults):
    """Record degraded performance to trigger rollback detection"""
    print("\n🧪 API Test 6: Record Degraded Performance")
    
    try:
        # Record multiple degraded snapshots
        for i in range(3):
            payload = {
                "model_id": "api_test_fraud_v1",
                "version": "1.0.0",
                "latency_p50_ms": 55.0,
                "latency_p95_ms": 110.0,
                "latency_p99_ms": 180.0,
                "requests_per_second": 120.0,
                "error_rate": 0.09,  # 9% - should trigger
                "ood_rate": 0.23,    # 23% - should trigger
                "input_drift_score": 0.38  # High drift
            }
            
            response = await client.post(
                f"{API_PREFIX}/models/api_test_fraud_v1/performance",
                json=payload
            )
            
            if response.status_code != 200:
                results.add_fail("Record Degraded Performance", f"Failed on snapshot {i}")
                return
        
        results.add_pass("Record Degraded Performance", 200)
        
    except Exception as e:
        results.add_fail("Record Degraded Performance", str(e))


async def test_rollback_check(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /models/{model_id}/rollback-check - Check rollback triggers"""
    print("\n🧪 API Test 7: Check Rollback Triggers")
    
    try:
        response = await client.get(
            f"{API_PREFIX}/models/api_test_fraud_v1/rollback-check",
            params={"window_minutes": 60, "auto_remediate": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            should_rollback = data.get("should_rollback")
            reasons = data.get("reasons", [])
            
            print(f"  ⚠️ Should Rollback: {should_rollback}")
            print(f"  ⚠️ Reasons: {reasons}")
            
            if should_rollback and len(reasons) > 0:
                results.add_pass("Rollback Check", response.status_code)
            else:
                results.add_fail("Rollback Check", "Expected rollback=True with reasons")
        else:
            results.add_fail("Rollback Check", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Rollback Check", str(e))


async def test_model_health(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /models/{model_id}/health - Get health summary"""
    print("\n🧪 API Test 8: Get Model Health")
    
    try:
        response = await client.get(f"{API_PREFIX}/models/api_test_fraud_v1/health")
        
        if response.status_code == 200:
            data = response.json()
            health_status = data.get("health_status")
            metrics = data.get("metrics", {})
            
            print(f"  🏥 Health Status: {health_status}")
            print(f"  📊 Error Rate: {metrics.get('avg_error_rate', 'N/A')}")
            print(f"  📊 OOD Rate: {metrics.get('avg_ood_rate', 'N/A')}")
            
            if health_status in ["healthy", "degraded", "critical"]:
                results.add_pass("Model Health", response.status_code)
            else:
                results.add_fail("Model Health", f"Invalid health status: {health_status}")
        else:
            results.add_fail("Model Health", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Model Health", str(e))


async def test_production_monitoring(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /monitor/production - Monitor production models"""
    print("\n🧪 API Test 9: Monitor Production")
    
    try:
        response = await client.get(
            f"{API_PREFIX}/monitor/production",
            params={"window_minutes": 60}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"  📊 Total Models: {data.get('total_models')}")
            print(f"  ✅ Healthy: {data.get('healthy')}")
            print(f"  ⚠️ Degraded: {data.get('degraded')}")
            print(f"  ❌ Failing: {data.get('failing')}")
            
            if "total_models" in data and "healthy" in data:
                results.add_pass("Production Monitoring", response.status_code)
            else:
                results.add_fail("Production Monitoring", f"Invalid response: {data}")
        else:
            results.add_fail("Production Monitoring", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Production Monitoring", str(e))


async def test_generate_model_card(client: httpx.AsyncClient, results: APITestResults):
    """Test POST /models/{model_id}/generate-card - Generate model card"""
    print("\n🧪 API Test 10: Generate Model Card")
    
    try:
        response = await client.post(
            f"{API_PREFIX}/models/api_test_fraud_v1/generate-card"
        )
        
        if response.status_code == 200:
            data = response.json()
            card_path = data.get("model_card_path")
            
            print(f"  📄 Model Card: {card_path}")
            
            if card_path:
                results.add_pass("Generate Model Card", response.status_code)
            else:
                results.add_fail("Generate Model Card", "No card path returned")
        else:
            results.add_fail("Generate Model Card", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Generate Model Card", str(e))


async def test_registry_stats(client: httpx.AsyncClient, results: APITestResults):
    """Test GET /stats - Get registry statistics"""
    print("\n🧪 API Test 11: Registry Stats")
    
    try:
        response = await client.get(f"{API_PREFIX}/stats")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"  📊 Total Models: {data.get('total_models')}")
            print(f"  📊 By Stage: {data.get('by_stage')}")
            print(f"  📊 By Framework: {data.get('by_framework')}")
            
            if "total_models" in data and "by_stage" in data:
                results.add_pass("Registry Stats", response.status_code)
            else:
                results.add_fail("Registry Stats", f"Invalid response: {data}")
        else:
            results.add_fail("Registry Stats", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Registry Stats", str(e))


async def test_rollback_execution(client: httpx.AsyncClient, results: APITestResults):
    """Test POST /models/{model_id}/rollback - Execute rollback"""
    print("\n🧪 API Test 12: Execute Rollback")
    
    try:
        response = await client.post(
            f"{API_PREFIX}/models/api_test_fraud_v1/rollback",
            params={
                "reason": "API test rollback",
                "target_version": "0.9.0"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"  🔄 Rollback Status: {data.get('status')}")
            print(f"  🔄 Target Version: {data.get('target_version')}")
            
            if data.get("status") == "rolled_back":
                results.add_pass("Rollback Execution", response.status_code)
            else:
                results.add_fail("Rollback Execution", f"Unexpected response: {data}")
        else:
            results.add_fail("Rollback Execution", f"Status {response.status_code}")
            
    except Exception as e:
        results.add_fail("Rollback Execution", str(e))


async def main():
    """Run all API E2E tests"""
    print("="*60)
    print("MODEL REGISTRY API E2E TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}{API_PREFIX}")
    print("="*60)
    
    results = APITestResults()
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Check if server is running
        try:
            response = await client.get("/health")
            print(f"✅ Server is running (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Server not reachable: {e}")
            print("\n⚠️ Make sure the backend server is running:")
            print("   python serve.py")
            sys.exit(1)
        
        # Run tests
        await test_register_model(client, results)
        await test_get_model(client, results)
        await test_list_models(client, results)
        await test_update_deployment(client, results)
        await test_record_performance(client, results)
        await test_record_degraded_performance(client, results)
        await test_rollback_check(client, results)
        await test_model_health(client, results)
        await test_production_monitoring(client, results)
        await test_generate_model_card(client, results)
        await test_registry_stats(client, results)
        await test_rollback_execution(client, results)
    
    # Summary
    results.summary()
    
    # Exit code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
