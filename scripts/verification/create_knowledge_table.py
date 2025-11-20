#!/usr/bin/env python3
"""Create knowledge_artifacts table specifically"""

import sys
import os
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(os.getcwd())))

import asyncio

async def create_knowledge_tables():
    """Create knowledge tables from model"""
    from backend.models.knowledge_models import Base
    from backend.models.base_models import engine
    
    print("Creating knowledge_artifacts table...")
    
    # Create knowledge tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Knowledge tables created!")

if __name__ == "__main__":
    asyncio.run(create_knowledge_tables())
