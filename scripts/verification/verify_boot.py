
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Mock uvicorn to prevent starting server
import uvicorn
uvicorn.run = lambda *args, **kwargs: print("Mock Uvicorn started")

# Import the boot function
from server import boot_grace_minimal

async def run_verification():
    print("Verifying Boot Sequence...")
    try:
        # Run boot
        result = await boot_grace_minimal()
        
        if result:
            print("\n✅ Boot verification successful!")
            print(f"Result type: {type(result)}")
        else:
            print("\n❌ Boot verification failed")
            
    except Exception as e:
        print(f"\n❌ Exception during boot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_verification())
