"""
Restore Manager - Backup restoration
"""

import secrets
from datetime import datetime
from typing import Dict, List, Optional
from .models import RestoreJob, RestoreStatus
from .backup_manager import BackupManager


class RestoreManager:
    """Manage restore operations"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.restore_jobs: Dict[str, RestoreJob] = {}
    
    def create_restore_job(
        self,
        backup_id: str,
        tenant_id: str,
        target_environment: str = "production",
        components_to_restore: Optional[List[str]] = None,
    ) -> RestoreJob:
        """Create a new restore job"""
        backup = self.backup_manager.get_backup(backup_id)
        if not backup:
            raise ValueError(f"Backup not found: {backup_id}")
        
        if backup.tenant_id != tenant_id:
            raise ValueError("Backup does not belong to tenant")
        
        restore_id = f"restore_{secrets.token_urlsafe(16)}"
        
        restore_job = RestoreJob(
            restore_id=restore_id,
            backup_id=backup_id,
            tenant_id=tenant_id,
            restore_point=backup.completed_at or backup.created_at,
            target_environment=target_environment,
            components_to_restore=components_to_restore or backup.components,
        )
        
        self.restore_jobs[restore_id] = restore_job
        
        self._execute_restore(restore_job, backup)
        
        return restore_job
    
    def _execute_restore(self, restore_job: RestoreJob, backup):
        """Execute restore (simulated)"""
        
        restore_job.status = RestoreStatus.IN_PROGRESS
        restore_job.started_at = datetime.utcnow()
        
        restore_job.progress_percent = 100.0
        restore_job.files_restored = backup.file_count
        restore_job.bytes_restored = backup.size_bytes
        
        restore_job.status = RestoreStatus.COMPLETED
        restore_job.completed_at = datetime.utcnow()
        restore_job.duration_seconds = 180.0  # Simulated
        restore_job.verification_passed = True
    
    def get_restore_job(self, restore_id: str) -> Optional[RestoreJob]:
        """Get restore job by ID"""
        return self.restore_jobs.get(restore_id)
    
    def list_restore_jobs(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[RestoreStatus] = None,
    ) -> List[RestoreJob]:
        """List restore jobs with optional filters"""
        jobs = list(self.restore_jobs.values())
        
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    def cancel_restore_job(self, restore_id: str) -> RestoreJob:
        """Cancel restore job"""
        job = self.get_restore_job(restore_id)
        if not job:
            raise ValueError(f"Restore job not found: {restore_id}")
        
        if job.status in [RestoreStatus.COMPLETED, RestoreStatus.FAILED]:
            raise ValueError("Cannot cancel completed or failed restore job")
        
        job.status = RestoreStatus.ROLLED_BACK
        job.updated_at = datetime.utcnow()
        return job
