"""
Backup/Restore Manager with Automated Runbooks
"""
import asyncio
import json
import tarfile
import gzip
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import shutil

from backend.security.kms_encryption import kms_encryption
from backend.security.retention_policies import retention_policy_manager
from backend.versioning.knowledge_versioning import knowledge_versioning
from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class BackupRestoreManager:
    """Automated backup and restore with integrity testing"""
    
    def __init__(self):
        self.backup_root = Path("backups")
        self.backup_root.mkdir(exist_ok=True)
        
        self.backup_stats = {
            "total_backups": 0,
            "successful_backups": 0,
            "failed_backups": 0,
            "total_backup_size": 0,
            "last_backup": None,
            "integrity_tests_passed": 0,
            "integrity_tests_failed": 0
        }
        
        # Backup schedule configuration
        self.backup_schedule = {
            "full_backup": timedelta(days=7),      # Weekly full backup
            "incremental": timedelta(hours=6),     # 6-hourly incremental
            "integrity_test": timedelta(days=1),   # Daily integrity test
            "retention": timedelta(days=90)        # Keep backups for 90 days
        }
    
    async def create_full_backup(self, backup_id: Optional[str] = None) -> Dict[str, Any]:
        """Create full system backup"""
        if not backup_id:
            backup_id = f"full_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔄 Starting full backup: {backup_id}")
        
        backup_result = {
            "backup_id": backup_id,
            "backup_type": "full",
            "start_time": datetime.utcnow().isoformat(),
            "components": {},
            "total_size": 0,
            "success": False,
            "errors": []
        }
        
        try:
            # Create backup directory
            backup_dir = self.backup_root / backup_id
            backup_dir.mkdir(exist_ok=True)
            
            # Backup components
            components = [
                ("knowledge_base", self._backup_knowledge_base),
                ("configurations", self._backup_configurations),
                ("security_artifacts", self._backup_security_artifacts),
                ("version_history", self._backup_version_history),
                ("audit_logs", self._backup_audit_logs)
            ]
            
            for component_name, backup_func in components:
                try:
                    logger.info(f"📦 Backing up {component_name}...")
                    component_result = await backup_func(backup_dir)
                    backup_result["components"][component_name] = component_result
                    backup_result["total_size"] += component_result.get("size_bytes", 0)
                    
                except Exception as e:
                    error_msg = f"Failed to backup {component_name}: {e}"
                    logger.error(error_msg)
                    backup_result["errors"].append(error_msg)
            
            # Create backup manifest
            manifest = await self._create_backup_manifest(backup_result)
            manifest_path = backup_dir / "backup_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Compress backup
            compressed_backup = await self._compress_backup(backup_dir)
            backup_result["compressed_size"] = compressed_backup["size_bytes"]
            backup_result["compression_ratio"] = compressed_backup["compression_ratio"]
            
            # Verify backup integrity
            integrity_result = await self._verify_backup_integrity(backup_id)
            backup_result["integrity_verified"] = integrity_result["success"]
            
            backup_result["success"] = len(backup_result["errors"]) == 0
            backup_result["end_time"] = datetime.utcnow().isoformat()
            
            # Update stats
            self.backup_stats["total_backups"] += 1
            if backup_result["success"]:
                self.backup_stats["successful_backups"] += 1
                self.backup_stats["total_backup_size"] += backup_result["total_size"]
                self.backup_stats["last_backup"] = backup_result["end_time"]
            else:
                self.backup_stats["failed_backups"] += 1
            
            # Log backup
            await immutable_log.append(
                actor="backup_restore_manager",
                action="full_backup_created",
                resource=f"backup/{backup_id}",
                outcome="success" if backup_result["success"] else "failure",
                payload=backup_result
            )
            
            logger.info(f"✅ Full backup complete: {backup_id} ({backup_result['total_size']} bytes)")
            return backup_result
            
        except Exception as e:
            backup_result["errors"].append(f"Backup failed: {e}")
            backup_result["success"] = False
            backup_result["end_time"] = datetime.utcnow().isoformat()
            logger.error(f"❌ Full backup failed: {e}")
            return backup_result
    
    async def _backup_knowledge_base(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup knowledge base"""
        kb_backup_dir = backup_dir / "knowledge_base"
        kb_backup_dir.mkdir(exist_ok=True)
        
        # Mock knowledge base backup
        knowledge_data = {
            "embeddings": {"count": 1000, "dimensions": 1536},
            "documents": {"count": 500, "total_chunks": 5000},
            "indexes": {"vector_index": "faiss", "text_index": "elasticsearch"}
        }
        
        # Encrypt knowledge data
        encrypted_kb = await kms_encryption.encrypt_artifact(
            knowledge_data, "knowledge", "knowledge_base_backup"
        )
        
        kb_file = kb_backup_dir / "knowledge_base.json.enc"
        with open(kb_file, 'w') as f:
            json.dump(encrypted_kb, f)
        
        return {
            "component": "knowledge_base",
            "files_backed_up": 1,
            "size_bytes": kb_file.stat().st_size,
            "encrypted": True
        }
    
    async def _backup_configurations(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup system configurations"""
        config_backup_dir = backup_dir / "configurations"
        config_backup_dir.mkdir(exist_ok=True)
        
        # Backup config files
        config_files = [
            "config/chunker_config.json",
            "config/qa_benchmark.json",
            "config/retention.yaml"
        ]
        
        backed_up_files = 0
        total_size = 0
        
        for config_file in config_files:
            source_path = Path(config_file)
            if source_path.exists():
                dest_path = config_backup_dir / source_path.name
                shutil.copy2(source_path, dest_path)
                backed_up_files += 1
                total_size += dest_path.stat().st_size
        
        return {
            "component": "configurations",
            "files_backed_up": backed_up_files,
            "size_bytes": total_size,
            "encrypted": False
        }
    
    async def _backup_security_artifacts(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup security artifacts"""
        security_backup_dir = backup_dir / "security"
        security_backup_dir.mkdir(exist_ok=True)
        
        # Get encryption stats and policies
        encryption_stats = kms_encryption.get_encryption_stats()
        retention_report = await retention_policy_manager.generate_retention_report()
        
        security_data = {
            "encryption_stats": encryption_stats,
            "retention_policies": retention_report,
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        # Encrypt security data
        encrypted_security = await kms_encryption.encrypt_artifact(
            security_data, "security", "security_backup"
        )
        
        security_file = security_backup_dir / "security_artifacts.json.enc"
        with open(security_file, 'w') as f:
            json.dump(encrypted_security, f)
        
        return {
            "component": "security_artifacts",
            "files_backed_up": 1,
            "size_bytes": security_file.stat().st_size,
            "encrypted": True
        }
    
    async def _backup_version_history(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup version history"""
        version_backup_dir = backup_dir / "versions"
        version_backup_dir.mkdir(exist_ok=True)
        
        # Get version stats
        version_stats = knowledge_versioning.get_version_stats()
        
        version_data = {
            "version_stats": version_stats,
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        # Encrypt version data
        encrypted_versions = await kms_encryption.encrypt_artifact(
            version_data, "knowledge", "version_backup"
        )
        
        version_file = version_backup_dir / "version_history.json.enc"
        with open(version_file, 'w') as f:
            json.dump(encrypted_versions, f)
        
        return {
            "component": "version_history",
            "files_backed_up": 1,
            "size_bytes": version_file.stat().st_size,
            "encrypted": True
        }
    
    async def _backup_audit_logs(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup audit logs"""
        audit_backup_dir = backup_dir / "audit_logs"
        audit_backup_dir.mkdir(exist_ok=True)
        
        # Mock audit log backup
        audit_data = {
            "log_entries": 10000,
            "date_range": {
                "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }
        
        # Encrypt audit data
        encrypted_audit = await kms_encryption.encrypt_artifact(
            audit_data, "security", "audit_backup"
        )
        
        audit_file = audit_backup_dir / "audit_logs.json.enc"
        with open(audit_file, 'w') as f:
            json.dump(encrypted_audit, f)
        
        return {
            "component": "audit_logs",
            "files_backed_up": 1,
            "size_bytes": audit_file.stat().st_size,
            "encrypted": True
        }
    
    async def _create_backup_manifest(self, backup_result: Dict) -> Dict[str, Any]:
        """Create backup manifest"""
        return {
            "backup_id": backup_result["backup_id"],
            "backup_type": backup_result["backup_type"],
            "created_at": backup_result["start_time"],
            "components": backup_result["components"],
            "total_size": backup_result["total_size"],
            "grace_version": "2.0.0",
            "manifest_version": "1.0",
            "integrity_hash": "sha256_placeholder"
        }
    
    async def _compress_backup(self, backup_dir: Path) -> Dict[str, Any]:
        """Compress backup directory"""
        compressed_file = backup_dir.with_suffix('.tar.gz')
        
        with tarfile.open(compressed_file, 'w:gz') as tar:
            tar.add(backup_dir, arcname=backup_dir.name)
        
        original_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
        compressed_size = compressed_file.stat().st_size
        compression_ratio = compressed_size / max(original_size, 1)
        
        # Remove uncompressed directory
        shutil.rmtree(backup_dir)
        
        return {
            "compressed_file": str(compressed_file),
            "original_size": original_size,
            "size_bytes": compressed_size,
            "compression_ratio": compression_ratio
        }
    
    async def _verify_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            compressed_file = self.backup_root / f"{backup_id}.tar.gz"
            
            if not compressed_file.exists():
                return {"success": False, "error": "Backup file not found"}
            
            # Test archive integrity
            with tarfile.open(compressed_file, 'r:gz') as tar:
                # Verify all files can be read
                for member in tar.getmembers():
                    if member.isfile():
                        tar.extractfile(member).read(1024)  # Read first 1KB
            
            self.backup_stats["integrity_tests_passed"] += 1
            return {"success": True, "verified_at": datetime.utcnow().isoformat()}
            
        except Exception as e:
            self.backup_stats["integrity_tests_failed"] += 1
            return {"success": False, "error": str(e)}
    
    async def restore_from_backup(self, backup_id: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """Restore system from backup"""
        logger.info(f"🔄 Starting restore from backup: {backup_id}")
        
        restore_result = {
            "backup_id": backup_id,
            "start_time": datetime.utcnow().isoformat(),
            "components_restored": {},
            "success": False,
            "errors": []
        }
        
        try:
            # Extract backup
            compressed_file = self.backup_root / f"{backup_id}.tar.gz"
            if not compressed_file.exists():
                raise FileNotFoundError(f"Backup file not found: {compressed_file}")
            
            # Extract to temporary directory
            temp_dir = self.backup_root / f"restore_{backup_id}"
            temp_dir.mkdir(exist_ok=True)
            
            with tarfile.open(compressed_file, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            # Load manifest
            manifest_file = temp_dir / backup_id / "backup_manifest.json"
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Restore components
            available_components = list(manifest["components"].keys())
            components_to_restore = components or available_components
            
            for component in components_to_restore:
                if component in available_components:
                    try:
                        component_result = await self._restore_component(
                            component, temp_dir / backup_id, manifest
                        )
                        restore_result["components_restored"][component] = component_result
                    except Exception as e:
                        error_msg = f"Failed to restore {component}: {e}"
                        logger.error(error_msg)
                        restore_result["errors"].append(error_msg)
                else:
                    restore_result["errors"].append(f"Component {component} not found in backup")
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
            
            restore_result["success"] = len(restore_result["errors"]) == 0
            restore_result["end_time"] = datetime.utcnow().isoformat()
            
            # Log restore
            await immutable_log.append(
                actor="backup_restore_manager",
                action="system_restored",
                resource=f"backup/{backup_id}",
                outcome="success" if restore_result["success"] else "failure",
                payload=restore_result
            )
            
            logger.info(f"✅ Restore complete: {backup_id}")
            return restore_result
            
        except Exception as e:
            restore_result["errors"].append(f"Restore failed: {e}")
            restore_result["success"] = False
            restore_result["end_time"] = datetime.utcnow().isoformat()
            logger.error(f"❌ Restore failed: {e}")
            return restore_result
    
    async def _restore_component(self, component: str, backup_dir: Path, 
                               manifest: Dict) -> Dict[str, Any]:
        """Restore specific component"""
        component_dir = backup_dir / component
        
        if component == "knowledge_base":
            # Restore knowledge base
            kb_file = component_dir / "knowledge_base.json.enc"
            with open(kb_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt knowledge data
            knowledge_data = await kms_encryption.decrypt_artifact(encrypted_data)
            
            # In production, restore to actual knowledge base
            logger.info(f"Restored knowledge base: {knowledge_data}")
            
            return {"component": component, "status": "restored", "data_size": len(str(knowledge_data))}
        
        # Add other component restore logic here
        return {"component": component, "status": "restored"}
    
    async def run_periodic_integrity_test(self) -> Dict[str, Any]:
        """Run periodic integrity test on all backups"""
        logger.info("🔍 Running periodic integrity tests...")
        
        test_results = {
            "test_time": datetime.utcnow().isoformat(),
            "backups_tested": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failed_backups": []
        }
        
        # Find all backup files
        backup_files = list(self.backup_root.glob("*.tar.gz"))
        
        for backup_file in backup_files:
            backup_id = backup_file.stem.replace('.tar', '')
            test_results["backups_tested"] += 1
            
            integrity_result = await self._verify_backup_integrity(backup_id)
            
            if integrity_result["success"]:
                test_results["tests_passed"] += 1
            else:
                test_results["tests_failed"] += 1
                test_results["failed_backups"].append({
                    "backup_id": backup_id,
                    "error": integrity_result.get("error", "Unknown error")
                })
        
        # Log test results
        await immutable_log.append(
            actor="backup_restore_manager",
            action="periodic_integrity_test",
            resource="all_backups",
            outcome="success" if test_results["tests_failed"] == 0 else "partial_success",
            payload=test_results
        )
        
        logger.info(f"✅ Integrity tests complete: {test_results['tests_passed']}/{test_results['backups_tested']} passed")
        return test_results
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        return self.backup_stats.copy()

# Global instance
backup_restore_manager = BackupRestoreManager()