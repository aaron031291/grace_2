"""Quick API Route Checker - Tests if memory endpoints are available"""

import requests
import sys

API_BASE = "http://localhost:8000"

def check_endpoint(method, path, name):
    """Check if an endpoint is available"""
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=2)
        elif method == "POST":
            response = requests.post(url, timeout=2)
        
        # 401/403 means auth required (endpoint exists)
        # 404 means endpoint not found
        if response.status_code == 404:
            print(f"[FAIL] {method} {path} - NOT FOUND")
            return False
        elif response.status_code in [401, 403]:
            print(f"[ OK ] {method} {path} - EXISTS (auth required)")
            return True
        else:
            print(f"[ OK ] {method} {path} - EXISTS (status {response.status_code})")
            return True
    except requests.exceptions.ConnectionError:
        print(f"[WARN] Cannot connect to {API_BASE}")
        return None
    except Exception as e:
        print(f"[WARN] {method} {path} - ERROR: {e}")
        return None

print("=" * 60)
print("Grace API Route Checker")
print("=" * 60)
print()

# Test server connection
print("Checking server connection...")
try:
    response = requests.get(f"{API_BASE}/docs", timeout=2)
    if response.status_code == 200:
        print(f"[ OK ] Server is running at {API_BASE}")
    else:
        print(f"[WARN] Server responded with status {response.status_code}")
except:
    print(f"[FAIL] Server is NOT running at {API_BASE}")
    print("\nPlease start the backend server first!")
    sys.exit(1)

print()
print("Checking Memory File API endpoints...")
print("-" * 60)

endpoints = [
    ("GET", "/api/memory/status", "Get filesystem status"),
    ("GET", "/api/memory/files", "List files"),
    ("GET", "/api/memory/file", "Read file"),
    ("POST", "/api/memory/file", "Save file"),
    ("POST", "/api/memory/folder", "Create folder"),
    ("GET", "/api/memory/tree", "Get memory tree"),
]

results = []
for method, path, description in endpoints:
    result = check_endpoint(method, path, description)
    results.append(result)

print()
print("=" * 60)

if all(r is True for r in results):
    print("SUCCESS: All memory endpoints are available!")
elif any(r is False for r in results):
    print("RESTART REQUIRED: Some endpoints are missing")
    print()
    print("To fix:")
    print("  1. Stop the backend server (Ctrl+C)")
    print("  2. Restart with: .\\GRACE.ps1")
    print("     or: python -m uvicorn backend.main:app --reload --port 8000")
else:
    print("WARNING: Could not verify all endpoints")

print("=" * 60)
