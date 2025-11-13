#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify Memory Panel backend API is working
Run this while backend is running: python test_memory_panel.py
"""

import requests
import json
import sys

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"

def test(name, method, path, **kwargs):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{method} {path}")
    try:
        r = requests.request(method, f"{BASE}{path}", **kwargs, timeout=5)
        status_icon = 'PASS' if r.ok else 'FAIL'
        print(f"Status: {r.status_code} [{status_icon}]")
        if r.ok:
            try:
                data = r.json()
                print(f"Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"Response: {r.text[:200]}")
        else:
            print(f"Error: {r.text}")
        return r.ok
    except requests.exceptions.ConnectionError:
        print("[FAIL] Backend not running - start with: python serve.py")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

print("Testing GRACE Memory Panel API")
print("="*60)

results = []

# Test file operations
results.append(test("List Files", "GET", "/api/memory/files/list?path=/"))
results.append(test("Create Test File", "POST", "/api/memory/files/create",
                   json={"path": "grace_training/test.txt", "content": "test"}))
results.append(test("Get File Content", "GET", "/api/memory/files/content?path=grace_training/test.txt"))
results.append(test("Save File", "PUT", "/api/memory/files/content",
                   json={"path": "grace_training/test.txt", "content": "updated"}))

# Test table operations  
results.append(test("List Tables", "GET", "/api/memory/tables/list"))
results.append(test("Get Linked Rows", "GET", "/api/memory/tables/linked?file_path=grace_training/test.txt"))

# Test schema proposals
results.append(test("Pending Schemas", "GET", "/api/memory/schemas/pending"))

print("\n" + "="*60)
print(f"RESULTS: {sum(results)}/{len(results)} passed")
print("="*60)

if sum(results) == len(results):
    print("[SUCCESS] All tests passed! Memory Panel backend is ready.")
else:
    print("[WARNING] Some tests failed. Check backend logs.")
