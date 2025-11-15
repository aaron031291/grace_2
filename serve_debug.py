"""
Debug version of serve.py with better error reporting
"""

import sys
import traceback

print("\n" + "="*70)
print("GRACE BACKEND - DEBUG MODE")
print("="*70)

# Test imports first
print("\n[1/4] Testing imports...")
try:
    from backend.main import app
    print("[OK] Main app imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import app: {e}")
    print("\nFull error:")
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n[2/4] Checking routes...")
try:
    print(f"[OK] App routes registered: {len(app.routes)} routes")
except Exception as e:
    print(f"[WARN] Error checking routes: {e}")

print("\n[3/4] Testing basic endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"[OK] Health endpoint works: {response.status_code}")
except Exception as e:
    print(f"[WARN] Could not test endpoint: {e}")

print("\n[4/4] Starting server...")
print("\nGrace will be available at:")
print("  - API: http://localhost:8000")
print("  - Docs: http://localhost:8000/docs")
print("  - Health: http://localhost:8000/health")
print("\nPress Ctrl+C to stop")
print("="*70)
print()

try:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except KeyboardInterrupt:
    print("\n\nShutting down gracefully...")
except Exception as e:
    print(f"\n[ERROR] Server error: {e}")
    traceback.print_exc()
    input("\nPress Enter to exit...")
