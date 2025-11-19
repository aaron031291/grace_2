"""
Test Script for Console Endpoints
Tests all backend endpoints used by the Grace Console
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
DEFAULT_PORT = 8000
try:
    PORT = int(os.getenv("GRACE_PORT", str(DEFAULT_PORT)))
except ValueError:
    PORT = DEFAULT_PORT

API_BASE = f"http://localhost:{PORT}"
TOKEN = "dev-token"

# Unicode safe symbols for Windows consoles
if sys.platform == 'win32':
    CHECK_MARK = "[OK]"
    CROSS_MARK = "[FAIL]"
    CLOCK_MARK = "[TIME]"
    HOSPITAL_MARK = "[HEALTH]"
    LOCK_MARK = "[VAULT]"
    TARGET_MARK = "[MISSION]"
    CLIPBOARD_MARK = "[LOGS]"
    INBOX_MARK = "[INGEST]"
else:
    CHECK_MARK = "✅"
    CROSS_MARK = "❌"
    CLOCK_MARK = "⏱️"
    HOSPITAL_MARK = "🏥"
    LOCK_MARK = "🔐"
    TARGET_MARK = "🎯"
    CLIPBOARD_MARK = "📋"
    INBOX_MARK = "📥"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, url, data=None, expected_status=200):
    """Test an endpoint and return result"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        
        status = CHECK_MARK if response.status_code == expected_status else CROSS_MARK
        return {
            "status": status,
            "code": response.status_code,
            "url": url,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
        }
    except requests.exceptions.ConnectionError:
        return {"status": CROSS_MARK, "code": "CONN_ERROR", "url": url, "data": {"error": "Connection refused - is backend running?"}}
    except requests.exceptions.Timeout:
        return {"status": CLOCK_MARK, "code": "TIMEOUT", "url": url, "data": None}
    except Exception as e:
        return {"status": CROSS_MARK, "code": "ERROR", "url": url, "data": {"error": str(e)}}

def print_result(name, result):
    """Print test result"""
    print(f"{result['status']} {name}")
    print(f"   Status: {result['code']}")
    if result.get('data'):
        if isinstance(result['data'], dict) and 'error' in result['data']:
            print(f"   Error: {result['data']['error']}")
        else:
            # Print first few keys/items
            if isinstance(result['data'], dict):
                keys = list(result['data'].keys())[:3]
                print(f"   Keys: {keys}")
            elif isinstance(result['data'], list):
                print(f"   Items: {len(result['data'])}")
    print()

def main():
    print("=" * 80)
    print(f"GRACE CONSOLE - ENDPOINT TESTS (Target: {API_BASE})")
    print("=" * 80)
    print()
    
    # Test basic health
    print(f"{HOSPITAL_MARK} HEALTH CHECKS")
    print("-" * 80)
    result = test_endpoint("GET", f"{API_BASE}/health")
    print_result("Backend Health", result)
    
    # Test Vault endpoints
    print(f"{LOCK_MARK} VAULT API")
    print("-" * 80)
    
    result = test_endpoint("GET", f"{API_BASE}/api/vault/secrets")
    print_result("List Secrets", result)
    
    result = test_endpoint("GET", f"{API_BASE}/api/vault/health")
    print_result("Vault Health", result)
    
    # Create test secret
    test_secret = {
        "name": "TEST_API_KEY",
        "value": "test-secret-value-12345",
        "secret_type": "api_key",
        "service": "testing",
        "description": "Test secret from endpoint verification"
    }
    result = test_endpoint("POST", f"{API_BASE}/api/vault/secrets", test_secret, expected_status=200)
    print_result("Create Secret", result)
    
    # Get secret
    result = test_endpoint("GET", f"{API_BASE}/api/vault/secrets/TEST_API_KEY")
    print_result("Get Secret", result)
    
    # Delete test secret
    result = test_endpoint("DELETE", f"{API_BASE}/api/vault/secrets/TEST_API_KEY")
    print_result("Delete Secret", result)
    
    # Test Mission Control endpoints
    print(f"{TARGET_MARK} MISSION CONTROL API")
    print("-" * 80)
    
    result = test_endpoint("GET", f"{API_BASE}/mission-control/status")
    print_result("Mission Control Status", result)
    
    result = test_endpoint("GET", f"{API_BASE}/mission-control/missions?limit=10")
    print_result("List Missions", result)
    
    result = test_endpoint("GET", f"{API_BASE}/mission-control/subsystems")
    print_result("Subsystems Health", result)
    
    # Test Logs endpoints
    print(f"{CLIPBOARD_MARK} LOGS API")
    print("-" * 80)
    
    result = test_endpoint("GET", f"{API_BASE}/api/logs/recent?limit=10")
    print_result("Recent Logs", result)
    
    result = test_endpoint("GET", f"{API_BASE}/api/logs/governance?limit=10")
    print_result("Governance Logs", result)
    
    result = test_endpoint("GET", f"{API_BASE}/api/logs/domains")
    print_result("Log Domains", result)
    
    result = test_endpoint("GET", f"{API_BASE}/api/logs/levels")
    print_result("Log Levels", result)
    
    result = test_endpoint("GET", f"{API_BASE}/api/logs/health")
    print_result("Logs Health", result)
    
    # Test Ingestion endpoints
    print(f"{INBOX_MARK} INGESTION API")
    print("-" * 80)
    
    result = test_endpoint("GET", f"{API_BASE}/api/ingest/artifacts?limit=10")
    print_result("List Artifacts", result)
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start backend: python server.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open console and test UI panels")
    print()

if __name__ == "__main__":
    main()
