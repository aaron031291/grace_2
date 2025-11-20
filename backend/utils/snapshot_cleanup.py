"""
Comprehensive snapshot and cache cleanup utility

Prevents disk bloat from accumulated snapshots, caches, and backups.
Runs automatically during boot or can be invoked manually.
"""

import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import yaml

logger = logging.getLogger(__name__)


class SnapshotCleanupManager:
    """Manages cleanup of snapshots, caches, and backups across Grace"""
    
    def __init__(self, config_path: str = "config/snapshot_retention.yaml"):
        self.config = self._load_config(config_path)
        self.stats = {
            "items_deleted": 0,
            "bytes_freed": 0,
            "errors": 0,
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load retention configuration"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file) as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load cleanup config: {e}")
        
        # Default configuration
        return {
            "boot_snapshots": {"max_count": 3, "max_age_days": 30},
            "boot_cache": {"max_count": 5, "max_age_days": 7},
            "pre_boot_snapshots": {"max_count": 5, "max_age_days": 14},
            "database_backups": {"max_count": 10, "max_age_days": 30},
            "port_registry_backups": {"max_count": 20, "max_age_days": 14},
            "global": {"auto_cleanup_enabled": True, "min_free_space_gb": 10, "dry_run": False}
        }
    
    def cleanup_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run all cleanup tasks"""
        
        if dry_run or self.config.get("global", {}).get("dry_run", False):
            logger.info("[CLEANUP] Running in DRY-RUN mode")
        
        logger.info("[CLEANUP] Starting comprehensive cleanup...")
        
        # Clean each category
        self._cleanup_boot_snapshots(dry_run)
        self._cleanup_boot_cache(dry_run)
        self._cleanup_database_backups(dry_run)
        self._cleanup_port_registry_backups(dry_run)
        self._cleanup_pre_boot_snapshots(dry_run)
        
        logger.info(f"[CLEANUP] Complete! Deleted {self.stats['items_deleted']} items, "
                   f"freed {self.stats['bytes_freed'] / 1024 / 1024:.2f} MB")
        
        return self.stats
    
    def _cleanup_boot_snapshots(self, dry_run: bool = False):
        """Clean up .grace_snapshots/boot-ok-* directories"""
        config = self.config.get("boot_snapshots", {})
        max_count = config.get("max_count", 3)
        max_age_days = config.get("max_age_days", 30)
        
        snapshots_dir = Path(".grace_snapshots")
        if not snapshots_dir.exists():
            return
        
        snapshots = sorted(
            [d for d in snapshots_dir.glob('boot-ok-*') if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for i, snapshot_dir in enumerate(snapshots):
            # Keep if within count or age limits
            age = datetime.fromtimestamp(snapshot_dir.stat().st_mtime)
            if i < max_count and age > cutoff_date:
                continue
            
            self._delete_directory(snapshot_dir, "boot snapshot", dry_run)
    
    def _cleanup_boot_cache(self, dry_run: bool = False):
        """Clean up .grace_snapshots/boot_*_cache directories and related files"""
        config = self.config.get("boot_cache", {})
        max_count = config.get("max_count", 5)
        
        snapshots_dir = Path(".grace_snapshots")
        if not snapshots_dir.exists():
            return
        
        # Cache directories
        cache_dirs = sorted(
            [d for d in snapshots_dir.glob('boot_*_cache') if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, cache_dir in enumerate(cache_dirs):
            if i < max_count:
                continue
            self._delete_directory(cache_dir, "boot cache", dry_run)
        
        # DB files
        db_files = sorted(
            snapshots_dir.glob('boot_*_db.sqlite'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, db_file in enumerate(db_files):
            if i < max_count:
                continue
            self._delete_file(db_file, "boot db", dry_run)
        
        # Metadata files
        metadata_files = sorted(
            snapshots_dir.glob('boot_*_metadata.json'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, meta_file in enumerate(metadata_files):
            if i < max_count:
                continue
            self._delete_file(meta_file, "boot metadata", dry_run)
    
    def _cleanup_database_backups(self, dry_run: bool = False):
        """Clean up databases/backups/*"""
        config = self.config.get("database_backups", {})
        max_count = config.get("max_count", 10)
        
        backups_dir = Path("databases/backups")
        if not backups_dir.exists():
            return
        
        backups = sorted(
            [f for f in backups_dir.iterdir() if f.is_file()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, backup_file in enumerate(backups):
            if i < max_count:
                continue
            self._delete_file(backup_file, "database backup", dry_run)
    
    def _cleanup_port_registry_backups(self, dry_run: bool = False):
        """Clean up databases/port_registry/port_registry_backup_*.json"""
        config = self.config.get("port_registry_backups", {})
        max_count = config.get("max_count", 20)
        
        port_dir = Path("databases/port_registry")
        if not port_dir.exists():
            return
        
        backups = sorted(
            [f for f in port_dir.glob('port_registry_backup_*.json')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, backup_file in enumerate(backups):
            if i < max_count:
                continue
            self._delete_file(backup_file, "port registry backup", dry_run)
    
    def _cleanup_pre_boot_snapshots(self, dry_run: bool = False):
        """Clean up storage/snapshots/pre_boot_* directories"""
        config = self.config.get("pre_boot_snapshots", {})
        max_count = config.get("max_count", 5)
        
        snapshots_dir = Path("storage/snapshots")
        if not snapshots_dir.exists():
            return
        
        snapshots = sorted(
            [d for d in snapshots_dir.glob('pre_boot_*') if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for i, snapshot_dir in enumerate(snapshots):
            if i < max_count:
                continue
            self._delete_directory(snapshot_dir, "pre-boot snapshot", dry_run)
    
    def _delete_directory(self, directory: Path, label: str, dry_run: bool):
        """Delete a directory and track stats"""
        try:
            size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            
            if dry_run:
                logger.info(f"[CLEANUP] [DRY-RUN] Would delete {label}: {directory.name} ({size / 1024 / 1024:.2f} MB)")
            else:
                shutil.rmtree(directory)
                self.stats["items_deleted"] += 1
                self.stats["bytes_freed"] += size
                logger.info(f"[CLEANUP] Deleted {label}: {directory.name} ({size / 1024 / 1024:.2f} MB)")
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"[CLEANUP] Failed to delete {directory}: {e}")
    
    def _delete_file(self, file_path: Path, label: str, dry_run: bool):
        """Delete a file and track stats"""
        try:
            size = file_path.stat().st_size
            
            if dry_run:
                logger.info(f"[CLEANUP] [DRY-RUN] Would delete {label}: {file_path.name} ({size / 1024:.2f} KB)")
            else:
                file_path.unlink()
                self.stats["items_deleted"] += 1
                self.stats["bytes_freed"] += size
                logger.info(f"[CLEANUP] Deleted {label}: {file_path.name} ({size / 1024:.2f} KB)")
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"[CLEANUP] Failed to delete {file_path}: {e}")
    
    def get_disk_usage_stats(self) -> Dict[str, Any]:
        """Get current disk usage statistics"""
        
        stats = {}
        
        # .grace_snapshots
        snapshots_dir = Path(".grace_snapshots")
        if snapshots_dir.exists():
            total_size = sum(f.stat().st_size for f in snapshots_dir.rglob('*') if f.is_file())
            file_count = len(list(snapshots_dir.rglob('*')))
            stats["grace_snapshots"] = {
                "total_bytes": total_size,
                "total_mb": total_size / 1024 / 1024,
                "file_count": file_count,
            }
        
        # storage/snapshots
        storage_snapshots = Path("storage/snapshots")
        if storage_snapshots.exists():
            total_size = sum(f.stat().st_size for f in storage_snapshots.rglob('*') if f.is_file())
            stats["storage_snapshots"] = {
                "total_bytes": total_size,
                "total_mb": total_size / 1024 / 1024,
            }
        
        # databases/backups
        db_backups = Path("databases/backups")
        if db_backups.exists():
            total_size = sum(f.stat().st_size for f in db_backups.rglob('*') if f.is_file())
            stats["database_backups"] = {
                "total_bytes": total_size,
                "total_mb": total_size / 1024 / 1024,
            }
        
        return stats


# Convenience function for server.py integration
async def run_cleanup(dry_run: bool = False) -> Dict[str, Any]:
    """Run cleanup and return stats"""
    manager = SnapshotCleanupManager()
    return manager.cleanup_all(dry_run=dry_run)
