"""
Multi-Tenancy Models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TenantConfig(BaseModel):
    """Tenant configuration"""
    rate_limit_rps: int = 100
    rate_limit_burst: int = 200
    max_concurrent_jobs: int = 10
    max_storage_gb: float = 10.0
    features_enabled: list[str] = Field(default_factory=list)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class TenantMetrics(BaseModel):
    """Tenant usage metrics"""
    tenant_id: str
    requests_total: int = 0
    requests_failed: int = 0
    requests_rate_limited: int = 0
    storage_used_gb: float = 0.0
    jobs_completed: int = 0
    jobs_failed: int = 0
    api_latency_p50_ms: float = 0.0
    api_latency_p95_ms: float = 0.0
    api_latency_p99_ms: float = 0.0
    last_request_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Tenant(BaseModel):
    """Tenant model"""
    tenant_id: str
    name: str
    email: str
    plan: str = "free"  # free, pro, enterprise
    status: str = "active"  # active, suspended, deleted
    config: TenantConfig = Field(default_factory=TenantConfig)
    metrics: TenantMetrics = Field(default_factory=lambda: TenantMetrics(tenant_id=""))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.metrics.tenant_id:
            self.metrics.tenant_id = self.tenant_id
