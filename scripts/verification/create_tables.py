#!/usr/bin/env python3
"""Create all database tables"""

import sys
import os
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(os.getcwd())))

import asyncio
from sqlalchemy import inspect

async def create_all_tables():
    """Create all tables defined in models"""
    from backend.models.base_models import Base, engine
    
    print("Creating all database tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Verify tables created
    async with engine.connect() as conn:
        def get_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(get_tables)
        print(f"\n[OK] Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
    
    print("\n[OK] All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_all_tables())
