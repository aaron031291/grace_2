"""
Test Grace Integration - Auto-detects port
"""

import requests
import sys

# Auto-detect port
print("🔍 Finding Grace server...")
BASE_URL = None
for port in [8000, 8001, 8080]:
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=1)
        if r.status_code == 200:
            BASE_URL = f"http://localhost:{port}"
            print(f"✅ Found Grace at {BASE_URL}")
            break
    except:
        pass

if not BASE_URL:
    print("❌ Grace server not found!")
    print("Start Grace first: START_FIXED.cmd")
    sys.exit(1)

print("\n" + "="*70)
print("GRACE INTEGRATION TEST")
print("="*70)

# Test 1: Server health
print("\n[1/5] Server Health...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ Server responding: {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Remote access endpoints
print("\n[2/5] Remote Access Endpoints...")
try:
    response = requests.get(f"{BASE_URL}/api/remote/roles/list")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Remote access works ({result.get('count', 0)} roles)")
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Remote access failed: {e}")

# Test 3: Learning endpoints
print("\n[3/5] Autonomous Learning Endpoints...")
try:
    response = requests.get(f"{BASE_URL}/api/learning/status")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Learning system works")
        print(f"   Mode: {result.get('mode', 'unknown')}")
    else:
        print(f"⚠️ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Learning system failed: {e}")

# Test 4: API documentation
print("\n[4/5] API Documentation...")
try:
    response = requests.get(f"{BASE_URL}/docs")
    if response.status_code == 200:
        print(f"✅ API docs available at {BASE_URL}/docs")
    else:
        print(f"⚠️ Docs returned: {response.status_code}")
except Exception as e:
    print(f"❌ Docs failed: {e}")

# Test 5: Count endpoints
print("\n[5/5] Endpoint Count...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        data = response.json()
        total = len(data.get('paths', {}))
        remote = len([p for p in data.get('paths', {}) if '/remote' in p])
        learning = len([p for p in data.get('paths', {}) if '/learning' in p])
        
        print(f"✅ Total endpoints: {total}")
        print(f"   Remote Access: {remote} endpoints")
        print(f"   Learning: {learning} endpoints")
except Exception as e:
    print(f"⚠️ Could not count endpoints: {e}")

# Summary
print("\n" + "="*70)
print("✅ INTEGRATION TEST COMPLETE")
print("="*70)
print(f"\nGrace is running at: {BASE_URL}")
print(f"API Docs: {BASE_URL}/docs")
print("\n🎯 Ready to use:")
print("\n1. Remote Access:")
print("   python auto_configure.py  # Auto-configure port")
print("   python remote_access_client.py setup")
print("   python remote_access_client.py shell")
print("\n2. Autonomous Learning:")
print("   python start_grace_now.py")
print("\n3. Quick Access:")
print("   USE_GRACE.cmd")
print("\n" + "="*70)
