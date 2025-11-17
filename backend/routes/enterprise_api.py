"""
Enterprise API - Tenancy, Billing, RBAC, Templates, DR
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/api/enterprise", tags=["enterprise"])

# Tenancy endpoints
@router.post("/tenants")
async def create_tenant(name: str, tier: str = "free") -> Dict[str, Any]:
    """Create a new tenant account"""
    try:
        from backend.tenancy.multi_tenant import get_tenant_manager, TenantTier, TenantStatus
        
        manager = get_tenant_manager()
        tenant = manager.create_tenant(name, TenantTier(tier), TenantStatus.TRIAL)
        
        return tenant.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tenants/{tenant_id}")
async def get_tenant_stats(tenant_id: str) -> Dict[str, Any]:
    """Get tenant statistics and quota usage"""
    try:
        from backend.tenancy.multi_tenant import get_tenant_manager
        
        manager = get_tenant_manager()
        stats = manager.get_tenant_stats(tenant_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Billing endpoints
@router.post("/billing/subscriptions")
async def create_subscription(tenant_id: str, plan_id: str, cycle: str = "monthly") -> Dict[str, Any]:
    """Create subscription for tenant"""
    try:
        from backend.billing.billing_integration import get_billing_manager, BillingCycle
        
        manager = get_billing_manager()
        subscription = manager.create_subscription(tenant_id, plan_id, BillingCycle(cycle))
        
        return asdict(subscription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/usage")
async def record_usage(tenant_id: str, metric: str, quantity: int) -> Dict[str, Any]:
    """Record usage for metered billing"""
    try:
        from backend.billing.billing_integration import get_billing_manager
        
        manager = get_billing_manager()
        record = manager.record_usage(tenant_id, metric, quantity)
        
        return asdict(record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/billing/invoices/{tenant_id}")
async def generate_invoice(tenant_id: str, subscription_id: str) -> Dict[str, Any]:
    """Generate invoice for tenant"""
    try:
        from backend.billing.billing_integration import get_billing_manager
        
        manager = get_billing_manager()
        invoice = manager.generate_invoice(tenant_id, subscription_id)
        
        return asdict(invoice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RBAC endpoints
@router.post("/users")
async def create_user(email: str, tenant_id: str, roles: List[str]) -> Dict[str, Any]:
    """Create user with roles"""
    try:
        from backend.auth.rbac_system import get_rbac_system
        
        rbac = get_rbac_system()
        user = rbac.create_user(email, tenant_id, roles)
        
        return asdict(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str) -> Dict[str, Any]:
    """Get all permissions for user"""
    try:
        from backend.auth.rbac_system import get_rbac_system
        
        rbac = get_rbac_system()
        permissions = rbac.get_user_permissions(user_id)
        
        return {
            "user_id": user_id,
            "permissions": [p.value for p in permissions]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product Templates endpoints
@router.get("/templates")
async def list_templates(category: Optional[str] = None) -> Dict[str, Any]:
    """List available product templates"""
    try:
        from backend.saas.product_templates import get_template_registry, TemplateCategory
        
        registry = get_template_registry()
        
        cat_filter = TemplateCategory(category) if category else None
        templates = registry.list_templates(cat_filter)
        
        return {
            "total_templates": len(templates),
            "templates": [asdict(t) for t in templates]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/instantiate")
async def instantiate_product(
    template_id: str,
    tenant_id: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Instantiate a product from template"""
    try:
        from backend.saas.product_templates import get_template_registry
        
        registry = get_template_registry()
        result = await registry.instantiate_template(template_id, tenant_id, config)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Observability endpoints
@router.get("/observability/golden-signals")
async def get_golden_signals() -> Dict[str, Any]:
    """Get golden signals (latency, traffic, errors, saturation)"""
    try:
        from backend.observability.golden_signals import get_golden_signals
        
        monitor = get_golden_signals()
        signals = monitor.get_all_signals()
        
        return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Disaster Recovery endpoints
@router.post("/dr/backup")
async def create_backup(backup_type: str = "incremental") -> Dict[str, Any]:
    """Create a backup"""
    try:
        from backend.disaster_recovery.dr_automation import get_dr_manager
        
        dr = get_dr_manager()
        backup = await dr.create_backup(backup_type)
        
        return asdict(backup)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dr/restore/{backup_id}")
async def restore_backup(backup_id: str) -> Dict[str, Any]:
    """Restore from backup"""
    try:
        from backend.disaster_recovery.dr_automation import get_dr_manager
        
        dr = get_dr_manager()
        result = await dr.restore_from_backup(backup_id)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dr/stats")
async def get_dr_stats() -> Dict[str, Any]:
    """Get disaster recovery statistics"""
    try:
        from backend.disaster_recovery.dr_automation import get_dr_manager
        
        dr = get_dr_manager()
        stats = dr.get_dr_stats()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
