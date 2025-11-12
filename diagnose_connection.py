"""Diagnose Memory Panel Connection Issues"""
import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 70)
print("GRACE MEMORY PANEL CONNECTION DIAGNOSTIC")
print("=" * 70)
print()

# Test 1: Basic server connection
print("1. Testing server connection...")
try:
    r = requests.get(f"{API_BASE}/docs", timeout=3)
    print(f"   [OK] Server responding on {API_BASE}")
    print(f"   Status: {r.status_code}")
except Exception as e:
    print(f"   [FAIL] Cannot connect to server: {e}")
    exit(1)

print()

# Test 2: Check if memory endpoints exist
print("2. Testing memory endpoints...")
endpoints = [
    ("GET", "/api/memory/status"),
    ("GET", "/api/memory/files"),
]

for method, path in endpoints:
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=2)
        
        if r.status_code == 404:
            print(f"   [FAIL] {method} {path} - NOT FOUND (404)")
            print(f"          Routes not registered! Backend needs restart.")
        elif r.status_code in [200, 401, 403, 422]:
            print(f"   [OK] {method} {path} - EXISTS (status {r.status_code})")
            if r.status_code == 200:
                print(f"        Response preview: {json.dumps(r.json(), indent=8)[:200]}...")
        else:
            print(f"   [WARN] {method} {path} - Unexpected status {r.status_code}")
    except Exception as e:
        print(f"   [ERROR] {method} {path} - {e}")

print()

# Test 3: Check frontend connectivity
print("3. Testing frontend server...")
try:
    r = requests.get("http://localhost:5173", timeout=2)
    print(f"   [OK] Frontend responding on http://localhost:5173")
except Exception as e:
    print(f"   [FAIL] Frontend not running: {e}")
    print(f"          Run: cd frontend && npm run dev")

print()

# Test 4: Check CORS
print("4. Testing CORS headers...")
try:
    r = requests.get(f"{API_BASE}/api/memory/status", headers={
        "Origin": "http://localhost:5173"
    })
    cors_header = r.headers.get("Access-Control-Allow-Origin")
    if cors_header:
        print(f"   [OK] CORS enabled: {cors_header}")
    else:
        print(f"   [WARN] No CORS header found - may cause issues")
except Exception as e:
    print(f"   [ERROR] {e}")

print()
print("=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print()

# Summary
print("NEXT STEPS:")
print()
print("If endpoints show 404:")
print("  1. Stop backend (Ctrl+C)")
print("  2. Restart with: python -m uvicorn backend.main:app --reload --port 8000")
print()
print("If frontend not running:")
print("  1. cd frontend")
print("  2. npm run dev")
print()
print("If endpoints show 401/403:")
print("  1. Login at http://localhost:5173")
print("  2. Check browser console for auth token")
print()
