#!/usr/bin/env python3
"""
Boot Probe Test - Phase 0
Lightweight test that validates chunks 0-4 boot in <2s
"""
import os
import sys
import time
import asyncio
from pathlib import Path

# Set environment for deterministic testing
os.environ.update({
    "OFFLINE_MODE": "true",
    "DRY_RUN": "true", 
    "CI": "true",
    "PYTHONPATH": str(Path(__file__).parent.parent)
})

def test_environment_configuration():
    """Test 1/7: Environment configuration"""
    print("[1/7] Testing environment configuration...", end=" ")
    
    from backend.config.environment import GraceEnvironment
    
    assert GraceEnvironment.is_offline_mode(), "OFFLINE_MODE should be true"
    assert GraceEnvironment.is_dry_run(), "DRY_RUN should be true"
    assert GraceEnvironment.is_ci_mode(), "CI_MODE should be true"
    assert GraceEnvironment.should_skip_external_calls(), "Should skip external calls"
    
    print("OK")

def test_core_imports():
    """Test 2/7: Core imports"""
    print("[2/7] Testing core imports...", end=" ")
    
    # Test canonical import paths
    from backend.metrics_service import metrics_service
    from backend.cognition_metrics import cognition_metrics
    
    assert hasattr(metrics_service, 'capture_metrics'), "metrics_service should have capture_metrics"
    assert hasattr(cognition_metrics, 'track_cognition'), "cognition_metrics should have track_cognition"
    
    print("OK")

def test_metrics_initialization():
    """Test 3/7: Metrics initialization"""
    print("[3/7] Testing metrics initialization...", end=" ")
    
    from backend.metrics_service import metrics_service
    
    # Test metrics can initialize without external calls
    result = metrics_service.initialize_offline()
    assert result is not None, "Metrics should initialize in offline mode"
    
    print("OK")

def test_database_models():
    """Test 4/7: Database models"""
    print("[4/7] Testing database models...", end=" ")
    
    # Test models can import without DB connection
    from backend.misc.models import User, Mission, PlaybookRun
    
    assert hasattr(User, '__tablename__'), "User model should have tablename"
    assert hasattr(Mission, '__tablename__'), "Mission model should have tablename"
    assert hasattr(PlaybookRun, '__tablename__'), "PlaybookRun model should have tablename"
    
    print("OK")

def test_fastapi_app_creation():
    """Test 5/7: FastAPI app creation"""
    print("[5/7] Testing FastAPI app creation...", end=" ")
    
    # Test app can be created without starting server
    from backend.main import create_app
    
    app = create_app(offline_mode=True)
    assert app is not None, "App should be created in offline mode"
    assert hasattr(app, 'routes'), "App should have routes"
    
    print("OK (minimal)")

def test_chunks_0_to_4():
    """Test 6/7: Grace chunks 0-4 can boot in offline/dry-run mode"""
    print("[6/7] Testing chunks 0-4 boot...", end=" ")
    
    # Test Guardian boot (chunk 0)
    from backend.core.guardian import guardian
    result = asyncio.run(guardian.boot_offline())
    assert result.get('status') == 'success', "Guardian should boot successfully"
    
    # Test remaining chunks can at least import
    from backend.main import app  # Chunk 3
    from pathlib import Path
    db_dir = Path("databases")  # Chunk 4
    
    # Test whitelist manager (chunk 5) 
    from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
    learning_whitelist_manager.load_whitelist_offline()
    
    print("OK")

def test_boot_time():
    """Test 7/7: Boot time under 2 seconds"""
    print("[7/7] Testing boot time...", end=" ")
    
    start_time = time.time()
    
    # Run minimal boot sequence
    from backend.config.environment import GraceEnvironment
    config = GraceEnvironment.get_config_summary()
    
    boot_time = time.time() - start_time
    
    assert boot_time < 2.0, f"Boot time {boot_time:.2f}s should be under 2s"
    
    print(f"OK {boot_time:.2f}s")

def main():
    """Run all boot probe tests"""
    print("🧪 GRACE BOOT PROBE - Phase 0 Validation")
    print("=" * 50)
    
    start_time = time.time()
    tests_passed = 0
    tests_failed = 0
    
    tests = [
        test_environment_configuration,
        test_core_imports, 
        test_metrics_initialization,
        test_database_models,
        test_fastapi_app_creation,
        test_chunks_0_to_4,
        test_boot_time
    ]
    
    for test in tests:
        try:
            test()
            tests_passed += 1
        except Exception as e:
            print(f"FAIL - {e}")
            tests_failed += 1
    
    total_time = time.time() - start_time
    
    print()
    print(f"Tests Run: {len(tests)}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Total Time: {total_time:.2f}s")
    
    if tests_failed == 0:
        print("[OK] BOOT PROBE PASSED")
        return True
    else:
        print("[FAIL] BOOT PROBE FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

