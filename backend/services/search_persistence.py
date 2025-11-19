import sqlite3
import json
import logging
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SearchPersistence:
    """
    Persistent storage for Search Service.
    Handles caching of search results and daily quota tracking.
    """
    
    def __init__(self, db_path: str = "data/search_cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Search Cache Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_cache (
                        query_hash TEXT PRIMARY KEY,
                        query TEXT NOT NULL,
                        results_json TEXT NOT NULL,
                        timestamp REAL NOT NULL
                    )
                """)
                
                # Daily Quota Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS daily_quota (
                        date_str TEXT PRIMARY KEY,
                        mission_used INTEGER DEFAULT 0,
                        learning_used INTEGER DEFAULT 0,
                        emergency_used INTEGER DEFAULT 0
                    )
                """)
                
                # Provenance/Log Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS search_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        query TEXT NOT NULL,
                        category TEXT NOT NULL,
                        task_id TEXT,
                        provider TEXT,
                        cached INTEGER
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Init failed: {e}")

    def _get_hash(self, query: str) -> str:
        """Generate consistent hash for query"""
        # Normalize: lowercase, strip whitespace
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def get_cached_results(self, query: str, ttl_seconds: int = 86400) -> Optional[Dict[str, Any]]:
        """Get cached results if valid"""
        query_hash = self._get_hash(query)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT results_json, timestamp FROM search_cache WHERE query_hash = ?", 
                    (query_hash,)
                )
                row = cursor.fetchone()
                
                if row:
                    results_json, timestamp = row
                    import time
                    age = time.time() - timestamp
                    
                    if age < ttl_seconds:
                        logger.debug(f"[SEARCH-PERSISTENCE] Cache hit for '{query}' (age: {age:.1f}s)")
                        return json.loads(results_json)
                    else:
                        logger.debug(f"[SEARCH-PERSISTENCE] Cache expired for '{query}'")
                        return None
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Cache read error: {e}")
            return None
        return None

    def cache_results(self, query: str, results: Any):
        """Cache search results"""
        query_hash = self._get_hash(query)
        import time
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO search_cache (query_hash, query, results_json, timestamp) VALUES (?, ?, ?, ?)",
                    (query_hash, query, json.dumps(results), time.time())
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Cache write error: {e}")

    def get_quota_usage(self) -> Dict[str, int]:
        """Get usage for today"""
        today = date.today().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT mission_used, learning_used, emergency_used FROM daily_quota WHERE date_str = ?",
                    (today,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "mission": row[0],
                        "learning": row[1],
                        "emergency": row[2],
                        "total": sum(row)
                    }
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Quota read error: {e}")
        
        return {"mission": 0, "learning": 0, "emergency": 0, "total": 0}

    def increment_quota(self, category: str = "learning"):
        """Increment quota usage for category"""
        today = date.today().isoformat()
        col_map = {
            "mission": "mission_used",
            "learning": "learning_used",
            "emergency": "emergency_used"
        }
        col = col_map.get(category, "learning_used")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Ensure row exists
                conn.execute(
                    "INSERT OR IGNORE INTO daily_quota (date_str) VALUES (?)",
                    (today,)
                )
                # Increment
                conn.execute(
                    f"UPDATE daily_quota SET {col} = {col} + 1 WHERE date_str = ?",
                    (today,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Quota update error: {e}")

    def log_search(self, query: str, category: str, task_id: Optional[str], provider: str, cached: bool):
        """Log search provenance"""
        import time
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO search_log 
                       (timestamp, query, category, task_id, provider, cached) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (time.time(), query, category, task_id, provider, 1 if cached else 0)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"[SEARCH-PERSISTENCE] Log error: {e}")
