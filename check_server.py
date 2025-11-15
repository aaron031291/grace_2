"""
Check which port Grace is running on
"""

import requests

print("\n" + "="*70)
print("CHECKING FOR GRACE SERVER")
print("="*70)

ports_to_check = [8000, 8001, 8080]
found = False

for port in ports_to_check:
    print(f"\nChecking port {port}...")
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ FOUND! Grace is running on port {port}")
            print(f"\n📍 Server Details:")
            print(f"   URL: http://localhost:{port}")
            print(f"   Docs: http://localhost:{port}/docs")
            print(f"   Health: http://localhost:{port}/health")
            
            # Check what's available
            try:
                response = requests.get(f"http://localhost:{port}/openapi.json", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    paths = data.get('paths', {})
                    
                    remote_paths = [p for p in paths.keys() if '/remote' in p]
                    learning_paths = [p for p in paths.keys() if '/learning' in p]
                    
                    print(f"\n📊 Available Features:")
                    if remote_paths:
                        print(f"   ✅ Remote Access: {len(remote_paths)} endpoints")
                    else:
                        print(f"   ❌ Remote Access: Not available")
                    
                    if learning_paths:
                        print(f"   ✅ Autonomous Learning: {len(learning_paths)} endpoints")
                    else:
                        print(f"   ❌ Autonomous Learning: Not available")
                    
                    print(f"   ✅ Total endpoints: {len(paths)}")
            except:
                pass
            
            print(f"\n🎯 To Use Grace:")
            print(f"   1. Remote Access:")
            print(f"      Edit remote_access_client.py - change BASE_URL to http://localhost:{port}")
            print(f"      python remote_access_client.py setup")
            print(f"   2. Learning:")
            print(f"      Edit start_grace_now.py - change BASE_URL to http://localhost:{port}")
            print(f"      python start_grace_now.py")
            
            found = True
            break
    except:
        print(f"   ❌ Not running on port {port}")

if not found:
    print("\n❌ Grace is NOT running on any common port")
    print("\n💡 Start Grace with:")
    print("   START_FIXED.cmd")
    print("   or")
    print("   python serve_fixed.py")

print("\n" + "="*70)
