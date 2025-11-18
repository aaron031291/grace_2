"""
RBAC Models
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field


class PermissionAction(str, Enum):
    """Permission actions"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"


class PermissionResource(str, Enum):
    """Permission resources"""
    TENANT = "tenant"
    USER = "user"
    ROLE = "role"
    PRODUCT = "product"
    BILLING = "billing"
    API_KEY = "api_key"
    MISSION = "mission"
    LEARNING = "learning"
    GOVERNANCE = "governance"
    SYSTEM = "system"


class Permission(BaseModel):
    """Permission model"""
    permission_id: str
    name: str
    description: str
    
    resource: PermissionResource
    action: PermissionAction
    
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Role(BaseModel):
    """Role model"""
    role_id: str
    name: str
    description: str
    
    permissions: Set[str] = Field(default_factory=set)  # Set of permission_ids
    
    parent_role_id: Optional[str] = None
    inherits_permissions: bool = True
    
    # Metadata
    is_system_role: bool = False  # System roles cannot be deleted
    tenant_id: Optional[str] = None  # None = global role
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    """User model (simplified for RBAC)"""
    user_id: str
    email: str
    name: str
    tenant_id: str
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RoleAssignment(BaseModel):
    """Role assignment to user"""
    assignment_id: str
    user_id: str
    role_id: str
    tenant_id: str
    
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    
    assigned_by: Optional[str] = None
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class AccessLog(BaseModel):
    """Access audit log"""
    log_id: str
    user_id: str
    tenant_id: str
    
    resource: PermissionResource
    action: PermissionAction
    resource_id: Optional[str] = None
    
    allowed: bool
    reason: Optional[str] = None
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
