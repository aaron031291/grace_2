"""
Role-Based Access Control (RBAC) System
Service account permissions for missions and operations

Features:
- Service accounts with scoped permissions
- Role-based access control
- Resource-level permissions
- Permission inheritance
- Audit trail for all checks
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Standard permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MODIFY = "modify"
    DEPLOY = "deploy"
    ADMIN = "admin"


class ServiceAccountRole(str, Enum):
    """Predefined service account roles"""
    LEARNING_MISSION = "learning_mission"  # For learning missions
    AGENT_PIPELINE = "agent_pipeline"  # For agent pipelines
    SELF_HEALING = "self_healing"  # For self-healing operations
    GUARDIAN = "guardian"  # Guardian has elevated permissions
    ADMIN = "admin"  # Full access
    READ_ONLY = "read_only"  # Read-only access


@dataclass
class ServiceAccount:
    """Service account with permissions"""
    
    account_id: str
    role: ServiceAccountRole
    permissions: Set[Permission] = field(default_factory=set)
    resource_scopes: Dict[str, List[str]] = field(default_factory=dict)  # resource_type -> [resource_ids]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'account_id': self.account_id,
            'role': self.role.value,
            'permissions': [p.value for p in self.permissions],
            'resource_scopes': self.resource_scopes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }


class RBACSystem:
    """
    Role-Based Access Control system
    
    Manages service accounts and permissions for all Grace operations
    """
    
    def __init__(self):
        self.running = False
        
        # Service accounts
        self.service_accounts: Dict[str, ServiceAccount] = {}
        
        # Role -> Permissions mapping
        self.role_permissions = {
            ServiceAccountRole.LEARNING_MISSION: {
                Permission.READ,  # Can read from resources
                Permission.WRITE  # Can write learned knowledge
            },
            ServiceAccountRole.AGENT_PIPELINE: {
                Permission.READ,
                Permission.WRITE,
                Permission.EXECUTE  # Can execute code
            },
            ServiceAccountRole.SELF_HEALING: {
                Permission.READ,
                Permission.WRITE,
                Permission.MODIFY  # Can modify configurations
            },
            ServiceAccountRole.GUARDIAN: {
                Permission.READ,
                Permission.WRITE,
                Permission.MODIFY,
                Permission.EXECUTE,
                Permission.DEPLOY  # Can deploy changes
            },
            ServiceAccountRole.ADMIN: {
                Permission.READ,
                Permission.WRITE,
                Permission.DELETE,
                Permission.MODIFY,
                Permission.EXECUTE,
                Permission.DEPLOY,
                Permission.ADMIN
            },
            ServiceAccountRole.READ_ONLY: {
                Permission.READ
            }
        }
        
        # Resource type -> Required permission mapping
        self.resource_permissions = {
            'production_db': Permission.ADMIN,  # Production DB needs admin
            'production_model': Permission.DEPLOY,  # Production models need deploy
            'staging_db': Permission.WRITE,
            'staging_model': Permission.WRITE,
            'vector_store': Permission.WRITE,
            'file_system': Permission.WRITE,
            'test_environment': Permission.READ
        }
        
        # Statistics
        self.stats = {
            'checks_performed': 0,
            'checks_allowed': 0,
            'checks_denied': 0
        }
        
        # Dependencies
        self.immutable_log = None
    
    async def start(self):
        """Start the RBAC system"""
        if self.running:
            return
        
        logger.info("[RBAC-SYSTEM] Starting RBAC system...")
        
        # Initialize dependencies
        try:
            from backend.core.immutable_log import immutable_log
            self.immutable_log = immutable_log
        except ImportError:
            logger.warning("[RBAC-SYSTEM] Immutable log not available")
        
        # Create default service accounts
        await self._create_default_accounts()
        
        self.running = True
        
        logger.info("[RBAC-SYSTEM] ✅ Started")
        logger.info(f"[RBAC-SYSTEM] Service accounts: {len(self.service_accounts)}")
    
    async def stop(self):
        """Stop the RBAC system"""
        self.running = False
        logger.info("[RBAC-SYSTEM] Stopped")
    
    async def _create_default_accounts(self):
        """Create default service accounts"""
        
        # Learning mission account
        await self.create_service_account(
            account_id='learning_mission_service',
            role=ServiceAccountRole.LEARNING_MISSION,
            resource_scopes={
                'vector_store': ['*'],  # All vector stores
                'staging_model': ['*'],  # All staging models
                'file_system': ['/grace_training/*']  # Training directory
            }
        )
        
        # Agent pipeline account
        await self.create_service_account(
            account_id='agent_pipeline_service',
            role=ServiceAccountRole.AGENT_PIPELINE,
            resource_scopes={
                'file_system': ['/backend/*', '/frontend/*'],
                'test_environment': ['*']
            }
        )
        
        # Self-healing account
        await self.create_service_account(
            account_id='self_healing_service',
            role=ServiceAccountRole.SELF_HEALING,
            resource_scopes={
                'staging_db': ['*'],
                'file_system': ['/config/*', '/logs/*']
            }
        )
        
        # Guardian account (elevated)
        await self.create_service_account(
            account_id='guardian_service',
            role=ServiceAccountRole.GUARDIAN,
            resource_scopes={
                '*': ['*']  # All resources
            }
        )
        
        logger.info(f"[RBAC-SYSTEM] Created {len(self.service_accounts)} default service accounts")
    
    async def create_service_account(
        self,
        account_id: str,
        role: ServiceAccountRole,
        resource_scopes: Optional[Dict[str, List[str]]] = None
    ) -> ServiceAccount:
        """
        Create a new service account
        
        Args:
            account_id: Unique account identifier
            role: Service account role
            resource_scopes: Optional resource scopes
            
        Returns:
            Created service account
        """
        
        if account_id in self.service_accounts:
            raise ValueError(f"Service account already exists: {account_id}")
        
        # Get permissions for role
        permissions = self.role_permissions.get(role, set())
        
        account = ServiceAccount(
            account_id=account_id,
            role=role,
            permissions=permissions,
            resource_scopes=resource_scopes or {}
        )
        
        self.service_accounts[account_id] = account
        
        logger.info(f"[RBAC-SYSTEM] Created service account: {account_id} (role: {role.value})")
        
        # Log to immutable log
        if self.immutable_log:
            await self.immutable_log.append_entry(
                category='rbac',
                subcategory='account_created',
                data=account.to_dict(),
                actor='rbac_system',
                action='create_service_account',
                resource=account_id
            )
        
        return account
    
    async def check_permission(
        self,
        principal: str,  # Service account ID
        resource_type: str,
        resource_id: str,
        action: str
    ) -> bool:
        """
        Check if principal has permission for action on resource
        
        Args:
            principal: Service account ID
            resource_type: Type of resource
            resource_id: Resource identifier
            action: Action to perform
            
        Returns:
            True if allowed, False if denied
        """
        
        self.stats['checks_performed'] += 1
        
        # Get service account
        account = self.service_accounts.get(principal)
        
        if not account:
            logger.warning(f"[RBAC-SYSTEM] Unknown service account: {principal}")
            self.stats['checks_denied'] += 1
            return False
        
        # Convert action to permission
        try:
            required_permission = Permission(action.lower())
        except ValueError:
            # Unknown action - deny
            logger.warning(f"[RBAC-SYSTEM] Unknown action: {action}")
            self.stats['checks_denied'] += 1
            return False
        
        # Check if account has required permission
        if required_permission not in account.permissions:
            # Check if account has ADMIN permission (grants all)
            if Permission.ADMIN not in account.permissions:
                logger.warning(
                    f"[RBAC-SYSTEM] Permission denied: {principal} lacks {required_permission.value}"
                )
                self.stats['checks_denied'] += 1
                
                # Log denial
                if self.immutable_log:
                    await self.immutable_log.append_entry(
                        category='rbac',
                        subcategory='permission_denied',
                        data={
                            'principal': principal,
                            'resource_type': resource_type,
                            'resource_id': resource_id,
                            'action': action,
                            'reason': f'Missing permission: {required_permission.value}'
                        },
                        actor=principal,
                        action='check_permission',
                        resource=f'{resource_type}:{resource_id}'
                    )
                
                return False
        
        # Check resource-specific permission
        resource_required_perm = self.resource_permissions.get(resource_type)
        
        if resource_required_perm:
            if resource_required_perm not in account.permissions:
                if Permission.ADMIN not in account.permissions:
                    logger.warning(
                        f"[RBAC-SYSTEM] Permission denied: {principal} lacks {resource_required_perm.value} "
                        f"for {resource_type}"
                    )
                    self.stats['checks_denied'] += 1
                    return False
        
        # Check resource scope
        if not await self._check_resource_scope(account, resource_type, resource_id):
            logger.warning(
                f"[RBAC-SYSTEM] Permission denied: {principal} out of scope for "
                f"{resource_type}:{resource_id}"
            )
            self.stats['checks_denied'] += 1
            return False
        
        # All checks passed
        self.stats['checks_allowed'] += 1
        
        logger.debug(
            f"[RBAC-SYSTEM] Permission granted: {principal} -> {action} on "
            f"{resource_type}:{resource_id}"
        )
        
        return True
    
    async def _check_resource_scope(
        self,
        account: ServiceAccount,
        resource_type: str,
        resource_id: str
    ) -> bool:
        """Check if resource is in account's scope"""
        
        # If account has wildcard scope, allow all
        if '*' in account.resource_scopes:
            wildcard_resources = account.resource_scopes['*']
            if '*' in wildcard_resources:
                return True
        
        # Check specific resource type scope
        if resource_type not in account.resource_scopes:
            return False
        
        allowed_resources = account.resource_scopes[resource_type]
        
        # Wildcard allows all resources of this type
        if '*' in allowed_resources:
            return True
        
        # Check exact match
        if resource_id in allowed_resources:
            return True
        
        # Check prefix match (e.g., /backend/* matches /backend/main.py)
        for allowed in allowed_resources:
            if allowed.endswith('/*'):
                prefix = allowed[:-2]
                if resource_id.startswith(prefix):
                    return True
        
        return False
    
    def get_service_account(self, account_id: str) -> Optional[ServiceAccount]:
        """Get service account by ID"""
        return self.service_accounts.get(account_id)
    
    def list_service_accounts(self) -> List[Dict[str, Any]]:
        """List all service accounts"""
        return [account.to_dict() for account in self.service_accounts.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RBAC statistics"""
        
        total_checks = self.stats['checks_performed']
        
        return {
            **self.stats,
            'running': self.running,
            'service_accounts': len(self.service_accounts),
            'permission_grant_rate': (
                self.stats['checks_allowed'] / max(1, total_checks) * 100
            )
        }


# Global instance
rbac_system = RBACSystem()
