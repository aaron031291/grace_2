"""
Pydantic schemas for all Grace API endpoints
Ensures proper API documentation and type safety
"""

from pydantic import BaseModel, Field, RootModel
from typing import Dict, List, Optional, Any
from datetime import datetime

# ============ Health & Status ============

class ServiceHealth(BaseModel):
    """Detailed health info for a single service"""
    status: str = Field(description="Service status", examples=["active"])
    last_check: str = Field(description="Last health check timestamp", examples=["2025-11-08T12:00:00Z"])
    uptime_seconds: Optional[float] = Field(default=None, description="Service-specific uptime", examples=[3600.5])
    metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Service-specific metrics",
        examples=[{"requests_processed": 1250, "avg_latency_ms": 45.2}]
    )

class SystemMetrics(BaseModel):
    """Overall system performance metrics"""
    total_requests: int = Field(description="Total API requests processed", examples=[15420])
    active_sessions: int = Field(description="Currently active user sessions", examples=[3])
    memory_usage_mb: float = Field(description="Memory usage in megabytes", examples=[256.8])
    cpu_usage_percent: float = Field(description="CPU usage percentage", examples=[23.5])
    database_connections: int = Field(description="Active database connections", examples=[5])
    event_queue_size: int = Field(description="Pending events in trigger mesh", examples=[12])

class HealthResponse(BaseModel):
    """Comprehensive health check with detailed metrics and service status"""
    status: str = Field(
        description="Overall system health: healthy, degraded, or down",
        examples=["healthy"]
    )
    message: str = Field(
        description="Human-readable status summary",
        examples=["Grace AI is fully operational - all systems nominal"]
    )
    version: str = Field(
        description="Grace API semantic version",
        examples=["3.0.0"]
    )
    uptime_seconds: float = Field(
        description="Total system uptime since last restart",
        examples=[3600.5]
    )
    services: Dict[str, ServiceHealth] = Field(
        description="Detailed health status of each service component",
        examples=[{
            "database": {
                "status": "connected",
                "last_check": "2025-11-08T12:00:00Z",
                "uptime_seconds": 3600.5,
                "metrics": {"active_connections": 5, "query_avg_ms": 12.3}
            },
            "trigger_mesh": {
                "status": "active",
                "last_check": "2025-11-08T12:00:00Z",
                "metrics": {"events_processed": 1420, "queue_size": 3}
            },
            "agentic_spine": {
                "status": "autonomous",
                "last_check": "2025-11-08T12:00:00Z",
                "metrics": {"active_agents": 6, "decisions_made": 89}
            }
        }]
    )
    metrics: SystemMetrics = Field(
        description="System-wide performance metrics",
        examples=[{
            "total_requests": 15420,
            "active_sessions": 3,
            "memory_usage_mb": 256.8,
            "cpu_usage_percent": 23.5,
            "database_connections": 5,
            "event_queue_size": 12
        }]
    )
    timestamp: str = Field(
        description="ISO 8601 timestamp when health check was performed",
        examples=["2025-11-08T12:00:00Z"]
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "healthy",
                "message": "Grace AI is fully operational",
                "version": "3.0.0",
                "uptime_seconds": 3600.5,
                "services": {
                    "database": "connected",
                    "trigger_mesh": "active",
                    "memory_system": "ready",
                    "agentic_spine": "autonomous",
                    "governance": "enforcing",
                    "self_heal": "monitoring"
                },
                "timestamp": "2025-11-08T12:00:00Z"
            }]
        }
    }

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
    id: int
    event_id: int
    status: str
    requested_by: str
    reason: str
    decision_by: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None

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
    id: int
    recommendation_type: str
    target: str
    current_value: Any
    proposed_value: Any
    recommendation_text: str
    confidence: float
    risk_level: str
    status: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class MetaAnalysisResponse(BaseModel):
    id: int
    type: str
    subject: str
    findings: str
    recommendation: str
    confidence: float
    applied: bool
    created_at: datetime

class MetaMetaEvaluationResponse(BaseModel):
    id: int
    metric: str
    before: float
    after: float
    improvement: float
    conclusion: str
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

# ============ Additional Responses ============

class DomainStatsResponse(BaseModel):
    domains: Dict[str, Dict[str, Any]]

class ExportBundleResponse(BaseModel):
    exported_at: str
    exported_by: str
    artifact_count: int
    domains: List[str]
    artifacts: List[Dict[str, Any]]

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    result: Optional[Any] = None

class ApprovalStatsResponse(BaseModel):
    pending: int
    approved: int
    rejected: int

# ============ Governance (Extended) ============

class PolicyResponse(BaseModel):
    id: int
    name: str
    description: str
    severity: str
    condition: str
    action: str

class PolicyListResponse(RootModel[List[PolicyResponse]]):
    root: List[PolicyResponse]

class PolicyCreateResponse(BaseModel):
    id: int
    name: str

class AuditLogResponse(BaseModel):
    id: int
    actor: str
    action: str
    resource: str
    policy_checked: str
    result: str
    timestamp: datetime

class AuditLogListResponse(RootModel[List[AuditLogResponse]]):
    root: List[AuditLogResponse]

class ConfigItemResponse(BaseModel):
    key: str
    value: str
    type: str
    approved: bool
    last_updated_by: Optional[str] = None

class ConfigListResponse(RootModel[List[ConfigItemResponse]]):
    root: List[ConfigItemResponse]

# ============ Memory (Extended) ============

class MemoryItemResponse(BaseModel):
    id: int
    path: str
    content: str
    domain: str
    category: str
    status: str
    version: int
    size: Optional[int] = None
    updated_at: Optional[datetime] = None
    audit_trail: Optional[List[Dict[str, Any]]] = None
    chain_verification: Optional[Dict[str, Any]] = None

class MemoryCreateResponse(BaseModel):
    id: int
    path: str
    security_alerts: int

class MemoryUpdateResponse(BaseModel):
    success: bool
    security_alerts: int

# ============ Knowledge (Extended) ============

class KnowledgeRevisionResponse(BaseModel):
    id: int
    revision_number: int
    edited_by: str
    change_summary: str
    diff: Optional[str] = None
    created_at: datetime

class KnowledgeRevisionListResponse(BaseModel):
    artifact_id: int
    revisions: List[KnowledgeRevisionResponse]
    count: int

class KnowledgeRenameResponse(BaseModel):
    status: str
    artifact_id: int
    new_title: str

class KnowledgeDeleteResponse(BaseModel):
    status: str
    artifact_id: int

class KnowledgeRestoreResponse(BaseModel):
    status: str
    artifact_id: int
    note: Optional[str] = None

class KnowledgeExportItem(BaseModel):
    id: int
    title: str
    type: str
    domain: str
    source: str
    tags: List[str]
    metadata: Dict[str, Any]
    content: Optional[str] = None

class KnowledgeExportResponse(BaseModel):
    count: int
    items: List[KnowledgeExportItem]

class KnowledgeDiscoveryResponse(BaseModel):
    status: str
    topic: str
    approved: List[str]
    pending_review: List[Dict[str, Any]]
    blocked: List[Dict[str, Any]]

class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int

# ============ Executor (Extended) ============

class ExecutorTaskSubmitResponse(BaseModel):
    task_id: str
    status: str

class ExecutorTaskListResponse(BaseModel):
    tasks: List[Dict[str, Any]]
    count: int

# ============ Meta API (Extended) ============

class MetaSampleCreateResponse(BaseModel):
    success: bool
    created: List[int]
    message: str

class MetaRecommendationStatsResponse(BaseModel):
    pending: int
    approved: int
    rejected: int
    applied: int
    rolled_back: int
    average_effectiveness: float

class MetaPerformanceResponse(BaseModel):
    effectiveness_over_time: List[Dict[str, Any]]
    acceptance_rate: float
    avg_improvement: float
    component_trends: Dict[str, List[Dict[str, Any]]]

class MetaMeasureResponse(BaseModel):
    success: bool
    effectiveness_score: Optional[float] = None
    message: Optional[str] = None

# ============ Autonomy (Extended) ============

class AutonomyStatusResponse(BaseModel):
    tiers: Dict[str, int]
    pending_approvals: int
    total_policies: int

class AutonomyPolicyItem(BaseModel):
    name: str
    description: str
    auto_approved: Optional[bool] = None
    approval_required: Optional[bool] = None
    impact: str

class AutonomyPoliciesResponse(BaseModel):
    tier_1_operational: List[AutonomyPolicyItem]
    tier_2_code_touching: List[AutonomyPolicyItem]
    tier_3_governance: List[AutonomyPolicyItem]

class AutonomyCheckResponse(BaseModel):
    can_execute: bool
    approval_id: Optional[str] = None
    requires_approval: Optional[bool] = None
    tier: Optional[str] = None

class AutonomyApprovalListResponse(RootModel[List[Dict[str, Any]]]):
    root: List[Dict[str, Any]]

class AutonomyApprovalResponse(BaseModel):
    status: str
    approval_id: str

class ShardTaskSubmitResponse(BaseModel):
    task_id: str
    status: str

class ShardQueueResponse(BaseModel):
    queued: int
    completed: int
    tasks: List[Dict[str, Any]]

# ============ Verification Routes (Extended) ============

class ContractItemResponse(BaseModel):
    id: str
    action_type: str
    playbook_id: Optional[str] = None
    status: str
    tier: str
    confidence_score: float
    created_at: Optional[str] = None
    verified_at: Optional[str] = None
    requires_approval: bool

class ContractListResponse(BaseModel):
    contracts: List[ContractItemResponse]

class ContractDetailResponse(BaseModel):
    id: str
    action_type: str
    playbook_id: Optional[str] = None
    run_id: Optional[str] = None
    status: str
    tier: str
    expected_effect: Optional[Dict[str, Any]] = None
    baseline_state: Optional[Dict[str, Any]] = None
    actual_effect: Optional[Dict[str, Any]] = None
    verification_result: Optional[Dict[str, Any]] = None
    confidence_score: float
    safe_hold_snapshot_id: Optional[str] = None
    created_at: Optional[str] = None
    executed_at: Optional[str] = None
    verified_at: Optional[str] = None
    triggered_by: Optional[str] = None

class SnapshotItemResponse(BaseModel):
    id: str
    snapshot_type: str
    status: str
    is_golden: bool
    is_validated: bool
    system_health_score: Optional[float] = None
    created_at: Optional[str] = None
    triggered_by: Optional[str] = None
    action_contract_id: Optional[str] = None
    notes: Optional[str] = None

class SnapshotListResponse(BaseModel):
    snapshots: List[SnapshotItemResponse]

class SnapshotDetailResponse(BaseModel):
    id: str
    snapshot_type: str
    status: str
    is_golden: bool
    is_validated: bool
    manifest: Optional[Dict[str, Any]] = None
    manifest_hash: Optional[str] = None
    storage_uri: Optional[str] = None
    baseline_metrics: Optional[Dict[str, Any]] = None
    system_health_score: Optional[float] = None
    created_at: Optional[str] = None
    validated_at: Optional[str] = None
    restored_at: Optional[str] = None
    triggered_by: Optional[str] = None
    action_contract_id: Optional[str] = None
    playbook_run_id: Optional[str] = None
    notes: Optional[str] = None

class SnapshotRestoreResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    dry_run: Optional[bool] = None
    details: Optional[Dict[str, Any]] = None

class GoldenSnapshotResponse(BaseModel):
    id: str
    snapshot_type: str
    system_health_score: Optional[float] = None
    created_at: Optional[str] = None
    validated_at: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None

class BenchmarkRunItemResponse(BaseModel):
    run_id: str
    benchmark_type: str
    passed: bool
    drift_detected: bool
    is_golden: bool
    duration_seconds: float
    created_at: Optional[str] = None
    triggered_by: Optional[str] = None

class BenchmarkRunListResponse(BaseModel):
    runs: List[BenchmarkRunItemResponse]

class BenchmarkRunDetailResponse(BaseModel):
    run_id: str
    benchmark_type: str
    passed: bool
    drift_detected: bool
    is_golden: bool
    results: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    baseline_id: Optional[str] = None
    delta_from_baseline: Optional[Dict[str, Any]] = None
    duration_seconds: float
    created_at: Optional[str] = None
    triggered_by: Optional[str] = None

class BenchmarkGoldenResponse(BaseModel):
    success: bool
    run_id: str
    status: str

class MissionStartResponse(BaseModel):
    mission_id: str
    mission_name: str
    started_at: Optional[str] = None
    planned_actions: int

class MissionCompleteResponse(BaseModel):
    mission_id: str
    status: str

class MissionHistoryResponse(BaseModel):
    missions: List[Dict[str, Any]]

class VerificationStatusResponse(BaseModel):
    mission: Optional[Dict[str, Any]] = None
    golden_snapshot: Optional[Dict[str, Any]] = None
    contracts: Dict[str, Any]
    timestamp: str

# ============ Tasks (Extended) ============

class TaskListResponse(RootModel[List[TaskResponse]]):
    root: List[TaskResponse]

class TaskUpdateErrorResponse(BaseModel):
    error: str

# ============ Autonomy (Additional) ============

class AutonomyTaskStatusResponse(BaseModel):
    task_id: str
    domain: str
    action: str
    status: str
    priority: int
    result: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class ShardStatusResponse(BaseModel):
    total_shards: int
    active_shards: int
    shards: Dict[str, Any]

# ============ Governance (Additional) ============

class PolicyItem(BaseModel):
    id: int
    name: str
    description: str
    severity: str
    condition: str
    action: str

class AuditLogItem(BaseModel):
    id: int
    actor: str
    action: str
    resource: str
    policy_checked: str
    result: str
    timestamp: datetime

class ConfigItem(BaseModel):
    key: str
    value: str
    type: str
    approved: bool
    last_updated_by: Optional[str] = None

# ============ Meta API (Additional) ============

class MetaAnalysisItem(BaseModel):
    id: int
    type: str
    subject: str
    findings: str
    recommendation: str
    confidence: float
    applied: bool
    created_at: datetime

class MetaMetaEvaluationItem(BaseModel):
    id: int
    metric: str
    before: float
    after: float
    improvement: float
    conclusion: str
    created_at: datetime

class MetaConfigItem(BaseModel):
    key: str
    value: str
    type: str
    approved: bool
    last_updated_by: Optional[str] = None

class MetaRecommendationItem(BaseModel):
    id: int
    recommendation_type: str
    target: str
    current_value: Any
    proposed_value: Any
    recommendation_text: str
    confidence: float
    risk_level: str
    status: str
    created_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

# ============ Cognition API ============

class CognitionIntentParseResponse(BaseModel):
    intent_type: str
    parameters: Dict[str, Any]
    confidence: float
    context: Optional[Dict[str, Any]] = None

class CognitionExecuteResponse(BaseModel):
    plan_id: str
    success: bool
    actions_completed: int
    actions_failed: int
    outputs: Dict[str, Any]
    verification: Optional[Dict[str, Any]] = None
    rollback_available: bool
    confidence: float

class CognitionIntentItemResponse(BaseModel):
    id: int
    utterance: str
    intent_type: str
    status: str
    plan_id: Optional[str] = None
    requires_approval: bool
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class CognitionSessionResponse(BaseModel):
    session_id: str
    intents: List[CognitionIntentItemResponse]

class CognitionRecentIntentItemResponse(BaseModel):
    id: int
    utterance: str
    intent_type: str
    status: str
    confidence: float
    created_at: Optional[str] = None

class CognitionRecentIntentsResponse(BaseModel):
    intents: List[CognitionRecentIntentItemResponse]

class CognitionCapabilitiesResponse(BaseModel):
    capabilities: List[Dict[str, Any]]
    count: int

class CognitionLLMToolsResponse(BaseModel):
    tools: List[Dict[str, Any]]

class CognitionStatusResponse(BaseModel):
    total_intents: int
    completed: int
    failed: int
    success_rate: float
    capabilities_registered: int
    status: str

# ============ Coding Agent API ============

class CodeParseResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    timestamp: str

class CodeContextResponse(BaseModel):
    status: str
    context: Dict[str, Any]
    timestamp: str

class CodeSuggestionsResponse(BaseModel):
    status: str
    suggestions: List[Dict[str, Any]]
    context: Dict[str, Any]
    timestamp: str

class CodeIntentResponse(BaseModel):
    status: str
    intent: Dict[str, Any]
    timestamp: str

class CodeGenerateResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    timestamp: str

class CodeTaskResponse(BaseModel):
    status: str
    task: Dict[str, Any]
    plan: Dict[str, Any]
    message: str
    timestamp: str

class CodeTaskProgressResponse(BaseModel):
    status: str
    progress: Dict[str, Any]
    timestamp: str

class CodeRelatedResponse(BaseModel):
    status: str
    related: List[Dict[str, Any]]
    timestamp: str

class CodePatternsResponse(BaseModel):
    status: str
    patterns: List[Dict[str, Any]]
    count: int
    timestamp: str

class CodeOrchestrationPlanResponse(BaseModel):
    status: str
    plan: Dict[str, Any]
    timestamp: str

class CodeOrchestrationExecuteResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    timestamp: str

# ============ Hunter API ============

class HunterAlertResponse(BaseModel):
    id: int
    timestamp: Optional[str] = None
    severity: str
    rule_name: str
    action_taken: str
    details: str
    user_id: Optional[str] = None

class HunterAlertsResponse(RootModel[List[HunterAlertResponse]]):
    root: List[HunterAlertResponse]

class HunterResolveResponse(BaseModel):
    status: str

class HunterRuleResponse(BaseModel):
    id: int
    name: str
    description: str
    severity: str
    enabled: bool
    pattern: str
    action: str
    created_at: Optional[str] = None

class HunterRulesResponse(RootModel[List[HunterRuleResponse]]):
    root: List[HunterRuleResponse]

class HunterRuleUpdateResponse(BaseModel):
    id: int
    enabled: bool

# ============ Immutable Log API ============

class ImmutableLogEntriesResponse(BaseModel):
    entries: List[Dict[str, Any]]
    count: int

class ImmutableLogVerifyResponse(BaseModel):
    success: bool
    valid: Optional[bool] = None
    errors: Optional[List[str]] = None
    verified_range: Optional[Dict[str, int]] = None

# ============ Temporal API ============

class TemporalPredictionResponse(BaseModel):
    predictions: List[Dict[str, Any]]
    discovered_patterns: List[Dict[str, Any]]
    timestamp: str

class TemporalSimulationResponse(BaseModel):
    simulation_result: Dict[str, Any]
    action: Dict[str, Any]
    iterations: int
    timestamp: str

class TemporalPatternsResponse(BaseModel):
    period: str
    active_patterns: List[Dict[str, Any]]
    historical_patterns: List[Dict[str, Any]]

class TemporalPlanResponse(BaseModel):
    plan: Dict[str, Any]
    goal: str
    timestamp: str

class TemporalDurationEstimateResponse(BaseModel):
    task_type: Optional[str] = None
    estimate: Dict[str, Any]
    source: str

class TemporalDurationsResponse(BaseModel):
    estimates: List[Dict[str, Any]]

class TemporalAnomaliesResponse(BaseModel):
    recent_anomalies: List[Dict[str, Any]]
    historical_anomalies: List[Dict[str, Any]]

class TemporalPeakLoadResponse(BaseModel):
    next_peak: Optional[str] = None
    patterns: List[Dict[str, Any]]
    recommendation: str

class TemporalPreventiveActionsResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    timestamp: str

class TemporalScenariosResponse(BaseModel):
    comparison: Dict[str, Any]
    timestamp: str

class TemporalSimulationDetailResponse(BaseModel):
    id: int
    scenario: str
    parameters: Optional[Dict[str, Any]] = None
    predicted_outcome: Optional[Dict[str, Any]] = None
    actual_outcome: Optional[Dict[str, Any]] = None
    accuracy_score: Optional[float] = None
    created_at: str

class TemporalActualOutcomeResponse(BaseModel):
    success: bool
    comparison: Dict[str, Any]

# ============ Learning API ============

class LearningAggregatesResponse(BaseModel):
    bucket: str
    time_range: str
    total_runs: int
    overall_success_rate: float
    by_status: Dict[str, int]
    by_playbook: Dict[str, Dict[str, Any]]
    by_service: Dict[str, Dict[str, Any]]
    playbook_rankings: List[Dict[str, Any]]
    recent_trends: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class LearningOutcomesResponse(BaseModel):
    outcomes: List[Dict[str, Any]]
    count: int
    service_filter: Optional[str] = None

# ============ Health Routes (Extended) ============

class HealthCheckItemResponse(BaseModel):
    component: str
    status: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    at: Optional[datetime] = None

class HealingActionItemResponse(BaseModel):
    component: str
    action: str
    result: str
    detail: Optional[str] = None
    at: Optional[datetime] = None

class HealthStatusResponse(BaseModel):
    system_mode: str
    mode_reason: Optional[str] = None
    mode_changed: Optional[datetime] = None
    checks: List[HealthCheckItemResponse]
    actions: List[HealingActionItemResponse]

class HealthRestartResponse(BaseModel):
    success: bool
    message: str
    component: str

class HealthModeResponse(BaseModel):
    mode: str
    reason: Optional[str] = None
    changed_at: Optional[datetime] = None

class HealthModeSetResponse(BaseModel):
    status: str
    mode: Optional[str] = None
    reason: Optional[str] = None
    decision: Optional[str] = None

# ============ Verification Routes (Additional) ============

class VerificationSmokeTestResponse(BaseModel):
    success: bool
    tests_run: int
    tests_passed: int
    duration: float

class VerificationRegressionResponse(BaseModel):
    success: bool
    drift_detected: bool
    baseline_compared: bool
    results: Dict[str, Any]
