"""
Tenant Isolation - Ensure data and resource isolation between tenants
"""

from typing import Optional, Any, Dict
from fastapi import Request, HTTPException, status


class TenantIsolation:
    """Enforce tenant isolation for data access"""
    
    @staticmethod
    def get_tenant_id(request: Request) -> str:
        """Get tenant ID from request, raise error if not found"""
        tenant_id = request.state.__dict__.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant ID not found in request"
            )
        return tenant_id
    
    @staticmethod
    def check_tenant_access(
        request: Request,
        resource_tenant_id: str
    ) -> bool:
        """Check if request tenant can access resource"""
        request_tenant_id = TenantIsolation.get_tenant_id(request)
        if request_tenant_id != resource_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Resource belongs to different tenant"
            )
        return True
    
    @staticmethod
    def filter_by_tenant(
        request: Request,
        items: list[Dict[str, Any]],
        tenant_field: str = "tenant_id"
    ) -> list[Dict[str, Any]]:
        """Filter list of items to only include current tenant's data"""
        tenant_id = TenantIsolation.get_tenant_id(request)
        return [
            item for item in items
            if item.get(tenant_field) == tenant_id
        ]
    
    @staticmethod
    def add_tenant_context(
        request: Request,
        data: Dict[str, Any],
        tenant_field: str = "tenant_id"
    ) -> Dict[str, Any]:
        """Add tenant ID to data being created"""
        tenant_id = TenantIsolation.get_tenant_id(request)
        data[tenant_field] = tenant_id
        return data
