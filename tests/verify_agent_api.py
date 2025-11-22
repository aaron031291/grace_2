# tests/verify_agent_api.py
import asyncio
import sys
import os
from fastapi.testclient import TestClient

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock some things to avoid full server startup overhead if possible,
# but server.py imports are complex. Let's try to just import and run boot.
from server import boot_grace_minimal
from backend.main import app

async def run_boot():
    print("Booting Grace (minimal)...")
    # We only need to run until chunk 2.5 (Agent API) is loaded.
    # But boot_grace_minimal runs all chunks.
    # We can just run it and hope it's fast enough or doesn't block forever.
    # However, some chunks might start infinite loops (like self-reflection).
    # We might need to patch boot_orchestrator to stop after chunk 2.5 or just run it in background.
    
    # For verification, we can just manually call the chunk function if we can access it,
    # but it's defined inside boot_grace_minimal.
    
    # Alternative: We can just run boot_grace_minimal() and cancel it after a few seconds?
    # Or better, we can rely on the fact that we added the routes to 'app'.
    # But the routes are added *inside* the chunk function, which is called by boot_orchestrator.
    
    # Let's try running boot_grace_minimal in a task, waiting a bit, then testing.
    task = asyncio.create_task(boot_grace_minimal())
    await asyncio.sleep(5) # Wait for chunks to load
    return task

def verify_api():
    print("\n=== Verifying Agent API ===")
    client = TestClient(app)
    
    # 1. Test GET /agent/history (should be empty initially or error if not initialized)
    # Note: GraceAgent is initialized in chunk 2.
    try:
        response = client.get("/agent/history")
        print(f"GET /agent/history: {response.status_code} {response.json()}")
        if response.status_code == 200:
            print("  [OK] History endpoint works")
        else:
            print("  [WARN] History endpoint returned error (maybe agent not ready)")
    except Exception as e:
        print(f"  [FAIL] GET /agent/history failed: {e}")

    # 2. Test POST /agent/goal
    try:
        response = client.post("/agent/goal", json={"goal": "Test Goal"})
        print(f"POST /agent/goal: {response.status_code} {response.json()}")
        if response.status_code == 200:
            print("  [OK] Goal endpoint works")
        else:
            print("  [WARN] Goal endpoint returned error")
    except Exception as e:
        print(f"  [FAIL] POST /agent/goal failed: {e}")

    # 3. Test GET /agent/plan
    try:
        response = client.get("/agent/plan")
        print(f"GET /agent/plan: {response.status_code} {response.json()}")
        if response.status_code == 200:
            print("  [OK] Plan endpoint works")
        else:
            print("  [WARN] Plan endpoint returned error")
    except Exception as e:
        print(f"  [FAIL] GET /agent/plan failed: {e}")

async def main():
    # Start boot in background
    boot_task = await run_boot()
    
    # Run verification
    verify_api()
    
    # Cleanup (optional, might not kill everything cleanly)
    print("\nStopping boot task...")
    boot_task.cancel()
    try:
        await boot_task
    except asyncio.CancelledError:
        pass
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
