"""
Phase 6 API - API Gateway, Multi-Tenancy, Observability, and Scaling
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List

from backend.multi_tenancy import Tenant, TenantConfig, TenantManager
from backend.api_gateway import APIKeyAuth
from backend.observability import MetricsCollector, HealthChecker
from backend.scaling import JobQueue, JobPriority

router = APIRouter(prefix="/api/phase6", tags=["phase6"])

tenant_manager = TenantManager()
api_key_auth = APIKeyAuth()
metrics_collector = MetricsCollector()
health_checker = HealthChecker.create_default_checks()
job_queue = JobQueue(max_workers=5)

job_queue.start()


class CreateTenantRequest(BaseModel):
    name: str
    email: str
    plan: str = "free"


class UpdateTenantRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    plan: Optional[str] = None
    config: Optional[TenantConfig] = None


class CreateAPIKeyRequest(BaseModel):
    name: str
    scopes: List[str]
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    key_id: str
    raw_key: str  # Only returned on creation
    tenant_id: str
    name: str
    scopes: List[str]
    created_at: str


class SubmitJobRequest(BaseModel):
    name: str
    priority: str = "normal"
    tenant_id: Optional[str] = None


@router.post("/tenants", response_model=Tenant)
async def create_tenant(request: CreateTenantRequest):
    """Create a new tenant"""
    tenant = tenant_manager.create_tenant(
        name=request.name,
        email=request.email,
        plan=request.plan
    )
    return tenant


@router.get("/tenants/{tenant_id}", response_model=Tenant)
async def get_tenant(tenant_id: str):
    """Get tenant by ID"""
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.get("/tenants", response_model=List[Tenant])
async def list_tenants(
    status_filter: Optional[str] = None,
    plan: Optional[str] = None
):
    """List all tenants with optional filters"""
    return tenant_manager.list_tenants(status=status_filter, plan=plan)


@router.put("/tenants/{tenant_id}", response_model=Tenant)
async def update_tenant(tenant_id: str, request: UpdateTenantRequest):
    """Update tenant details"""
    tenant = tenant_manager.update_tenant(
        tenant_id=tenant_id,
        name=request.name,
        email=request.email,
        plan=request.plan,
        config=request.config
    )
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str):
    """Suspend a tenant"""
    success = tenant_manager.suspend_tenant(tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return {"message": "Tenant suspended successfully"}


@router.post("/tenants/{tenant_id}/activate")
async def activate_tenant(tenant_id: str):
    """Activate a suspended tenant"""
    success = tenant_manager.activate_tenant(tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return {"message": "Tenant activated successfully"}


@router.post("/tenants/{tenant_id}/api-keys", response_model=APIKeyResponse)
async def create_api_key(tenant_id: str, request: CreateAPIKeyRequest):
    """Create a new API key for a tenant"""
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    raw_key, api_key = api_key_auth.generate_key(
        tenant_id=tenant_id,
        name=request.name,
        scopes=request.scopes,
        expires_in_days=request.expires_in_days
    )
    
    return APIKeyResponse(
        key_id=api_key.key_id,
        raw_key=raw_key,
        tenant_id=api_key.tenant_id,
        name=api_key.name,
        scopes=api_key.scopes,
        created_at=api_key.created_at.isoformat()
    )


@router.get("/tenants/{tenant_id}/api-keys")
async def list_api_keys(tenant_id: str):
    """List all API keys for a tenant"""
    keys = api_key_auth.list_keys(tenant_id)
    return [
        {
            "key_id": key.key_id,
            "name": key.name,
            "scopes": key.scopes,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "is_active": key.is_active
        }
        for key in keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str):
    """Revoke an API key"""
    success = api_key_auth.revoke_key(key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key revoked successfully"}


@router.get("/metrics/golden-signals")
async def get_golden_signals():
    """Get golden signals metrics"""
    signals = metrics_collector.get_golden_signals()
    system_metrics = health_checker.get_system_metrics()
    
    return {
        "latency": {
            "p50_ms": signals.latency_p50_ms,
            "p95_ms": signals.latency_p95_ms,
            "p99_ms": signals.latency_p99_ms
        },
        "traffic": {
            "requests_per_second": signals.requests_per_second,
            "requests_total": signals.requests_total
        },
        "errors": {
            "error_rate": signals.error_rate,
            "errors_total": signals.errors_total
        },
        "saturation": {
            "cpu_percent": system_metrics["cpu_percent"],
            "memory_percent": system_metrics["memory_percent"],
            "disk_percent": system_metrics["disk_percent"],
            "active_connections": system_metrics["active_connections"]
        }
    }


@router.get("/metrics/endpoints")
async def get_endpoint_metrics():
    """Get per-endpoint metrics"""
    return metrics_collector.get_endpoint_stats()


@router.get("/metrics/tenants/{tenant_id}")
async def get_tenant_metrics(tenant_id: str):
    """Get metrics for a specific tenant"""
    tenant = tenant_manager.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    stats = metrics_collector.get_tenant_stats(tenant_id)
    return {
        "tenant_id": tenant_id,
        "metrics": tenant.metrics.dict(),
        "api_stats": stats
    }


@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = health_checker.run_checks()
    overall_status = health_checker.get_overall_status()
    system_metrics = health_checker.get_system_metrics()
    
    return {
        "status": overall_status,
        "checks": {
            name: {
                "status": check.status,
                "message": check.message,
                "duration_ms": check.duration_ms
            }
            for name, check in checks.items()
        },
        "system": system_metrics
    }


@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe"""
    overall_status = health_checker.get_overall_status()
    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    return {"status": "ready"}


@router.post("/jobs")
async def submit_job(request: SubmitJobRequest):
    """Submit a background job"""
    def example_job():
        import time
        time.sleep(2)
        return {"result": "Job completed successfully"}
    
    priority_map = {
        "low": JobPriority.LOW,
        "normal": JobPriority.NORMAL,
        "high": JobPriority.HIGH,
        "critical": JobPriority.CRITICAL
    }
    
    job = job_queue.submit(
        example_job,
        name=request.name,
        priority=priority_map.get(request.priority, JobPriority.NORMAL),
        tenant_id=request.tenant_id
    )
    
    return {
        "job_id": job.job_id,
        "name": job.name,
        "status": job.status,
        "priority": job.priority,
        "created_at": job.created_at
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    job = job_queue.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "job_id": job.job_id,
        "name": job.name,
        "status": job.status,
        "priority": job.priority,
        "progress": job.progress,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "duration_ms": job.duration_ms(),
        "result": job.result,
        "error": job.error
    }


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    tenant_id: Optional[str] = None
):
    """List jobs with optional filters"""
    from backend.scaling.job_queue import JobStatus
    
    status_filter = JobStatus(status) if status else None
    jobs = job_queue.list_jobs(status=status_filter, tenant_id=tenant_id)
    
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status,
                "priority": job.priority,
                "progress": job.progress,
                "created_at": job.created_at,
                "tenant_id": job.tenant_id
            }
            for job in jobs[:100]  # Limit to 100 jobs
        ]
    }


@router.get("/jobs/stats")
async def get_job_stats():
    """Get job queue statistics"""
    return job_queue.get_stats()


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a pending job"""
    success = job_queue.cancel_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled (not found or already running)"
        )
    return {"message": "Job cancelled successfully"}
