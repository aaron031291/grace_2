"""
Backup Manager - Automated backup management
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .models import Backup, BackupType, BackupStatus


class BackupManager:
    """Manage backups"""
    
    def __init__(self):
        self.backups: Dict[str, Backup] = {}
    
    def create_backup(
        self,
        tenant_id: str,
        backup_type: BackupType = BackupType.FULL,
        components: Optional[List[str]] = None,
        retention_days: int = 30,
    ) -> Backup:
        """Create a new backup"""
        backup_id = f"backup_{secrets.token_urlsafe(16)}"
        
        components = components or ["database", "files", "config", "secrets"]
        
        backup = Backup(
            backup_id=backup_id,
            tenant_id=tenant_id,
            backup_type=backup_type,
            status=BackupStatus.PENDING,
            components=components,
            retention_days=retention_days,
            expires_at=datetime.utcnow() + timedelta(days=retention_days),
        )
        
        self.backups[backup_id] = backup
        
        self._execute_backup(backup)
        
        return backup
    
    def _execute_backup(self, backup: Backup):
        """Execute backup (simulated)"""
        
        backup.status = BackupStatus.IN_PROGRESS
        backup.started_at = datetime.utcnow()
        
        backup.status = BackupStatus.COMPLETED
        backup.completed_at = datetime.utcnow()
        backup.duration_seconds = 120.5  # Simulated
        backup.size_bytes = 1024 * 1024 * 500  # 500 MB
        backup.compressed_size_bytes = 1024 * 1024 * 100  # 100 MB compressed
        backup.file_count = 1500
        backup.storage_location = f"s3://grace-backups/{backup.tenant_id}/{backup.backup_id}.tar.gz.enc"
    
    def get_backup(self, backup_id: str) -> Optional[Backup]:
        """Get backup by ID"""
        return self.backups.get(backup_id)
    
    def list_backups(
        self,
        tenant_id: Optional[str] = None,
        backup_type: Optional[BackupType] = None,
        status: Optional[BackupStatus] = None,
    ) -> List[Backup]:
        """List backups with optional filters"""
        backups = list(self.backups.values())
        
        if tenant_id:
            backups = [b for b in backups if b.tenant_id == tenant_id]
        if backup_type:
            backups = [b for b in backups if b.backup_type == backup_type]
        if status:
            backups = [b for b in backups if b.status == status]
        
        return sorted(backups, key=lambda b: b.created_at, reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete backup"""
        backup = self.get_backup(backup_id)
        if not backup:
            return False
        
        del self.backups[backup_id]
        return True
    
    def cleanup_expired_backups(self) -> int:
        """Clean up expired backups"""
        now = datetime.utcnow()
        expired = [
            b for b in self.backups.values()
            if b.expires_at and b.expires_at < now
        ]
        
        for backup in expired:
            self.delete_backup(backup.backup_id)
        
        return len(expired)
    
    def get_backup_stats(self, tenant_id: Optional[str] = None) -> Dict:
        """Get backup statistics"""
        backups = self.list_backups(tenant_id=tenant_id)
        
        if not backups:
            return {
                "total_backups": 0,
                "total_size_gb": 0.0,
                "latest_backup": None,
                "success_rate": 0.0,
            }
        
        completed = [b for b in backups if b.status == BackupStatus.COMPLETED]
        failed = [b for b in backups if b.status == BackupStatus.FAILED]
        
        total_size = sum(b.size_bytes for b in completed)
        
        return {
            "total_backups": len(backups),
            "completed_backups": len(completed),
            "failed_backups": len(failed),
            "total_size_gb": total_size / (1024 ** 3),
            "latest_backup": backups[0].created_at.isoformat() if backups else None,
            "success_rate": len(completed) / len(backups) if backups else 0.0,
        }
