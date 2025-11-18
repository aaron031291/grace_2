"""
Tenant Manager - CRUD operations and tenant lifecycle
"""

import secrets
from typing import Optional, List
from datetime import datetime

from .models import Tenant, TenantConfig, TenantMetrics


class TenantManager:
    """Manage tenants and their configurations"""
    
    def __init__(self):
        self.tenants: dict[str, Tenant] = {}
    
    def create_tenant(
        self,
        name: str,
        email: str,
        plan: str = "free",
        config: Optional[TenantConfig] = None
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = f"tenant_{secrets.token_urlsafe(16)}"
        
        if not config:
            config = self._get_default_config(plan)
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            email=email,
            plan=plan,
            config=config,
            metrics=TenantMetrics(tenant_id=tenant_id)
        )
        
        self.tenants[tenant_id] = tenant
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def list_tenants(
        self,
        status: Optional[str] = None,
        plan: Optional[str] = None
    ) -> List[Tenant]:
        """List tenants with optional filters"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        if plan:
            tenants = [t for t in tenants if t.plan == plan]
        
        return tenants
    
    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        plan: Optional[str] = None,
        config: Optional[TenantConfig] = None
    ) -> Optional[Tenant]:
        """Update tenant details"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        if name:
            tenant.name = name
        if email:
            tenant.email = email
        if plan:
            tenant.plan = plan
            if not config:
                tenant.config = self._get_default_config(plan)
        if config:
            tenant.config = config
        
        tenant.updated_at = datetime.utcnow()
        return tenant
    
    def suspend_tenant(self, tenant_id: str) -> bool:
        """Suspend a tenant"""
        tenant = self.tenants.get(tenant_id)
        if tenant:
            tenant.status = "suspended"
            tenant.updated_at = datetime.utcnow()
            return True
        return False
    
    def activate_tenant(self, tenant_id: str) -> bool:
        """Activate a suspended tenant"""
        tenant = self.tenants.get(tenant_id)
        if tenant:
            tenant.status = "active"
            tenant.updated_at = datetime.utcnow()
            return True
        return False
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Soft delete a tenant"""
        tenant = self.tenants.get(tenant_id)
        if tenant:
            tenant.status = "deleted"
            tenant.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_metrics(
        self,
        tenant_id: str,
        **metrics_updates
    ) -> Optional[TenantMetrics]:
        """Update tenant metrics"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        for key, value in metrics_updates.items():
            if hasattr(tenant.metrics, key):
                setattr(tenant.metrics, key, value)
        
        tenant.metrics.updated_at = datetime.utcnow()
        return tenant.metrics
    
    def increment_metric(
        self,
        tenant_id: str,
        metric_name: str,
        amount: int = 1
    ) -> Optional[int]:
        """Increment a tenant metric"""
        tenant = self.tenants.get(tenant_id)
        if not tenant or not hasattr(tenant.metrics, metric_name):
            return None
        
        current = getattr(tenant.metrics, metric_name)
        new_value = current + amount
        setattr(tenant.metrics, metric_name, new_value)
        tenant.metrics.updated_at = datetime.utcnow()
        
        return new_value
    
    @staticmethod
    def _get_default_config(plan: str) -> TenantConfig:
        """Get default configuration for a plan"""
        configs = {
            "free": TenantConfig(
                rate_limit_rps=10,
                rate_limit_burst=20,
                max_concurrent_jobs=2,
                max_storage_gb=1.0,
                features_enabled=["basic"]
            ),
            "pro": TenantConfig(
                rate_limit_rps=100,
                rate_limit_burst=200,
                max_concurrent_jobs=10,
                max_storage_gb=10.0,
                features_enabled=["basic", "advanced", "analytics"]
            ),
            "enterprise": TenantConfig(
                rate_limit_rps=1000,
                rate_limit_burst=2000,
                max_concurrent_jobs=100,
                max_storage_gb=100.0,
                features_enabled=["basic", "advanced", "analytics", "custom"]
            )
        }
        return configs.get(plan, configs["free"])
