"""
Phase 7 API - SaaS Readiness & Business Workflows
Provides REST API endpoints for all Phase 7 functionality
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from backend.product_templates import (
    ProductTemplate, TemplateCategory, TemplateInstance,
    TemplateManager, TemplateRegistry
)
from backend.billing import (
    Subscription, SubscriptionPlan, Invoice, InvoiceStatus,
    UsageRecord, UsageRecordType,
    BillingManager, StripeIntegration
)
from backend.rbac import (
    Role, Permission, User, RoleAssignment,
    PermissionAction, PermissionResource,
    RBACManager, PermissionChecker
)
from backend.disaster_recovery import (
    Backup, BackupType, BackupStatus,
    RestoreJob, RestoreStatus,
    ChaosTest, ChaosTestType, ChaosTestStatus,
    BackupManager, RestoreManager, ChaosEngineer
)

router = APIRouter(prefix="/api/phase7", tags=["Phase 7: SaaS Readiness"])

template_manager = TemplateManager()
billing_manager = BillingManager()
stripe_integration = StripeIntegration()
rbac_manager = RBACManager()
permission_checker = PermissionChecker(rbac_manager)
backup_manager = BackupManager()
restore_manager = RestoreManager(backup_manager)
chaos_engineer = ChaosEngineer()


# ============================================================================
# ============================================================================

@router.get("/templates", response_model=List[ProductTemplate])
async def list_templates(
    category: Optional[TemplateCategory] = None,
    search: Optional[str] = None,
):
    """List all product templates"""
    if search:
        return template_manager.registry.search_templates(search)
    return template_manager.registry.list_templates(category=category)


@router.get("/templates/{template_id}", response_model=ProductTemplate)
async def get_template(template_id: str):
    """Get template by ID"""
    template = template_manager.registry.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/instances", response_model=TemplateInstance)
async def create_instance(
    template_id: str,
    tenant_id: str,
    name: str,
    description: Optional[str] = None,
    customizations: Optional[dict] = None,
):
    """Create a new product instance from template"""
    try:
        instance = template_manager.create_instance(
            template_id=template_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            customizations=customizations,
        )
        return instance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/instances", response_model=List[TemplateInstance])
async def list_instances(
    tenant_id: Optional[str] = None,
    template_id: Optional[str] = None,
    status: Optional[str] = None,
):
    """List product instances"""
    return template_manager.list_instances(
        tenant_id=tenant_id,
        template_id=template_id,
        status=status,
    )


@router.get("/instances/{instance_id}", response_model=TemplateInstance)
async def get_instance(instance_id: str):
    """Get instance by ID"""
    instance = template_manager.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.put("/instances/{instance_id}", response_model=TemplateInstance)
async def update_instance(
    instance_id: str,
    customizations: Optional[dict] = None,
    resources: Optional[dict] = None,
):
    """Update instance configuration"""
    try:
        instance = template_manager.update_instance(
            instance_id=instance_id,
            customizations=customizations,
            resources=resources,
        )
        return instance
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/instances/{instance_id}/suspend", response_model=TemplateInstance)
async def suspend_instance(instance_id: str):
    """Suspend instance"""
    try:
        return template_manager.suspend_instance(instance_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/instances/{instance_id}/activate", response_model=TemplateInstance)
async def activate_instance(instance_id: str):
    """Activate suspended instance"""
    try:
        return template_manager.activate_instance(instance_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/instances/{instance_id}")
async def delete_instance(instance_id: str):
    """Delete instance"""
    success = template_manager.delete_instance(instance_id)
    if not success:
        raise HTTPException(status_code=404, detail="Instance not found")
    return {"message": "Instance deleted successfully"}


@router.get("/instances/{instance_id}/metrics")
async def get_instance_metrics(instance_id: str):
    """Get instance metrics"""
    try:
        return template_manager.get_instance_metrics(instance_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# ============================================================================

@router.get("/subscriptions", response_model=List[Subscription])
async def list_subscriptions(tenant_id: Optional[str] = None):
    """List all subscriptions, optionally filtered by tenant"""
    if tenant_id:
        return [s for s in billing_manager.subscriptions.values() if s.tenant_id == tenant_id]
    return list(billing_manager.subscriptions.values())


@router.post("/subscriptions", response_model=Subscription)
async def create_subscription(
    tenant_id: str,
    plan: SubscriptionPlan,
    billing_cycle: str = "monthly",
    trial_days: int = 14,
):
    """Create a new subscription"""
    return billing_manager.create_subscription(
        tenant_id=tenant_id,
        plan=plan,
        billing_cycle=billing_cycle,
        trial_days=trial_days,
    )


@router.get("/subscriptions/{subscription_id}", response_model=Subscription)
async def get_subscription(subscription_id: str):
    """Get subscription by ID"""
    subscription = billing_manager.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.get("/subscriptions/tenant/{tenant_id}", response_model=Subscription)
async def get_subscription_by_tenant(tenant_id: str):
    """Get subscription for tenant"""
    subscription = billing_manager.get_subscription_by_tenant(tenant_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found for tenant")
    return subscription


@router.put("/subscriptions/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: str,
    plan: Optional[SubscriptionPlan] = None,
    billing_cycle: Optional[str] = None,
):
    """Update subscription"""
    try:
        return billing_manager.update_subscription(
            subscription_id=subscription_id,
            plan=plan,
            billing_cycle=billing_cycle,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/subscriptions/{subscription_id}/cancel", response_model=Subscription)
async def cancel_subscription(subscription_id: str):
    """Cancel subscription"""
    try:
        return billing_manager.cancel_subscription(subscription_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/invoices", response_model=Invoice)
async def create_invoice(
    tenant_id: str,
    subscription_id: Optional[str] = None,
    line_items: Optional[List[dict]] = None,
):
    """Create a new invoice"""
    return billing_manager.create_invoice(
        tenant_id=tenant_id,
        subscription_id=subscription_id,
        line_items=line_items,
    )


@router.get("/invoices", response_model=List[Invoice])
async def list_invoices(
    tenant_id: Optional[str] = None,
    status: Optional[InvoiceStatus] = None,
):
    """List invoices"""
    return billing_manager.list_invoices(tenant_id=tenant_id, status=status)


@router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    """Get invoice by ID"""
    invoice = billing_manager.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/invoices/{invoice_id}/pay", response_model=Invoice)
async def pay_invoice(invoice_id: str):
    """Mark invoice as paid"""
    try:
        return billing_manager.pay_invoice(invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/usage", response_model=UsageRecord)
async def record_usage(
    tenant_id: str,
    usage_type: UsageRecordType,
    quantity: float,
    unit: str,
    metadata: Optional[dict] = None,
):
    """Record usage"""
    from decimal import Decimal
    return billing_manager.record_usage(
        tenant_id=tenant_id,
        usage_type=usage_type,
        quantity=Decimal(str(quantity)),
        unit=unit,
        metadata=metadata,
    )


@router.get("/usage/{tenant_id}/summary")
async def get_usage_summary(tenant_id: str):
    """Get usage summary for tenant"""
    return billing_manager.get_usage_summary(tenant_id)


# ============================================================================
# ============================================================================

@router.post("/roles", response_model=Role)
async def create_role(
    name: str,
    description: str,
    permissions: Optional[List[str]] = None,
    parent_role_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
):
    """Create a new role"""
    return rbac_manager.create_role(
        name=name,
        description=description,
        permissions=set(permissions) if permissions else None,
        parent_role_id=parent_role_id,
        tenant_id=tenant_id,
    )


@router.get("/roles", response_model=List[Role])
async def list_roles(tenant_id: Optional[str] = None):
    """List roles"""
    return rbac_manager.list_roles(tenant_id=tenant_id)


@router.get("/roles/{role_id}", response_model=Role)
async def get_role(role_id: str):
    """Get role by ID"""
    role = rbac_manager.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    permissions: Optional[List[str]] = None,
):
    """Update role"""
    try:
        return rbac_manager.update_role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=set(permissions) if permissions else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str):
    """Delete role"""
    try:
        success = rbac_manager.delete_role(role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"message": "Role deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permissions", response_model=List[Permission])
async def list_permissions():
    """List all permissions"""
    return list(rbac_manager.permissions.values())


@router.post("/users", response_model=User)
async def create_user(email: str, name: str, tenant_id: str):
    """Create a new user"""
    return rbac_manager.create_user(email=email, name=name, tenant_id=tenant_id)


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    user = rbac_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/role-assignments", response_model=RoleAssignment)
async def assign_role(
    user_id: str,
    role_id: str,
    tenant_id: str,
    assigned_by: Optional[str] = None,
):
    """Assign role to user"""
    try:
        return rbac_manager.assign_role(
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            assigned_by=assigned_by,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/users/{user_id}/roles", response_model=List[Role])
async def get_user_roles(user_id: str, tenant_id: str):
    """Get all roles for user"""
    return rbac_manager.get_user_roles(user_id=user_id, tenant_id=tenant_id)


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str, tenant_id: str):
    """Get all permissions for user"""
    permissions = rbac_manager.get_user_permissions(user_id=user_id, tenant_id=tenant_id)
    return {"permissions": list(permissions)}


@router.post("/check-permission")
async def check_permission(
    user_id: str,
    tenant_id: str,
    resource: PermissionResource,
    action: PermissionAction,
    resource_id: Optional[str] = None,
):
    """Check if user has permission"""
    allowed = permission_checker.check_permission(
        user_id=user_id,
        tenant_id=tenant_id,
        resource=resource,
        action=action,
        resource_id=resource_id,
    )
    return {"allowed": allowed}


@router.get("/access-logs")
async def get_access_logs(
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
):
    """Get access logs"""
    logs = rbac_manager.get_access_logs(user_id=user_id, tenant_id=tenant_id, limit=limit)
    return {"logs": logs}


# ============================================================================
# ============================================================================

@router.post("/backups", response_model=Backup)
async def create_backup(
    tenant_id: str,
    backup_type: BackupType = BackupType.FULL,
    components: Optional[List[str]] = None,
    retention_days: int = 30,
):
    """Create a new backup"""
    return backup_manager.create_backup(
        tenant_id=tenant_id,
        backup_type=backup_type,
        components=components,
        retention_days=retention_days,
    )


@router.get("/backups", response_model=List[Backup])
async def list_backups(
    tenant_id: Optional[str] = None,
    backup_type: Optional[BackupType] = None,
    status: Optional[BackupStatus] = None,
):
    """List backups"""
    return backup_manager.list_backups(
        tenant_id=tenant_id,
        backup_type=backup_type,
        status=status,
    )


@router.get("/backups/{backup_id}", response_model=Backup)
async def get_backup(backup_id: str):
    """Get backup by ID"""
    backup = backup_manager.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    return backup


@router.delete("/backups/{backup_id}")
async def delete_backup(backup_id: str):
    """Delete backup"""
    success = backup_manager.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    return {"message": "Backup deleted successfully"}


@router.get("/backups/stats")
async def get_backup_stats(tenant_id: Optional[str] = None):
    """Get backup statistics"""
    return backup_manager.get_backup_stats(tenant_id=tenant_id)


@router.post("/restore", response_model=RestoreJob)
async def create_restore_job(
    backup_id: str,
    tenant_id: str,
    target_environment: str = "production",
    components_to_restore: Optional[List[str]] = None,
):
    """Create a new restore job"""
    try:
        return restore_manager.create_restore_job(
            backup_id=backup_id,
            tenant_id=tenant_id,
            target_environment=target_environment,
            components_to_restore=components_to_restore,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/restore", response_model=List[RestoreJob])
async def list_restore_jobs(
    tenant_id: Optional[str] = None,
    status: Optional[RestoreStatus] = None,
):
    """List restore jobs"""
    return restore_manager.list_restore_jobs(tenant_id=tenant_id, status=status)


@router.get("/restore/{restore_id}", response_model=RestoreJob)
async def get_restore_job(restore_id: str):
    """Get restore job by ID"""
    job = restore_manager.get_restore_job(restore_id)
    if not job:
        raise HTTPException(status_code=404, detail="Restore job not found")
    return job


@router.post("/restore/{restore_id}/cancel", response_model=RestoreJob)
async def cancel_restore_job(restore_id: str):
    """Cancel restore job"""
    try:
        return restore_manager.cancel_restore_job(restore_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/chaos-tests", response_model=ChaosTest)
async def create_chaos_test(
    tenant_id: str,
    name: str,
    description: str,
    test_type: ChaosTestType,
    target_service: str,
    target_environment: str = "staging",
    duration_seconds: int = 300,
    intensity: float = 0.5,
):
    """Create a new chaos test"""
    return chaos_engineer.create_chaos_test(
        tenant_id=tenant_id,
        name=name,
        description=description,
        test_type=test_type,
        target_service=target_service,
        target_environment=target_environment,
        duration_seconds=duration_seconds,
        intensity=intensity,
    )


@router.post("/chaos-tests/{test_id}/execute", response_model=ChaosTest)
async def execute_chaos_test(test_id: str):
    """Execute chaos test"""
    try:
        return chaos_engineer.execute_chaos_test(test_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/chaos-tests", response_model=List[ChaosTest])
async def list_chaos_tests(
    tenant_id: Optional[str] = None,
    status: Optional[ChaosTestStatus] = None,
):
    """List chaos tests"""
    return chaos_engineer.list_chaos_tests(tenant_id=tenant_id, status=status)


@router.get("/chaos-tests/{test_id}", response_model=ChaosTest)
async def get_chaos_test(test_id: str):
    """Get chaos test by ID"""
    test = chaos_engineer.get_chaos_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Chaos test not found")
    return test


@router.get("/chaos-tests/stats")
async def get_chaos_stats(tenant_id: Optional[str] = None):
    """Get chaos engineering statistics"""
    return chaos_engineer.get_chaos_stats(tenant_id=tenant_id)


@router.get("/runbooks")
async def list_runbooks():
    """List all DR runbooks"""
    return chaos_engineer.list_runbooks()


@router.get("/runbooks/{runbook_id}")
async def get_runbook(runbook_id: str):
    """Get DR runbook by ID"""
    runbook = chaos_engineer.get_runbook(runbook_id)
    if not runbook:
        raise HTTPException(status_code=404, detail="Runbook not found")
    return runbook


# ============================================================================
# ============================================================================

@router.get("/summary")
async def get_phase7_summary():
    """Get Phase 7 summary and statistics"""
    return {
        "phase": "Phase 7: SaaS Readiness & Business Workflows",
        "status": "operational",
        "components": {
            "product_templates": {
                "total_templates": len(template_manager.registry.templates),
                "total_instances": len(template_manager.instances),
                "categories": [c.value for c in TemplateCategory],
            },
            "billing": {
                "total_subscriptions": len(billing_manager.subscriptions),
                "total_invoices": len(billing_manager.invoices),
                "total_usage_records": len(billing_manager.usage_records),
                "plans": [p.value for p in SubscriptionPlan],
            },
            "rbac": {
                "total_roles": len(rbac_manager.roles),
                "total_users": len(rbac_manager.users),
                "total_permissions": len(rbac_manager.permissions),
                "total_assignments": len(rbac_manager.assignments),
                "total_access_logs": len(rbac_manager.access_logs),
            },
            "disaster_recovery": {
                "total_backups": len(backup_manager.backups),
                "total_restore_jobs": len(restore_manager.restore_jobs),
                "total_chaos_tests": len(chaos_engineer.chaos_tests),
                "total_runbooks": len(chaos_engineer.runbooks),
            },
        },
        "endpoints": {
            "product_templates": 11,
            "billing": 11,
            "rbac": 13,
            "disaster_recovery": 14,
            "total": 49,
        },
    }
