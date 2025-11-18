"""
Permission Checker - Check user permissions
"""

from typing import Optional
from .models import PermissionAction, PermissionResource
from .rbac_manager import RBACManager


class PermissionChecker:
    """Check if user has permission"""
    
    def __init__(self, rbac_manager: RBACManager):
        self.rbac = rbac_manager
    
    def check_permission(
        self,
        user_id: str,
        tenant_id: str,
        resource: PermissionResource,
        action: PermissionAction,
        resource_id: Optional[str] = None,
    ) -> bool:
        """Check if user has permission"""
        permissions = self.rbac.get_user_permissions(user_id, tenant_id)
        
        permission_str = f"{resource.value}:{action.value}"
        
        allowed = permission_str in permissions
        
        self.rbac.log_access(
            user_id=user_id,
            tenant_id=tenant_id,
            resource=resource,
            action=action,
            allowed=allowed,
            reason="Permission granted" if allowed else "Permission denied",
            resource_id=resource_id,
        )
        
        return allowed
    
    def require_permission(
        self,
        user_id: str,
        tenant_id: str,
        resource: PermissionResource,
        action: PermissionAction,
        resource_id: Optional[str] = None,
    ):
        """Require permission or raise exception"""
        if not self.check_permission(user_id, tenant_id, resource, action, resource_id):
            raise PermissionError(
                f"User {user_id} does not have permission to {action.value} {resource.value}"
            )
