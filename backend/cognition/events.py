"""Event Definitions for Cognition System

Events emitted to trigger_mesh during feedback integration
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class FeedbackRecorded:
    """Event: Feedback successfully integrated into memory"""
    loop_id: str
    component: str
    memory_ref: str  # Reference to stored memory
    trust_score: float
    compliance_score: float
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_event_payload(self) -> dict:
        """Convert to event payload for trigger_mesh"""
        return {
            'loop_id': self.loop_id,
            'component': self.component,
            'memory_ref': self.memory_ref,
            'trust_score': self.trust_score,
            'compliance_score': self.compliance_score,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class ConstitutionalViolation:
    """Event: Constitutional principle violated"""
    loop_id: str
    component: str
    violation_type: str
    principle_ids: list
    severity: str
    reason: str
    timestamp: datetime
    action_blocked: bool
    
    def to_event_payload(self) -> dict:
        return {
            'loop_id': self.loop_id,
            'component': self.component,
            'violation_type': self.violation_type,
            'principle_ids': self.principle_ids,
            'severity': self.severity,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'action_blocked': self.action_blocked
        }

@dataclass
class TrustScoreUpdated:
    """Event: Trust score computed for output"""
    loop_id: str
    component: str
    trust_score: float
    confidence: float
    evidence_quality: float
    timestamp: datetime
    
    def to_event_payload(self) -> dict:
        return {
            'loop_id': self.loop_id,
            'component': self.component,
            'trust_score': self.trust_score,
            'confidence': self.confidence,
            'evidence_quality': self.evidence_quality,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class MemoryDecayed:
    """Event: Memory importance decayed over time"""
    memory_ref: str
    old_importance: float
    new_importance: float
    decay_factor: float
    timestamp: datetime
    
    def to_event_payload(self) -> dict:
        return {
            'memory_ref': self.memory_ref,
            'old_importance': self.old_importance,
            'new_importance': self.new_importance,
            'decay_factor': self.decay_factor,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class GovernanceEscalation:
    """Event: Output requires parliamentary review"""
    loop_id: str
    component: str
    escalation_reason: str
    verdict: Dict[str, Any]
    timestamp: datetime
    parliament_ticket_id: Optional[str] = None
    
    def to_event_payload(self) -> dict:
        return {
            'loop_id': self.loop_id,
            'component': self.component,
            'escalation_reason': self.escalation_reason,
            'verdict': self.verdict,
            'timestamp': self.timestamp.isoformat(),
            'parliament_ticket_id': self.parliament_ticket_id
        }
