"""
Start Grace and Begin Learning
Kicks off autonomous learning system
"""

import asyncio
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to start...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   Still waiting... ({i}s)")
    
    print("❌ Backend not responding")
    return False

def check_backend_running():
    """Check if backend is already running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

print("\n" + "="*70)
print("GRACE - AUTONOMOUS AI LEARNING SYSTEM")
print("="*70)
print()

# Check if backend is running
if check_backend_running():
    print("✅ Backend already running")
else:
    print("⚠️  Backend not running!")
    print("\nPlease start in another terminal:")
    print("  python serve.py")
    print()
    print("Then run this script again.")
    print()
    exit(1)

print("\n" + "="*70)
print("STEP 1: Get Curriculum Overview")
print("="*70)

try:
    response = requests.get(f"{BASE_URL}/api/learning/curriculum/overview")
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📚 Total Knowledge Domains: {data['curriculum']['total_domains']}")
        print(f"🎓 Domains Mastered: {data['curriculum']['domains_mastered']}")
        print(f"✅ Projects Completed: {data['curriculum']['projects_completed']}")
        
        print("\n🎯 Priority Projects (Business Value):")
        for i, proj in enumerate(data['priority_projects'], 1):
            print(f"   {i}. {proj}")
        
        print("\n📖 Knowledge Domains:")
        for domain_id, domain in data['domains'].items():
            mastery = domain['mastery_level']
            status = "✅" if mastery >= 80 else "🔄" if mastery > 0 else "⏳"
            print(f"   {status} {domain['name']}: {mastery:.1f}% mastery ({domain['projects_completed']}/{domain['total_projects']} projects)")
    else:
        print(f"❌ Failed to get curriculum: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n" + "="*70)
print("STEP 2: Check Current Status")
print("="*70)

try:
    response = requests.get(f"{BASE_URL}/api/learning/status")
    if response.status_code == 200:
        status = response.json()
        
        print(f"\n🤖 System: {status['system']}")
        print(f"📝 Mode: {status['mode']}")
        print(f"🧠 LLM: {status['llm']}")
        print(f"🧪 Sandbox: {'Enabled' if status['sandbox_enabled'] else 'Disabled'}")
        
        if status['current_project']['active']:
            proj = status['current_project']['project']
            print(f"\n🔨 Active Project:")
            print(f"   Name: {proj['name']}")
            print(f"   Domain: {proj['domain']}")
            print(f"   Progress: {proj['progress']:.1f}%")
        else:
            print(f"\n💤 No active project")
            print(f"   Ready to start learning!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("STEP 3: Start First Project")
print("="*70)

print("\n🚀 Starting next learning project...")

try:
    response = requests.post(f"{BASE_URL}/api/learning/project/start")
    if response.status_code == 200:
        result = response.json()
        
        if result.get('started'):
            proj = result['project']
            print(f"\n✅ Project Started!")
            print(f"   ID: {proj['project_id']}")
            print(f"   Name: {proj['name']}")
            print(f"   Domain: {proj['domain']}")
            print(f"   Sandbox: {proj['sandbox_dir']}")
            
            if 'plan' in proj:
                plan = proj['plan']
                print(f"\n📋 Project Plan:")
                print(f"   Total Phases: {plan['total_phases']}")
                print(f"   Estimated Hours: {plan['estimated_hours']}")
                
                print(f"\n   Phases:")
                for phase in plan['phases']:
                    print(f"      {phase['phase']}. {phase['name']}")
                    print(f"         Objectives: {', '.join(phase['objectives'][:3])}")
        else:
            print(f"\n{result}")
    else:
        print(f"❌ Failed to start project: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("STEP 4: Grace Works on Project")
print("="*70)

print("\n🔨 Grace is working autonomously...")
print("   She will:")
print("   - Implement features")
print("   - Discover edge cases in sandbox")
print("   - Test multiple solutions")
print("   - Optimize performance")
print("   - Document everything")

work_hours = 1.0  # Start with 1 hour of work

try:
    response = requests.post(
        f"{BASE_URL}/api/learning/project/work",
        json={"hours": work_hours}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Work Session Complete!")
        print(f"   Progress: {result['progress']:.1f}%")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Edge Cases Discovered: {result['edge_cases_found']}")
        print(f"   Solutions Tested: {result['solutions_tested']}")
        print(f"   Learnings Recorded: {result['learnings']}")
    else:
        print(f"❌ Work session failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("STEP 5: Check Progress")
print("="*70)

try:
    response = requests.get(f"{BASE_URL}/api/learning/progress")
    if response.status_code == 200:
        data = response.json()
        
        if data['active_project']['active']:
            proj = data['active_project']['project']
            print(f"\n📊 Current Project Status:")
            print(f"   Name: {proj['name']}")
            print(f"   Progress: {proj['progress']:.1f}%")
            print(f"   Iterations: {data['active_project']['iterations']}")
            print(f"   Edge Cases: {data['active_project']['edge_cases_discovered']}")
            print(f"   Solutions: {data['active_project']['solutions_tested']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ GRACE IS NOW LEARNING!")
print("="*70)

print("\n🎯 Next Steps:")
print()
print("   1. Let Grace continue working:")
print("      curl -X POST http://localhost:8000/api/learning/project/work -d '{\"hours\": 2.0}'")
print()
print("   2. Check her progress:")
print("      curl http://localhost:8000/api/learning/progress")
print()
print("   3. View API docs:")
print("      http://localhost:8000/docs")
print()
print("   4. When project is ~100% complete:")
print("      curl -X POST http://localhost:8000/api/learning/project/complete")
print()
print("Grace will autonomously:")
print("   ✅ Build real systems from scratch")
print("   ✅ Discover edge cases through testing")
print("   ✅ Test multiple solution approaches")
print("   ✅ Record all learnings to memory")
print("   ✅ Master 11 knowledge domains")
print()
print("She's learning right now! 🚀")
print()
