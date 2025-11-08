"""
Extended Pydantic schemas for endpoints missing response_model
All schemas include execution_trace and data_provenance for pipeline traceability
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from .schemas import ExecutionTrace, DataProvenance, SuccessResponse

# ============ External API Responses ============

class GitHubIssueResponse(SuccessResponse):
    """GitHub issue creation response"""
    issue_url: Optional[str] = Field(None, description="URL of created issue")
    issue_number: Optional[int] = Field(None, description="Issue number")

class GitHubReposResponse(BaseModel):
    repos: List[Dict[str, Any]] = Field(description="List of GitHub repositories")
    count: int = Field(description="Number of repositories")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GitHubRepoIssuesResponse(BaseModel):
    issues: List[Dict[str, Any]] = Field(description="List of repository issues")
    count: int = Field(description="Number of issues")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GitHubPRResponse(SuccessResponse):
    """GitHub pull request creation response"""
    pr_url: Optional[str] = Field(None, description="URL of created PR")
    pr_number: Optional[int] = Field(None, description="PR number")

class GitHubCommitsResponse(BaseModel):
    commits: List[Dict[str, Any]] = Field(description="List of repository commits")
    count: int = Field(description="Number of commits")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SlackMessageResponse(SuccessResponse):
    """Slack message send response"""
    channel_id: Optional[str] = Field(None, description="Channel message was sent to")
    message_ts: Optional[str] = Field(None, description="Message timestamp")

class SlackChannelsResponse(BaseModel):
    channels: List[Dict[str, Any]] = Field(description="List of Slack channels")
    count: int = Field(description="Number of channels")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SlackHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]] = Field(description="Channel message history")
    count: int = Field(description="Number of messages")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_S3UploadResponse(SuccessResponse):
    """AWS S3 file upload response"""
    object_key: Optional[str] = Field(None, description="S3 object key")
    bucket: Optional[str] = Field(None, description="S3 bucket name")
    url: Optional[str] = Field(None, description="Object URL")

class AWS_S3DownloadResponse(SuccessResponse):
    """AWS S3 file download response"""
    object_key: Optional[str] = Field(None, description="S3 object key")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")
    content: Optional[str] = Field(None, description="File content if text")

class AWS_S3ListResponse(BaseModel):
    objects: List[Dict[str, Any]] = Field(description="List of S3 objects")
    count: int = Field(description="Number of objects")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_LambdaInvokeResponse(BaseModel):
    status_code: int = Field(description="Lambda invocation status code")
    response_payload: Dict[str, Any] = Field(description="Lambda response")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_LambdaListResponse(BaseModel):
    functions: List[Dict[str, Any]] = Field(description="List of Lambda functions")
    count: int = Field(description="Number of functions")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_EC2InstancesResponse(BaseModel):
    instances: List[Dict[str, Any]] = Field(description="List of EC2 instances")
    count: int = Field(description="Number of instances")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_EC2InstanceStatusResponse(BaseModel):
    instance_id: str = Field(description="Instance ID")
    state: str = Field(description="Instance state")
    details: Dict[str, Any] = Field(description="Instance details")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AWS_CostsResponse(BaseModel):
    period: str = Field(description="Cost report period")
    total_cost: float = Field(description="Total cost")
    by_service: Dict[str, float] = Field(description="Cost breakdown by service")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SecretsListResponse(BaseModel):
    secrets: List[Dict[str, Any]] = Field(description="List of secrets (keys only)")
    count: int = Field(description="Number of secrets")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SecretResponse(BaseModel):
    key: str = Field(description="Secret key")
    value: Optional[str] = Field(None, description="Secret value (only for GET)")
    created_at: Optional[str] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Concurrent API Responses ============

class ConcurrentTaskSubmitResponse(BaseModel):
    task_id: str = Field(description="Unique task identifier")
    domain: str = Field(description="Task domain")
    status: str = Field(description="Initial task status", examples=["queued"])
    position: int = Field(description="Position in queue")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentBatchResponse(BaseModel):
    batch_id: str = Field(description="Batch identifier")
    task_ids: List[str] = Field(description="Task IDs in batch")
    total_tasks: int = Field(description="Number of tasks in batch")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentTaskStatusResponse(BaseModel):
    task_id: str
    domain: str
    status: str
    progress: float = Field(description="Progress 0-100")
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentQueueStatusResponse(BaseModel):
    total_queued: int
    by_domain: Dict[str, int]
    workers_active: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentDomainsResponse(BaseModel):
    domains: List[str]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentDomainMetricsResponse(BaseModel):
    domain: str
    total_tasks: int
    completed: int
    failed: int
    success_rate: float
    avg_duration_ms: float
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConcurrentAllMetricsResponse(BaseModel):
    metrics_by_domain: Dict[str, Dict[str, Any]]
    total_tasks: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Constitutional API Responses ============

class ConstitutionalPrinciplesResponse(BaseModel):
    principles: List[Dict[str, Any]] = Field(description="Constitutional principles")
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalPrincipleResponse(BaseModel):
    id: int
    name: str
    description: str
    priority: int
    active: bool
    violation_count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalViolationsResponse(BaseModel):
    violations: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalViolationStatsResponse(BaseModel):
    total_violations: int
    by_principle: Dict[str, int]
    by_severity: Dict[str, int]
    recent_trend: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalComplianceResponse(BaseModel):
    action_id: str
    compliant: bool
    violations: List[str]
    warnings: List[str]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalCheckResponse(BaseModel):
    decision: str = Field(description="allow, warn, or block")
    compliant: bool
    violated_principles: List[str]
    recommendations: List[str]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalReportResponse(BaseModel):
    period: str
    total_checks: int
    compliant: int
    violations: int
    compliance_rate: float
    top_violations: List[Dict[str, Any]]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalClarificationsResponse(BaseModel):
    clarifications: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalClarificationResponse(BaseModel):
    request_id: str
    principle_id: int
    question: str
    answer: Optional[str] = None
    status: str
    created_at: str
    answered_at: Optional[str] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalStatsResponse(BaseModel):
    total_principles: int
    active_principles: int
    total_checks: int
    compliance_rate: float
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ConstitutionalTenetsResponse(BaseModel):
    tenets: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Causal Graph API Responses ============

class CausalGraphBuildResponse(BaseModel):
    graph_id: str
    nodes_count: int
    edges_count: int
    build_time_ms: float
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalCausesResponse(BaseModel):
    event_id: str
    causes: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalEffectsResponse(BaseModel):
    event_id: str
    effects: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalPathResponse(BaseModel):
    from_event: str
    to_event: str
    path: List[str]
    path_length: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalInfluenceResponse(BaseModel):
    top_influencers: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalCyclesResponse(BaseModel):
    cycles: List[List[str]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalVisualizeResponse(BaseModel):
    visualization: str = Field(description="Mermaid diagram or DOT format")
    format: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalAnalysisResponse(BaseModel):
    analysis_type: str
    findings: Dict[str, Any]
    recommendations: List[str]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CausalPatternsResponse(BaseModel):
    patterns: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Commit Routes Responses ============

class CommitStatusResponse(BaseModel):
    status: str
    workflows_pending: int
    message: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CommitWorkflowsResponse(BaseModel):
    workflows: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Execution API Responses ============

class ExecutionLanguagesResponse(BaseModel):
    languages: List[str]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ExecutionPresetsResponse(BaseModel):
    presets: Dict[str, Any]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class ExecutionValidateResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class EvaluationConfidenceResponse(BaseModel):
    confidence: float
    factors: Dict[str, Any]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class EvaluationResponse(BaseModel):
    evaluation_id: str
    result: Dict[str, Any]
    score: float
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Continue with remaining endpoints... ============

class AgenticInsightsStatusResponse(BaseModel):
    status: str
    total_runs: int
    active_runs: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AgenticInsightsTimelineResponse(BaseModel):
    run_id: str
    timeline: List[Dict[str, Any]]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AgenticInsightsSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class AgenticInsightsHealthResponse(BaseModel):
    status: str
    metrics: Dict[str, Any]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class CognitionRequestResponse(BaseModel):
    request_id: str
    intent_type: str
    plan_id: Optional[str] = None
    status: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Parliament API Responses ============

class ParliamentMemberResponse(SuccessResponse):
    """Parliament member creation/details response"""
    member: Optional[Dict[str, Any]] = Field(None, description="Member details")

class ParliamentMembersListResponse(SuccessResponse):
    """List of parliament members"""
    members: List[Dict[str, Any]] = Field(default_factory=list, description="Member list")

class ParliamentSessionResponse(SuccessResponse):
    """Voting session response"""
    session: Optional[Dict[str, Any]] = Field(None, description="Session details")

class ParliamentSessionsListResponse(SuccessResponse):
    """List of voting sessions"""
    sessions: List[Dict[str, Any]] = Field(default_factory=list, description="Sessions list")

class ParliamentVoteResponse(SuccessResponse):
    """Vote casting response"""
    vote: Optional[Dict[str, Any]] = Field(None, description="Vote details")

class ParliamentSessionStatusResponse(SuccessResponse):
    """Voting session status"""
    status: Optional[Dict[str, Any]] = Field(None, description="Session status details")

class ParliamentCommitteeResponse(SuccessResponse):
    """Committee creation/details response"""
    committee: Optional[Dict[str, Any]] = Field(None, description="Committee details")

class ParliamentCommitteesListResponse(SuccessResponse):
    """List of committees"""
    committees: List[Dict[str, Any]] = Field(default_factory=list, description="Committees list")

class ParliamentStatsResponse(SuccessResponse):
    """Parliament statistics"""
    stats: Optional[Dict[str, Any]] = Field(None, description="Statistics")

class ParliamentMemberStatsResponse(SuccessResponse):
    """Member statistics"""
    stats: Optional[Dict[str, Any]] = Field(None, description="Member statistics")

# ============ Speech API Responses ============

class SpeechUploadResponse(BaseModel):
    speech_id: int = Field(description="Speech message ID")
    status: str = Field(description="Processing status")
    verification_id: Optional[str] = Field(None, description="Verification ID")
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SpeechMessageResponse(BaseModel):
    speech_id: int
    user: str
    transcript: Optional[str] = None
    audio_path: str
    audio_format: str
    status: str
    confidence: Optional[float] = None
    created_at: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SpeechListResponse(BaseModel):
    messages: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SpeechReviewResponse(BaseModel):
    speech_id: int
    approved: bool
    reviewed_by: str
    notes: Optional[str] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SpeechDeleteResponse(BaseModel):
    deleted: bool
    speech_id: int
    approval_id: Optional[int] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class TTSGenerateResponse(BaseModel):
    tts_id: int
    audio_path: str
    status: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Trust API Responses ============

class TrustedSourcesListResponse(BaseModel):
    sources: List[Dict[str, Any]] = Field(description="List of trusted sources")
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class TrustedSourceResponse(BaseModel):
    id: int
    domain: str
    trust_score: float
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class TrustSourceUpdateResponse(BaseModel):
    status: str
    id: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class TrustSourceDeleteResponse(BaseModel):
    status: str
    id: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class TrustScoreResponse(BaseModel):
    url: str
    trust_score: float
    auto_approve: bool
    recommendation: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

# ============ Sandbox API Responses ============

class SandboxFilesListResponse(BaseModel):
    files: List[str]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SandboxFileReadResponse(BaseModel):
    file_path: str
    content: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SandboxFileWriteResponse(SuccessResponse):
    """File write operation response"""
    file_path: Optional[str] = Field(None, description="Written file path")

class SandboxRunResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    success: bool
    security_alerts: int = 0
    issue_id: Optional[int] = None
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class SandboxResetResponse(SuccessResponse):
    """Sandbox reset response"""
    pass

# ============ Grace Architect API Responses ============

class GraceArchitectLearnResponse(BaseModel):
    status: str
    patterns_learned: int
    phases_analyzed: int
    knowledge_depth: str
    message: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectExtendResponse(BaseModel):
    status: str
    request_id: str
    files_generated: int
    constitutional_compliant: bool
    ready_to_deploy: bool
    code: Dict[str, Any]
    tests: Dict[str, Any]
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectPatternsResponse(BaseModel):
    patterns: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectExtensionsListResponse(BaseModel):
    extensions: List[Dict[str, Any]]
    count: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectExtensionResponse(BaseModel):
    request_id: str
    feature_request: str
    business_need: Optional[str] = None
    status: str
    code_generated: Optional[Dict[str, Any]] = None
    tests_generated: Optional[Dict[str, Any]] = None
    implementation_plan: Optional[Dict[str, Any]] = None
    constitutional_compliant: bool
    deployed: bool
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectDeployResponse(BaseModel):
    status: str
    extension_id: Optional[str] = None
    parliament_session: Optional[str] = None
    message: str
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)

class GraceArchitectKnowledgeResponse(BaseModel):
    knowledge: List[Dict[str, Any]]
    total: int
    execution_trace: Optional[ExecutionTrace] = None
    data_provenance: List[DataProvenance] = Field(default_factory=list)
