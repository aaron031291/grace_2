"""
Simple Database Helper for Grace
Provides async database access using aiosqlite with helper methods
"""

import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any


# Database path
DB_PATH = "databases/memory_fusion.db"

# Global connection (singleton)
_db_connection: Optional['DatabaseConnection'] = None


class DatabaseConnection:
    """Wrapper around aiosqlite.Connection with helper methods"""
    
    def __init__(self, conn: aiosqlite.Connection):
        self.conn = conn
        self.conn.row_factory = aiosqlite.Row
    
    async def execute(self, sql: str, parameters: tuple = None):
        """Execute SQL statement"""
        if parameters:
            return await self.conn.execute(sql, parameters)
        return await self.conn.execute(sql)
    
    async def commit(self):
        """Commit transaction"""
        await self.conn.commit()
    
    async def fetch_one(self, sql: str, parameters: tuple = None):
        """Fetch single row"""
        cursor = await self.execute(sql, parameters)
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def fetch_all(self, sql: str, parameters: tuple = None):
        """Fetch all rows"""
        cursor = await self.execute(sql, parameters)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def close(self):
        """Close connection"""
        await self.conn.close()


async def get_db() -> DatabaseConnection:
    """Get database connection (singleton)"""
    global _db_connection
    
    if _db_connection is None:
        # Ensure databases directory exists
        db_path = Path(DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        conn = await aiosqlite.connect(str(db_path))
        _db_connection = DatabaseConnection(conn)
        
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
