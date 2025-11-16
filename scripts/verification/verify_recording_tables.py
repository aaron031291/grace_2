"""Verify recording tables were created"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.base_models import engine
from sqlalchemy import text

async def verify():
    async with engine.begin() as conn:
        result = await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'recording%' OR name LIKE 'consent%') ORDER BY name")
            ).fetchall()
        )
        
        print("\nRecording tables created:")
        for table in result:
            print(f"  - {table[0]}")
        
        return len(result)

if __name__ == "__main__":
    count = asyncio.run(verify())
    print(f"\nTotal: {count} tables")
