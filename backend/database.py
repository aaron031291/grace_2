"""
Simple Database Helper for Grace
Provides async database access using aiosqlite
"""

import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any


# Database path
DB_PATH = "databases/memory_fusion.db"

# Global connection (singleton)
_db_connection: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """Get database connection (singleton)"""
    global _db_connection
    
    if _db_connection is None:
        # Ensure databases directory exists
        db_path = Path(DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        _db_connection = await aiosqlite.connect(str(db_path))
        _db_connection.row_factory = aiosqlite.Row
        
    return _db_connection


async def init_database():
    """Initialize database connection"""
    await get_db()


async def close_db():
    """Close database connection"""
    global _db_connection
    
    if _db_connection:
        await _db_connection.close()
        _db_connection = None
