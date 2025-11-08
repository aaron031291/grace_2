"""Standardized Output Format for All Grace Components

One schema everywhere - enables governance linting, memory scoring,
and reproducible audit trails without per-component adapters.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class OutputType(Enum):
    """Type of loop output"""
    REASONING = "reasoning"
    DECISION = "decision"
    OBSERVATION = "observation"
    ACTION = "action"
    REFLECTION = "reflection"
    PREDICTION = "prediction"
    GENERATION = "generation"

class ConfidenceLevel(Enum):
    """Confidence in output"""
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30

@dataclass
class Citation:
    """Source citation for claims"""
    source: str  # memory_ref, knowledge_artifact, model_name
    confidence: float
    excerpt: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class PolicyTag:
    """Governance policy tag"""
    policy_name: str
    status: str  # compliant, requires_review, violation
    reason: Optional[str] = None

@dataclass
class Diagnostic:
    """Diagnostic information for debugging"""
    level: str  # info, warning, error, critical
    message: str
    component: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraceLoopOutput:
    """
    Standardized output format for ALL Grace components
    
    This is THE schema that flows through:
    - Specialists -> Quorum -> Governance -> FeedbackIntegrator -> Memory
    """
    
    # Identity
    loop_id: str  # Which loop produced this
    component: str  # Which component (reflection, hunter, meta, causal, etc.)
    output_type: OutputType
    
    # Primary content
    result: Any  # The actual output (string, dict, list, etc.)
    reasoning_chain_id: Optional[str] = None  # Links to detailed reasoning
    
    # Confidence & quality
    confidence: float = 1.0  # 0.0 (very uncertain) to 1.0 (certain)
    quality_score: Optional[float] = None  # 0.0-1.0 quality assessment
    
    # Evidence & citations
    citations: List[Citation] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    
    # Governance & policy
    policy_tags: List[PolicyTag] = field(default_factory=list)
    constitutional_compliance: bool = True
    requires_approval: bool = False
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Diagnostics
    diagnostics: List[Diagnostic] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[int] = None
    
    # Verification
    verification_envelope_id: Optional[str] = None
    audit_log_id: Optional[int] = None
    
    # Memory hints
    importance: float = 0.5  # Suggested importance for memory storage
    expires_at: Optional[datetime] = None  # Optional TTL
    
    def add_citation(self, source: str, confidence: float, excerpt: str = None):
        """Add a citation to this output"""
        self.citations.append(Citation(
            source=source,
            confidence=confidence,
            excerpt=excerpt,
            timestamp=datetime.utcnow()
        ))
    
    def add_policy_tag(self, policy_name: str, status: str, reason: str = None):
        """Add governance policy tag"""
        self.policy_tags.append(PolicyTag(
            policy_name=policy_name,
            status=status,
            reason=reason
        ))
    
    def add_diagnostic(self, level: str, message: str, component: str, metadata: Dict = None):
        """Add diagnostic information"""
        self.diagnostics.append(Diagnostic(
            level=level,
            message=message,
            component=component,
            metadata=metadata or {}
        ))
    
    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)
    
    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'loop_id': self.loop_id,
            'component': self.component,
            'output_type': self.output_type.value,
            'result': self.result,
            'reasoning_chain_id': self.reasoning_chain_id,
            'confidence': self.confidence,
            'quality_score': self.quality_score,
            'citations': [
                {
                    'source': c.source,
                    'confidence': c.confidence,
                    'excerpt': c.excerpt,
                    'timestamp': c.timestamp.isoformat() if c.timestamp else None
                }
                for c in self.citations
            ],
            'evidence': self.evidence,
            'policy_tags': [
                {
                    'policy_name': p.policy_name,
                    'status': p.status,
                    'reason': p.reason
                }
                for p in self.policy_tags
            ],
            'constitutional_compliance': self.constitutional_compliance,
            'requires_approval': self.requires_approval,
            'context': self.context,
            'metadata': self.metadata,
            'diagnostics': [
                {
                    'level': d.level,
                    'message': d.message,
                    'component': d.component,
                    'timestamp': d.timestamp.isoformat(),
                    'metadata': d.metadata
                }
                for d in self.diagnostics
            ],
            'warnings': self.warnings,
            'errors': self.errors,
            'created_at': self.created_at.isoformat(),
            'processing_time_ms': self.processing_time_ms,
            'verification_envelope_id': self.verification_envelope_id,
            'audit_log_id': self.audit_log_id,
            'importance': self.importance,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraceLoopOutput':
        """Create from dictionary"""
        # TODO: Implement full deserialization
        return cls(
            loop_id=data['loop_id'],
            component=data['component'],
            output_type=OutputType(data['output_type']),
            result=data['result'],
            confidence=data.get('confidence', 1.0)
        )
