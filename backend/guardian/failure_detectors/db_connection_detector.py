"""
Database Connection Failure Detector
Failure Mode #1: Database Corruption/Unavailable

Detects:
- Database corruption
- Connection timeouts
- File lock errors
- Read/write failures
"""

import logging
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseConnectionDetector:
    """
    Detects database connection and corruption issues
    """
    
    def __init__(self, db_path: str = "grace.db"):
        self.db_path = Path(db_path)
        self.check_interval = 30  # seconds
        self.last_check = None
        self.failure_count = 0
        self.consecutive_failures = 0
        
    async def detect(self) -> Optional[Dict[str, Any]]:
        """
        Detect database connection issues
        
        Returns:
            Failure details if issue detected, None otherwise
        """
        try:
            failure = await self._check_database_health()
            
            if failure:
                self.consecutive_failures += 1
                self.failure_count += 1
                logger.warning(f"[DB-DETECTOR] Failure detected: {failure['type']}")
                return failure
            else:
                self.consecutive_failures = 0
                return None
                
        except Exception as e:
            logger.error(f"[DB-DETECTOR] Detector error: {e}")
            return {
                'type': 'detector_error',
                'severity': 'low',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }
    
    async def _check_database_health(self) -> Optional[Dict[str, Any]]:
        """
        Check database health
        
        Returns:
            Failure info if unhealthy, None if healthy
        """
        
        # Check 1: Database file exists
        if not self.db_path.exists():
            return {
                'type': 'db_file_missing',
                'severity': 'critical',
                'db_path': str(self.db_path),
                'details': 'Database file not found',
                'timestamp': datetime.utcnow().isoformat(),
                'remediation': 'restore_from_backup',
            }
        
        # Check 2: File is readable
        try:
            if not self.db_path.is_file():
                return {
                    'type': 'db_not_file',
                    'severity': 'critical',
                    'details': 'Database path exists but is not a file',
                    'timestamp': datetime.utcnow().isoformat(),
                }
        except Exception as e:
            return {
                'type': 'db_access_error',
                'severity': 'critical',
                'details': f'Cannot access database file: {e}',
                'timestamp': datetime.utcnow().isoformat(),
            }
        
        # Check 3: Can open connection
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=5.0,
                check_same_thread=False
            )
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower():
                return {
                    'type': 'db_locked',
                    'severity': 'high',
                    'details': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'clear_locks',
                }
            elif 'malformed' in str(e).lower() or 'corrupt' in str(e).lower():
                return {
                    'type': 'db_corrupted',
                    'severity': 'critical',
                    'details': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'restore_from_backup',
                }
            else:
                return {
                    'type': 'db_connection_failed',
                    'severity': 'high',
                    'details': str(e),
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'retry_connection',
                }
        except Exception as e:
            return {
                'type': 'db_unknown_error',
                'severity': 'high',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }
        
        # Check 4: Integrity check
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] != 'ok':
                conn.close()
                return {
                    'type': 'db_integrity_failed',
                    'severity': 'critical',
                    'details': f'Integrity check result: {result[0]}',
                    'timestamp': datetime.utcnow().isoformat(),
                    'remediation': 'restore_from_backup',
                }
        except Exception as e:
            conn.close()
            return {
                'type': 'db_integrity_check_failed',
                'severity': 'medium',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }
        
        # Check 5: Can execute simple query
        try:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        except Exception as e:
            conn.close()
            return {
                'type': 'db_query_failed',
                'severity': 'high',
                'details': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'remediation': 'clear_locks',
            }
        
        # Check 6: Check WAL files
        wal_file = Path(str(self.db_path) + '-wal')
        shm_file = Path(str(self.db_path) + '-shm')
        
        wal_size = wal_file.stat().st_size if wal_file.exists() else 0
        
        # Large WAL file indicates checkpoint issues
        if wal_size > 100 * 1024 * 1024:  # 100MB
            conn.close()
            return {
                'type': 'wal_file_too_large',
                'severity': 'medium',
                'details': f'WAL file size: {wal_size / 1024 / 1024:.1f} MB',
                'timestamp': datetime.utcnow().isoformat(),
                'remediation': 'checkpoint_wal',
            }
        
        # All checks passed
        conn.close()
        self.last_check = datetime.utcnow()
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            'detector': 'DatabaseConnection',
            'failure_mode': 'FM-001',
            'db_path': str(self.db_path),
            'check_interval': self.check_interval,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'total_failures': self.failure_count,
            'consecutive_failures': self.consecutive_failures,
        }


# Global instance
db_connection_detector = DatabaseConnectionDetector()
