"""
Role-Based Access Control (RBAC) System
Manages roles, permissions, and access policies
"""

from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class Permission(str, Enum):
    """System permissions"""
    # Read permissions
    READ_KNOWLEDGE = "knowledge:read"
    READ_METRICS = "metrics:read"
    READ_CONFIG = "config:read"
    
    # Write permissions
    WRITE_KNOWLEDGE = "knowledge:write"
    WRITE_CONFIG = "config:write"
    APPROVE_GOVERNANCE = "governance:approve"
    
    # Execute permissions
    EXECUTE_PLAYBOOKS = "playbooks:execute"
    CREATE_CODING_TASKS = "coding:create"
    TRIGGER_LEARNING = "learning:trigger"
    
    # Admin permissions
    MANAGE_USERS = "users:manage"
    MANAGE_TENANTS = "tenants:manage"
    MANAGE_BILLING = "billing:manage"
    VIEW_AUDIT_LOGS = "audit:view"

@dataclass
class Role:
    """User role"""
    role_id: str
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[str] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has permission"""
        return permission in self.permissions

@dataclass
class User:
    """User account"""
    user_id: str
    email: str
    tenant_id: str
    roles: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class RBACSystem:
    """Role-Based Access Control system"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        
        # Initialize default roles
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Create default role hierarchy"""
        # Viewer - read-only
        self.roles["viewer"] = Role(
            role_id="viewer",
            name="Viewer",
            description="Read-only access",
            permissions={
                Permission.READ_KNOWLEDGE,
                Permission.READ_METRICS,
            }
        )
        
        # Developer - can execute and create
        self.roles["developer"] = Role(
            role_id="developer",
            name="Developer",
            description="Can execute playbooks and create tasks",
            permissions={
                Permission.READ_KNOWLEDGE,
                Permission.READ_METRICS,
                Permission.READ_CONFIG,
                Permission.EXECUTE_PLAYBOOKS,
                Permission.CREATE_CODING_TASKS,
                Permission.WRITE_KNOWLEDGE,
            }
        )
        
        # Approver - can approve governance
        self.roles["approver"] = Role(
            role_id="approver",
            name="Approver",
            description="Can approve governance decisions",
            permissions={
                Permission.READ_KNOWLEDGE,
                Permission.READ_METRICS,
                Permission.APPROVE_GOVERNANCE,
                Permission.VIEW_AUDIT_LOGS,
            }
        )
        
        # Admin - full access
        self.roles["admin"] = Role(
            role_id="admin",
            name="Administrator",
            description="Full system access",
            permissions={
                Permission.READ_KNOWLEDGE,
                Permission.READ_METRICS,
                Permission.READ_CONFIG,
                Permission.WRITE_KNOWLEDGE,
                Permission.WRITE_CONFIG,
                Permission.APPROVE_GOVERNANCE,
                Permission.EXECUTE_PLAYBOOKS,
                Permission.CREATE_CODING_TASKS,
                Permission.TRIGGER_LEARNING,
                Permission.MANAGE_USERS,
                Permission.MANAGE_TENANTS,
                Permission.MANAGE_BILLING,
                Permission.VIEW_AUDIT_LOGS,
            }
        )
    
    def create_user(
        self,
        email: str,
        tenant_id: str,
        roles: List[str]
    ) -> User:
        """Create a new user"""
        user_id = f"user_{email.split('@')[0]}_{datetime.now().strftime('%Y%m%d')}"
        
        user = User(
            user_id=user_id,
            email=email,
            tenant_id=tenant_id,
            roles=roles,
            created_at=datetime.now()
        )
        
        self.users[user_id] = user
        return user
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Check all user's roles
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role and role.has_permission(permission):
                return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        user = self.users.get(user_id)
        if not user:
            return set()
        
        permissions = set()
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                permissions.update(role.permissions)
        
        return permissions
    
    def assign_role(self, user_id: str, role_id: str):
        """Assign role to user"""
        user = self.users.get(user_id)
        if user and role_id not in user.roles:
            user.roles.append(role_id)
    
    def revoke_role(self, user_id: str, role_id: str):
        """Revoke role from user"""
        user = self.users.get(user_id)
        if user and role_id in user.roles:
            user.roles.remove(role_id)

# Global instance
_rbac_system: Optional[RBACSystem] = None

def get_rbac_system() -> RBACSystem:
    """Get global RBAC system"""
    global _rbac_system
    if _rbac_system is None:
        _rbac_system = RBACSystem()
    return _rbac_system
