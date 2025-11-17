"""Cognition System Data Models

Consensus, linting, and specialist coordination models.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from .GraceLoopOutput import GraceLoopOutput

class RiskLevel(Enum):
    """Risk level for decision tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DecisionStrategy(Enum):
    """Consensus decision strategies"""
    MAJORITY = "majority"
    SOFTMAX_WEIGHTED = "softmax_weighted"
    MIN_RISK = "min_risk"
    UNANIMOUS = "unanimous"

class ViolationSeverity(Enum):
    """Severity of linting violations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SpecialistProposal:
    """A proposal from a specialist component"""
    specialist_name: str  # reflection, hunter, meta, causal, mldl
    output: GraceLoopOutput
    trust_score: float  # Component reputation 0.0-1.0
    track_record: float  # Historical accuracy 0.0-1.0
    recency_weight: float  # Recent performance 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DecisionTask:
    """A task requiring specialist consensus"""
    task_id: str
    description: str
    context: Dict[str, Any]
    specialist_proposals: List[SpecialistProposal] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)  # Governance requirements
    risk_level: RiskLevel = RiskLevel.MEDIUM
    deadline: Optional[datetime] = None
    strategy: DecisionStrategy = DecisionStrategy.SOFTMAX_WEIGHTED
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConsensusDecision:
    """Result of quorum deliberation"""
    task_id: str
    chosen_proposal: GraceLoopOutput
    rationale: str
    weights: Dict[str, float]  # Specialist -> weight mapping
    dissent: List[GraceLoopOutput] = field(default_factory=list)
    confidence: float = 0.0  # Overall decision confidence
    governance_validated: bool = False
    strategy_used: DecisionStrategy = DecisionStrategy.SOFTMAX_WEIGHTED
    voting_summary: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'chosen_proposal': self.chosen_proposal.to_dict(),
            'rationale': self.rationale,
            'weights': self.weights,
            'dissent': [d.to_dict() for d in self.dissent],
            'confidence': self.confidence,
            'governance_validated': self.governance_validated,
            'strategy_used': self.strategy_used.value,
            'voting_summary': self.voting_summary,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class Violation:
    """A linting violation found"""
    violation_type: str  # conflict, policy_drift, causal_mismatch, temporal_inconsistency
    severity: ViolationSeverity
    description: str
    location: str  # Where in output
    conflicting_items: List[str] = field(default_factory=list)
    suggested_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Patch:
    """A suggested fix for a violation"""
    patch_id: str
    violation_type: str
    action: str  # merge, remove, replace, escalate
    target: str  # What to patch
    replacement: Optional[Any] = None
    confidence: float = 0.0
    rationale: str = ""
    safe_to_auto_apply: bool = False

@dataclass
class LintReport:
    """Result of cognition linting"""
    output_id: str  # ID of linted output
    severity: ViolationSeverity
    violations: List[Violation] = field(default_factory=list)
    suggested_fixes: List[Patch] = field(default_factory=list)
    auto_remediable: bool = False
    passed: bool = True
    summary: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'output_id': self.output_id,
            'severity': self.severity.value,
            'violations': [
                {
                    'type': v.violation_type,
                    'severity': v.severity.value,
                    'description': v.description,
                    'location': v.location,
                    'conflicting_items': v.conflicting_items,
                    'suggested_action': v.suggested_action
                }
                for v in self.violations
            ],
            'suggested_fixes': [
                {
                    'patch_id': p.patch_id,
                    'violation_type': p.violation_type,
                    'action': p.action,
                    'target': p.target,
                    'confidence': p.confidence,
                    'safe_to_auto_apply': p.safe_to_auto_apply
                }
                for p in self.suggested_fixes
            ],
            'auto_remediable': self.auto_remediable,
            'passed': self.passed,
            'summary': self.summary,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class GovernanceVerdict:
    """Result of constitutional validation"""
    decision: str  # ALLOW, DENY, ESCALATE
    tags: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    reason: str = ""
    compliance_score: float = 1.0

@dataclass
class GovernanceDecision:
    """Detailed governance decision with metadata"""
    verdict: GovernanceVerdict
    output_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RemediationAction:
    """A remediation action to fix governance issues"""
    action_type: str
    description: str
    priority: str = "medium"
    auto_executable: bool = False

# Re-export memory models for convenience
