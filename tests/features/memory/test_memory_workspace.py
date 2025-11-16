"""
Comprehensive Test Suite for Memory Workspace
Tests all components: file ops, Grace agent, pipelines, search
"""

import asyncio
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"
AUTH_TOKEN = None  # Will be set after login


def login():
    """Login and get auth token"""
    global AUTH_TOKEN
    
    response = requests.post(f"{API_BASE}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        AUTH_TOKEN = data.get("access_token")
        print("✓ Logged in successfully")
        return True
    else:
        print("✗ Login failed")
        return False


def get_headers():
    """Get auth headers"""
    if AUTH_TOKEN:
        return {"Authorization": f"Bearer {AUTH_TOKEN}"}
    return {}


def test_memory_file_api():
    """Test Memory File API endpoints"""
    print("\n" + "="*60)
    print("TEST: Memory File API")
    print("="*60)
    
    # Test 1: Get status
    print("\n1. Testing GET /api/memory/status")
    r = requests.get(f"{API_BASE}/api/memory/status", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Status: {data.get('status')}")
        print(f"   ✓ Files: {data.get('total_files')}")
        print(f"   ✓ Storage: {data.get('total_size_mb')} MB")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 2: List files
    print("\n2. Testing GET /api/memory/files")
    r = requests.get(f"{API_BASE}/api/memory/files", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Root folder: {data.get('name')}")
        print(f"   ✓ Type: {data.get('type')}")
        if data.get('children'):
            print(f"   ✓ Contains {len(data['children'])} items")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 3: Create test file
    print("\n3. Testing POST /api/memory/file (create)")
    test_content = f"# Test File\n\nCreated at {datetime.utcnow().isoformat()}\n"
    r = requests.post(
        f"{API_BASE}/api/memory/file",
        params={"path": "test_file.md", "content": test_content},
        headers=get_headers()
    )
    if r.status_code == 200:
        print("   ✓ File created successfully")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 4: Read file back
    print("\n4. Testing GET /api/memory/file (read)")
    r = requests.get(
        f"{API_BASE}/api/memory/file",
        params={"path": "test_file.md"},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ File read successfully")
        print(f"   ✓ Size: {data.get('size')} bytes")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 5: Search
    print("\n5. Testing GET /api/memory/search")
    r = requests.get(
        f"{API_BASE}/api/memory/search",
        params={"query": "test", "limit": 10},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Search executed")
        print(f"   ✓ Results: {data.get('count')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")


def test_grace_memory_api():
    """Test Grace Memory Agent API"""
    print("\n" + "="*60)
    print("TEST: Grace Memory Agent API")
    print("="*60)
    
    # Test 1: List categories
    print("\n1. Testing GET /api/grace/memory/categories")
    r = requests.get(f"{API_BASE}/api/grace/memory/categories", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        categories = data.get('categories', {})
        print(f"   ✓ Found {len(categories)} categories")
        for cat_name in list(categories.keys())[:3]:
            print(f"   ✓ Category: {cat_name}")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 2: Grace saves research
    print("\n2. Testing POST /api/grace/memory/research")
    r = requests.post(
        f"{API_BASE}/api/grace/memory/research",
        json={
            "title": "Test Research Finding",
            "content": "This is a test research note from automated testing.",
            "domain": "testing",
            "tags": ["test", "automation"],
            "auto_sync": False
        },
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Research saved")
        print(f"   ✓ Path: {data.get('path')}")
        print(f"   ✓ Synced: {data.get('synced')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 3: Grace saves insight
    print("\n3. Testing POST /api/grace/memory/insight")
    r = requests.post(
        f"{API_BASE}/api/grace/memory/insight",
        json={
            "insight": "Automated testing reveals system is working correctly",
            "category_type": "observations",
            "confidence": 0.99,
            "auto_sync": False
        },
        headers=get_headers()
    )
    if r.status_code == 200:
        print("   ✓ Insight saved")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 4: Get action log
    print("\n4. Testing GET /api/grace/memory/actions")
    r = requests.get(
        f"{API_BASE}/api/grace/memory/actions",
        params={"limit": 10},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Action log retrieved")
        print(f"   ✓ Total actions: {data.get('count')}")
        if data.get('actions'):
            latest = data['actions'][-1] if data['actions'] else None
            if latest:
                print(f"   ✓ Latest: {latest.get('action')} - {latest.get('file')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 5: Grace status
    print("\n5. Testing GET /api/grace/memory/status")
    r = requests.get(f"{API_BASE}/api/grace/memory/status", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Agent status: {data.get('status')}")
        print(f"   ✓ Actions logged: {data.get('actions_logged')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")


def test_ingestion_api():
    """Test Ingestion Pipeline API"""
    print("\n" + "="*60)
    print("TEST: Ingestion Pipeline API")
    print("="*60)
    
    # Test 1: List pipelines
    print("\n1. Testing GET /api/ingestion/pipelines")
    r = requests.get(f"{API_BASE}/api/ingestion/pipelines", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        pipelines = data.get('pipelines', [])
        print(f"   ✓ Found {len(pipelines)} pipelines")
        for p in pipelines[:3]:
            print(f"   ✓ Pipeline: {p.get('name')} ({p.get('stages')} stages)")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 2: Get metrics
    print("\n2. Testing GET /api/ingestion/metrics")
    r = requests.get(f"{API_BASE}/api/ingestion/metrics", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Total jobs: {data.get('total_jobs')}")
        print(f"   ✓ Completed: {data.get('complete')}")
        print(f"   ✓ Success rate: {data.get('success_rate')}%")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 3: List jobs
    print("\n3. Testing GET /api/ingestion/jobs")
    r = requests.get(f"{API_BASE}/api/ingestion/jobs", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Jobs found: {data.get('count')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # Test 4: Get insights
    print("\n4. Testing GET /api/ingestion/insights")
    r = requests.get(f"{API_BASE}/api/ingestion/insights", headers=get_headers())
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Insights retrieved")
        if data.get('total_files'):
            print(f"   ✓ Files analyzed: {data.get('total_files')}")
            print(f"   ✓ Avg quality: {data.get('average_quality')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")


def test_file_operations():
    """Test full file workflow"""
    print("\n" + "="*60)
    print("TEST: Complete File Workflow")
    print("="*60)
    
    test_path = f"test_workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    test_content = "This is a comprehensive test of the memory workspace system.\n"
    
    # Create
    print(f"\n1. Creating file: {test_path}")
    r = requests.post(
        f"{API_BASE}/api/memory/file",
        params={"path": test_path, "content": test_content},
        headers=get_headers()
    )
    print(f"   {'✓' if r.status_code == 200 else '✗'} Create: {r.status_code}")
    
    # Read
    print("\n2. Reading file")
    r = requests.get(
        f"{API_BASE}/api/memory/file",
        params={"path": test_path},
        headers=get_headers()
    )
    print(f"   {'✓' if r.status_code == 200 else '✗'} Read: {r.status_code}")
    
    # Update
    print("\n3. Updating file")
    updated_content = test_content + "Updated content!\n"
    r = requests.post(
        f"{API_BASE}/api/memory/file",
        params={"path": test_path, "content": updated_content},
        headers=get_headers()
    )
    print(f"   {'✓' if r.status_code == 200 else '✗'} Update: {r.status_code}")
    
    # Index for search
    print("\n4. Indexing file for search")
    r = requests.post(
        f"{API_BASE}/api/memory/index/{test_path}",
        headers=get_headers()
    )
    print(f"   {'✓' if r.status_code == 200 else '✗'} Index: {r.status_code}")
    
    # Search for it
    print("\n5. Searching for file")
    r = requests.get(
        f"{API_BASE}/api/memory/search",
        params={"query": "comprehensive test", "limit": 10},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        found = any(test_path in str(r) for r in data.get('results', []))
        print(f"   {'✓' if found else '✗'} Found in search: {found}")
    else:
        print(f"   ✗ Search failed: {r.status_code}")
    
    # Delete
    print("\n6. Deleting file")
    r = requests.delete(
        f"{API_BASE}/api/memory/file",
        params={"path": test_path},
        headers=get_headers()
    )
    print(f"   {'✓' if r.status_code == 200 else '✗'} Delete: {r.status_code}")


def test_grace_workflow():
    """Test Grace autonomous workflow"""
    print("\n" + "="*60)
    print("TEST: Grace Autonomous Workflow")
    print("="*60)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # 1. Grace saves research
    print("\n1. Grace saves research")
    r = requests.post(
        f"{API_BASE}/api/grace/memory/research",
        json={
            "title": f"Test Research {timestamp}",
            "content": "This is automated test research content.",
            "domain": "testing",
            "tags": ["test", "automation", "research"],
            "auto_sync": False
        },
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Research saved to: {data.get('path')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # 2. Grace saves insight
    print("\n2. Grace saves insight")
    r = requests.post(
        f"{API_BASE}/api/grace/memory/insight",
        json={
            "insight": f"Test insight generated at {timestamp}",
            "category_type": "observations",
            "confidence": 0.95,
            "auto_sync": False
        },
        headers=get_headers()
    )
    if r.status_code == 200:
        print("   ✓ Insight saved")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # 3. Grace logs immutable event
    print("\n3. Grace logs immutable event")
    r = requests.post(
        f"{API_BASE}/api/grace/memory/immutable-log",
        params={
            "event_type": "test_event",
        },
        json={
            "test_id": timestamp,
            "action": "automated_test",
            "result": "success"
        },
        headers=get_headers()
    )
    if r.status_code == 200:
        print("   ✓ Immutable event logged")
    else:
        print(f"   ✗ Failed: {r.status_code}")
    
    # 4. Check action log
    print("\n4. Checking Grace's action log")
    r = requests.get(
        f"{API_BASE}/api/grace/memory/actions",
        params={"limit": 5},
        headers=get_headers()
    )
    if r.status_code == 200:
        data = r.json()
        actions = data.get('actions', [])
        print(f"   ✓ Recent actions: {len(actions)}")
        for action in actions[:3]:
            print(f"     - {action.get('action')}: {action.get('file', 'N/A')}")
    else:
        print(f"   ✗ Failed: {r.status_code}")


def test_all_endpoints():
    """Test all critical endpoints"""
    print("\n" + "="*60)
    print("TEST: All Endpoint Availability")
    print("="*60)
    
    endpoints = [
        ("GET", "/api/memory/status", "Memory Status"),
        ("GET", "/api/memory/files", "List Files"),
        ("GET", "/api/memory/tree", "Memory Tree"),
        ("GET", "/api/grace/memory/categories", "Grace Categories"),
        ("GET", "/api/grace/memory/status", "Grace Status"),
        ("GET", "/api/ingestion/pipelines", "Ingestion Pipelines"),
        ("GET", "/api/ingestion/metrics", "Ingestion Metrics"),
        ("GET", "/api/ingestion/insights", "Content Insights"),
        ("GET", "/api/memory/search/stats", "Search Stats"),
    ]
    
    print()
    for method, path, name in endpoints:
        url = f"{API_BASE}{path}"
        try:
            r = requests.get(url, headers=get_headers(), timeout=2)
            status = "✓" if r.status_code in [200, 422] else "✗"
            print(f"{status} {name:<25} {r.status_code}")
        except Exception as e:
            print(f"✗ {name:<25} ERROR: {e}")


def main():
    """Run all tests"""
    print("="*60)
    print("GRACE MEMORY WORKSPACE - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"\nStarted: {datetime.utcnow().isoformat()}")
    print(f"Target: {API_BASE}")
    
    # Login first
    print("\n" + "="*60)
    print("AUTHENTICATION")
    print("="*60)
    if not login():
        print("\n✗ Cannot proceed without authentication")
        return
    
    # Run tests
    try:
        test_all_endpoints()
        test_memory_file_api()
        test_grace_memory_api()
        test_ingestion_api()
        test_file_operations()
        test_grace_workflow()
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)
    print(f"\nFinished: {datetime.utcnow().isoformat()}")
    print("\nReview results above for any failures (✗)")
    print("All checks passed (✓) means system is working correctly!")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
