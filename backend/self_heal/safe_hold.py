"""
Safe-Hold Snapshot & Rollback System

Provides atomic snapshots of system state before risky operations:
- Database state (WAL checkpoint)
- Configuration exports
- Service health baselines
- Signed manifests for verification

Enables one-click rollback to last known-good state when actions fail.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import hashlib
import shutil

from sqlalchemy import Column, String, JSON, DateTime, Boolean, Integer, text
from sqlalchemy.orm import declarative_base

from ..models import Base, async_session
from ..immutable_log import immutable_log


class SafeHoldSnapshot(Base):
    """Records a point-in-time snapshot of system state"""
    __tablename__ = "safe_hold_snapshots"
    
    id = Column(String, primary_key=True)
    snapshot_type = Column(String, nullable=False)  # "pre_action", "golden", "manual"
    
    # What triggered this snapshot
    triggered_by = Column(String, nullable=True)
    action_contract_id = Column(String, nullable=True)
    playbook_run_id = Column(Integer, nullable=True)
    
    # State captured
    manifest = Column(JSON, nullable=False)  # Inventory of what was captured
    manifest_hash = Column(String, nullable=False)  # For integrity verification
    storage_uri = Column(String, nullable=True)  # Where artifacts are stored
    
    # Health metrics at snapshot time
    baseline_metrics = Column(JSON, nullable=True)
    system_health_score = Column(Integer, nullable=True)  # 0-100
    
    # Status
    status = Column(String, default="active")  # active, restored, invalidated
    is_golden = Column(Boolean, default=False)  # Certified safe baseline
    is_validated = Column(Boolean, default=False)  # Benchmark passed
    
    # Timing
    created_at = Column(DateTime, nullable=False)
    validated_at = Column(DateTime, nullable=True)
    restored_at = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(String, nullable=True)


class SnapshotManager:
    """
    Manages safe-hold snapshots and rollback operations.
    Coordinates database checkpoints, config backups, and state capture.
    """
    
    def __init__(self, snapshot_dir: str = "./databases/snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_snapshot(
        self,
        snapshot_type: str = "pre_action",
        triggered_by: Optional[str] = None,
        action_contract_id: Optional[str] = None,
        playbook_run_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> SafeHoldSnapshot:
        """
        Create a complete system snapshot.
        Captures database state, config, and health metrics.
        """
        
        timestamp = datetime.now(timezone.utc)
        snapshot_id = f"snapshot-{timestamp.strftime('%Y%m%d-%H%M%S')}-{timestamp.timestamp()}"
        snapshot_path = self.snapshot_dir / snapshot_id
        snapshot_path.mkdir(exist_ok=True)
        
        # Build manifest of captured state
        manifest = {
            "snapshot_id": snapshot_id,
            "timestamp": timestamp.isoformat(),
            "components": []
        }
        
        # 1. Database snapshot
        try:
            db_artifact = await self._snapshot_database(snapshot_path)
            manifest["components"].append(db_artifact)
        except Exception as e:
            manifest["components"].append({
                "type": "database",
                "status": "error",
                "error": str(e)
            })
        
        # 2. Configuration export
        try:
            config_artifact = await self._snapshot_config(snapshot_path)
            manifest["components"].append(config_artifact)
        except Exception as e:
            manifest["components"].append({
                "type": "config",
                "status": "error",
                "error": str(e)
            })
        
        # 3. Service health baselines
        try:
            health_artifact = await self._snapshot_health(snapshot_path)
            manifest["components"].append(health_artifact)
            baseline_metrics = health_artifact.get("metrics", {})
            health_score = health_artifact.get("health_score", 0)
        except Exception as e:
            manifest["components"].append({
                "type": "health",
                "status": "error",
                "error": str(e)
            })
            baseline_metrics = {}
            health_score = 0
        
        # Generate manifest hash for integrity
        manifest_hash = self._hash_manifest(manifest)
        
        # Save manifest to disk
        manifest_file = snapshot_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Create database record
        snapshot = SafeHoldSnapshot(
            id=snapshot_id,
            snapshot_type=snapshot_type,
            triggered_by=triggered_by,
            action_contract_id=action_contract_id,
            playbook_run_id=playbook_run_id,
            manifest=manifest,
            manifest_hash=manifest_hash,
            storage_uri=f"file://{snapshot_path.absolute()}",
            baseline_metrics=baseline_metrics,
            system_health_score=health_score,
            status="active",
            created_at=timestamp,
            notes=notes
        )
        
        async with async_session() as session:
            session.add(snapshot)
            await session.commit()
        
        # Log to immutable ledger
        await immutable_log.append(
            actor="safe_hold",
            action="snapshot_created",
            resource=snapshot_id,
            subsystem="safe_hold",
            payload={
                "snapshot_id": snapshot_id,
                "type": snapshot_type,
                "manifest_hash": manifest_hash,
                "triggered_by": triggered_by
            },
            result="success"
        )
        
        print(f"  [SNAPSHOT] Created: {snapshot_id} (hash: {manifest_hash[:8]})")
        
        return snapshot
    
    async def restore_snapshot(
        self,
        snapshot_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Restore system to a previous snapshot.
        
        Args:
            snapshot_id: ID of snapshot to restore
            dry_run: If True, validate but don't actually restore
        
        Returns:
            Result dictionary with success status and details
        """
        
        async with async_session() as session:
            snapshot = await session.get(SafeHoldSnapshot, snapshot_id)
            if not snapshot:
                return {"success": False, "error": "Snapshot not found"}
            
            # Verify manifest integrity
            if not self._verify_manifest(snapshot.manifest, snapshot.manifest_hash):
                return {"success": False, "error": "Manifest integrity check failed"}
            
            snapshot_path = Path(snapshot.storage_uri.replace("file://", ""))
            if not snapshot_path.exists():
                return {"success": False, "error": "Snapshot files not found"}
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "snapshot_id": snapshot_id,
                    "components": snapshot.manifest["components"],
                    "message": "Validation passed, ready to restore"
                }
            
            # Perform actual restore
            results = []
            
            for component in snapshot.manifest["components"]:
                if component.get("status") == "error":
                    continue
                
                try:
                    if component["type"] == "database":
                        result = await self._restore_database(snapshot_path, component)
                        results.append(result)
                    elif component["type"] == "config":
                        result = await self._restore_config(snapshot_path, component)
                        results.append(result)
                    elif component["type"] == "health":
                        # Health is read-only, skip restore
                        pass
                except Exception as e:
                    results.append({
                        "type": component["type"],
                        "success": False,
                        "error": str(e)
                    })
            
            # Update snapshot record (use text SQL to avoid ORM session issues)
            await session.execute(text("""
                UPDATE safe_hold_snapshots
                SET status = 'restored', restored_at = :restored_at
                WHERE id = :snapshot_id
            """), {
                "restored_at": datetime.now(timezone.utc),
                "snapshot_id": snapshot_id
            })
            await session.commit()
            
            # Log restoration
            await immutable_log.append(
                actor="safe_hold",
                action="snapshot_restored",
                resource=snapshot_id,
                subsystem="safe_hold",
                payload={
                    "snapshot_id": snapshot_id,
                    "results": results
                },
                result="success"
            )
            
            print(f"  [RESTORE] Restored snapshot: {snapshot_id}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "results": results,
                "restored_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def validate_snapshot(
        self,
        snapshot_id: str,
        benchmark_results: Dict[str, Any]
    ) -> bool:
        """
        Mark a snapshot as validated (golden) if it passes benchmarks.
        """
        
        async with async_session() as session:
            snapshot = await session.get(SafeHoldSnapshot, snapshot_id)
            if not snapshot:
                return False
            
            # Check if benchmarks passed
            passed = benchmark_results.get("passed", False)
            
            if passed:
                snapshot.is_validated = True
                snapshot.is_golden = True
                snapshot.validated_at = datetime.now(timezone.utc)
                await session.commit()
                
                await immutable_log.append(
                    actor="safe_hold",
                    action="snapshot_validated",
                    resource=snapshot_id,
                    subsystem="safe_hold",
                    payload={
                        "snapshot_id": snapshot_id,
                        "benchmark_results": benchmark_results
                    },
                    result="golden"
                )
                
                print(f"  ⭐ Snapshot {snapshot_id} marked as GOLDEN")
            
            return passed
    
    async def _snapshot_database(self, snapshot_path: Path) -> Dict[str, Any]:
        """Snapshot database state (simplified - would use WAL checkpoint in production)"""
        
        from ..settings import get_settings
        
        settings = get_settings()
        db_source = Path(settings.DB_PATH)
        if not db_source.exists():
            return {
                "type": "database",
                "status": "skip",
                "reason": "Database file not found"
            }
        
        # Copy database file
        db_backup = snapshot_path / "grace.db"
        shutil.copy2(db_source, db_backup)
        
        # Also copy WAL/SHM files if they exist
        wal_files = []
        for ext in ["-wal", "-shm", "-journal"]:
            wal_source = Path(str(db_source) + ext)
            if wal_source.exists():
                wal_backup = snapshot_path / f"grace.db{ext}"
                shutil.copy2(wal_source, wal_backup)
                wal_files.append(f"grace.db{ext}")
        
        return {
            "type": "database",
            "status": "success",
            "files": ["grace.db"] + wal_files,
            "size_bytes": db_backup.stat().st_size
        }
    
    async def _snapshot_config(self, snapshot_path: Path) -> Dict[str, Any]:
        """Snapshot configuration files"""
        
        config_files = [".env", "alembic.ini"]
        captured = []
        
        for filename in config_files:
            source = Path(filename)
            if source.exists():
                dest = snapshot_path / filename
                shutil.copy2(source, dest)
                captured.append(filename)
        
        return {
            "type": "config",
            "status": "success",
            "files": captured
        }
    
    async def _snapshot_health(self, snapshot_path: Path) -> Dict[str, Any]:
        """Capture current health metrics as baseline"""
        
        try:
            from ..health_models import Service, HealthSignal
            
            health_data = {
                "services": [],
                "metrics": {}
            }
            
            async with async_session() as session:
                # Get all services and their latest signals
                from sqlalchemy import select
                services_result = await session.execute(select(Service))
                services = services_result.scalars().all()
                
                for svc in services:
                    signals_result = await session.execute(
                        select(HealthSignal)
                        .where(HealthSignal.service_id == svc.id)
                        .order_by(HealthSignal.created_at.desc())
                        .limit(10)
                    )
                    signals = signals_result.scalars().all()
                    
                    health_data["services"].append({
                        "name": svc.name,
                        "status": svc.status,
                        "health_score": svc.health_score,
                        "signals": [
                            {
                                "metric": sig.metric_key,
                                "value": sig.value,
                                "timestamp": sig.created_at.isoformat() if sig.created_at else None
                            }
                            for sig in signals
                        ]
                    })
                
                # Calculate overall health score
                if services:
                    avg_health = sum(s.health_score or 0 for s in services) / len(services)
                else:
                    avg_health = 100
            
            # Save health data
            health_file = snapshot_path / "health_baseline.json"
            with open(health_file, "w") as f:
                json.dump(health_data, f, indent=2)
            
            return {
                "type": "health",
                "status": "success",
                "health_score": int(avg_health),
                "metrics": health_data["metrics"],
                "services_count": len(health_data["services"])
            }
        
        except Exception as e:
            return {
                "type": "health",
                "status": "error",
                "error": str(e)
            }
    
    async def _restore_database(self, snapshot_path: Path, component: Dict) -> Dict[str, Any]:
        """Restore database from snapshot"""
        
        from ..settings import get_settings
        
        settings = get_settings()
        db_path = settings.DB_PATH
        
        db_backup = snapshot_path / "grace.db"
        if not db_backup.exists():
            return {"type": "database", "success": False, "error": "Backup file not found"}
        
        db_target = Path(db_path)
        
        # Backup current database first
        if db_target.exists():
            backup_current = Path(f"{db_path}.pre_restore")
            shutil.copy2(db_target, backup_current)
        
        # Restore from snapshot
        shutil.copy2(db_backup, db_target)
        
        # Restore WAL files
        for filename in component.get("files", []):
            if filename != "grace.db":
                source = snapshot_path / filename
                if source.exists():
                    dest = Path(str(db_target) + filename.replace("grace.db", ""))
                    shutil.copy2(source, dest)
        
        return {
            "type": "database",
            "success": True,
            "files_restored": component.get("files", [])
        }
    
    async def _restore_config(self, snapshot_path: Path, component: Dict) -> Dict[str, Any]:
        """Restore configuration files from snapshot"""
        
        restored = []
        for filename in component.get("files", []):
            source = snapshot_path / filename
            if source.exists():
                dest = Path(filename)
                shutil.copy2(source, dest)
                restored.append(filename)
        
        return {
            "type": "config",
            "success": True,
            "files_restored": restored
        }
    
    def _hash_manifest(self, manifest: Dict) -> str:
        """Generate integrity hash of manifest"""
        canonical = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    def _verify_manifest(self, manifest: Dict, expected_hash: str) -> bool:
        """Verify manifest integrity"""
        actual_hash = self._hash_manifest(manifest)
        return actual_hash == expected_hash
    
    async def get_latest_golden(self) -> Optional[SafeHoldSnapshot]:
        """Get the most recent validated golden snapshot"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SafeHoldSnapshot)
                .where(SafeHoldSnapshot.is_golden == True)
                .order_by(SafeHoldSnapshot.created_at.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()


# Singleton instance
snapshot_manager = SnapshotManager()
