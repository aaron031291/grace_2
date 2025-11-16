"""
Trust Score Calculation System
Implements: truth × governance × sovereignty × workflow_integrity
"""

from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class TrustLevel(Enum):
    """Trust level categories"""
    VERY_LOW = "very_low"  # < 0.3
    LOW = "low"  # 0.3 - 0.5
    MEDIUM = "medium"  # 0.5 - 0.7
    HIGH = "high"  # 0.7 - 0.85
    VERY_HIGH = "very_high"  # 0.85 - 1.0


@dataclass
class TrustScore:
    """
    Complete trust score with component breakdown
    
    Formula: trust = truth × governance × sovereignty × workflow_integrity
    """
    
    # Component scores (0.0 to 1.0)
    truth_score: float  # Factual accuracy, citation quality
    governance_score: float  # Policy compliance, approval status
    sovereignty_score: float  # Open source ratio, local processing
    workflow_integrity_score: float  # Process adherence, audit trail
    
    # Composite
    composite_score: float  # Product of all components
    trust_level: TrustLevel
    
    # Metadata
    calculated_at: str
    model_used: str
    context_window_used: int
    confidence: Optional[float] = None
    
    # Evidence
    citations: List[str] = None
    verification_chain: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.verification_chain is None:
            self.verification_chain = []
        if self.warnings is None:
            self.warnings = []
    
    def needs_human_review(self) -> bool:
        """Check if human review is required"""
        return (
            self.composite_score < 0.7 or
            self.truth_score < 0.6 or
            self.governance_score < 0.8 or
            len(self.warnings) > 2
        )
    
    def can_auto_approve(self) -> bool:
        """Check if can auto-approve without review"""
        return (
            self.composite_score >= 0.85 and
            self.truth_score >= 0.8 and
            self.governance_score >= 0.9 and
            len(self.warnings) == 0
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'truth_score': self.truth_score,
            'governance_score': self.governance_score,
            'sovereignty_score': self.sovereignty_score,
            'workflow_integrity_score': self.workflow_integrity_score,
            'composite_score': self.composite_score,
            'trust_level': self.trust_level.value,
            'calculated_at': self.calculated_at,
            'model_used': self.model_used,
            'context_window_used': self.context_window_used,
            'confidence': self.confidence,
            'citations': self.citations,
            'verification_chain': self.verification_chain,
            'warnings': self.warnings,
            'needs_human_review': self.needs_human_review(),
            'can_auto_approve': self.can_auto_approve()
        }


def calculate_trust_score(
    truth: float,
    governance: float,
    sovereignty: float,
    workflow_integrity: float,
    model_used: str,
    context_window_used: int,
    confidence: Optional[float] = None,
    citations: Optional[List[str]] = None,
    verification_chain: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None
) -> TrustScore:
    """
    Calculate composite trust score
    
    Args:
        truth: Factual accuracy (0-1)
        governance: Policy compliance (0-1)
        sovereignty: Open source ratio (0-1)
        workflow_integrity: Process adherence (0-1)
        model_used: Which model generated output
        context_window_used: Tokens used
        confidence: Model's self-reported confidence
        citations: List of citations
        verification_chain: Chain of verification
        warnings: Any warnings flagged
    
    Returns:
        TrustScore object with composite score
    """
    
    # Calculate composite (product of all components)
    composite = truth * governance * sovereignty * workflow_integrity
    
    # Determine trust level
    if composite >= 0.85:
        trust_level = TrustLevel.VERY_HIGH
    elif composite >= 0.7:
        trust_level = TrustLevel.HIGH
    elif composite >= 0.5:
        trust_level = TrustLevel.MEDIUM
    elif composite >= 0.3:
        trust_level = TrustLevel.LOW
    else:
        trust_level = TrustLevel.VERY_LOW
    
    return TrustScore(
        truth_score=truth,
        governance_score=governance,
        sovereignty_score=sovereignty,
        workflow_integrity_score=workflow_integrity,
        composite_score=composite,
        trust_level=trust_level,
        calculated_at=datetime.utcnow().isoformat(),
        model_used=model_used,
        context_window_used=context_window_used,
        confidence=confidence,
        citations=citations or [],
        verification_chain=verification_chain or [],
        warnings=warnings or []
    )


def calculate_truth_score(
    has_citations: bool,
    citation_quality: float,
    fact_check_passed: bool,
    retrieval_confidence: float
) -> float:
    """
    Calculate truth component
    
    Factors:
    - Citation presence and quality
    - Fact checking results
    - Retrieval confidence
    """
    
    score = 0.0
    
    # Citations (40%)
    if has_citations:
        score += 0.4 * citation_quality
    
    # Fact checking (40%)
    if fact_check_passed:
        score += 0.4
    
    # Retrieval confidence (20%)
    score += 0.2 * retrieval_confidence
    
    return min(1.0, score)


def calculate_governance_score(
    policy_compliant: bool,
    has_approval: bool,
    audit_trail_complete: bool,
    no_violations: bool
) -> float:
    """
    Calculate governance component
    
    Factors:
    - Policy compliance
    - Approval status
    - Audit trail completeness
    - No violations flagged
    """
    
    score = 0.0
    
    if policy_compliant:
        score += 0.3
    if has_approval:
        score += 0.3
    if audit_trail_complete:
        score += 0.2
    if no_violations:
        score += 0.2
    
    return score


def calculate_sovereignty_score(
    open_source_ratio: float,
    local_processing_ratio: float,
    no_vendor_lock: bool
) -> float:
    """
    Calculate sovereignty component
    
    Factors:
    - Open source model usage
    - Local processing ratio
    - No vendor lock-in
    """
    
    score = 0.0
    
    # Open source usage (50%)
    score += 0.5 * open_source_ratio
    
    # Local processing (30%)
    score += 0.3 * local_processing_ratio
    
    # No vendor lock-in (20%)
    if no_vendor_lock:
        score += 0.2
    
    return score


def calculate_workflow_integrity_score(
    process_followed: bool,
    quorum_passed: bool,
    verification_complete: bool,
    no_shortcuts: bool
) -> float:
    """
    Calculate workflow integrity component
    
    Factors:
    - Process adherence
    - Quorum consensus
    - Verification completion
    - No shortcuts taken
    """
    
    score = 0.0
    
    if process_followed:
        score += 0.3
    if quorum_passed:
        score += 0.3
    if verification_complete:
        score += 0.2
    if no_shortcuts:
        score += 0.2
    
    return score
