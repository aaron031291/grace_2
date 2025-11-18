"""
Database Recovery Playbook
Remediates Failure Mode #1: Database Connection Issues

Handles:
- Database corruption
- Connection timeouts
- File locks
- WAL checkpoint issues
"""

import logging
import sqlite3
import shutil
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseRecoveryPlaybook:
    """
    Automatic database recovery and remediation
    """
    
    def __init__(self, db_path: str = "grace.db"):
        self.db_path = Path(db_path)
        self.backup_dir = Path("databases/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    async def remediate(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remediate database failure
        
        Args:
            failure: Failure details from detector
            
        Returns:
            Remediation result with MTTR
        """
        start_time = datetime.utcnow()
        failure_type = failure.get('type', 'unknown')
        
        logger.info(f"[DB-RECOVERY] Starting remediation for: {failure_type}")
        
        result = {
            'failure_type': failure_type,
            'remediation_started': start_time.isoformat(),
            'steps': [],
            'success': False,
            'mttr_seconds': 0,
        }
        
        try:
            # Route to specific remediation
            if failure_type == 'db_locked':
                remediation_result = await self._clear_locks()
            elif failure_type == 'db_corrupted' or failure_type == 'db_integrity_failed':
                remediation_result = await self._restore_from_backup()
            elif failure_type == 'wal_file_too_large':
                remediation_result = await self._checkpoint_wal()
            elif failure_type == 'db_file_missing':
                remediation_result = await self._restore_from_backup()
            elif failure_type == 'db_connection_failed':
                remediation_result = await self._retry_connection()
            else:
                remediation_result = {
                    'success': False,
                    'message': f'No remediation for {failure_type}',
                    'steps': []
                }
            
            result.update(remediation_result)
            
        except Exception as e:
            logger.error(f"[DB-RECOVERY] Remediation failed: {e}")
            result['error'] = str(e)
            result['success'] = False
        
        # Calculate MTTR
        end_time = datetime.utcnow()
        mttr = (end_time - start_time).total_seconds()
        result['mttr_seconds'] = mttr
        result['remediation_completed'] = end_time.isoformat()
        
        logger.info(f"[DB-RECOVERY] Remediation {'succeeded' if result['success'] else 'failed'} (MTTR: {mttr:.2f}s)")
        
        return result
    
    async def _clear_locks(self) -> Dict[str, Any]:
        """Clear database locks"""
        steps = []
        
        # Step 1: Close all connections
        steps.append("Closing all database connections")
        await asyncio.sleep(0.1)  # Give connections time to close
        
        # Step 2: Remove lock files
        wal_file = Path(str(self.db_path) + '-wal')
        shm_file = Path(str(self.db_path) + '-shm')
        
        removed_files = []
        if shm_file.exists():
            shm_file.unlink()
            removed_files.append('shm')
            steps.append("Removed .db-shm lock file")
        
        if wal_file.exists():
            # Backup WAL before removing
            wal_backup = self.backup_dir / f"{wal_file.name}.{int(datetime.utcnow().timestamp())}"
            shutil.copy2(wal_file, wal_backup)
            steps.append(f"Backed up WAL to {wal_backup.name}")
        
        # Step 3: Try to reconnect
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            conn.execute("SELECT 1")
            conn.close()
            steps.append("Successfully reconnected to database")
            return {
                'success': True,
                'message': 'Database locks cleared',
                'steps': steps,
                'files_removed': removed_files,
            }
        except Exception as e:
            steps.append(f"Reconnection failed: {e}")
            return {
                'success': False,
                'message': f'Failed to clear locks: {e}',
                'steps': steps,
            }
    
    async def _checkpoint_wal(self) -> Dict[str, Any]:
        """Checkpoint WAL file to reduce size"""
        steps = []
        
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10.0)
            
            # Get WAL file size before
            wal_file = Path(str(self.db_path) + '-wal')
            size_before = wal_file.stat().st_size if wal_file.exists() else 0
            steps.append(f"WAL size before: {size_before / 1024 / 1024:.1f} MB")
            
            # Run checkpoint
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            result = cursor.fetchone()
            steps.append(f"Checkpoint result: {result}")
            
            conn.close()
            
            # Get WAL file size after
            size_after = wal_file.stat().st_size if wal_file.exists() else 0
            steps.append(f"WAL size after: {size_after / 1024 / 1024:.1f} MB")
            
            return {
                'success': True,
                'message': 'WAL checkpoint completed',
                'steps': steps,
                'size_before_mb': size_before / 1024 / 1024,
                'size_after_mb': size_after / 1024 / 1024,
                'reduced_mb': (size_before - size_after) / 1024 / 1024,
            }
            
        except Exception as e:
            steps.append(f"Checkpoint failed: {e}")
            return {
                'success': False,
                'message': f'WAL checkpoint failed: {e}',
                'steps': steps,
            }
    
    async def _restore_from_backup(self) -> Dict[str, Any]:
        """Restore database from latest backup"""
        steps = []
        
        # Step 1: Create backup of corrupted file
        timestamp = int(datetime.utcnow().timestamp())
        corrupted_backup = self.backup_dir / f"{self.db_path.name}.corrupted.{timestamp}"
        
        try:
            if self.db_path.exists():
                shutil.copy2(self.db_path, corrupted_backup)
                steps.append(f"Backed up corrupted file to {corrupted_backup.name}")
        except Exception as e:
            steps.append(f"Could not backup corrupted file: {e}")
        
        # Step 2: Find latest backup
        backups = sorted(
            self.backup_dir.glob(f"{self.db_path.name}.backup.*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not backups:
            steps.append("No backups found - creating fresh database")
            
            # Create fresh database
            try:
                if self.db_path.exists():
                    self.db_path.unlink()
                
                # Create new empty database
                conn = sqlite3.connect(str(self.db_path))
                conn.execute("CREATE TABLE IF NOT EXISTS _recovery_marker (recovered_at TEXT)")
                conn.execute("INSERT INTO _recovery_marker VALUES (?)", (datetime.utcnow().isoformat(),))
                conn.commit()
                conn.close()
                
                steps.append("Created fresh database")
                
                return {
                    'success': True,
                    'message': 'Created fresh database (no backups available)',
                    'steps': steps,
                    'data_loss': True,
                }
            except Exception as e:
                steps.append(f"Failed to create fresh database: {e}")
                return {
                    'success': False,
                    'message': f'Could not create fresh database: {e}',
                    'steps': steps,
                }
        
        # Step 3: Restore from latest backup
        latest_backup = backups[0]
        steps.append(f"Found backup: {latest_backup.name}")
        
        try:
            # Remove corrupted file
            if self.db_path.exists():
                self.db_path.unlink()
            
            # Copy backup to main location
            shutil.copy2(latest_backup, self.db_path)
            steps.append(f"Restored from {latest_backup.name}")
            
            # Verify restored database
            conn = sqlite3.connect(str(self.db_path), timeout=5.0)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()
            conn.close()
            
            if integrity and integrity[0] == 'ok':
                steps.append("Integrity check passed on restored database")
                return {
                    'success': True,
                    'message': 'Database restored from backup',
                    'steps': steps,
                    'backup_used': latest_backup.name,
                    'data_loss': False,
                }
            else:
                steps.append(f"Integrity check failed on backup: {integrity}")
                return {
                    'success': False,
                    'message': 'Backup also corrupted',
                    'steps': steps,
                }
                
        except Exception as e:
            steps.append(f"Restore failed: {e}")
            return {
                'success': False,
                'message': f'Restore from backup failed: {e}',
                'steps': steps,
            }
    
    async def _retry_connection(self) -> Dict[str, Any]:
        """Retry database connection with backoff"""
        steps = []
        
        for attempt in range(3):
            try:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                if attempt > 0:
                    steps.append(f"Waiting {wait_time}s before retry {attempt}")
                    await asyncio.sleep(wait_time)
                
                conn = sqlite3.connect(str(self.db_path), timeout=10.0)
                conn.execute("SELECT 1")
                conn.close()
                
                steps.append(f"Connection successful on attempt {attempt + 1}")
                return {
                    'success': True,
                    'message': f'Connection restored on attempt {attempt + 1}',
                    'steps': steps,
                    'attempts': attempt + 1,
                }
                
            except Exception as e:
                steps.append(f"Attempt {attempt + 1} failed: {e}")
        
        return {
            'success': False,
            'message': 'All connection attempts failed',
            'steps': steps,
            'attempts': 3,
        }
    
    async def create_backup(self) -> Optional[Path]:
        """
        Create backup of current database
        
        Returns:
            Path to backup file if successful, None otherwise
        """
        if not self.db_path.exists():
            return None
        
        timestamp = int(datetime.utcnow().timestamp())
        backup_path = self.backup_dir / f"{self.db_path.name}.backup.{timestamp}"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"[DB-RECOVERY] Created backup: {backup_path.name}")
            return backup_path
        except Exception as e:
            logger.error(f"[DB-RECOVERY] Backup failed: {e}")
            return None


# Global instance
db_recovery_playbook = DatabaseRecoveryPlaybook()
