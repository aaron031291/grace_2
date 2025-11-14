"""
Direct migration script for recording models
Applies recording tables directly to database
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.base_models import engine, Base
from backend.models.recording_models import (
    RecordingSession,
    RecordingTranscript,
    RecordingAccess,
    ConsentRecord
)


async def apply_recording_migration():
    """Create recording tables in database"""
    
    print("[RECORDING] Applying recording models migration...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    
    print("[RECORDING] Migration applied successfully!")
    print("\nCreated tables:")
    print("  - recording_sessions")
    print("  - recording_transcripts")
    print("  - recording_access")
    print("  - consent_records")


if __name__ == "__main__":
    asyncio.run(apply_recording_migration())
