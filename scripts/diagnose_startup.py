"""
Startup Diagnostics Script
Tests all imports and routes before starting server
"""

import sys
import os
import io

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test critical imports"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    tests = [
        ("Metrics Service", "from backend.metrics_service import publish_metric"),
        ("Cognition Metrics", "from backend.cognition_metrics import cognition_engine"),
        ("Guardian Registry", "from backend.guardian.playbook_registry import guardian_registry"),
        ("OSI Canary Probes", "from backend.guardian.osi_canary_probes import osi_canary_probes"),
        ("Metrics Publisher", "from backend.guardian.metrics_publisher import guardian_metrics_publisher"),
        ("Vector API Router", "from backend.routes.vector_api import router"),
        ("Phase 6 API Router", "from backend.routes.phase6_api import router"),
        ("FastAPI App", "from backend.main import app"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed.append((name, str(e)))
    
    return failed

def test_routes():
    """Test route registration"""
    print("\n" + "="*60)
    print("TESTING ROUTE REGISTRATION")
    print("="*60)
    
    try:
        from backend.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        required_routes = [
            "/health",
            "/api/vectors/health",
            "/api/guardian/health",
        ]
        
        for req_route in required_routes:
            if req_route in routes:
                print(f"[OK] {req_route}")
            else:
                print(f"[FAIL] {req_route} - NOT FOUND")
        
        print(f"\nTotal routes registered: {len(routes)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to check routes: {e}")
        return False

def test_guardian_metrics():
    """Test Guardian metrics publisher"""
    print("\n" + "="*60)
    print("TESTING GUARDIAN METRICS PUBLISHER")
    print("="*60)
    
    try:
        from backend.guardian.metrics_publisher import guardian_metrics_publisher
        import asyncio
        
        # Test OSI probe import within publisher
        result = asyncio.run(guardian_metrics_publisher.publish_osi_probe_metrics())
        print(f"[OK] OSI metrics published successfully")
        return True
        
    except Exception as e:
        print(f"[FAIL] Guardian metrics publisher failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    print("\n" + "="*60)
    print("GRACE STARTUP DIAGNOSTICS")
    print("="*60)
    
    # Test imports
    import_failures = test_imports()
    
    # Test routes
    routes_ok = test_routes()
    
    # Test Guardian metrics
    metrics_ok = test_guardian_metrics()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if not import_failures and routes_ok and metrics_ok:
        print("[SUCCESS] ALL CHECKS PASSED - Ready to start server")
        return 0
    else:
        print("[ERROR] SOME CHECKS FAILED")
        if import_failures:
            print("\nFailed imports:")
            for name, error in import_failures:
                print(f"  - {name}: {error}")
        print("\nFix errors before starting server")
        return 1

if __name__ == "__main__":
    sys.exit(main())
