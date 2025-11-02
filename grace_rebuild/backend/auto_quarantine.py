"""Auto-quarantine system for malicious files"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from .governance import governance_engine
from .immutable_log import append_to_log


class QuarantineManager:
    """Manage file quarantine and restoration"""
    
    def __init__(self, quarantine_dir: str = ".quarantine"):
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(exist_ok=True)
        self.manifest_path = self.quarantine_dir / "manifest.json"
        self._load_manifest()
    
    def _load_manifest(self):
        """Load quarantine manifest"""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {}
            self._save_manifest()
    
    def _save_manifest(self):
        """Save quarantine manifest"""
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    async def quarantine_file(self, file_path: str, reason: str, actor: str = "system") -> Dict[str, Any]:
        """Move file to quarantine directory"""
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Generate quarantine ID
            quarantine_id = f"Q{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{source_path.name}"
            quarantine_path = self.quarantine_dir / quarantine_id
            
            # Copy file to quarantine (keep original temporarily)
            shutil.copy2(source_path, quarantine_path)
            
            # Store metadata
            self.manifest[quarantine_id] = {
                'original_path': str(source_path.absolute()),
                'quarantine_path': str(quarantine_path.absolute()),
                'reason': reason,
                'actor': actor,
                'quarantined_at': datetime.utcnow().isoformat(),
                'status': 'quarantined',
                'file_size': source_path.stat().st_size,
                'file_hash': self._calculate_hash(source_path),
            }
            self._save_manifest()
            
            # Remove original file
            source_path.unlink()
            
            # Log to audit trail
            await append_to_log(
                actor=actor,
                action="file_quarantine",
                resource=file_path,
                result="success",
                details=json.dumps({
                    'quarantine_id': quarantine_id,
                    'reason': reason
                })
            )
            
            return {
                'success': True,
                'quarantine_id': quarantine_id,
                'quarantine_path': str(quarantine_path),
                'reason': reason
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_quarantined(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all quarantined files"""
        results = []
        
        for q_id, metadata in self.manifest.items():
            if status is None or metadata.get('status') == status:
                results.append({
                    'quarantine_id': q_id,
                    **metadata
                })
        
        return sorted(results, key=lambda x: x['quarantined_at'], reverse=True)
    
    async def restore_file(self, quarantine_id: str, actor: str) -> Dict[str, Any]:
        """Restore quarantined file with governance approval"""
        try:
            if quarantine_id not in self.manifest:
                return {
                    'success': False,
                    'error': 'Quarantine ID not found'
                }
            
            metadata = self.manifest[quarantine_id]
            
            # Check governance approval
            decision = await governance_engine.check(
                actor=actor,
                action="restore_quarantined_file",
                resource=quarantine_id,
                payload={'original_path': metadata['original_path']}
            )
            
            if decision['decision'] == 'block':
                return {
                    'success': False,
                    'error': f"Blocked by governance: {decision['policy']}"
                }
            
            if decision['decision'] == 'review':
                return {
                    'success': False,
                    'requires_approval': True,
                    'approval_request_id': decision.get('audit_id'),
                    'message': 'Restoration requires manual approval'
                }
            
            # Restore file
            quarantine_path = Path(metadata['quarantine_path'])
            original_path = Path(metadata['original_path'])
            
            # Check if destination already exists
            if original_path.exists():
                return {
                    'success': False,
                    'error': 'Destination file already exists'
                }
            
            # Create parent directories if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore file
            shutil.copy2(quarantine_path, original_path)
            
            # Update manifest
            metadata['status'] = 'restored'
            metadata['restored_at'] = datetime.utcnow().isoformat()
            metadata['restored_by'] = actor
            self._save_manifest()
            
            # Log action
            await append_to_log(
                actor=actor,
                action="file_restore",
                resource=quarantine_id,
                result="success",
                details=json.dumps({
                    'restored_to': str(original_path),
                    'governance_decision': decision['decision']
                })
            )
            
            return {
                'success': True,
                'restored_to': str(original_path),
                'quarantine_id': quarantine_id
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_quarantined(self, quarantine_id: str, actor: str) -> Dict[str, Any]:
        """Permanently delete quarantined file"""
        try:
            if quarantine_id not in self.manifest:
                return {
                    'success': False,
                    'error': 'Quarantine ID not found'
                }
            
            metadata = self.manifest[quarantine_id]
            
            # Check governance approval for deletion
            decision = await governance_engine.check(
                actor=actor,
                action="delete_quarantined_file",
                resource=quarantine_id,
                payload={'original_path': metadata['original_path']}
            )
            
            if decision['decision'] == 'block':
                return {
                    'success': False,
                    'error': f"Blocked by governance: {decision['policy']}"
                }
            
            if decision['decision'] == 'review':
                return {
                    'success': False,
                    'requires_approval': True,
                    'message': 'Deletion requires manual approval'
                }
            
            # Delete file
            quarantine_path = Path(metadata['quarantine_path'])
            if quarantine_path.exists():
                quarantine_path.unlink()
            
            # Update manifest
            metadata['status'] = 'deleted'
            metadata['deleted_at'] = datetime.utcnow().isoformat()
            metadata['deleted_by'] = actor
            self._save_manifest()
            
            # Log action
            await append_to_log(
                actor=actor,
                action="file_delete_quarantine",
                resource=quarantine_id,
                result="success",
                details=json.dumps({
                    'original_path': metadata['original_path'],
                    'governance_decision': decision['decision']
                })
            )
            
            return {
                'success': True,
                'quarantine_id': quarantine_id,
                'status': 'deleted'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_quarantine_info(self, quarantine_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a quarantined file"""
        if quarantine_id not in self.manifest:
            return None
        
        return {
            'quarantine_id': quarantine_id,
            **self.manifest[quarantine_id]
        }
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        import hashlib
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        
        return sha256.hexdigest()


quarantine_manager = QuarantineManager()
