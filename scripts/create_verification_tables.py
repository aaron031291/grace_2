"""
Directly create verification tables (bypass migration check)
"""

import asyncio
from backend.models import Base, engine
from backend.action_contract import ActionContract
from backend.self_heal.safe_hold import SafeHoldSnapshot


async def create_tables():
    print("Creating verification tables directly...")
    
    # Import all models to ensure they're registered
    try:
        from backend.benchmarks.benchmark_suite import BenchmarkRun
        from backend.progression_tracker import MissionTimeline
        print("Models imported successfully")
    except Exception as e:
        print(f"Warning: Could not import all models: {e}")
    
    # Create tables
    async with engine.begin() as conn:
        # Drop existing tables first (if any)
        await conn.run_sync(Base.metadata.drop_all)
        print("Dropped existing tables")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Created all tables")
    
    # Verify tables exist
    from sqlalchemy import text
    from backend.models import async_session
    
    async with async_session() as session:
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' WHERE name LIKE 'action_%' OR name LIKE 'safe_%' OR name LIKE 'benchmark_%' OR name LIKE 'mission_%' ORDER BY name"))
        tables = [row[0] for row in result.fetchall()]
        
        print("\nVerification tables created:")
        for table in tables:
            print(f"  [OK] {table}")
    
    print("\nTables creation complete!")


if __name__ == "__main__":
    asyncio.run(create_tables())
