"""
Test backend imports and setup
"""

import sys
import traceback

print("="*70)
print("TESTING GRACE BACKEND")
print("="*70)

tests = []

# Test 1: Import main
print("\n[Test 1] Importing main.py...")
try:
    from backend.main import app
    print("✅ PASS: Main app imported")
    tests.append(("Import main", True))
except Exception as e:
    print(f"❌ FAIL: {e}")
    traceback.print_exc()
    tests.append(("Import main", False))

# Test 2: Check remote access
print("\n[Test 2] Checking remote access...")
try:
    from backend.remote_access.zero_trust_gate import zero_trust_gate
    from backend.remote_access.rbac_enforcer import rbac_enforcer
    print("✅ PASS: Remote access modules loaded")
    tests.append(("Remote access", True))
except Exception as e:
    print(f"❌ FAIL: {e}")
    traceback.print_exc()
    tests.append(("Remote access", False))

# Test 3: Check learning system
print("\n[Test 3] Checking learning system...")
try:
    from backend.learning_systems.autonomous_curriculum import autonomous_curriculum
    from backend.learning_systems.project_builder import project_builder
    print("✅ PASS: Learning system loaded")
    print(f"   Domains: {autonomous_curriculum.total_domains}")
    tests.append(("Learning system", True))
except Exception as e:
    print(f"❌ FAIL: {e}")
    traceback.print_exc()
    tests.append(("Learning system", False))

# Test 4: Check routes
print("\n[Test 4] Checking API routes...")
try:
    if 'app' in locals():
        route_count = len(app.routes)
        print(f"✅ PASS: {route_count} routes registered")
        tests.append(("API routes", True))
    else:
        print("❌ FAIL: App not loaded")
        tests.append(("API routes", False))
except Exception as e:
    print(f"❌ FAIL: {e}")
    tests.append(("API routes", False))

# Test 5: Test health endpoint
print("\n[Test 5] Testing health endpoint...")
try:
    from fastapi.testclient import TestClient
    if 'app' in locals():
        client = TestClient(app)
        response = client.get("/health")
        if response.status_code == 200:
            print(f"✅ PASS: Health endpoint returns 200")
            tests.append(("Health endpoint", True))
        else:
            print(f"❌ FAIL: Health endpoint returns {response.status_code}")
            tests.append(("Health endpoint", False))
    else:
        print("❌ FAIL: App not loaded")
        tests.append(("Health endpoint", False))
except Exception as e:
    print(f"❌ FAIL: {e}")
    tests.append(("Health endpoint", False))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for _, result in tests if result)
failed = sum(1 for _, result in tests if not result)

for test_name, result in tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

print(f"\nTotal: {passed} passed, {failed} failed")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED!")
    print("\nGrace is ready to start:")
    print("  python serve.py")
    print("  or")
    print("  START.cmd")
else:
    print(f"\n⚠️  {failed} test(s) failed")
    print("\nFix errors above before starting Grace")

print("="*70)
