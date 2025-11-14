# -*- coding: utf-8 -*-
"""
Test all CRUD operations for Memory Workspace
Run after restarting backend: python test_crud_operations.py
"""

import requests
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"

def test(name, method, path, **kwargs):
    print(f"\n{name}")
    print(f"  {method} {path}")
    try:
        r = requests.request(method, f"{BASE}{path}", timeout=5, **kwargs)
        if r.ok:
            print(f"  [PASS] {r.status_code}")
            return True
        else:
            print(f"  [FAIL] {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

print("="*60)
print("CRUD Operations Test")
print("="*60)

results = []

# CREATE operations
print("\n--- CREATE ---")
results.append(test("Create file", "POST", "/api/memory/file?path=documents/test_file.txt&content=Test content"))
results.append(test("Create folder", "POST", "/api/memory/folder?path=documents/test_folder"))

# READ operations
print("\n--- READ ---")
results.append(test("List files", "GET", "/api/memory/files"))
results.append(test("Read file", "GET", "/api/memory/file?path=documents/test_file.txt"))

# UPDATE operations
print("\n--- UPDATE ---")
results.append(test("Update file", "POST", "/api/memory/file?path=documents/test_file.txt&content=Updated content"))

# RENAME operations
print("\n--- RENAME ---")
results.append(test("Rename file", "PATCH", "/api/memory/file?old_path=documents/test_file.txt&new_path=documents/renamed_file.txt"))

# DELETE operations
print("\n--- DELETE ---")
results.append(test("Delete file", "DELETE", "/api/memory/file?path=documents/renamed_file.txt"))
results.append(test("Delete folder", "DELETE", "/api/memory/file?path=documents/test_folder"))

# Summary
print("\n" + "="*60)
print(f"RESULTS: {sum(results)}/{len(results)} passed")
print("="*60)

if sum(results) == len(results):
    print("\n[SUCCESS] All CRUD operations work!")
else:
    print("\n[FAIL] Some operations failed. Check errors above.")
    print("\nTroubleshooting:")
    print("1. Make sure backend is restarted: python serve.py")
    print("2. Check backend logs for errors")
    print("3. Verify grace_training folder exists")
