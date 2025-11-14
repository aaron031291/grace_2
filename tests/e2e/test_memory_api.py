#!/usr/bin/env python3
"""
Test script for Memory API endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, path: str, description: str, **kwargs) -> Dict[str, Any]:
    """Test an API endpoint and return results"""
    url = f"{BASE_URL}{path}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {path}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        response = requests.request(method, url, **kwargs)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return {"success": response.ok, "status": response.status_code, "data": data}
        except:
            print(f"Response: {response.text[:200]}")
            return {"success": response.ok, "status": response.status_code, "text": response.text}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}

def run_tests():
    """Run all memory API tests"""
    
    print("=" * 60)
    print("GRACE Memory API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: List files
    results.append(test_endpoint(
        "GET", 
        "/api/memory/files/list?path=/",
        "List files in root directory"
    ))
    
    # Test 2: Create a test file
    results.append(test_endpoint(
        "POST",
        "/api/memory/files/create",
        "Create a test file",
        json={"path": "/test_file.txt", "content": "Hello from test"}
    ))
    
    # Test 3: Get file content
    results.append(test_endpoint(
        "GET",
        "/api/memory/files/content?path=/test_file.txt",
        "Get file content"
    ))
    
    # Test 4: Update file content
    results.append(test_endpoint(
        "PUT",
        "/api/memory/files/content",
        "Update file content",
        json={"path": "/test_file.txt", "content": "Updated content"}
    ))
    
    # Test 5: List tables
    results.append(test_endpoint(
        "GET",
        "/api/memory/tables/list",
        "List all memory tables"
    ))
    
    # Test 6: Get pending schemas
    results.append(test_endpoint(
        "GET",
        "/api/memory/schemas/pending",
        "Get pending schema proposals"
    ))
    
    # Test 7: Create folder
    results.append(test_endpoint(
        "POST",
        "/api/memory/files/folder",
        "Create a test folder",
        json={"path": "/test_folder"}
    ))
    
    # Test 8: Delete test file
    results.append(test_endpoint(
        "DELETE",
        "/api/memory/files/delete",
        "Delete test file",
        json={"path": "/test_file.txt"}
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r.get("success"))
    total_count = len(results)
    
    print(f"Passed: {success_count}/{total_count}")
    print(f"Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the backend implementation.")

if __name__ == "__main__":
    run_tests()
