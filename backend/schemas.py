"""
Pydantic schemas for all Grace API endpoints
Ensures proper API documentation and type safety
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

# ============ Health & Status ============

class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall system health status")
    message: str = Field(..., description="Human-readable status message")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
    services: Dict[str, str] = Field(..., description="Status of individual services")
    timestamp: str = Field(..., description="ISO timestamp of health check")

# ============ Memory ============

class MemoryArtifactResponse(BaseModel):
    id: int
    path: str
    domain: str
    category: str
    status: str
    version: int
    size: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MemoryTreeResponse(BaseModel):
    tree: Dict[str, Any]
    flat_list: List[MemoryArtifactResponse]

class MemoryCreateRequest(BaseModel):
    path: str
    content: str
    domain: str = "general"
    category: str = "knowledge"
    metadata: Optional[Dict[str, Any]] = None
    reason: str = ""

# ============ Tasks ============

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    auto_generated: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

# ============ Agents ============

class AgentStatusResponse(BaseModel):
    task_id: str
    agent_type: str
    task: str
    domain: str
    status: str
    progress: int
    started_at: str
    result: Optional[Dict[str, Any]] = None

class ActiveAgentsResponse(BaseModel):
    agents: Dict[str, AgentStatusResponse]
    total: int
    running: int

class SpawnAgentRequest(BaseModel):
    agent_type: str
    task: str
    domain: str = "core"

class SpawnAgentResponse(BaseModel):
    success: bool
    task_id: str
    message: str

# ============ Governance ============

class GovernanceCheckRequest(BaseModel):
    actor: str
    action: str
    resource: str
    payload: Dict[str, Any]

class GovernanceCheckResponse(BaseModel):
    decision: str  # "allow", "warn", "block"
    policy: str
    verdict: str
    reasons: List[str]
    requires_approval: bool

class ApprovalRequest(BaseModel):
    action: str
    resource: str
    reason: str
    metadata: Optional[Dict[str, Any]] = None

class ApprovalResponse(BaseModel):
    approval_id: str
    status: str
    tier: str
    can_auto_approve: bool

# ============ Knowledge ============

class KnowledgeQueryRequest(BaseModel):
    query: str
    limit: int = 10
    domain: Optional[str] = None

class KnowledgeItemResponse(BaseModel):
    id: int
    title: str
    content: str
    domain: str
    trust_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class KnowledgeQueryResponse(BaseModel):
    results: List[KnowledgeItemResponse]
    total: int
    query_time_ms: float

# ============ Execution ============

class ExecutionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]
    domain: str = "core"

class ExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

# ============ Verification ============

class VerificationResultResponse(BaseModel):
    verification_id: str
    action: str
    verdict: str  # "passed", "failed", "warning"
    checks_passed: int
    checks_failed: int
    details: List[str]
    timestamp: datetime

class VerificationAuditResponse(BaseModel):
    audit_logs: List[Dict[str, Any]]
    total: int
    time_range_hours: int

# ============ Meta Loop ============

class MetaLoopStatusResponse(BaseModel):
    status: str
    current_focus: Optional[str] = None
    optimizations_applied: int
    recommendations_pending: int
    last_cycle_at: Optional[datetime] = None

class MetaRecommendationResponse(BaseModel):
    id: str
    recommendation: str
    impact: str
    confidence: float
    status: str
    created_at: datetime

# ============ Code Generation ============

class CodeGenerationRequest(BaseModel):
    spec: Dict[str, Any]
    language: str = "python"
    use_patterns: bool = True

class CodeGenerationResponse(BaseModel):
    code: str
    language: str
    security_scan: Dict[str, Any]
    governance_verdict: str
    suggestions: List[str]

# ============ Generic Responses ============

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    timestamp: datetime
    metrics: Optional[Dict[str, Any]] = None
