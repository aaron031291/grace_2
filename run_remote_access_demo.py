"""
Remote Access System Demo
Quick demonstration of zero-trust remote access
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("GRACE REMOTE ACCESS SYSTEM - DEMO")
print("="*70)

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("\n✅ Backend is running")
            return True
    except:
        pass
    
    print("\n❌ Backend not running!")
    print("\nPlease start backend first:")
    print("  python serve.py")
    return False

if not check_backend():
    exit(1)

print("\n" + "-"*70)
print("STEP 1: Register Device")
print("-"*70)

device_data = {
    "device_name": "aaron_laptop",
    "device_type": "laptop",
    "user_identity": "aaron",
    "device_fingerprint": "AA:BB:CC:DD:EE:FF:00:11",
    "approved_by": "aaron"
}

response = requests.post(f"{BASE_URL}/api/remote/devices/register", json=device_data)
result = response.json()

if 'error' in result:
    print(f"❌ Error: {result['error']}")
    if result['error'] == 'device_already_registered':
        device_id = result['device_id']
        print(f"✅ Device already registered: {device_id}")
    else:
        exit(1)
else:
    device_id = result['device_id']
    print(f"✅ Device registered: {device_id}")
    print(f"   Status: {result['status']}")

print("\n" + "-"*70)
print("STEP 2: Allowlist Device (Admin Approval)")
print("-"*70)

allowlist_data = {
    "device_id": device_id,
    "approved_by": "aaron"
}

response = requests.post(f"{BASE_URL}/api/remote/devices/allowlist", json=allowlist_data)
result = response.json()

if 'error' not in result:
    print(f"✅ Device allowlisted")
    print(f"   Device: {result.get('device_name', 'unknown')}")
else:
    print(f"⚠️  {result}")

print("\n" + "-"*70)
print("STEP 3: Assign RBAC Role")
print("-"*70)

role_data = {
    "device_id": device_id,
    "role_name": "developer",
    "approved_by": "aaron"
}

response = requests.post(f"{BASE_URL}/api/remote/roles/assign", json=role_data)
result = response.json()

if 'error' not in result:
    print(f"✅ Role assigned: {result['role']}")
    print(f"   Permissions: {', '.join(result['permissions'][:5])}...")
else:
    print(f"⚠️  {result}")

print("\n" + "-"*70)
print("STEP 4: Create Remote Session (with MFA)")
print("-"*70)

session_data = {
    "device_id": device_id,
    "mfa_token": "TEST_123456"  # Development MFA token
}

response = requests.post(f"{BASE_URL}/api/remote/session/create", json=session_data)
result = response.json()

if 'allowed' in result and result['allowed']:
    session_token = result['token']
    session_id = result['session_id']
    print(f"✅ Session created: {session_id}")
    print(f"   Token: {session_token[:30]}...")
    print(f"   Expires: {result['expires_at']}")
    print(f"   MFA Verified: {result['mfa_verified']}")
    print(f"   Recording ID: {result.get('recording_id', 'unknown')}")
else:
    print(f"❌ Session creation failed: {result}")
    exit(1)

print("\n" + "-"*70)
print("STEP 5: Execute Remote Commands")
print("-"*70)

commands = [
    "echo 'Hello from remote access!'",
    "python -c \"print('Grace remote access is working!')\"",
    "dir" if True else "ls -la",  # Windows command
]

for i, cmd in enumerate(commands, 1):
    print(f"\n[Command {i}] {cmd}")
    
    exec_data = {
        "token": session_token,
        "command": cmd,
        "timeout": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/remote/execute", json=exec_data)
    result = response.json()
    
    if 'success' in result and result['success']:
        print(f"✅ Executed successfully")
        print(f"   Exit code: {result['exit_code']}")
        if result.get('stdout'):
            print(f"   Output:\n{result['stdout'][:200]}")
    else:
        print(f"❌ Failed: {result}")
    
    time.sleep(0.5)

print("\n" + "-"*70)
print("STEP 6: Check Active Sessions")
print("-"*70)

response = requests.get(f"{BASE_URL}/api/remote/sessions/active")
result = response.json()

print(f"✅ Active sessions: {result['count']}")
for session in result.get('active_sessions', []):
    print(f"   - {session['session_id']} ({session['user_identity']})")

print("\n" + "-"*70)
print("STEP 7: Get Session Recordings")
print("-"*70)

response = requests.get(f"{BASE_URL}/api/remote/recordings")
result = response.json()

print(f"✅ Total recordings: {result.get('count', 0)}")
if result.get('count', 0) > 0:
    print("\nLatest recordings:")
    for rec in result.get('recordings', [])[:3]:
        print(f"   - {rec.get('recording_id', 'unknown')}")
        print(f"     Device: {rec.get('device_name', 'unknown')}")
        print(f"     Commands: {rec.get('total_commands', 0)}")

print("\n" + "="*70)
print("✅ REMOTE ACCESS DEMO COMPLETE")
print("="*70)
print("\nWhat happened:")
print("  1. Registered device with zero-trust verification")
print("  2. Admin approved device (allowlisted)")
print("  3. Assigned developer role (RBAC)")
print("  4. Created session with MFA authentication")
print("  5. Executed commands with full recording")
print("  6. All actions logged to immutable audit log")
print("\nSecurity features active:")
print("  ✅ Zero-trust device verification")
print("  ✅ Multi-factor authentication")
print("  ✅ RBAC permission enforcement")
print("  ✅ Complete session recording")
print("  ✅ Suspicious activity detection")
print("  ✅ Immutable audit logging")
print("\nRecordings saved to: logs/remote_sessions/")
print("\nAPI Documentation: http://localhost:8000/docs")
print()
