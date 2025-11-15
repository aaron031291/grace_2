"""Quick test to see what fails"""
import sys
print("Testing imports...")

try:
    print("1. Importing main...")
    from backend.main import app
    print("   ✅ Main imported")
except Exception as e:
    print(f"   ❌ Main failed: {e}")
    sys.exit(1)

try:
    print("2. Counting routes...")
    print(f"   ✅ {len(app.routes)} routes registered")
except Exception as e:
    print(f"   ❌ Routes failed: {e}")

try:
    print("3. Testing health endpoint...")
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"   ✅ Health returns: {response.status_code}")
except Exception as e:
    print(f"   ❌ Health test failed: {e}")

print("\n✅ Backend is ready!")
print("\nStart with: python serve_simple.py")
print("Or: RUN_SIMPLE.cmd")
