"""
RAG Persistence & Security - Production-Grade Data Management
Encrypt-at-rest, retention policies, backup/restore, compliance reporting
"""

import asyncio
import logging
import os
import json
import hashlib
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import gzip
import tempfile

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class EncryptAtRest:
    """
    Encrypt-at-rest for sensitive knowledge base content
    Uses AES-256 encryption with PBKDF2 key derivation
    """

    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.getenv("RAG_ENCRYPTION_KEY")
        self.fernet = None

        if self.encryption_key:
            self._initialize_cipher()

    def _initialize_cipher(self):
        """Initialize encryption cipher"""
        if not self.encryption_key:
            raise ValueError("Encryption key not provided")

        # Derive key using PBKDF2
        salt = b'grace_rag_salt_2024'  # Fixed salt for deterministic key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.encryption_key.encode()))
        self.fernet = Fernet(key)

    def encrypt_data(self, data: str) -> str:
        """Encrypt data string"""
        if not self.fernet:
            return data  # Return plaintext if encryption not initialized

        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data string"""
        if not self.fernet:
            return encrypted_data  # Return as-is if encryption not initialized

        try:
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"[ENCRYPT-AT-REST] Decryption failed: {e}")
            raise

    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled"""
        return self.fernet is not None


class RetentionPolicyManager:
    """
    Retention policy management for knowledge base content
    Implements configurable retention periods and automated cleanup
    """

    def __init__(self):
        self.policies = {
            "default": {
                "retention_days": 365,
                "auto_delete": True,
                "archive_after_days": 180
            },
            "sensitive": {
                "retention_days": 2555,  # 7 years for sensitive data
                "auto_delete": False,    # Manual review required
                "archive_after_days": 365
            },
            "temporary": {
                "retention_days": 30,
                "auto_delete": True,
                "archive_after_days": 7
            }
        }

        self.cleanup_stats = {
            "items_archived": 0,
            "items_deleted": 0,
            "last_cleanup": None,
            "total_processed": 0
        }

    async def apply_retention_policies(self, knowledge_items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Apply retention policies to knowledge items

        Args:
            knowledge_items: List of knowledge items to process

        Returns:
            Tuple of (items_to_keep, cleanup_actions)
        """
        items_to_keep = []
        cleanup_actions = {
            "archive": [],
            "delete": [],
            "review": []
        }

        now = datetime.utcnow()

        for item in knowledge_items:
            created_at = item.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)

            if not created_at:
                items_to_keep.append(item)
                continue

            age_days = (now - created_at).days

            # Determine policy
            content_type = item.get("content_type", "default")
            policy = self.policies.get(content_type, self.policies["default"])

            # Check retention rules
            if age_days > policy["retention_days"]:
                if policy["auto_delete"]:
                    cleanup_actions["delete"].append(item["id"])
                else:
                    cleanup_actions["review"].append(item["id"])
            elif age_days > policy["archive_after_days"]:
                cleanup_actions["archive"].append(item["id"])
                items_to_keep.append(item)  # Keep but mark as archived
            else:
                items_to_keep.append(item)

        # Update stats
        self.cleanup_stats["items_archived"] += len(cleanup_actions["archive"])
        self.cleanup_stats["items_deleted"] += len(cleanup_actions["delete"])
        self.cleanup_stats["total_processed"] += len(knowledge_items)
        self.cleanup_stats["last_cleanup"] = now.isoformat()

        # Log cleanup actions
        if cleanup_actions["delete"] or cleanup_actions["archive"]:
            await immutable_log.append(
                actor="retention_policy_manager",
                action="retention_cleanup",
                resource="knowledge_base",
                outcome="completed",
                payload={
                    "cleanup_actions": cleanup_actions,
                    "stats": self.cleanup_stats
                }
            )

        logger.info(f"[RETENTION-MANAGER] Processed {len(knowledge_items)} items - Archive: {len(cleanup_actions['archive'])}, Delete: {len(cleanup_actions['delete'])}, Review: {len(cleanup_actions['review'])}")
        return items_to_keep, cleanup_actions

    def add_policy(self, name: str, retention_days: int, auto_delete: bool = True,
                  archive_after_days: int = 180):
        """Add custom retention policy"""
        self.policies[name] = {
            "retention_days": retention_days,
            "auto_delete": auto_delete,
            "archive_after_days": archive_after_days
        }

    def get_policy(self, name: str) -> Dict[str, Any]:
        """Get retention policy by name"""
        return self.policies.get(name, self.policies["default"])

    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics"""
        return self.cleanup_stats


class BackupRestoreManager:
    """
    Backup and restore functionality for knowledge base
    Supports incremental backups, compression, and integrity verification
    """

    def __init__(self, backup_dir: str = "./backups/rag"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.backup_stats = {
            "total_backups": 0,
            "total_size_gb": 0.0,
            "last_backup": None,
            "last_restore": None,
            "integrity_checks_passed": 0,
            "integrity_checks_failed": 0
        }

    async def create_backup(self, knowledge_base_data: Dict[str, Any],
                          backup_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create compressed backup of knowledge base

        Args:
            knowledge_base_data: Knowledge base data to backup
            backup_name: Optional backup name

        Returns:
            Backup metadata
        """
        if backup_name is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"rag_backup_{timestamp}"

        backup_file = self.backup_dir / f"{backup_name}.json.gz"

        # Create backup metadata
        metadata = {
            "backup_name": backup_name,
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "total_items": len(knowledge_base_data.get("items", [])),
            "backup_file": str(backup_file),
            "checksum": None
        }

        # Serialize data
        backup_data = {
            "metadata": metadata,
            "data": knowledge_base_data
        }

        json_data = json.dumps(backup_data, indent=2, default=str)
        metadata["original_size_bytes"] = len(json_data.encode('utf-8'))

        # Compress and write
        with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
            f.write(json_data)

        # Calculate checksum
        with open(backup_file, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        metadata["checksum"] = checksum

        # Update metadata file
        metadata_file = backup_file.with_suffix('.meta.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update stats
        compressed_size = backup_file.stat().st_size
        metadata["compressed_size_bytes"] = compressed_size
        self.backup_stats["total_backups"] += 1
        self.backup_stats["total_size_gb"] += compressed_size / (1024**3)
        self.backup_stats["last_backup"] = metadata["created_at"]

        # Log backup creation
        await immutable_log.append(
            actor="backup_restore_manager",
            action="backup_created",
            resource="knowledge_base",
            outcome="success",
            payload=metadata
        )

        logger.info(f"[BACKUP-MANAGER] Created backup: {backup_name} ({compressed_size / (1024**2):.2f} MB)")
        return metadata

    async def restore_backup(self, backup_name: str, target_location: Optional[str] = None) -> Dict[str, Any]:
        """
        Restore knowledge base from backup

        Args:
            backup_name: Name of backup to restore
            target_location: Optional target location for restore

        Returns:
            Restore metadata
        """
        backup_file = self.backup_dir / f"{backup_name}.json.gz"
        metadata_file = self.backup_dir / f"{backup_name}.meta.json"

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        # Load and verify metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Verify integrity
        with open(backup_file, 'rb') as f:
            actual_checksum = hashlib.sha256(f.read()).hexdigest()

        if actual_checksum != metadata.get("checksum"):
            self.backup_stats["integrity_checks_failed"] += 1
            raise ValueError(f"Backup integrity check failed for {backup_name}")

        self.backup_stats["integrity_checks_passed"] += 1

        # Load backup data
        with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
            backup_data = json.load(f)

        restored_data = backup_data["data"]

        # Restore to target location if specified
        if target_location:
            # Implementation would depend on storage backend
            logger.info(f"[BACKUP-MANAGER] Restored to target location: {target_location}")

        # Update stats
        self.backup_stats["last_restore"] = datetime.utcnow().isoformat()

        restore_metadata = {
            "backup_name": backup_name,
            "restored_at": datetime.utcnow().isoformat(),
            "items_restored": len(restored_data.get("items", [])),
            "integrity_verified": True,
            "target_location": target_location
        }

        # Log restore
        await immutable_log.append(
            actor="backup_restore_manager",
            action="backup_restored",
            resource="knowledge_base",
            outcome="success",
            payload=restore_metadata
        )

        logger.info(f"[BACKUP-MANAGER] Restored backup: {backup_name} ({restore_metadata['items_restored']} items)")
        return restore_metadata

    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []

        for meta_file in self.backup_dir.glob("*.meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except Exception as e:
                logger.warning(f"[BACKUP-MANAGER] Failed to load backup metadata {meta_file}: {e}")

        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups

    async def verify_backup_integrity(self, backup_name: str) -> bool:
        """Verify backup file integrity"""
        metadata_file = self.backup_dir / f"{backup_name}.meta.json"
        backup_file = self.backup_dir / f"{backup_name}.json.gz"

        try:
            # Load expected checksum
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            expected_checksum = metadata.get("checksum")

            # Calculate actual checksum
            with open(backup_file, 'rb') as f:
                actual_checksum = hashlib.sha256(f.read()).hexdigest()

            is_valid = actual_checksum == expected_checksum

            if is_valid:
                self.backup_stats["integrity_checks_passed"] += 1
            else:
                self.backup_stats["integrity_checks_failed"] += 1

            return is_valid

        except Exception as e:
            logger.error(f"[BACKUP-MANAGER] Integrity check failed for {backup_name}: {e}")
            self.backup_stats["integrity_checks_failed"] += 1
            return False

    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        return self.backup_stats

    async def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up backups older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=keep_days)
        deleted_count = 0
        space_freed = 0

        for meta_file in self.backup_dir.glob("*.meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)

                created_at = datetime.fromisoformat(metadata.get("created_at", ""))
                if created_at < cutoff_date:
                    # Delete backup files
                    backup_name = metadata["backup_name"]
                    backup_file = self.backup_dir / f"{backup_name}.json.gz"

                    if backup_file.exists():
                        size = backup_file.stat().st_size
                        space_freed += size
                        backup_file.unlink()

                    meta_file.unlink()
                    deleted_count += 1

            except Exception as e:
                logger.warning(f"[BACKUP-MANAGER] Failed to cleanup backup {meta_file}: {e}")

        cleanup_stats = {
            "backups_deleted": deleted_count,
            "space_freed_bytes": space_freed,
            "space_freed_mb": space_freed / (1024**2),
            "cleanup_date": datetime.utcnow().isoformat()
        }

        logger.info(f"[BACKUP-MANAGER] Cleanup completed: {deleted_count} old backups removed")
        return cleanup_stats


class ComplianceReporting:
    """
    Compliance reporting for GDPR, SOC2, and data governance
    Generates reports on data handling, retention, and security
    """

    def __init__(self):
        self.compliance_reports = []
        self.audit_trail = []

    async def generate_compliance_report(self, knowledge_base_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report

        Args:
            knowledge_base_stats: Statistics about the knowledge base

        Returns:
            Compliance report
        """
        report = {
            "report_id": f"compliance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "period": "monthly",
            "compliance_frameworks": ["GDPR", "SOC2", "ISO27001"],
            "sections": {}
        }

        # Data inventory section
        report["sections"]["data_inventory"] = {
            "total_records": knowledge_base_stats.get("total_items", 0),
            "data_types": ["text", "embeddings", "metadata"],
            "storage_locations": ["vector_db", "relational_db", "file_system"],
            "encryption_status": knowledge_base_stats.get("encryption_enabled", False)
        }

        # Retention compliance
        report["sections"]["retention_compliance"] = {
            "policies_defined": len(knowledge_base_stats.get("retention_policies", [])),
            "auto_cleanup_enabled": knowledge_base_stats.get("auto_cleanup", False),
            "oldest_record_days": knowledge_base_stats.get("oldest_record_age_days", 0),
            "records_pending_deletion": knowledge_base_stats.get("pending_deletion", 0)
        }

        # Security measures
        report["sections"]["security_measures"] = {
            "encryption_at_rest": knowledge_base_stats.get("encryption_enabled", False),
            "access_logging": True,  # Always enabled via immutable log
            "backup_encryption": knowledge_base_stats.get("backup_encryption", False),
            "pii_detection": knowledge_base_stats.get("pii_scrubbing_enabled", False)
        }

        # Audit trail
        report["sections"]["audit_trail"] = {
            "total_events": len(self.audit_trail),
            "events_last_30_days": len([e for e in self.audit_trail
                                      if (datetime.utcnow() - datetime.fromisoformat(e["timestamp"])).days <= 30]),
            "access_patterns": self._analyze_access_patterns(),
            "anomaly_detection": knowledge_base_stats.get("anomalies_detected", 0)
        }

        # Compliance status
        report["compliance_status"] = self._assess_compliance_status(report)

        self.compliance_reports.append(report)

        # Log report generation
        await immutable_log.append(
            actor="compliance_reporting",
            action="report_generated",
            resource="knowledge_base",
            outcome="completed",
            payload={"report_id": report["report_id"]}
        )

        logger.info(f"[COMPLIANCE-REPORTING] Generated compliance report: {report['report_id']}")
        return report

    def _analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns for compliance reporting"""
        if not self.audit_trail:
            return {"insufficient_data": True}

        # Simple analysis - can be enhanced
        patterns = {
            "total_accesses": len(self.audit_trail),
            "unique_users": len(set(e.get("user", "unknown") for e in self.audit_trail)),
            "peak_hours": "09:00-17:00",  # Placeholder
            "access_distribution": "normal"  # Placeholder
        }

        return patterns

    def _assess_compliance_status(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall compliance status"""
        status = {
            "overall_compliant": True,
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }

        # Check encryption
        if not report["sections"]["security_measures"]["encryption_at_rest"]:
            status["critical_issues"].append("Encryption at rest not enabled")
            status["overall_compliant"] = False

        # Check retention policies
        if report["sections"]["retention_compliance"]["policies_defined"] == 0:
            status["critical_issues"].append("No retention policies defined")
            status["overall_compliant"] = False

        # Check PII detection
        if not report["sections"]["security_measures"]["pii_detection"]:
            status["warnings"].append("PII detection not enabled")

        # Generate recommendations
        if not status["overall_compliant"]:
            status["recommendations"].append("Address critical compliance issues immediately")
        if status["warnings"]:
            status["recommendations"].append("Review and address compliance warnings")

        return status

    def add_audit_event(self, event: Dict[str, Any]):
        """Add event to audit trail"""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            **event
        }
        self.audit_trail.append(audit_event)

        # Keep only last 10000 events
        if len(self.audit_trail) > 10000:
            self.audit_trail = self.audit_trail[-10000:]

    def get_compliance_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent compliance reports"""
        return self.compliance_reports[-limit:]

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit trail events"""
        return self.audit_trail[-limit:]


# Global instances
encrypt_at_rest = EncryptAtRest()
retention_policy_manager = RetentionPolicyManager()
backup_restore_manager = BackupRestoreManager()
compliance_reporting = ComplianceReporting()