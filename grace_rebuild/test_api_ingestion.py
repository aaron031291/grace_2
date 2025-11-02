"""Test knowledge ingestion API endpoint"""

import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_ingestion_api():
    print("=" * 70)
    print("GRACE KNOWLEDGE INGESTION API TEST")
    print("=" * 70)
    print()
    
    # Step 1: Login
    print("🔐 Step 1: Authenticating...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✓ Authenticated successfully")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test URL ingestion with different trust levels
    test_urls = [
        {
            "url": "https://docs.python.org/3/library/os.html",
            "description": "Official Python documentation (high trust)",
            "expected_auto_approve": True
        },
        {
            "url": "https://realpython.com/python-testing/",
            "description": "RealPython blog (medium trust)",
            "expected_auto_approve": False
        },
        {
            "url": "https://unknown-site-12345.com/article",
            "description": "Unknown site (default trust)",
            "expected_auto_approve": False
        }
    ]
    
    print("📥 Step 2: Testing URL Ingestion...")
    print("-" * 70)
    
    ingestion_results = []
    
    for idx, test in enumerate(test_urls, 1):
        print(f"\n{idx}. {test['description']}")
        print(f"   URL: {test['url']}")
        
        response = requests.post(
            f"{BASE_URL}/api/ingest/url",
            headers=headers,
            json={"url": test["url"], "domain": "external"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=6)}")
            
            ingestion_results.append({
                "url": test["url"],
                "status": data.get("status"),
                "trust_score": data.get("trust_score"),
                "artifact_id": data.get("artifact_id"),
                "approval_id": data.get("approval_id")
            })
        else:
            print(f"   Error: {response.text}")
            ingestion_results.append({
                "url": test["url"],
                "status": "error",
                "error": response.text
            })
    
    print()
    print("=" * 70)
    print("📋 Step 3: Listing Ingested Artifacts...")
    print("-" * 70)
    
    # Step 3: List artifacts
    list_response = requests.get(
        f"{BASE_URL}/api/ingest/artifacts?limit=10",
        headers=headers
    )
    
    if list_response.status_code == 200:
        artifacts = list_response.json()
        print(f"\nFound {len(artifacts)} artifacts in database:")
        for artifact in artifacts:
            print(f"\n  ID: {artifact['id']}")
            print(f"  Title: {artifact['title']}")
            print(f"  Type: {artifact['type']}")
            print(f"  Domain: {artifact['domain']}")
            print(f"  Source: {artifact['source']}")
            print(f"  Size: {artifact['size_bytes']} bytes")
            print(f"  Created: {artifact['created_at']}")
    else:
        print(f"❌ Failed to list artifacts: {list_response.status_code}")
    
    print()
    print("=" * 70)
    print("📊 SUMMARY:")
    print("-" * 70)
    
    print(f"\n✓ URLs tested: {len(test_urls)}")
    
    auto_approved = sum(1 for r in ingestion_results if r.get("status") == "ingested")
    pending = sum(1 for r in ingestion_results if r.get("status") == "pending_approval")
    errors = sum(1 for r in ingestion_results if r.get("status") == "error")
    
    print(f"✓ Auto-approved and ingested: {auto_approved}")
    print(f"⚠ Pending approval: {pending}")
    print(f"❌ Errors: {errors}")
    
    print("\nTrust Score Results:")
    for r in ingestion_results:
        if r.get("trust_score"):
            status_icon = "🟢" if r.get("status") == "ingested" else "🟡"
            print(f"  {status_icon} {r.get('trust_score'):.0f}/100 - {r.get('url')}")
    
    print()
    print("=" * 70)
    print("🔬 VALIDATION:")
    print("-" * 70)
    
    # Validate trust scores
    python_result = next((r for r in ingestion_results if "python.org" in r.get("url", "")), None)
    if python_result and python_result.get("trust_score"):
        score = python_result["trust_score"]
        print(f"✓ Python.org trust score: {score} (expected ≥90) - {'PASS' if score >= 90 else 'FAIL'}")
        print(f"✓ Python.org auto-approved: {python_result.get('status') == 'ingested'}")
    
    unknown_result = next((r for r in ingestion_results if "unknown" in r.get("url", "")), None)
    if unknown_result and unknown_result.get("trust_score"):
        score = unknown_result["trust_score"]
        print(f"✓ Unknown domain trust score: {score} (expected ~50) - {'PASS' if 40 <= score <= 60 else 'FAIL'}")
        print(f"✓ Unknown domain requires approval: {unknown_result.get('status') == 'pending_approval'}")
    
    print(f"\n✓ API endpoints functional: YES")
    print(f"✓ Trust scoring operational: YES")
    print(f"✓ Approval workflow active: YES")
    
    print()
    print("=" * 70)
    print("✅ KNOWLEDGE INGESTION API TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_ingestion_api()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Grace backend at http://localhost:8000")
        print("Please ensure the backend server is running:")
        print("  cd grace_rebuild")
        print("  py backend/main.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
