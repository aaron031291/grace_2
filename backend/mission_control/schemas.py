"""
Mission Control Schemas
Pydantic models for mission packages, diagnostics, and orchestration

Compliant with ISO/SOC/NIST requirements for traceability and governance
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Literal
from datetime import datetime
from enum import Enum


# ========== Enums ==========

class Severity(str, Enum):
    """Mission severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MissionStatus(str, Enum):
    """Mission lifecycle states"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_VALIDATION = "awaiting_validation"
    OBSERVING = "observing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    FAILED = "failed"


class MemoryWriteScope(str, Enum):
    """Memory access levels"""
    READ_ONLY = "read_only"
    PROPOSE = "propose"
    PERSIST = "persist"


class Comparator(str, Enum):
    """Metric comparison operators"""
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    EQ = "=="
    NEQ = "!="


# ========== Sub-Models ==========

class MissionContext(BaseModel):
    """Context about the environment and state"""
    git_sha: str = Field(..., description="Current git commit SHA")
    config_hash: str = Field(..., description="Hash of current configuration")
    env: Literal["dev", "stage", "prod"] = Field(..., description="Environment")
    previous_mission_id: Optional[str] = Field(None, description="Related previous mission")
    branch: Optional[str] = Field(None, description="Git branch")
    version: Optional[str] = Field(None, description="Grace version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "git_sha": "a1b2c3d4e5f6",
                "config_hash": "sha256:abc123",
                "env": "prod",
                "branch": "main",
                "version": "2.0.0"
            }
        }


class Symptom(BaseModel):
    """A symptom or anomaly detected"""
    description: str = Field(..., min_length=1)
    metric_id: Optional[str] = None
    observed_value: Optional[float] = None
    threshold: Optional[float] = None
    log_snippet: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class EvidenceLog(BaseModel):
    """Log file evidence"""
    path: str = Field(..., description="Path to log file")
    excerpt: str = Field(..., min_length=1, description="Relevant log excerpt")
    line_number: Optional[int] = None
    timestamp: Optional[datetime] = None


class TestResult(BaseModel):
    """Test execution result"""
    test_id: str = Field(..., description="Test identifier")
    passed: bool
    elapsed_seconds: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    evidence_path: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class MetricObservation(BaseModel):
    """Metric observation at a point in time"""
    metric_id: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    unit: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Evidence bundle for a mission"""
    logs: List[EvidenceLog] = Field(default_factory=list)
    diagnostics_report_id: Optional[str] = None
    stress_test_id: Optional[str] = None
    test_results: List[TestResult] = Field(default_factory=list)
    metrics_snapshot: List[MetricObservation] = Field(default_factory=list)
    screenshots: List[str] = Field(default_factory=list)
    artifacts: Dict[str, str] = Field(default_factory=dict)


class MetricTarget(BaseModel):
    """Target threshold for a metric"""
    metric_id: str = Field(..., description="Metric identifier from catalog")
    comparator: Comparator
    target: float
    rolling_window_minutes: int = Field(default=10, ge=1)
    
    def evaluate(self, observed_value: float) -> bool:
        """Evaluate if observed value meets target"""
        if self.comparator == Comparator.LT:
            return observed_value < self.target
        elif self.comparator == Comparator.LTE:
            return observed_value <= self.target
        elif self.comparator == Comparator.GT:
            return observed_value > self.target
        elif self.comparator == Comparator.GTE:
            return observed_value >= self.target
        elif self.comparator == Comparator.EQ:
            return abs(observed_value - self.target) < 0.0001
        elif self.comparator == Comparator.NEQ:
            return abs(observed_value - self.target) >= 0.0001
        return False


class AcceptanceCriteria(BaseModel):
    """Criteria that must be met to resolve mission"""
    must_pass_tests: List[str] = Field(default_factory=list, description="Required test IDs")
    metric_targets: List[MetricTarget] = Field(default_factory=list)
    observation_window_minutes: int = Field(default=30, ge=1)
    require_human_approval: bool = Field(default=False)
    max_attempts: int = Field(default=3, ge=1)


class PatchCandidate(BaseModel):
    """A proposed code change"""
    path: str = Field(..., description="File path relative to repo root")
    diff: str = Field(..., description="Git diff or patch content")
    justification: str = Field(..., min_length=1)
    risk_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reviewed_by: Optional[str] = None
    approved: bool = Field(default=False)


class Dependency(BaseModel):
    """A dependency to install or update"""
    package: str
    version: str
    source: Literal["pip", "apt", "npm", "cargo", "manual"] = "pip"
    signature: Optional[str] = None
    verified: bool = Field(default=False)


class WorkspaceInfo(BaseModel):
    """Workspace information for mission execution"""
    repo_path: str = Field(..., description="Path to repository")
    working_branch: str = Field(..., description="Branch for changes")
    patch_candidates: List[PatchCandidate] = Field(default_factory=list)
    dependencies: List[Dependency] = Field(default_factory=list)
    backup_sha: Optional[str] = Field(None, description="SHA to rollback to")


class TrustRequirements(BaseModel):
    """Trust and permission requirements"""
    required_trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    allowed_roles: List[str] = Field(default_factory=list)
    memory_write_scope: MemoryWriteScope = MemoryWriteScope.READ_ONLY
    requires_governance_approval: bool = Field(default=True)
    requires_crypto_signature: bool = Field(default=True)


class CryptoSignature(BaseModel):
    """Cryptographic signature for verification"""
    component_id: str = Field(..., description="ID of signing component")
    signature: str = Field(..., description="Ed25519 signature")
    signed_at: datetime = Field(default_factory=datetime.utcnow)
    public_key: Optional[str] = None
    verified: bool = Field(default=False)


class RemediationEvent(BaseModel):
    """A remediation action taken"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = Field(..., description="Agent or user ID")
    role: Literal["agent", "sub_agent", "human", "system"]
    action: str = Field(..., description="Action taken")
    result: str = Field(..., description="Result of action")
    diagnostics_id: Optional[str] = None
    stress_result_id: Optional[str] = None
    success: bool = Field(default=False)
    error_message: Optional[str] = None


# ========== Main Mission Package ==========

class MissionPackage(BaseModel):
    """
    Complete mission package for autonomous coding/healing
    
    This is the contract between Mission Control and all agents.
    Every mission follows this schema for full traceability.
    """
    
    # Core identification
    mission_id: str = Field(..., description="Unique mission identifier")
    subsystem_id: str = Field(..., description="Target subsystem (e.g., trigger_mesh)")
    severity: Severity
    
    # Lifecycle
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    detected_by: str = Field(..., description="Component that detected issue")
    assigned_to: str = Field(..., description="Agent assigned to mission")
    status: MissionStatus = MissionStatus.OPEN
    
    # Context
    context: MissionContext
    
    # Problem definition
    symptoms: List[Symptom] = Field(default_factory=list)
    evidence: Evidence = Field(default_factory=Evidence)
    
    # Success criteria
    acceptance_criteria: AcceptanceCriteria
    
    # Execution history
    remediation_history: List[RemediationEvent] = Field(default_factory=list)
    
    # Workspace
    workspace: WorkspaceInfo
    
    # Security & governance
    trust_requirements: TrustRequirements = Field(default_factory=TrustRequirements)
    crypto_signatures: List[CryptoSignature] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    # Related missions
    parent_mission_id: Optional[str] = None
    child_mission_ids: List[str] = Field(default_factory=list)
    
    # Tags for search/filtering
    tags: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "mission_id": "mission_20250110_001",
                "subsystem_id": "trigger_mesh",
                "severity": "high",
                "detected_by": "diagnostics_suite",
                "assigned_to": "elite_coding_agent",
                "status": "open",
                "context": {
                    "git_sha": "a1b2c3d4",
                    "config_hash": "sha256:abc123",
                    "env": "prod",
                    "branch": "main"
                },
                "symptoms": [
                    {
                        "description": "Event delivery latency > 100ms",
                        "metric_id": "trigger_mesh.latency_p95",
                        "observed_value": 150.5,
                        "threshold": 100.0
                    }
                ],
                "acceptance_criteria": {
                    "must_pass_tests": ["test_trigger_mesh_latency"],
                    "metric_targets": [
                        {
                            "metric_id": "trigger_mesh.latency_p95",
                            "comparator": "<",
                            "target": 100.0
                        }
                    ],
                    "observation_window_minutes": 30
                },
                "workspace": {
                    "repo_path": "/app",
                    "working_branch": "fix/trigger_mesh_latency"
                },
                "trust_requirements": {
                    "required_trust_score": 0.8,
                    "allowed_roles": ["elite_coding_agent"],
                    "memory_write_scope": "persist"
                }
            }
        }
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v):
        """Always update timestamp"""
        return datetime.utcnow()
    
    def add_remediation_event(
        self,
        actor: str,
        role: str,
        action: str,
        result: str,
        success: bool = False,
        **kwargs
    ):
        """Add a remediation event to history"""
        event = RemediationEvent(
            actor=actor,
            role=role,
            action=action,
            result=result,
            success=success,
            **kwargs
        )
        self.remediation_history.append(event)
        self.updated_at = datetime.utcnow()
    
    def add_signature(self, component_id: str, signature: str, public_key: Optional[str] = None):
        """Add cryptographic signature"""
        sig = CryptoSignature(
            component_id=component_id,
            signature=signature,
            public_key=public_key
        )
        self.crypto_signatures.append(sig)
        self.updated_at = datetime.utcnow()
    
    def evaluate_acceptance_criteria(self, test_results: List[TestResult], metrics: List[MetricObservation]) -> bool:
        """
        Evaluate if acceptance criteria are met
        
        Returns:
            True if all criteria pass, False otherwise
        """
        # Check required tests
        test_ids = {t.test_id for t in test_results}
        for required_test in self.acceptance_criteria.must_pass_tests:
            if required_test not in test_ids:
                return False
            # Check if test passed
            test = next((t for t in test_results if t.test_id == required_test), None)
            if not test or not test.passed:
                return False
        
        # Check metric targets
        for target in self.acceptance_criteria.metric_targets:
            # Find matching metric
            metric = next((m for m in metrics if m.metric_id == target.metric_id), None)
            if not metric:
                return False
            if not target.evaluate(metric.value):
                return False
        
        return True
    
    def can_agent_execute(self, agent_id: str, agent_role: str, trust_score: float) -> bool:
        """Check if agent has permission to execute this mission"""
        # Check trust score
        if trust_score < self.trust_requirements.required_trust_score:
            return False
        
        # Check role
        if self.trust_requirements.allowed_roles and agent_role not in self.trust_requirements.allowed_roles:
            return False
        
        return True


# ========== Health & Status Models ==========

class SubsystemHealth(BaseModel):
    """Health status of a subsystem"""
    subsystem_id: str
    status: Literal["healthy", "degraded", "critical", "unknown"]
    last_check: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = Field(default_factory=dict)
    active_missions: List[str] = Field(default_factory=list)
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0)


class MissionControlStatus(BaseModel):
    """Overall Mission Control status"""
    git_sha: str
    git_branch: str
    grace_version: str
    environment: str
    
    total_missions: int
    open_missions: int
    in_progress_missions: int
    resolved_missions: int
    
    subsystems: List[SubsystemHealth]
    
    diagnostics_reports_count: int
    stress_test_results_count: int
    capa_tickets_count: int
    
    overall_health: Literal["healthy", "degraded", "critical"]
    last_updated: datetime = Field(default_factory=datetime.utcnow)

