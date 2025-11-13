# -*- coding: utf-8 -*-
"""
Complete CRUD Verification with detailed logging
"""
import requests
import sys
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")

def test_operation(name, method, path, expect_pass=True, **kwargs):
    """Test a single operation with detailed logging"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {method} {path}")
    
    try:
        r = requests.request(method, f"{BASE}{path}", timeout=5, **kwargs)
        
        # Parse response
        try:
            data = r.json()
            response_preview = json.dumps(data, indent=2)[:300]
        except:
            response_preview = r.text[:300]
        
        # Check result
        passed = r.ok if expect_pass else not r.ok
        status = "PASS" if passed else "FAIL"
        
        print(f"Status Code: {r.status_code}")
        print(f"Expected: {'Success (2xx)' if expect_pass else 'Error (4xx/5xx)'}")
        print(f"Result: [{status}]")
        print(f"Response: {response_preview}")
        
        return passed
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

print("="*60)
print("GRACE Memory Workspace - Complete CRUD Verification")
print("="*60)

results = []

# Test 1: CREATE a new file
log("Creating test file...")
results.append(test_operation(
    "CREATE File",
    "POST",
    "/api/memory/file?path=test_verify/sample.txt&content=Initial content",
    expect_pass=True
))

# Test 2: READ the file
log("Reading file content...")
results.append(test_operation(
    "READ File Content",
    "GET",
    "/api/memory/file?path=test_verify/sample.txt",
    expect_pass=True
))

# Test 3: UPDATE the file
log("Updating file content...")
results.append(test_operation(
    "UPDATE File",
    "POST",
    "/api/memory/file?path=test_verify/sample.txt&content=Modified content here",
    expect_pass=True
))

# Test 4: Verify update worked
log("Verifying update...")
r = requests.get(f"{BASE}/api/memory/file?path=test_verify/sample.txt")
if r.ok and "Modified content" in r.json().get('content', ''):
    print("\n[PASS] File content was updated correctly")
    results.append(True)
else:
    print("\n[FAIL] File content not updated")
    results.append(False)

# Test 5: CREATE a folder
log("Creating test folder...")
results.append(test_operation(
    "CREATE Folder",
    "POST",
    "/api/memory/folder?path=test_verify/subfolder",
    expect_pass=True
))

# Test 6: CREATE file in subfolder
log("Creating file in subfolder...")
results.append(test_operation(
    "CREATE File in Subfolder",
    "POST",
    "/api/memory/file?path=test_verify/subfolder/nested.txt&content=Nested file",
    expect_pass=True
))

# Test 7: RENAME the file
log("Renaming file...")
results.append(test_operation(
    "RENAME File",
    "PATCH",
    "/api/memory/file?old_path=test_verify/sample.txt&new_path=test_verify/renamed.txt",
    expect_pass=True
))

# Test 8: Verify rename worked (old path should not exist)
log("Verifying old path is gone...")
r = requests.get(f"{BASE}/api/memory/file?path=test_verify/sample.txt")
if r.status_code == 404 or 'not found' in r.text.lower():
    print("\n[PASS] Old path no longer exists")
    results.append(True)
else:
    print("\n[FAIL] Old path still exists")
    results.append(False)

# Test 9: Verify new path exists
log("Verifying new path exists...")
r = requests.get(f"{BASE}/api/memory/file?path=test_verify/renamed.txt")
if r.ok and "Modified content" in r.json().get('content', ''):
    print("\n[PASS] File renamed successfully with content intact")
    results.append(True)
else:
    print("\n[FAIL] Renamed file not found or content lost")
    results.append(False)

# Test 10: DELETE file
log("Deleting renamed file...")
results.append(test_operation(
    "DELETE File",
    "DELETE",
    "/api/memory/file?path=test_verify/renamed.txt",
    expect_pass=True
))

# Test 11: DELETE nested file
log("Deleting nested file...")
results.append(test_operation(
    "DELETE Nested File",
    "DELETE",
    "/api/memory/file?path=test_verify/subfolder/nested.txt",
    expect_pass=True
))

# Test 12: DELETE folder
log("Deleting folder...")
results.append(test_operation(
    "DELETE Folder",
    "DELETE",
    "/api/memory/file?path=test_verify/subfolder",
    expect_pass=True
))

# Test 13: DELETE parent folder
log("Deleting parent folder...")
results.append(test_operation(
    "DELETE Parent Folder",
    "DELETE",
    "/api/memory/file?path=test_verify",
    expect_pass=True
))

# Final Summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
passed = sum(results)
total = len(results)
print(f"\nTests Passed: {passed}/{total}")
print(f"Success Rate: {(passed/total*100):.1f}%")

if passed == total:
    print("\n✓ ALL CRUD OPERATIONS VERIFIED AND WORKING")
    print("\nMemory Workspace is 100% functional:")
    print("  ✓ Create files and folders")
    print("  ✓ Read file content")
    print("  ✓ Update/save files")
    print("  ✓ Rename files")
    print("  ✓ Delete files and folders")
    print("\nYou can now use the Memory Workspace UI with full CRUD functionality!")
else:
    print(f"\n✗ {total - passed} operation(s) failed")
    print("\nCheck the errors above and:")
    print("1. Ensure backend is restarted")
    print("2. Check backend logs for detailed errors")
    print("3. Verify file paths are relative to grace_training/")

print("="*60)
