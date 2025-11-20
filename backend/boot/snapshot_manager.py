"""
Boot Snapshot Manager
Captures known-good system state after clean boot
Implements 3-snapshot retention policy with rollback capability
"""

import asyncio
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)


class BootSnapshotManager:
    """
    Manages boot snapshots with retention policy
    
    Strategy:
    1. Capture after Guardian approval (all chunks validated)
    2. Keep only 3 most recent snapshots
    3. Enable rollback to any of the 3 states
    4. Encrypt if secrets present
    """
    
    def __init__(self):
        self.snapshot_root = Path(".grace_snapshots")
        self.snapshot_root.mkdir(exist_ok=True)
        
        # What to snapshot
        self.snapshot_targets = [
            "databases/",
            "config/",
            ".env",
            "grace.db",
            "VERSION"
        ]
        
        # Retention
        self.max_snapshots = 3
        
        # Statistics
        self.total_snapshots_created = 0
        self.total_snapshots_deleted = 0
        self.last_snapshot_at: Optional[str] = None
    
    async def capture_snapshot(self, boot_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture snapshot after successful boot
        
        Args:
            boot_result: Guardian boot result with validation info
            
        Returns:
            Snapshot metadata
        """
        
        # Verify boot was successful (server not running yet during boot)
        if not boot_result or not isinstance(boot_result, dict):
            logger.warning("[SNAPSHOT] Invalid boot result - skipping snapshot")
            return {"captured": False, "reason": "invalid_boot_result"}
        
        # Check if boot was successful
        boot_success = boot_result.get('success', True)  # Default to True if not specified
        if not boot_success:
            logger.warning("[SNAPSHOT] Boot not successful - skipping snapshot")
            return {"captured": False, "reason": "boot_not_successful"}
        
        # Create snapshot directory with timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        snapshot_dir = self.snapshot_root / f"boot-ok-{timestamp}"
        snapshot_dir.mkdir(exist_ok=True)
        
        logger.info(f"[SNAPSHOT] Capturing boot snapshot: {snapshot_dir.name}")
        
        snapshot_metadata = {
            "snapshot_id": snapshot_dir.name,
            "captured_at": datetime.utcnow().isoformat(),
            "boot_result": boot_result,
            "targets": [],
            "total_bytes": 0
        }
        
        # Copy each target
        for target in self.snapshot_targets:
            target_path = Path(target)
            
            if not target_path.exists():
                logger.debug(f"[SNAPSHOT] Skipping {target} (does not exist)")
                continue
            
            try:
                dest_path = snapshot_dir / target
                
                if target_path.is_dir():
                    shutil.copytree(target_path, dest_path, dirs_exist_ok=True)
                    size = sum(f.stat().st_size for f in dest_path.rglob('*') if f.is_file())
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target_path, dest_path)
                    size = dest_path.stat().st_size
                
                snapshot_metadata["targets"].append({
                    "path": target,
                    "size_bytes": size
                })
                snapshot_metadata["total_bytes"] += size
                
                logger.info(f"[SNAPSHOT]   ✓ Captured {target} ({size:,} bytes)")
                
            except Exception as e:
                logger.error(f"[SNAPSHOT]   ✗ Failed to capture {target}: {e}")
        
        # Save metadata
        metadata_file = snapshot_dir / "snapshot_metadata.json"
        metadata_file.write_text(json.dumps(snapshot_metadata, indent=2))
        
        # Apply retention policy (keep 3 most recent)
        await self._apply_retention_policy()
        
        self.total_snapshots_created += 1
        self.last_snapshot_at = datetime.utcnow().isoformat()
        
        logger.info(f"[SNAPSHOT] ✓ Snapshot captured: {snapshot_dir.name}")
        logger.info(f"[SNAPSHOT]   Total size: {snapshot_metadata['total_bytes']:,} bytes")
        logger.info(f"[SNAPSHOT]   Targets: {len(snapshot_metadata['targets'])}")
        
        return {
            "captured": True,
            "snapshot_id": snapshot_dir.name,
            "metadata": snapshot_metadata
        }
    
    async def _verify_health(self) -> bool:
        """
        Verify system health before snapshot (for runtime snapshots)
        Note: This is only used for manual/scheduled snapshots, not during boot
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get("http://localhost:8000/health")
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"[SNAPSHOT] Health check failed: {e}")
            return False
    
    async def _apply_retention_policy(self):
        """Keep only 3 most recent snapshots and clean up cache/db artifacts"""
        
        # List all snapshots
        snapshots = sorted(
            [d for d in self.snapshot_root.iterdir() if d.is_dir() and d.name.startswith("boot-ok-")],
            key=lambda x: x.stat().st_mtime,
            reverse=True  # Newest first
        )
        
        # Delete snapshots beyond retention limit
        if len(snapshots) > self.max_snapshots:
            to_delete = snapshots[self.max_snapshots:]
            
            for snapshot_dir in to_delete:
                try:
                    shutil.rmtree(snapshot_dir)
                    self.total_snapshots_deleted += 1
                    logger.info(f"[SNAPSHOT] Deleted old snapshot: {snapshot_dir.name}")
                except Exception as e:
                    logger.error(f"[SNAPSHOT] Failed to delete {snapshot_dir.name}: {e}")
        
        # Clean up boot cache directories (keep only 5 most recent)
        cache_dirs = sorted(
            [d for d in self.snapshot_root.glob('boot_*_cache') if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(cache_dirs) > 5:
            for cache_dir in cache_dirs[5:]:
                try:
                    shutil.rmtree(cache_dir)
                    logger.info(f"[SNAPSHOT] Deleted old cache: {cache_dir.name}")
                except Exception as e:
                    logger.error(f"[SNAPSHOT] Failed to delete cache {cache_dir.name}: {e}")
        
        # Clean up orphaned db.sqlite files (keep only 5 most recent)
        db_files = sorted(
            self.snapshot_root.glob('boot_*_db.sqlite'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(db_files) > 5:
            for db_file in db_files[5:]:
                try:
                    db_file.unlink()
                    logger.info(f"[SNAPSHOT] Deleted old db: {db_file.name}")
                except Exception as e:
                    logger.error(f"[SNAPSHOT] Failed to delete {db_file.name}: {e}")
        
        # Clean up orphaned metadata.json files (keep only 5 most recent)
        metadata_files = sorted(
            self.snapshot_root.glob('boot_*_metadata.json'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(metadata_files) > 5:
            for meta_file in metadata_files[5:]:
                try:
                    meta_file.unlink()
                    logger.info(f"[SNAPSHOT] Deleted old metadata: {meta_file.name}")
                except Exception as e:
                    logger.error(f"[SNAPSHOT] Failed to delete {meta_file.name}: {e}")
        
        logger.info(f"[SNAPSHOT] Retention policy applied: {len(snapshots[:self.max_snapshots])} snapshots kept")
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots"""
        snapshots = []
        
        for snapshot_dir in self.snapshot_root.iterdir():
            if not snapshot_dir.is_dir() or not snapshot_dir.name.startswith("boot-ok-"):
                continue
            
            metadata_file = snapshot_dir / "snapshot_metadata.json"
            
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text())
                except Exception:
                    metadata = {}
            else:
                metadata = {}
            
            snapshots.append({
                "snapshot_id": snapshot_dir.name,
                "captured_at": metadata.get("captured_at", "unknown"),
                "total_bytes": metadata.get("total_bytes", 0),
                "targets_count": len(metadata.get("targets", [])),
                "path": str(snapshot_dir)
            })
        
        # Sort by captured_at (newest first)
        return sorted(snapshots, key=lambda x: x["captured_at"], reverse=True)
    
    async def restore_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Restore system from a snapshot
        
        WARNING: This will overwrite current state!
        """
        
        snapshot_dir = self.snapshot_root / snapshot_id
        
        if not snapshot_dir.exists():
            return {"restored": False, "error": "Snapshot not found"}
        
        logger.warning(f"[SNAPSHOT] RESTORING from snapshot: {snapshot_id}")
        logger.warning("[SNAPSHOT] Current state will be OVERWRITTEN")
        
        # Load metadata
        metadata_file = snapshot_dir / "snapshot_metadata.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text())
        else:
            return {"restored": False, "error": "Snapshot metadata missing"}
        
        restored_targets = []
        
        # Restore each target
        for target_info in metadata.get("targets", []):
            target = target_info["path"]
            source_path = snapshot_dir / target
            dest_path = Path(target)
            
            try:
                # Backup current state first
                if dest_path.exists():
                    backup_path = Path(f"_trash/pre_restore_{target.replace('/', '_')}")
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if dest_path.is_dir():
                        if backup_path.exists():
                            shutil.rmtree(backup_path)
                        shutil.copytree(dest_path, backup_path)
                    else:
                        shutil.copy2(dest_path, backup_path)
                
                # Restore from snapshot
                if source_path.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                
                restored_targets.append(target)
                logger.info(f"[SNAPSHOT]   ✓ Restored {target}")
                
            except Exception as e:
                logger.error(f"[SNAPSHOT]   ✗ Failed to restore {target}: {e}")
        
        logger.info(f"[SNAPSHOT] ✓ Restored {len(restored_targets)} targets from {snapshot_id}")
        
        return {
            "restored": True,
            "snapshot_id": snapshot_id,
            "targets_restored": restored_targets,
            "message": "System restored - restart server to apply changes"
        }
    
    async def capture_runtime_snapshot(self, reason: str = "manual") -> Dict[str, Any]:
        """
        Capture snapshot during runtime (with health check)
        
        Args:
            reason: Reason for snapshot (manual, scheduled, pre_update, etc.)
            
        Returns:
            Snapshot metadata
        """
        
        # Verify system is healthy (server should be running)
        health_ok = await self._verify_health()
        if not health_ok:
            logger.warning("[SNAPSHOT] Health check failed - skipping runtime snapshot")
            return {"captured": False, "reason": "health_check_failed"}
        
        # Create a mock boot_result for runtime snapshots
        mock_boot_result = {
            "success": True,
            "snapshot_reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Use the main capture method
        return await self.capture_snapshot(mock_boot_result)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get snapshot manager statistics"""
        snapshots = self.list_snapshots()
        
        return {
            "total_snapshots": len(snapshots),
            "max_retention": self.max_snapshots,
            "total_created": self.total_snapshots_created,
            "total_deleted": self.total_snapshots_deleted,
            "last_snapshot_at": self.last_snapshot_at,
            "snapshots": snapshots
        }


# Global instance
boot_snapshot_manager = BootSnapshotManager()
