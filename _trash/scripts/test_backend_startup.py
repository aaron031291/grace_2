"""
Test Backend Startup
Verifies backend can initialize without running server
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 80)
print("BACKEND STARTUP TEST")
print("=" * 80)

tests_passed = 0
tests_failed = 0

# Test 1: Import FastAPI app
print("\n[1/5] Importing FastAPI app...")
try:
    from grace_rebuild.backend.main import app
    print("  PASS: FastAPI app imported")
    print(f"  App title: {app.title}")
    print(f"  App version: {app.version}")
    tests_passed += 1
except Exception as e:
    print(f"  FAIL: {e}")
    tests_failed += 1

# Test 2: Check routes registered
print("\n[2/5] Checking routes...")
try:
    routes = [r.path for r in app.routes]
    cognition_routes = [r for r in routes if '/cognition' in r]
    
    print(f"  PASS: {len(routes)} total routes")
    print(f"  Cognition routes: {len(cognition_routes)}")
    for r in cognition_routes[:5]:
        print(f"    - {r}")
    tests_passed += 1
except Exception as e:
    print(f"  FAIL: {e}")
    tests_failed += 1

# Test 3: Check database models
print("\n[3/5] Checking database models...")
try:
    from grace_rebuild.backend.models import Base
    from grace_rebuild.backend.metrics_models import MetricEvent, MetricsRollup
    
    tables = Base.metadata.tables.keys()
    metrics_tables = [t for t in tables if 'metric' in t]
    
    print(f"  PASS: {len(tables)} total tables")
    print(f"  Metrics tables: {metrics_tables}")
    tests_passed += 1
except Exception as e:
    print(f"  FAIL: {e}")
    tests_failed += 1

# Test 4: Check metrics system
print("\n[4/5] Checking metrics system...")
try:
    from grace_rebuild.backend.metrics_service import get_metrics_collector
    from grace_rebuild.backend.cognition_metrics import get_metrics_engine
    
    collector = get_metrics_collector()
    engine = get_metrics_engine()
    
    print(f"  PASS: Metrics system ready")
    print(f"  Collector metrics: {len(collector.metrics)}")
    print(f"  Engine domains: {len(engine.domains)}")
    tests_passed += 1
except Exception as e:
    print(f"  FAIL: {e}")
    tests_failed += 1

# Test 5: Check cognition router
print("\n[5/5] Checking cognition router...")
try:
    from grace_rebuild.backend.routers.cognition import router
    
    routes = [r.path for r in router.routes]
    print(f"  PASS: Cognition router loaded")
    print(f"  Routes: {len(routes)}")
    for r in routes[:5]:
        print(f"    - {r}")
    tests_passed += 1
except Exception as e:
    print(f"  FAIL: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 80)
print("STARTUP TEST SUMMARY")
print("=" * 80)
print(f"Passed: {tests_passed}/5")
print(f"Failed: {tests_failed}/5")

if tests_failed == 0:
    print("\nSUCCESS: Backend can start. Run: batch_scripts\\start_backend.bat")
else:
    print("\nFAILURE: Fix errors above before starting backend")

print("=" * 80)

sys.exit(0 if tests_failed == 0 else 1)
