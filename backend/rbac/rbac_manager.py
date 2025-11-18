"""
RBAC Manager - Role and permission management
"""

import secrets
from datetime import datetime
from typing import Dict, List, Optional, Set
from .models import (
    Role, Permission, User, RoleAssignment, AccessLog,
    PermissionAction, PermissionResource
)


class RBACManager:
    """Manage roles, permissions, and assignments"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.users: Dict[str, User] = {}
        self.assignments: Dict[str, RoleAssignment] = {}
        self.access_logs: List[AccessLog] = []
        
        self._create_system_roles()
        self._create_system_permissions()
    
    def _create_system_permissions(self):
        """Create system permissions"""
        permissions = [
            ("tenant:create", "Create tenants", PermissionResource.TENANT, PermissionAction.CREATE),
            ("tenant:read", "Read tenant data", PermissionResource.TENANT, PermissionAction.READ),
            ("tenant:update", "Update tenant settings", PermissionResource.TENANT, PermissionAction.UPDATE),
            ("tenant:delete", "Delete tenants", PermissionResource.TENANT, PermissionAction.DELETE),
            ("tenant:manage", "Manage tenant", PermissionResource.TENANT, PermissionAction.MANAGE),
            
            ("user:create", "Create users", PermissionResource.USER, PermissionAction.CREATE),
            ("user:read", "Read user data", PermissionResource.USER, PermissionAction.READ),
            ("user:update", "Update users", PermissionResource.USER, PermissionAction.UPDATE),
            ("user:delete", "Delete users", PermissionResource.USER, PermissionAction.DELETE),
            
            ("role:create", "Create roles", PermissionResource.ROLE, PermissionAction.CREATE),
            ("role:read", "Read roles", PermissionResource.ROLE, PermissionAction.READ),
            ("role:update", "Update roles", PermissionResource.ROLE, PermissionAction.UPDATE),
            ("role:delete", "Delete roles", PermissionResource.ROLE, PermissionAction.DELETE),
            
            ("product:create", "Create products", PermissionResource.PRODUCT, PermissionAction.CREATE),
            ("product:read", "Read products", PermissionResource.PRODUCT, PermissionAction.READ),
            ("product:update", "Update products", PermissionResource.PRODUCT, PermissionAction.UPDATE),
            ("product:delete", "Delete products", PermissionResource.PRODUCT, PermissionAction.DELETE),
            
            ("billing:read", "Read billing data", PermissionResource.BILLING, PermissionAction.READ),
            ("billing:manage", "Manage billing", PermissionResource.BILLING, PermissionAction.MANAGE),
            
            ("api_key:create", "Create API keys", PermissionResource.API_KEY, PermissionAction.CREATE),
            ("api_key:read", "Read API keys", PermissionResource.API_KEY, PermissionAction.READ),
            ("api_key:delete", "Delete API keys", PermissionResource.API_KEY, PermissionAction.DELETE),
            
            ("mission:create", "Create missions", PermissionResource.MISSION, PermissionAction.CREATE),
            ("mission:read", "Read missions", PermissionResource.MISSION, PermissionAction.READ),
            ("mission:execute", "Execute missions", PermissionResource.MISSION, PermissionAction.EXECUTE),
            
            ("system:manage", "Manage system", PermissionResource.SYSTEM, PermissionAction.MANAGE),
        ]
        
        for perm_id, name, resource, action in permissions:
            self.permissions[perm_id] = Permission(
                permission_id=perm_id,
                name=name,
                description=f"{action.value.capitalize()} {resource.value}",
                resource=resource,
                action=action,
            )
    
    def _create_system_roles(self):
        """Create system roles"""
        owner_perms = set(self.permissions.keys()) if self.permissions else set()
        self.roles["owner"] = Role(
            role_id="owner",
            name="Owner",
            description="Full access to all resources",
            permissions=owner_perms,
            is_system_role=True,
        )
        
        admin_perms = {
            "tenant:read", "tenant:update",
            "user:create", "user:read", "user:update", "user:delete",
            "role:create", "role:read", "role:update",
            "product:create", "product:read", "product:update", "product:delete",
            "billing:read", "billing:manage",
            "api_key:create", "api_key:read", "api_key:delete",
            "mission:create", "mission:read", "mission:execute",
        }
        self.roles["admin"] = Role(
            role_id="admin",
            name="Admin",
            description="Administrative access",
            permissions=admin_perms,
            is_system_role=True,
        )
        
        developer_perms = {
            "product:create", "product:read", "product:update",
            "api_key:create", "api_key:read",
            "mission:create", "mission:read", "mission:execute",
        }
        self.roles["developer"] = Role(
            role_id="developer",
            name="Developer",
            description="Developer access",
            permissions=developer_perms,
            is_system_role=True,
        )
        
        viewer_perms = {
            "tenant:read", "user:read", "role:read",
            "product:read", "billing:read", "mission:read",
        }
        self.roles["viewer"] = Role(
            role_id="viewer",
            name="Viewer",
            description="Read-only access",
            permissions=viewer_perms,
            is_system_role=True,
        )
    
    def create_role(
        self,
        name: str,
        description: str,
        permissions: Optional[Set[str]] = None,
        parent_role_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Role:
        """Create a new role"""
        role_id = f"role_{secrets.token_urlsafe(16)}"
        
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions or set(),
            parent_role_id=parent_role_id,
            tenant_id=tenant_id,
        )
        
        self.roles[role_id] = role
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        return self.roles.get(role_id)
    
    def list_roles(self, tenant_id: Optional[str] = None) -> List[Role]:
        """List roles"""
        roles = list(self.roles.values())
        if tenant_id:
            roles = [r for r in roles if r.tenant_id == tenant_id or r.tenant_id is None]
        return roles
    
    def update_role(
        self,
        role_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[Set[str]] = None,
    ) -> Role:
        """Update role"""
        role = self.get_role(role_id)
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        
        if role.is_system_role:
            raise ValueError("Cannot modify system role")
        
        if name:
            role.name = name
        if description:
            role.description = description
        if permissions is not None:
            role.permissions = permissions
        
        role.updated_at = datetime.utcnow()
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """Delete role"""
        role = self.get_role(role_id)
        if not role:
            return False
        
        if role.is_system_role:
            raise ValueError("Cannot delete system role")
        
        del self.roles[role_id]
        return True
    
    def create_user(
        self,
        email: str,
        name: str,
        tenant_id: str,
    ) -> User:
        """Create a new user"""
        user_id = f"user_{secrets.token_urlsafe(16)}"
        
        user = User(
            user_id=user_id,
            email=email,
            name=name,
            tenant_id=tenant_id,
        )
        
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def assign_role(
        self,
        user_id: str,
        role_id: str,
        tenant_id: str,
        assigned_by: Optional[str] = None,
    ) -> RoleAssignment:
        """Assign role to user"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        role = self.get_role(role_id)
        if not role:
            raise ValueError(f"Role not found: {role_id}")
        
        assignment_id = f"assign_{secrets.token_urlsafe(16)}"
        
        assignment = RoleAssignment(
            assignment_id=assignment_id,
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            assigned_by=assigned_by,
        )
        
        self.assignments[assignment_id] = assignment
        return assignment
    
    def get_user_roles(self, user_id: str, tenant_id: str) -> List[Role]:
        """Get all roles for user"""
        assignments = [
            a for a in self.assignments.values()
            if a.user_id == user_id and a.tenant_id == tenant_id
        ]
        
        roles = []
        for assignment in assignments:
            role = self.get_role(assignment.role_id)
            if role:
                roles.append(role)
        
        return roles
    
    def get_user_permissions(self, user_id: str, tenant_id: str) -> Set[str]:
        """Get all permissions for user (including inherited)"""
        roles = self.get_user_roles(user_id, tenant_id)
        
        all_permissions = set()
        for role in roles:
            all_permissions.update(role.permissions)
            
            if role.inherits_permissions and role.parent_role_id:
                parent = self.get_role(role.parent_role_id)
                if parent:
                    all_permissions.update(parent.permissions)
        
        return all_permissions
    
    def log_access(
        self,
        user_id: str,
        tenant_id: str,
        resource: PermissionResource,
        action: PermissionAction,
        allowed: bool,
        reason: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        """Log access attempt"""
        log_id = f"log_{secrets.token_urlsafe(16)}"
        
        log = AccessLog(
            log_id=log_id,
            user_id=user_id,
            tenant_id=tenant_id,
            resource=resource,
            action=action,
            resource_id=resource_id,
            allowed=allowed,
            reason=reason,
        )
        
        self.access_logs.append(log)
    
    def get_access_logs(
        self,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AccessLog]:
        """Get access logs"""
        logs = self.access_logs
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        if tenant_id:
            logs = [l for l in logs if l.tenant_id == tenant_id]
        
        logs = sorted(logs, key=lambda l: l.timestamp, reverse=True)
        return logs[:limit]
