"""
Mission Manifest System
Every user thread becomes a governed mission with intent, constraints, and KPIs
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class MissionStatus(Enum):
    """Mission lifecycle states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFICATION = "verification"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class RiskLevel(Enum):
    """Mission risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MissionKPI:
    """Key Performance Indicator for a mission"""
    name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    met: bool = False
    
    def update(self, value: float):
        """Update KPI value and check if met"""
        self.current_value = value
        self.met = self.current_value >= self.target_value
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'unit': self.unit,
            'met': self.met,
            'progress': min(100, (self.current_value / self.target_value * 100)) if self.target_value > 0 else 0
        }


@dataclass
class MissionManifest:
    """
    Complete mission specification with governance
    
    Every user interaction becomes a mission with:
    - Clear intent
    - Constraints
    - KPIs to measure success
    - Dependencies
    - Risk assessment
    """
    
    # Identity
    mission_id: str = field(default_factory=lambda: f"mission_{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Core
    intent: str = ""  # What user wants to achieve
    user_query: str = ""  # Original user input
    
    # Classification
    status: MissionStatus = MissionStatus.PENDING
    risk_level: RiskLevel = RiskLevel.MEDIUM
    priority: int = 5  # 1-10
    
    # Constraints
    max_token_budget: int = 100_000
    max_duration_seconds: int = 300
    requires_approval: bool = False
    governance_required: bool = True
    
    # KPIs
    kpis: List[MissionKPI] = field(default_factory=list)
    
    # Dependencies
    required_models: List[str] = field(default_factory=list)
    required_data_sources: List[str] = field(default_factory=list)
    depends_on_missions: List[str] = field(default_factory=list)
    
    # Governance
    sovereignty_requirement: float = 0.8  # 80% open source minimum
    min_trust_score: float = 0.7
    verification_required: bool = True
    quorum_size: int = 3  # Number of models for consensus
    
    # Execution
    assigned_agent: Optional[str] = None
    sub_missions: List[str] = field(default_factory=list)
    
    # Results
    token_count: int = 0
    duration_seconds: float = 0.0
    trust_score: Optional[float] = None
    confidence: Optional[float] = None
    
    # Evidence trail
    citations: List[str] = field(default_factory=list)
    verification_chain: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    escalation_reason: Optional[str] = None
    
    # Audit
    completed_at: Optional[str] = None
    approved_by: Optional[str] = None
    
    def add_kpi(self, name: str, target: float, unit: str = ""):
        """Add a KPI to track"""
        self.kpis.append(MissionKPI(name=name, target_value=target, unit=unit))
    
    def update_kpi(self, name: str, value: float):
        """Update KPI value"""
        for kpi in self.kpis:
            if kpi.name == name:
                kpi.update(value)
                break
    
    def all_kpis_met(self) -> bool:
        """Check if all KPIs are met"""
        return all(kpi.met for kpi in self.kpis) if self.kpis else False
    
    def kpi_progress(self) -> float:
        """Overall KPI progress percentage"""
        if not self.kpis:
            return 100.0
        met_count = sum(1 for kpi in self.kpis if kpi.met)
        return (met_count / len(self.kpis)) * 100
    
    def is_within_budget(self) -> bool:
        """Check if within token budget"""
        return self.token_count <= self.max_token_budget
    
    def is_within_time(self) -> bool:
        """Check if within time budget"""
        return self.duration_seconds <= self.max_duration_seconds
    
    def needs_escalation(self) -> bool:
        """Check if mission needs human escalation"""
        return (
            not self.is_within_budget() or
            not self.is_within_time() or
            (self.trust_score is not None and self.trust_score < self.min_trust_score) or
            len(self.warnings) > 3 or
            self.status == MissionStatus.FAILED
        )
    
    def can_proceed(self) -> bool:
        """Check if mission can proceed to next stage"""
        if self.requires_approval and not self.approved_by:
            return False
        if not self.is_within_budget() or not self.is_within_time():
            return False
        if self.trust_score is not None and self.trust_score < self.min_trust_score:
            return False
        return True
    
    def mark_completed(self, trust_score: float, confidence: float):
        """Mark mission as completed"""
        self.status = MissionStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat()
        self.trust_score = trust_score
        self.confidence = confidence
    
    def mark_failed(self, reason: str):
        """Mark mission as failed"""
        self.status = MissionStatus.FAILED
        self.escalation_reason = reason
        self.warnings.append(f"Failed: {reason}")
    
    def escalate(self, reason: str):
        """Escalate mission for human review"""
        self.status = MissionStatus.ESCALATED
        self.escalation_reason = reason
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/logging"""
        return {
            'mission_id': self.mission_id,
            'created_at': self.created_at,
            'intent': self.intent,
            'user_query': self.user_query,
            'status': self.status.value,
            'risk_level': self.risk_level.value,
            'priority': self.priority,
            'constraints': {
                'max_token_budget': self.max_token_budget,
                'max_duration_seconds': self.max_duration_seconds,
                'requires_approval': self.requires_approval,
                'governance_required': self.governance_required
            },
            'kpis': [kpi.to_dict() for kpi in self.kpis],
            'kpi_progress': self.kpi_progress(),
            'all_kpis_met': self.all_kpis_met(),
            'dependencies': {
                'required_models': self.required_models,
                'required_data_sources': self.required_data_sources,
                'depends_on_missions': self.depends_on_missions
            },
            'governance': {
                'sovereignty_requirement': self.sovereignty_requirement,
                'min_trust_score': self.min_trust_score,
                'verification_required': self.verification_required,
                'quorum_size': self.quorum_size
            },
            'execution': {
                'assigned_agent': self.assigned_agent,
                'sub_missions': self.sub_missions,
                'token_count': self.token_count,
                'duration_seconds': self.duration_seconds
            },
            'results': {
                'trust_score': self.trust_score,
                'confidence': self.confidence,
                'citations': self.citations,
                'verification_chain': self.verification_chain,
                'warnings': self.warnings
            },
            'status_checks': {
                'within_budget': self.is_within_budget(),
                'within_time': self.is_within_time(),
                'needs_escalation': self.needs_escalation(),
                'can_proceed': self.can_proceed()
            },
            'completed_at': self.completed_at,
            'approved_by': self.approved_by,
            'escalation_reason': self.escalation_reason
        }


def create_mission_from_query(
    user_query: str,
    intent: str,
    risk_level: RiskLevel = RiskLevel.MEDIUM,
    required_models: Optional[List[str]] = None
) -> MissionManifest:
    """
    Create a mission manifest from user query
    
    Args:
        user_query: User's original input
        intent: Parsed intent/goal
        risk_level: Assessed risk level
        required_models: Models needed for this mission
    
    Returns:
        MissionManifest ready to execute
    """
    
    manifest = MissionManifest(
        user_query=user_query,
        intent=intent,
        risk_level=risk_level,
        required_models=required_models or []
    )
    
    # Set defaults based on risk level
    if risk_level == RiskLevel.CRITICAL:
        manifest.requires_approval = True
        manifest.quorum_size = 5
        manifest.min_trust_score = 0.9
        manifest.sovereignty_requirement = 0.95
    elif risk_level == RiskLevel.HIGH:
        manifest.quorum_size = 4
        manifest.min_trust_score = 0.8
        manifest.sovereignty_requirement = 0.9
    elif risk_level == RiskLevel.MEDIUM:
        manifest.quorum_size = 3
        manifest.min_trust_score = 0.7
        manifest.sovereignty_requirement = 0.8
    else:  # LOW
        manifest.quorum_size = 2
        manifest.min_trust_score = 0.6
        manifest.sovereignty_requirement = 0.7
    
    # Add default KPIs
    manifest.add_kpi("citation_coverage", 0.8, "%")
    manifest.add_kpi("evidence_ratio", 0.7, "%")
    manifest.add_kpi("verification_depth", 2.0, "layers")
    
    return manifest
