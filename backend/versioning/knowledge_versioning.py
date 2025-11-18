"""
Knowledge Entry Versioning with Diff View
"""
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import difflib
import logging

from backend.security.kms_encryption import kms_encryption
from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeVersion:
    """Knowledge entry version"""
    version_id: str
    entry_id: str
    content: Dict[str, Any]
    author: str
    created_at: datetime
    change_summary: str
    parent_version: Optional[str] = None
    content_hash: str = ""
    size_bytes: int = 0

class KnowledgeVersioning:
    """Manage knowledge entry versions with diff view"""
    
    def __init__(self):
        self.versions = {}  # entry_id -> List[KnowledgeVersion]
        self.version_stats = {
            "total_versions": 0,
            "total_entries": 0,
            "storage_bytes": 0,
            "diffs_generated": 0
        }
    
    async def create_version(self, entry_id: str, content: Dict[str, Any], 
                           author: str, change_summary: str) -> KnowledgeVersion:
        """Create new version of knowledge entry"""
        # Get previous version
        previous_versions = self.versions.get(entry_id, [])
        parent_version = previous_versions[-1].version_id if previous_versions else None
        
        # Create version
        version_id = f"{entry_id}_v{len(previous_versions) + 1}_{int(datetime.utcnow().timestamp())}"
        content_json = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()
        
        version = KnowledgeVersion(
            version_id=version_id,
            entry_id=entry_id,
            content=content,
            author=author,
            created_at=datetime.utcnow(),
            change_summary=change_summary,
            parent_version=parent_version,
            content_hash=content_hash,
            size_bytes=len(content_json)
        )
        
        # Store version
        if entry_id not in self.versions:
            self.versions[entry_id] = []
            self.version_stats["total_entries"] += 1
        
        self.versions[entry_id].append(version)
        self.version_stats["total_versions"] += 1
        self.version_stats["storage_bytes"] += version.size_bytes
        
        # Encrypt and persist version
        await self._persist_version(version)
        
        # Log version creation
        await immutable_log.append(
            actor=author,
            action="knowledge_version_created",
            resource=f"knowledge/{entry_id}",
            outcome="success",
            payload={
                "version_id": version_id,
                "entry_id": entry_id,
                "change_summary": change_summary,
                "content_hash": content_hash,
                "size_bytes": version.size_bytes
            }
        )
        
        logger.info(f"Created version {version_id} for entry {entry_id}")
        return version
    
    async def get_version(self, entry_id: str, version_id: Optional[str] = None) -> Optional[KnowledgeVersion]:
        """Get specific version (latest if version_id not specified)"""
        versions = self.versions.get(entry_id, [])
        if not versions:
            return None
        
        if version_id:
            for version in versions:
                if version.version_id == version_id:
                    return version
            return None
        else:
            return versions[-1]  # Latest version
    
    async def get_version_history(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get version history for entry"""
        versions = self.versions.get(entry_id, [])
        
        history = []
        for version in versions:
            history.append({
                "version_id": version.version_id,
                "author": version.author,
                "created_at": version.created_at.isoformat(),
                "change_summary": version.change_summary,
                "content_hash": version.content_hash,
                "size_bytes": version.size_bytes,
                "parent_version": version.parent_version
            })
        
        return history
    
    async def generate_diff(self, entry_id: str, from_version: str, 
                          to_version: str) -> Dict[str, Any]:
        """Generate diff between two versions"""
        from_ver = await self.get_version(entry_id, from_version)
        to_ver = await self.get_version(entry_id, to_version)
        
        if not from_ver or not to_ver:
            raise ValueError("One or both versions not found")
        
        # Convert content to formatted strings for diffing
        from_content = json.dumps(from_ver.content, indent=2, sort_keys=True)
        to_content = json.dumps(to_ver.content, indent=2, sort_keys=True)
        
        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            from_content.splitlines(keepends=True),
            to_content.splitlines(keepends=True),
            fromfile=f"{entry_id} ({from_version})",
            tofile=f"{entry_id} ({to_version})",
            lineterm=""
        ))
        
        # Parse diff for structured output
        additions = []
        deletions = []
        modifications = []
        
        for line in diff_lines:
            if line.startswith('+') and not line.startswith('+++'):
                additions.append(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                deletions.append(line[1:].strip())
        
        # Calculate diff stats
        diff_stats = {
            "lines_added": len(additions),
            "lines_removed": len(deletions),
            "total_changes": len(additions) + len(deletions)
        }
        
        diff_result = {
            "entry_id": entry_id,
            "from_version": from_version,
            "to_version": to_version,
            "from_author": from_ver.author,
            "to_author": to_ver.author,
            "from_date": from_ver.created_at.isoformat(),
            "to_date": to_ver.created_at.isoformat(),
            "unified_diff": "".join(diff_lines),
            "structured_diff": {
                "additions": additions,
                "deletions": deletions,
                "modifications": modifications
            },
            "stats": diff_stats,
            "change_summary": to_ver.change_summary
        }
        
        self.version_stats["diffs_generated"] += 1
        
        # Log diff generation
        await immutable_log.append(
            actor="knowledge_versioning",
            action="diff_generated",
            resource=f"knowledge/{entry_id}",
            outcome="success",
            payload={
                "from_version": from_version,
                "to_version": to_version,
                "total_changes": diff_stats["total_changes"]
            }
        )
        
        return diff_result
    
    async def rollback_to_version(self, entry_id: str, target_version: str, 
                                author: str, reason: str) -> KnowledgeVersion:
        """Rollback entry to specific version"""
        target_ver = await self.get_version(entry_id, target_version)
        if not target_ver:
            raise ValueError(f"Target version {target_version} not found")
        
        # Create new version with rolled-back content
        rollback_version = await self.create_version(
            entry_id=entry_id,
            content=target_ver.content.copy(),
            author=author,
            change_summary=f"Rollback to {target_version}: {reason}"
        )
        
        # Log rollback
        await immutable_log.append(
            actor=author,
            action="knowledge_rollback",
            resource=f"knowledge/{entry_id}",
            outcome="success",
            payload={
                "target_version": target_version,
                "new_version": rollback_version.version_id,
                "reason": reason
            }
        )
        
        return rollback_version
    
    async def _persist_version(self, version: KnowledgeVersion):
        """Persist version with encryption"""
        # Encrypt version data
        encrypted_version = await kms_encryption.encrypt_artifact(
            data={
                "version_id": version.version_id,
                "entry_id": version.entry_id,
                "content": version.content,
                "author": version.author,
                "created_at": version.created_at.isoformat(),
                "change_summary": version.change_summary,
                "parent_version": version.parent_version,
                "content_hash": version.content_hash,
                "size_bytes": version.size_bytes
            },
            domain="knowledge",
            artifact_type="version",
            metadata={
                "entry_id": version.entry_id,
                "version_id": version.version_id,
                "author": version.author
            }
        )
        
        # In production, save to persistent storage
        # For demo, just log the encryption
        logger.debug(f"Persisted encrypted version {version.version_id}")
    
    def get_version_stats(self) -> Dict[str, Any]:
        """Get versioning statistics"""
        return self.version_stats.copy()
    
    async def cleanup_old_versions(self, entry_id: str, keep_versions: int = 10) -> int:
        """Cleanup old versions, keeping only the most recent N"""
        versions = self.versions.get(entry_id, [])
        if len(versions) <= keep_versions:
            return 0
        
        # Keep the most recent versions
        versions_to_remove = versions[:-keep_versions]
        self.versions[entry_id] = versions[-keep_versions:]
        
        # Update stats
        removed_bytes = sum(v.size_bytes for v in versions_to_remove)
        self.version_stats["storage_bytes"] -= removed_bytes
        self.version_stats["total_versions"] -= len(versions_to_remove)
        
        # Log cleanup
        await immutable_log.append(
            actor="knowledge_versioning",
            action="versions_cleaned",
            resource=f"knowledge/{entry_id}",
            outcome="success",
            payload={
                "versions_removed": len(versions_to_remove),
                "bytes_freed": removed_bytes,
                "versions_kept": keep_versions
            }
        )
        
        return len(versions_to_remove)

# Global instance
knowledge_versioning = KnowledgeVersioning()