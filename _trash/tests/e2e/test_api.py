"""
Quick API test to verify book routes are registered
"""
import requests

print("Testing Grace Book API endpoints...")
print("="*60)

base_url = "http://localhost:8000"

endpoints = [
    "/api/books/stats",
    "/api/books/recent",
    "/api/librarian/file-operations",
    "/api/librarian/organization-suggestions"
]

for endpoint in endpoints:
    try:
        response = requests.get(base_url + endpoint, timeout=2)
        status = "✓" if response.status_code != 404 else "✗"
        print(f"{status} {endpoint} → {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"✗ {endpoint} → ERROR: {e}")

print("="*60)
print("\nIf you see 404s, routes aren't registered.")
print("Restart backend: python serve.py")
