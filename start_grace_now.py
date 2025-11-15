"""
Start Grace Learning - Clean Version
Auto-detects server port
"""

import requests
import sys

# Auto-detect server
print("🔍 Finding Grace server...")
BASE_URL = None
for port in [8000, 8001, 8002, 8080]:
    try:
        r = requests.get(f"http://localhost:{port}/health", timeout=1)
        if r.status_code == 200:
            BASE_URL = f"http://localhost:{port}"
            print(f"✅ Found Grace at {BASE_URL}")
            break
    except:
        pass

if not BASE_URL:
    print("❌ Grace is not running!")
    print("\nStart Grace first:")
    print("  python serve.py")
    sys.exit(1)

print("\n" + "="*70)
print("GRACE AUTONOMOUS LEARNING")
print("="*70)

# Get curriculum
print("\n[1/4] Getting curriculum...")
try:
    response = requests.get(f"{BASE_URL}/api/learning/curriculum/overview")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['curriculum']['total_domains']} domains available")
        print(f"   {data['curriculum']['projects_completed']} projects completed")
    else:
        print(f"⚠️ Could not get curriculum")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Start first project
print("\n[2/4] Starting project...")
try:
    response = requests.post(f"{BASE_URL}/api/learning/project/start")
    if response.status_code == 200:
        result = response.json()
        if result.get('started'):
            print(f"✅ Started: {result['project']['name']}")
            print(f"   Domain: {result['project']['domain']}")
        else:
            print(f"   {result.get('message', 'Already working or all complete')}")
    else:
        print(f"⚠️ Could not start project")
except Exception as e:
    print(f"❌ Error: {e}")

# Work on it
print("\n[3/4] Grace working for 1 hour...")
try:
    response = requests.post(
        f"{BASE_URL}/api/learning/project/work",
        json={"hours": 1.0}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Progress: {result['progress']:.1f}%")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Edge cases found: {result['edge_cases_found']}")
        print(f"   Solutions tested: {result['solutions_tested']}")
    else:
        print(f"⚠️ Work session issue")
except Exception as e:
    print(f"❌ Error: {e}")

# Check progress
print("\n[4/4] Current progress...")
try:
    response = requests.get(f"{BASE_URL}/api/learning/progress")
    if response.status_code == 200:
        data = response.json()
        if data['active_project']['active']:
            proj = data['active_project']['project']
            print(f"✅ Working on: {proj['name']}")
            print(f"   Progress: {proj['progress']:.1f}%")
    else:
        print(f"⚠️ Could not get progress")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ GRACE IS LEARNING!")
print("="*70)
print("\nContinue learning:")
print(f"  curl -X POST {BASE_URL}/api/learning/project/work -d '{{\"hours\": 2.0}}'")
print("\nCheck progress:")
print(f"  curl {BASE_URL}/api/learning/progress")
print("\nAPI Docs:")
print(f"  {BASE_URL}/docs")
print("="*70)
