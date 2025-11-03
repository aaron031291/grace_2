"""Simple Grace Initialization

Creates core tables without complex imports.
"""

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./grace.db"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)

async def init_db():
    """Create all tables"""
    
    print("\n" + "="*70)
    print(" GRACE DATABASE INITIALIZATION")
    print("="*70)
    print()
    
    print("Creating tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("SUCCESS: Database initialized")
    print()
    print("Tables created. Grace is ready.")
    print()
    print("Next steps:")
    print("  1. Start backend: cd backend && py main.py")
    print("  2. Seed data: py -m backend.seed_governance_policies")
    print("  3. Test API: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    print("\nGrace Simple Initialization\n")
    asyncio.run(init_db())
