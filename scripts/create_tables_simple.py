"""Quick table creation for testing"""
import asyncio
from backend.base_models import Base, engine
from backend import event_persistence, action_contract
from sqlalchemy import text

async def create_tables():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
    print("[OK] All tables created")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
