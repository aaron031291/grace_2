"""
Create Layer 3 database tables
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.intent_api import IntentRecord
from backend.learning_systems.learning_loop import OutcomeRecord, PlaybookStatistics
from backend.models.base_models import Base, engine


async def create_tables():
    """Create all Layer 3 tables"""
    
    print("Creating Layer 3 database tables...")
    
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Tables created:")
    print("   - intent_records")
    print("   - outcome_records")
    print("   - playbook_statistics")
    print("\nLayer 3 database ready!")


if __name__ == "__main__":
    asyncio.run(create_tables())
