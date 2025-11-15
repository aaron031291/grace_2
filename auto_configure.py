"""
Auto-configure clients to use the correct port
"""

import requests
from pathlib import Path

print("\n" + "="*70)
print("AUTO-CONFIGURING GRACE CLIENTS")
print("="*70)

# Find running server
ports = [8000, 8001, 8080]
found_port = None

print("\n[1/3] Finding Grace server...")
for port in ports:
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=1)
        if response.status_code == 200:
            found_port = port
            print(f"✅ Found Grace on port {port}")
            break
    except:
        pass

if not found_port:
    print("❌ Grace is not running!")
    print("\nStart Grace first:")
    print("  START_FIXED.cmd")
    exit(1)

BASE_URL = f"http://localhost:{found_port}"

# Update remote_access_client.py
print(f"\n[2/3] Configuring remote access client...")
client_file = Path("remote_access_client.py")
if client_file.exists():
    content = client_file.read_text()
    
    # Replace BASE_URL
    import re
    new_content = re.sub(
        r'BASE_URL = "http://localhost:\d+"',
        f'BASE_URL = "{BASE_URL}"',
        content
    )
    
    client_file.write_text(new_content)
    print(f"✅ Updated remote_access_client.py to use {BASE_URL}")

# Update start_grace_now.py
print(f"\n[3/3] Configuring learning client...")
learning_file = Path("start_grace_now.py")
if learning_file.exists():
    content = learning_file.read_text()
    
    new_content = re.sub(
        r'BASE_URL = "http://localhost:\d+"',
        f'BASE_URL = "{BASE_URL}"',
        content
    )
    
    learning_file.write_text(new_content)
    print(f"✅ Updated start_grace_now.py to use {BASE_URL}")

print("\n" + "="*70)
print("✅ CONFIGURATION COMPLETE")
print("="*70)
print(f"\nGrace server: {BASE_URL}")
print(f"API Docs: {BASE_URL}/docs")
print("\n🎯 Now you can use:")
print("\n1. Remote Access:")
print("   python remote_access_client.py setup")
print("   python remote_access_client.py shell")
print("\n2. Autonomous Learning:")
print("   python start_grace_now.py")
print("\n3. Test Integration:")
print("   python test_remote_access_integration.py")
print("\n" + "="*70)
