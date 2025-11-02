#!/usr/bin/env python3
"""Comprehensive system test - Find what works and what breaks"""

import requests
import time
import json

BASE = "http://localhost:8000"
TOKEN = None

def test(name, func):
    """Run test and report result"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print('='*60)
        func()
        print(f"[PASS] {name}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}")
        print(f"   Error: {e}")
        return False

def test_health():
    """Test 1: Backend health"""
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    print(f"   Response: {r.json()}")

def test_register():
    """Test 2: User registration"""
    r = requests.post(f"{BASE}/api/auth/register", json={
        "username": "testuser",
        "password": "testpass"
    })
    if r.status_code == 201:
        global TOKEN
        TOKEN = r.json()["access_token"]
        print(f"   Token obtained: {TOKEN[:20]}...")
    elif r.status_code == 400 and "already registered" in r.text:
        print("   User exists, trying login...")
        test_login()
    else:
        raise Exception(f"Unexpected status: {r.status_code}")

def test_login():
    """Test 3: User login"""
    r = requests.post(f"{BASE}/api/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert r.status_code == 200
    global TOKEN
    TOKEN = r.json()["access_token"]
    print(f"   Token: {TOKEN[:20]}...")

def test_chat():
    """Test 4: Chat message"""
    r = requests.post(f"{BASE}/api/chat/", 
        json={"message": "Hello Grace"},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert r.status_code == 200
    print(f"   Grace: {r.json()['response'][:50]}...")

def test_metrics():
    """Test 5: Metrics"""
    r = requests.get(f"{BASE}/api/metrics/summary")
    assert r.status_code == 200
    print(f"   Metrics: {r.json()}")

def test_reflections():
    """Test 6: Reflections"""
    r = requests.get(f"{BASE}/api/reflections/")
    assert r.status_code == 200
    print(f"   Reflections: {len(r.json())} found")

def test_tasks():
    """Test 7: Tasks"""
    r = requests.get(f"{BASE}/api/tasks/",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert r.status_code == 200
    print(f"   Tasks: {len(r.json())} found")

def test_sandbox_files():
    """Test 8: Sandbox file list"""
    r = requests.get(f"{BASE}/api/sandbox/files",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert r.status_code == 200
    print(f"   Files: {r.json()}")

def test_memory_tree():
    """Test 9: Memory tree"""
    r = requests.get(f"{BASE}/api/memory/tree",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    assert r.status_code == 200
    print(f"   Tree structure exists")

def test_governance_policies():
    """Test 10: Governance policies"""
    r = requests.get(f"{BASE}/api/governance/policies")
    assert r.status_code == 200
    print(f"   Policies: {len(r.json())} found")

def test_hunter_alerts():
    """Test 11: Hunter alerts"""
    r = requests.get(f"{BASE}/api/hunter/alerts")
    assert r.status_code == 200
    print(f"   Alerts: {len(r.json())} found")

def test_health_status():
    """Test 12: Health status"""
    r = requests.get(f"{BASE}/api/health/status")
    assert r.status_code == 200
    data = r.json()
    print(f"   System mode: {data.get('system_mode')}")
    print(f"   Health checks: {len(data.get('checks', []))}")

def test_trust_sources():
    """Test 13: Trusted sources"""
    r = requests.get(f"{BASE}/api/trust/sources")
    assert r.status_code == 200
    sources = r.json()
    print(f"   Trusted sources: {len(sources)}")
    if sources:
        print(f"   Example: {sources[0]['domain']} (score: {sources[0]['trust_score']})")

def test_immutable_log():
    """Test 14: Immutable log"""
    r = requests.get(f"{BASE}/api/log/entries?limit=5")
    assert r.status_code == 200
    print(f"   Log entries: {r.json()['count']}")

def test_knowledge_ingest():
    """Test 15: Knowledge ingestion"""
    r = requests.post(f"{BASE}/api/ingest/text",
        json={
            "title": "Test Knowledge",
            "content": "This is a test knowledge article about testing.",
            "domain": "test"
        },
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    if r.status_code in [200, 201]:
        print(f"   Ingested: {r.json()}")
    else:
        print(f"   Status: {r.status_code} - {r.text[:100]}")

def main():
    print("\n" + "="*60)
    print("GRACE SYSTEM TEST")
    print("="*60)
    print("\nTesting all major subsystems...")
    
    results = {
        "✅ PASS": [],
        "❌ FAIL": []
    }
    
    tests = [
        ("Backend Health", test_health),
        ("User Registration", test_register),
        ("User Login", test_login),
        ("Chat Message", test_chat),
        ("Metrics API", test_metrics),
        ("Reflections", test_reflections),
        ("Tasks", test_tasks),
        ("Sandbox Files", test_sandbox_files),
        ("Memory Tree", test_memory_tree),
        ("Governance Policies", test_governance_policies),
        ("Hunter Alerts", test_hunter_alerts),
        ("Health Status", test_health_status),
        ("Trusted Sources", test_trust_sources),
        ("Immutable Log", test_immutable_log),
        ("Knowledge Ingestion", test_knowledge_ingest),
    ]
    
    for name, test_func in tests:
        if test(name, test_func):
            results["✅ PASS"].append(name)
        else:
            results["❌ FAIL"].append(name)
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"\nPASSED: {len(results['✅ PASS'])}/{len(tests)}")
    for name in results["✅ PASS"]:
        print(f"   [+] {name}")
    
    print(f"\nFAILED: {len(results['❌ FAIL'])}/{len(tests)}")
    for name in results["❌ FAIL"]:
        print(f"   [-] {name}")
    
    print("\n" + "="*60)
    if len(results["❌ FAIL"]) == 0:
        print("SUCCESS: ALL SYSTEMS OPERATIONAL!")
    else:
        print(f"WARNING: {len(results['❌ FAIL'])} systems need attention")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
