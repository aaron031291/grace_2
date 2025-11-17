"""
Multi-Tenancy System
Tenant isolation, per-tenant metrics, and resource management
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

class TenantTier(str, Enum):
    """Tenant subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class TenantStatus(str, Enum):
    """Tenant account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CHURNED = "churned"

@dataclass
class Tenant:
    """Tenant account"""
    tenant_id: str
    name: str
    tier: TenantTier
    status: TenantStatus
    created_at: datetime
    api_key: str
    quotas: Dict[str, int]
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

class MultiTenantManager:
    """Manages multi-tenant accounts and isolation"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        
        # Default quotas by tier
        self.tier_quotas = {
            TenantTier.FREE: {
                "api_calls_per_day": 1000,
                "storage_mb": 100,
                "learning_jobs_per_day": 5,
                "coding_tasks_per_day": 3
            },
            TenantTier.STARTER: {
                "api_calls_per_day": 10000,
                "storage_mb": 1000,
                "learning_jobs_per_day": 50,
                "coding_tasks_per_day": 25
            },
            TenantTier.PRO: {
                "api_calls_per_day": 100000,
                "storage_mb": 10000,
                "learning_jobs_per_day": 500,
                "coding_tasks_per_day": 200
            },
            TenantTier.ENTERPRISE: {
                "api_calls_per_day": -1,  # Unlimited
                "storage_mb": -1,
                "learning_jobs_per_day": -1,
                "coding_tasks_per_day": -1
            }
        }
    
    def create_tenant(
        self,
        name: str,
        tier: TenantTier = TenantTier.FREE,
        status: TenantStatus = TenantStatus.TRIAL
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
        api_key = f"gk_{uuid.uuid4().hex}"
        
        quotas = self.tier_quotas[tier].copy()
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            tier=tier,
            status=status,
            created_at=datetime.now(),
            api_key=api_key,
            quotas=quotas,
            usage={}
        )
        
        self.tenants[tenant_id] = tenant
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_api_key(self, api_key: str) -> Optional[Tenant]:
        """Get tenant by API key"""
        for tenant in self.tenants.values():
            if tenant.api_key == api_key:
                return tenant
        return None
    
    def check_quota(self, tenant_id: str, quota_type: str) -> bool:
        """Check if tenant is within quota"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return False
        
        quota_limit = tenant.quotas.get(quota_type, 0)
        
        # -1 means unlimited
        if quota_limit == -1:
            return True
        
        usage = tenant.usage.get(quota_type, 0)
        return usage < quota_limit
    
    def increment_usage(self, tenant_id: str, quota_type: str, amount: int = 1):
        """Increment tenant usage"""
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.usage[quota_type] = tenant.usage.get(quota_type, 0) + amount
    
    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant statistics"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return {}
        
        return {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "tier": tenant.tier.value,
            "status": tenant.status.value,
            "quotas": tenant.quotas,
            "usage": tenant.usage,
            "quota_utilization": {
                quota_type: (
                    (usage / tenant.quotas.get(quota_type, 1)) * 100
                    if tenant.quotas.get(quota_type, -1) > 0 else 0
                )
                for quota_type, usage in tenant.usage.items()
            }
        }
    
    def list_tenants(self, status: Optional[TenantStatus] = None) -> List[Tenant]:
        """List all tenants, optionally filtered by status"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        return tenants
    
    def upgrade_tenant(self, tenant_id: str, new_tier: TenantTier):
        """Upgrade tenant to new tier"""
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.tier = new_tier
            tenant.quotas = self.tier_quotas[new_tier].copy()
    
    def suspend_tenant(self, tenant_id: str, reason: str):
        """Suspend a tenant"""
        tenant = self.get_tenant(tenant_id)
        if tenant:
            tenant.status = TenantStatus.SUSPENDED
            tenant.metadata['suspension_reason'] = reason
            tenant.metadata['suspended_at'] = datetime.now().isoformat()

# Global instance
_tenant_manager: Optional[MultiTenantManager] = None

def get_tenant_manager() -> MultiTenantManager:
    """Get global tenant manager"""
    global _tenant_manager
    if _tenant_manager is None:
        _tenant_manager = MultiTenantManager()
    return _tenant_manager
