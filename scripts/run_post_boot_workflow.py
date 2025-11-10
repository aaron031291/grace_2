"""
Run post-boot workflow manually
Usage: python scripts/run_post_boot_workflow.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.post_boot_orchestrator import post_boot_orchestrator


async def main():
    """Run post-boot workflow"""
    
    result = await post_boot_orchestrator.run_post_boot_workflow()
    
    if result["success"]:
        print("\n[SUCCESS] Post-boot workflow complete")
        print(f"  Watchdog: {'ACTIVE' if result['watchdog_active'] else 'INACTIVE'}")
        sys.exit(0)
    else:
        print("\n[PARTIAL] Post-boot workflow completed with issues")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
