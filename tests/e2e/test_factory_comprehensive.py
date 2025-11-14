#!/usr/bin/env python3
"""
Comprehensive Factory API Tests
Tests all endpoints in the new clean architecture
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_endpoint(name: str, url: str, method: str = "GET", data: Dict[str, Any] = None) -> bool:
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{url}", json=data)
        else:
            print(f"  ❌ {name} - Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] {name}")
            return True
        else:
            print(f"  [FAIL] {name} - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  [FAIL] {name} - Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Factory API Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    total_tests = 0
    passed_tests = 0
    
    # System Tests
    print("[SYSTEM] Endpoints:")
    tests = [
        ("Health Check", "/health"),
        ("System Health", "/system/health"),
        ("System Metrics", "/system/metrics"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Self-Healing Tests
    print("[SELF-HEALING] Endpoints:")
    tests = [
        ("Stats", "/self-healing/stats"),
        ("Incidents", "/self-healing/incidents?limit=5"),
        ("Playbooks", "/self-healing/playbooks"),
        ("Recent Actions", "/self-healing/actions/recent?limit=5"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Librarian Tests
    print("[LIBRARIAN] Endpoints:")
    tests = [
        ("Status", "/librarian/status"),
        ("Schema Proposals", "/librarian/schema-proposals"),
        ("File Operations", "/librarian/file-operations?limit=5"),
        ("Organization Suggestions", "/librarian/organization-suggestions"),
        ("Active Agents", "/librarian/agents"),
        ("Immutable Logs", "/librarian/logs/immutable?limit=5"),
        ("Log Tail", "/librarian/logs/tail?lines=5"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Memory Tests
    print("[MEMORY] Endpoints:")
    tests = [
        ("Stats", "/memory/stats"),
        ("Domains", "/memory/domains"),
        ("Recent Activity", "/memory/recent-activity?limit=5"),
        ("Search", "/memory/search?query=test&limit=3"),
        ("Get Artifact", "/memory/artifacts/123"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Ingestion Tests
    print("[INGESTION] Endpoints:")
    tests = [
        ("Status", "/ingestion/status"),
        ("Jobs List", "/ingestion/jobs?limit=5"),
        ("Job Details", "/ingestion/jobs/1"),
        ("Metrics", "/ingestion/metrics"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Trusted Sources Tests
    print("[TRUSTED-SOURCES] Endpoints:")
    tests = [
        ("List Sources", "/trusted-sources/"),
        ("Get Source", "/trusted-sources/1"),
    ]
    for name, url in tests:
        total_tests += 1
        if test_endpoint(name, url):
            passed_tests += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("\nAll tests passed! Clean architecture working perfectly!")
    else:
        print(f"\n{total_tests - passed_tests} test(s) failed")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
