"""Data Models for Cognition System"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class GovernanceDecision(Enum):
    """Governance verdict decision"""
    GO = "go"  # Action approved
    BLOCK = "block"  # Action denied
    DEGRADE = "degrade"  # Action allowed with reduced trust
    ESCALATE = "escalate"  # Requires human/parliament review

class RemediationAction(Enum):
    """Actions to remediate policy violations"""
    REDACT = "redact"  # Remove sensitive information
    DOWNGRADE = "downgrade"  # Reduce trust score
    BLOCK = "block"  # Prevent action execution
    ESCALATE = "escalate"  # Send to Parliament
    LOG = "log"  # Log violation only
    NOTIFY = "notify"  # Notify user

@dataclass
class GovernanceVerdict:
    """
    Constitutional governance verdict for a GraceLoopOutput
    
    Issued by GovernancePrimeDirective before any action is taken
    """
    
    # Decision
    decision: GovernanceDecision
    
    # Policy tags
    tags: List[str]  # ['requires_human_review', 'restricted_context', etc.]
    
    # Remediation actions to take
    remediation_actions: List[RemediationAction]
    
    # Explanation
    reason: str
    
    # Constitutional principles checked
    constitutional_checks: List[int]  # Principle IDs
    
    # Compliance score (0.0 = complete violation, 1.0 = full compliance)
    compliance_score: float
    
    # Additional metadata
    severity: str = "info"  # info, warning, critical
    requires_approval: bool = False
    safe_to_store: bool = True  # Can this be stored in memory?
    
    def is_approved(self) -> bool:
        """Check if action is approved"""
        return self.decision in [GovernanceDecision.GO, GovernanceDecision.DEGRADE]
    
    def needs_escalation(self) -> bool:
        """Check if requires escalation"""
        return self.decision == GovernanceDecision.ESCALATE or self.requires_approval
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'decision': self.decision.value,
            'tags': self.tags,
            'remediation_actions': [a.value for a in self.remediation_actions],
            'reason': self.reason,
            'constitutional_checks': self.constitutional_checks,
            'compliance_score': self.compliance_score,
            'severity': self.severity,
            'requires_approval': self.requires_approval,
            'safe_to_store': self.safe_to_store
        }

# Database models for LoopMemoryBank (placeholders - will be integrated with actual DB)
@dataclass
class MemoryArtifact:
    """Database model for stored memory artifacts"""
    id: int
    memory_ref: str
    loop_id: str
    component: str
    output_type: str
    result_json: str
    trust_score: float
    importance: float
    created_at: str
    last_accessed_at: Optional[str] = None
    access_count: int = 0
    archived: bool = False

@dataclass
class TrustEvent:
    """Trust score update event"""
    id: int
    memory_ref: str
    event_type: str
    old_trust: float
    new_trust: float
    reason: str
    timestamp: str

@dataclass
class MemoryIndex:
    """Index for fast memory retrieval"""
    id: int
    memory_ref: str
    component: str
    output_type: str
    keywords: str
    created_at: str

@dataclass
class GarbageCollectionLog:
    """GC operation log"""
    id: int
    policy_name: str
    artifacts_archived: int
    artifacts_deleted: int
    timestamp: str
    details_json: str
