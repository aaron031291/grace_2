import asyncio
from typing import Dict, Any

class TestLauncher:
    async def _stage_service_launch(self) -> Dict[str, Any]:
        print("Testing async method...")
        return {"success": True, "test": "working"}
    
    async def launch(self):
        result = await self._stage_service_launch()
        print(f"Result: {result}")

if __name__ == "__main__":
    launcher = TestLauncher()
    asyncio.run(launcher.launch())