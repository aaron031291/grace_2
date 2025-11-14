"""Standalone runner for constitutional seed script"""

import asyncio
import sys
import os

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

async def main():
    from backend.seed_constitution import seed_constitutional_principles, seed_operational_tenets
    
    await seed_constitutional_principles()
    await seed_operational_tenets()
    print("\nConstitutional AI Framework Ready")

if __name__ == "__main__":
    asyncio.run(main())
