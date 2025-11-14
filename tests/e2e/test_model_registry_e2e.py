"""
End-to-End Test for Model Registry Integration

Tests:
1. Model registration
2. Performance snapshot recording
3. Rollback trigger detection
4. Incident creation integration
5. Self-healing integration
6. Monitoring event emission
7. API endpoints
"""

import asyncio
import sys
import io
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.model_registry import (
    ModelRegistry,
    ModelRegistryEntry,
    ModelPerformanceSnapshot,
    DeploymentStage,
    get_registry
)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        self.tests.append((test_name, "✅ PASSED"))
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.tests.append((test_name, f"❌ FAILED: {error}"))
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        for name, result in self.tests:
            print(f"{result}")
        print(f"\nTotal: {self.passed + self.failed} | Passed: {self.passed} | Failed: {self.failed}")
        print("="*60)


# Track incidents and events
incidents_created = []
monitoring_events = []
self_healing_triggered = []
test_registry = None  # Shared registry instance


async def incident_callback(**kwargs):
    """Mock incident creation"""
    incidents_created.append(kwargs)
    print(f"  📝 Incident created: {kwargs['title']}")


async def monitoring_callback(**kwargs):
    """Mock monitoring event"""
    monitoring_events.append(kwargs)
    print(f"  📊 Monitoring event: {kwargs['event_type']}")


async def self_healing_callback(**kwargs):
    """Mock self-healing trigger"""
    self_healing_triggered.append(kwargs)
    print(f"  🔧 Self-healing triggered: {kwargs['playbook']}")


async def test_basic_registration(results: TestResults):
    """Test 1: Basic model registration"""
    print("\n🧪 Test 1: Basic Model Registration")
    
    try:
        registry = ModelRegistry(registry_path="test_registry.yaml")
        
        entry = ModelRegistryEntry(
            model_id="test_model_001",
            name="Test Fraud Detector",
            version="1.0.0",
            artifact_path="models/test_fraud.pkl",
            framework="sklearn",
            model_type="classification",
            owner="test_user",
            team="ml_team",
            training_data_hash="abc123",
            training_dataset_size=10000,
            training_timestamp=datetime.now(),
            evaluation_metrics={
                "accuracy": 0.95,
                "precision": 0.93,
                "recall": 0.92,
                "f1_score": 0.925
            },
            description="Test fraud detection model",
            tags=["fraud", "classification", "test"]
        )
        
        success = registry.register_model(entry)
        
        if success:
            # Verify it was saved
            loaded_entry = registry.get_model("test_model_001")
            if loaded_entry and loaded_entry.name == "Test Fraud Detector":
                results.add_pass("Model Registration")
            else:
                results.add_fail("Model Registration", "Model not found after save")
        else:
            results.add_fail("Model Registration", "Registration returned False")
            
    except Exception as e:
        results.add_fail("Model Registration", str(e))


async def test_deployment_lifecycle(results: TestResults):
    """Test 2: Deployment lifecycle"""
    print("\n🧪 Test 2: Deployment Lifecycle")
    
    try:
        registry = ModelRegistry(registry_path="test_registry.yaml")
        
        # Should start in DEVELOPMENT
        entry = registry.get_model("test_model_001")
        if entry.deploy_status != DeploymentStage.DEVELOPMENT:
            results.add_fail("Initial Deployment Status", f"Expected DEVELOPMENT, got {entry.deploy_status}")
            return
        
        # Move to SANDBOX
        registry.update_deployment_status("test_model_001", DeploymentStage.SANDBOX)
        entry = registry.get_model("test_model_001")
        if entry.deploy_status != DeploymentStage.SANDBOX:
            results.add_fail("Deployment Status Update", "Failed to update to SANDBOX")
            return
        
        # Move to PRODUCTION
        registry.update_deployment_status("test_model_001", DeploymentStage.PRODUCTION)
        entry = registry.get_model("test_model_001")
        if entry.deploy_status == DeploymentStage.PRODUCTION and entry.deployed_at is not None:
            results.add_pass("Deployment Lifecycle")
        else:
            results.add_fail("Deployment Lifecycle", "Failed to promote to PRODUCTION")
            
    except Exception as e:
        results.add_fail("Deployment Lifecycle", str(e))


async def test_performance_snapshots(results: TestResults):
    """Test 3: Performance snapshot recording"""
    print("\n🧪 Test 3: Performance Snapshot Recording")
    
    global test_registry  # Keep registry instance across tests
    
    try:
        test_registry = ModelRegistry(registry_path="test_registry.yaml")
        test_registry.set_monitoring_callback(monitoring_callback)
        test_registry.set_incident_callback(incident_callback)
        test_registry.set_self_healing_callback(self_healing_callback)
        
        # Clear previous events
        monitoring_events.clear()
        
        # Record healthy snapshot
        snapshot = ModelPerformanceSnapshot(
            model_id="test_model_001",
            version="1.0.0",
            timestamp=datetime.now(),
            latency_p50_ms=45.2,
            latency_p95_ms=89.5,
            latency_p99_ms=125.3,
            requests_per_second=150.0,
            error_rate=0.001,  # 0.1% - healthy
            ood_rate=0.05,
            input_drift_score=0.05
        )
        
        await test_registry.record_performance_snapshot(snapshot)
        
        # Verify snapshot was recorded
        if "test_model_001" in test_registry.performance_history:
            snapshots = test_registry.performance_history["test_model_001"]
            if len(snapshots) > 0 and len(monitoring_events) > 0:
                results.add_pass("Performance Snapshot Recording")
            else:
                results.add_fail("Performance Snapshot Recording", "No monitoring event emitted")
        else:
            results.add_fail("Performance Snapshot Recording", "Snapshot not in history")
            
    except Exception as e:
        results.add_fail("Performance Snapshot Recording", str(e))


async def test_rollback_detection(results: TestResults):
    """Test 4: Rollback trigger detection"""
    print("\n🧪 Test 4: Rollback Trigger Detection")
    
    global test_registry
    
    try:
        # Use shared registry
        # Record degraded performance snapshots
        for i in range(5):
            snapshot = ModelPerformanceSnapshot(
                model_id="test_model_001",
                version="1.0.0",
                timestamp=datetime.now(),
                latency_p50_ms=50.0,
                latency_p95_ms=95.0,
                latency_p99_ms=130.0,
                requests_per_second=140.0,
                error_rate=0.08,  # 8% - should trigger rollback
                ood_rate=0.25,    # 25% - should trigger rollback
                input_drift_score=0.35  # High drift - should trigger
            )
            await test_registry.record_performance_snapshot(snapshot)
        
        # Check rollback triggers (without auto-remediate)
        should_rollback, reasons = await test_registry.check_rollback_triggers(
            "test_model_001",
            window_minutes=60,
            auto_remediate=False
        )
        
        if should_rollback and len(reasons) >= 2:
            print(f"  ⚠️ Rollback reasons: {reasons}")
            results.add_pass("Rollback Detection")
        else:
            results.add_fail("Rollback Detection", f"Expected rollback=True, got {should_rollback}")
            
    except Exception as e:
        results.add_fail("Rollback Detection", str(e))


async def test_incident_integration(results: TestResults):
    """Test 5: Incident creation integration"""
    print("\n🧪 Test 5: Incident Integration")
    
    global test_registry
    
    try:
        # Clear previous incidents
        incidents_created.clear()
        self_healing_triggered.clear()
        
        # Trigger rollback with auto-remediate (creates incident)
        should_rollback, reasons = await test_registry.check_rollback_triggers(
            "test_model_001",
            window_minutes=60,
            auto_remediate=True
        )
        
        print(f"  Should rollback: {should_rollback}, Incidents: {len(incidents_created)}")
        
        # Verify incident was created
        if len(incidents_created) > 0:
            incident = incidents_created[0]
            if (incident['source'] == 'model_registry' and 
                incident['resource_type'] == 'ml_model' and
                'High error rate' in str(incident['description'])):
                results.add_pass("Incident Integration")
            else:
                results.add_fail("Incident Integration", f"Unexpected incident format: {incident}")
        else:
            results.add_fail("Incident Integration", f"No incident created (should_rollback={should_rollback}, reasons={reasons})")
            
    except Exception as e:
        results.add_fail("Incident Integration", str(e))


async def test_self_healing_integration(results: TestResults):
    """Test 6: Self-healing integration"""
    print("\n🧪 Test 6: Self-Healing Integration")
    
    try:
        # Use the already triggered self-healing from test 5
        print(f"  Self-healing triggers from test 5: {len(self_healing_triggered)}")
        
        # Verify self-healing was triggered in previous test
        if len(self_healing_triggered) > 0:
            trigger = self_healing_triggered[0]
            if (trigger['playbook'] == 'model_rollback' and
                trigger['resource_type'] == 'ml_model' and
                trigger['resource_id'] == 'test_model_001'):
                results.add_pass("Self-Healing Integration")
            else:
                results.add_fail("Self-Healing Integration", f"Unexpected trigger: {trigger}")
        else:
            results.add_fail("Self-Healing Integration", "No self-healing triggered")
            
    except Exception as e:
        results.add_fail("Self-Healing Integration", str(e))


async def test_rollback_execution(results: TestResults):
    """Test 7: Rollback execution"""
    print("\n🧪 Test 7: Rollback Execution")
    
    try:
        registry = ModelRegistry(registry_path="test_registry.yaml")
        registry.set_incident_callback(incident_callback)
        registry.set_monitoring_callback(monitoring_callback)
        
        incidents_created.clear()
        monitoring_events.clear()
        
        # Perform rollback
        success = await registry.perform_rollback("test_model_001", target_version="0.9.5")
        
        if success:
            # Verify status changed to ROLLBACK
            entry = registry.get_model("test_model_001")
            if entry.deploy_status == DeploymentStage.ROLLBACK:
                # Check incident and event were created
                incident_created = any(i['title'].startswith('Model rollback executed') for i in incidents_created)
                event_emitted = any(e['event_type'] == 'model.rollback' for e in monitoring_events)
                
                if incident_created and event_emitted:
                    results.add_pass("Rollback Execution")
                else:
                    results.add_fail("Rollback Execution", "Missing incident or event")
            else:
                results.add_fail("Rollback Execution", f"Status not ROLLBACK: {entry.deploy_status}")
        else:
            results.add_fail("Rollback Execution", "Rollback returned False")
            
    except Exception as e:
        results.add_fail("Rollback Execution", str(e))


async def test_health_monitoring(results: TestResults):
    """Test 8: Health monitoring"""
    print("\n🧪 Test 8: Health Monitoring")
    
    try:
        registry = ModelRegistry(registry_path="test_registry.yaml")
        
        # Get health summary
        summary = registry.get_model_health_summary("test_model_001")
        
        if 'error' in summary:
            results.add_fail("Health Monitoring", summary['error'])
            return
        
        # Verify summary structure
        if (summary['model_id'] == 'test_model_001' and
            'health_status' in summary and
            'metrics' in summary):
            print(f"  📊 Health Status: {summary['health_status']}")
            print(f"  📊 Metrics: {summary['metrics']}")
            results.add_pass("Health Monitoring")
        else:
            results.add_fail("Health Monitoring", "Invalid summary structure")
            
    except Exception as e:
        results.add_fail("Health Monitoring", str(e))


async def test_production_monitoring(results: TestResults):
    """Test 9: Production fleet monitoring"""
    print("\n🧪 Test 9: Production Fleet Monitoring")
    
    try:
        registry = ModelRegistry(registry_path="test_registry.yaml")
        
        # Note: test_model_001 is in ROLLBACK status now, so no production models
        # Let's create another model in production
        
        prod_model = ModelRegistryEntry(
            model_id="prod_model_001",
            name="Production Model",
            version="2.0.0",
            artifact_path="models/prod.pkl",
            framework="pytorch",
            model_type="classification",
            owner="ml_ops",
            team="platform",
            training_data_hash="xyz789",
            training_dataset_size=50000,
            training_timestamp=datetime.now(),
            deploy_status=DeploymentStage.PRODUCTION,
            evaluation_metrics={"accuracy": 0.98}
        )
        
        registry.register_model(prod_model)
        
        # Add healthy snapshot
        snapshot = ModelPerformanceSnapshot(
            model_id="prod_model_001",
            version="2.0.0",
            timestamp=datetime.now(),
            latency_p50_ms=30.0,
            latency_p95_ms=60.0,
            latency_p99_ms=90.0,
            requests_per_second=300.0,
            error_rate=0.005,  # 0.5% - healthy
            ood_rate=0.03
        )
        
        await registry.record_performance_snapshot(snapshot)
        
        # Monitor production fleet
        health = await registry.monitor_production_models(window_minutes=60)
        
        print(f"  📊 Production Fleet: {health['total_models']} total, "
              f"{health['healthy']} healthy, {health['degraded']} degraded, {health['failing']} failing")
        
        if health['total_models'] >= 1:
            results.add_pass("Production Monitoring")
        else:
            results.add_fail("Production Monitoring", f"Expected production models, got {health}")
            
    except Exception as e:
        results.add_fail("Production Monitoring", str(e))


async def test_model_card_generation(results: TestResults):
    """Test 10: Model card generation"""
    print("\n🧪 Test 10: Model Card Generation")
    
    global test_registry
    
    try:
        # Generate model card
        card_path = test_registry.generate_model_card("test_model_001", output_path="test_model_card.md")
        
        # Verify file exists
        if Path(card_path).exists():
            with open(card_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key sections
            if ("# Model Card:" in content and
                "## Model Details" in content and
                "## Evaluation Metrics" in content and
                "## Governance" in content):
                print(f"  📄 Model card generated: {card_path}")
                results.add_pass("Model Card Generation")
            else:
                results.add_fail("Model Card Generation", "Missing expected sections")
        else:
            results.add_fail("Model Card Generation", "File not created")
            
    except Exception as e:
        import traceback
        results.add_fail("Model Card Generation", f"{str(e)}\n{traceback.format_exc()}")


async def cleanup():
    """Cleanup test files"""
    print("\n🧹 Cleaning up test files...")
    
    files_to_remove = [
        "test_registry.yaml",
        "test_model_card.md"
    ]
    
    for file in files_to_remove:
        try:
            Path(file).unlink(missing_ok=True)
        except Exception as e:
            print(f"  ⚠️ Could not remove {file}: {e}")


async def main():
    """Run all E2E tests"""
    print("="*60)
    print("MODEL REGISTRY E2E INTEGRATION TESTS")
    print("="*60)
    
    results = TestResults()
    
    # Run tests in sequence
    await test_basic_registration(results)
    await test_deployment_lifecycle(results)
    await test_performance_snapshots(results)
    await test_rollback_detection(results)
    await test_incident_integration(results)
    await test_self_healing_integration(results)
    await test_rollback_execution(results)
    await test_health_monitoring(results)
    await test_production_monitoring(results)
    await test_model_card_generation(results)
    
    # Show integration summary
    print("\n" + "="*60)
    print("INTEGRATION VERIFICATION")
    print("="*60)
    print(f"Incidents Created: {len(incidents_created)}")
    print(f"Monitoring Events: {len(monitoring_events)}")
    print(f"Self-Healing Triggered: {len(self_healing_triggered)}")
    
    # Show summary
    results.summary()
    
    # Cleanup
    await cleanup()
    
    # Exit code
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
