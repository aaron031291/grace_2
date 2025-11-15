"""
RBAC Enforcer
Role-based access control for remote sessions
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class Role:
    """Role definition"""
    name: str
    permissions: List[str]
    description: str


class RBACEnforcer:
    """
    Role-Based Access Control
    Enforces least-privilege permissions for remote sessions
    """
    
    def __init__(self):
        # Define roles
        self.roles: Dict[str, Role] = {
            'observer': Role(
                name='observer',
                permissions=['read_logs', 'read_config', 'read_data', 'view_status'],
                description='Read-only monitoring access'
            ),
            'executor': Role(
                name='executor',
                permissions=['read_logs', 'read_config', 'read_data', 'execute_script', 'write_logs'],
                description='Execute pre-approved scripts'
            ),
            'developer': Role(
                name='developer',
                permissions=[
                    'read_logs', 'read_config', 'read_data', 'read_code',
                    'write_logs', 'write_data', 'write_code',
                    'execute', 'execute_script', 'modify_code',
                    'run_tests', 'view_status'
                ],
                description='Development access (no sudo)'
            ),
            'grace_sandbox': Role(
                name='grace_sandbox',
                permissions=['read_data', 'execute_script', 'write_logs', 'run_tests'],
                description='Grace autonomous learning in sandbox'
            ),
            'admin': Role(
                name='admin',
                permissions=[
                    'read_logs', 'read_config', 'read_data', 'read_code', 'read_secrets',
                    'write_logs', 'write_data', 'write_code', 'write_config',
                    'execute', 'execute_script', 'modify_code',
                    'install_package', 'manage_services', 'run_tests',
                    'view_status', 'manage_users'
                ],
                description='Full administrative access (no sudo)'
            )
        }
        
        # NEVER GRANTED PERMISSIONS (security-critical)
        self.blocked_permissions = [
            'sudo_escalation',
            'modify_kernel',
            'access_raw_secrets',
            'bypass_governance'
        ]
        
        # Device role assignments
        self.device_roles: Dict[str, str] = {}
        
        # Persistence
        self.storage_path = Path("databases/remote_access")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._load_state()
    
    def assign_role(
        self,
        device_id: str,
        role_name: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """
        Assign role to device
        
        Args:
            device_id: Device to assign role to
            role_name: Role to assign
            approved_by: Admin who approved
        
        Returns:
            Role assignment result
        """
        if role_name not in self.roles:
            return {'error': 'invalid_role', 'available_roles': list(self.roles.keys())}
        
        role = self.roles[role_name]
        self.device_roles[device_id] = role_name
        self._save_state()
        
        logger.info(f"[RBAC] ✅ Role assigned: {role_name} to {device_id} by {approved_by}")
        
        return {
            'device_id': device_id,
            'role': role_name,
            'permissions': role.permissions,
            'approved_by': approved_by
        }
    
    def check_permission(
        self,
        device_id: str,
        action: str,
        resource: str
    ) -> Dict[str, Any]:
        """
        Check if device has permission for action
        
        Args:
            device_id: Device requesting action
            action: Action to perform
            resource: Resource being accessed
        
        Returns:
            Permission check result
        """
        # Check if device has role assigned
        if device_id not in self.device_roles:
            logger.warning(f"[RBAC] 🚫 No role assigned for device: {device_id}")
            return {
                'allowed': False,
                'reason': 'no_role_assigned',
                'action': action,
                'resource': resource
            }
        
        role_name = self.device_roles[device_id]
        role = self.roles[role_name]
        
        # Check if action is blocked globally
        if action in self.blocked_permissions:
            logger.warning(f"[RBAC] 🚫 BLOCKED action attempted: {action} by {device_id}")
            return {
                'allowed': False,
                'reason': 'action_globally_blocked',
                'action': action,
                'resource': resource,
                'role': role_name
            }
        
        # Check if role has permission
        if action in role.permissions:
            logger.info(f"[RBAC] ✅ Permission granted: {action} for {device_id} (role: {role_name})")
            return {
                'allowed': True,
                'action': action,
                'resource': resource,
                'role': role_name
            }
        else:
            logger.warning(f"[RBAC] 🚫 Permission denied: {action} for {device_id} (role: {role_name})")
            return {
                'allowed': False,
                'reason': 'insufficient_permissions',
                'action': action,
                'resource': resource,
                'role': role_name,
                'required_permission': action
            }
    
    def get_role_permissions(self, role_name: str) -> Optional[List[str]]:
        """Get permissions for a role"""
        if role_name not in self.roles:
            return None
        return self.roles[role_name].permissions
    
    def get_device_role(self, device_id: str) -> Optional[str]:
        """Get role assigned to device"""
        return self.device_roles.get(device_id)
    
    def list_roles(self) -> List[Dict[str, Any]]:
        """List all available roles"""
        return [
            {
                'name': role.name,
                'permissions': role.permissions,
                'description': role.description
            }
            for role in self.roles.values()
        ]
    
    def _save_state(self):
        """Save state to disk"""
        state = {
            'device_roles': self.device_roles
        }
        state_file = self.storage_path / "rbac_state.json"
        state_file.write_text(json.dumps(state, indent=2))
    
    def _load_state(self):
        """Load state from disk"""
        state_file = self.storage_path / "rbac_state.json"
        if not state_file.exists():
            return
        
        try:
            state = json.loads(state_file.read_text())
            self.device_roles = state.get('device_roles', {})
            logger.info(f"[RBAC] Loaded {len(self.device_roles)} role assignments")
        except Exception as e:
            logger.error(f"[RBAC] Failed to load state: {e}")


# Global instance
rbac_enforcer = RBACEnforcer()
