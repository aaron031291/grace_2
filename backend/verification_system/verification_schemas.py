"""
Pydantic Schemas for Verification System

Enforces data validation at API boundaries and Trigger Mesh payloads.
Auto-generates OpenAPI docs that match reality.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ContractStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    VERIFIED = "verified"
    VIOLATED = "violated"
    ROLLED_BACK = "rolled_back"


class SnapshotType(str, Enum):
    PRE_ACTION = "pre_action"
    POST_ROLLBACK = "post_rollback"
    PERIODIC = "periodic"


class BenchmarkType(str, Enum):
    POST_ACTION = "post_action"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"


class MissionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


# ============================================================================
# Action Contract Schemas
# ============================================================================

class ExpectedEffectSchema(BaseModel):
    """Schema for expected action effects"""
    description: str = Field(..., description="Human-readable effect description")
    metric_thresholds: Optional[Dict[str, float]] = Field(None, description="Expected metric ranges")
    state_changes: Optional[Dict[str, Any]] = Field(None, description="Expected state modifications")
    health_checks: Optional[List[str]] = Field(None, description="Health checks that should pass")


class ContractCreateRequest(BaseModel):
    """Request to create an action contract"""
    action_type: str = Field(..., description="Type of action being contracted")
    expected_effect: ExpectedEffectSchema
    baseline_state: Dict[str, Any] = Field(..., description="System state before action")
    playbook_id: Optional[str] = None
    run_id: Optional[int] = None
    triggered_by: Optional[str] = None
    tier: str = Field("tier_1", description="Autonomy tier: tier_1, tier_2, tier_3")
    mission_id: Optional[str] = Field(None, description="Associated mission ID")


class ContractResponse(BaseModel):
    """Response for contract queries"""
    id: int
    action_type: str
    status: ContractStatus
    tier: str
    expected_effect: Dict[str, Any]
    actual_outcome: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    safe_hold_snapshot_id: Optional[int] = None
    playbook_id: Optional[str] = None
    run_id: Optional[int] = None
    triggered_by: Optional[str] = None
    rollback_reason: Optional[str] = None
    mission_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Snapshot Schemas
# ============================================================================

class SnapshotCreateRequest(BaseModel):
    """Request to create a safe-hold snapshot"""
    snapshot_type: SnapshotType
    triggered_by: Optional[str] = None
    action_contract_id: Optional[int] = None
    playbook_run_id: Optional[int] = None
    notes: Optional[str] = None


class SnapshotResponse(BaseModel):
    """Response for snapshot queries"""
    id: int
    snapshot_type: SnapshotType
    triggered_by: Optional[str] = None
    action_contract_id: Optional[int] = None
    playbook_run_id: Optional[int] = None
    created_at: Optional[datetime] = None
    restored_at: Optional[datetime] = None
    state_hash: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class SnapshotDetailResponse(SnapshotResponse):
    """Detailed snapshot with state data"""
    state_data: Optional[Dict[str, Any]] = None


# ============================================================================
# Benchmark Schemas
# ============================================================================

class BenchmarkRunRequest(BaseModel):
    """Request to run a benchmark"""
    benchmark_type: BenchmarkType
    action_contract_id: Optional[int] = None
    mission_id: Optional[str] = None


class BenchmarkResponse(BaseModel):
    """Response for benchmark queries"""
    id: int
    benchmark_type: BenchmarkType
    action_contract_id: Optional[int] = None
    passed: bool
    score: float
    metrics: Optional[Dict[str, Any]] = None
    executed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Mission Schemas
# ============================================================================

class MissionCreateRequest(BaseModel):
    """Request to create a mission"""
    mission_id: str = Field(..., description="Unique mission identifier")
    goal: str = Field(..., description="Mission objective")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class MissionResponse(BaseModel):
    """Response for mission queries"""
    id: int
    mission_id: str
    status: MissionStatus
    goal: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: Optional[float] = None
    current_phase: Optional[str] = None
    total_actions: Optional[int] = None
    completed_actions: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Event Schemas
# ============================================================================

class ActionEventPayload(BaseModel):
    """Schema for agentic.action_* event payloads"""
    action_id: str
    error_id: Optional[str] = None
    actions: Optional[List[str]] = None
    can_auto_execute: Optional[bool] = None
    approval_id: Optional[str] = None
    confidence: Optional[float] = None
    guardrails: Optional[List[str]] = None
    mission_id: Optional[str] = None
    success: Optional[bool] = None
    results: Optional[List[Dict[str, Any]]] = None
    tier: Optional[str] = None


class ApprovalEventPayload(BaseModel):
    """Schema for approval.* event payloads"""
    approval_id: int
    event_id: Optional[int] = None
    reason: Optional[str] = None
    tier: str = Field("tier_2", description="Approval tier")
    contract_id: Optional[int] = None
    mission_id: Optional[str] = None


# ============================================================================
# Job Schemas
# ============================================================================

class JobEnqueueRequest(BaseModel):
    """Request to enqueue a background job"""
    job_type: str = Field(..., description="Type of job: benchmark, verification, aggregation")
    contract_id: Optional[int] = None
    mission_id: Optional[str] = None
    max_attempts: int = Field(3, ge=1, le=10)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    """Response for job queries"""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int
    max_attempts: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Response Envelopes
# ============================================================================

class DataResponse(BaseModel):
    """Generic data response with metadata"""
    data: Any
    meta: Dict[str, Any] = Field(default_factory=dict)


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    data: List[Any]
    meta: Dict[str, Any] = Field(
        ...,
        description="Pagination metadata: total, limit, offset, count"
    )
    
    @validator("meta")
    def validate_meta(cls, v):
        required_fields = {"total", "limit", "offset", "count"}
        if not required_fields.issubset(v.keys()):
            raise ValueError(f"Meta must contain: {required_fields}")
        return v


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    request_id: Optional[str] = Field(None, description="Request correlation ID")


# ============================================================================
# Learning & Analytics Schemas
# ============================================================================

class PlaybookStatsResponse(BaseModel):
    """Playbook success rate statistics"""
    playbook_id: str
    total_executions: int
    successful: int
    failed: int
    success_rate: float


class LearningStatsResponse(BaseModel):
    """Aggregated learning statistics"""
    playbook_success_rates: Dict[str, PlaybookStatsResponse]
    contracts: Dict[str, Any]
    benchmarks: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """System health check response"""
    status: str = Field(..., description="overall health: healthy, degraded, unhealthy")
    contracts_today: int
    benchmarks_today: int
    components: Dict[str, str] = Field(..., description="Component statuses")
    checked_at: datetime
