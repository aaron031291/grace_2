
import asyncio
import sys
import os
from unittest.mock import MagicMock

# Mock uvicorn to prevent actual server start
sys.modules["uvicorn"] = MagicMock()

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_boot():
    print("Starting Boot Verification...")
    
    # Import server module
    import server
    
    # Run the boot sequence
    # We expect this to print the boot chunks
    try:
        result = await server.boot_grace_minimal()
        
        if result:
            print("\nBOOT SUCCESSFUL")
        else:
            print("\nBOOT FAILED")
            
    except Exception as e:
        print(f"\nBOOT ERROR: {e}")

if __name__ == "__main__":
    # Redirect stdout to capture it if needed, but for now we just let it print
    asyncio.run(test_boot())
