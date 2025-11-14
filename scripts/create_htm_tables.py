"""Create HTM tracking tables"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.htm_models import HTMTask, HTMTaskAttempt, HTMMetrics
from backend.models.base_models import Base, engine


async def create_tables():
    print("Creating HTM tracking tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Tables created:")
    print("   - htm_tasks (complete task tracking)")
    print("   - htm_task_attempts (retry attempts)")
    print("   - htm_metrics (aggregated metrics)")
    print("\nHTM tracking database ready!")


if __name__ == "__main__":
    asyncio.run(create_tables())
