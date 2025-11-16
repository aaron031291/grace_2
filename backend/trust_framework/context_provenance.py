"""
Context Provenance System - PRODUCTION
Every chunk has source_id, confidence, freshness with trustscore gate before re-use
"""

import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FreshnessLevel(Enum):
    """How fresh is the data"""
    REAL_TIME = "real_time"  # <1 hour
    FRESH = "fresh"  # 1-24 hours
    RECENT = "recent"  # 1-7 days
    STALE = "stale"  # 7-30 days
    OUTDATED = "outdated"  # >30 days


@dataclass
class ProvenanceHash:
    """Cryptographic hash of content for verification"""
    
    content_hash: str  # SHA-256 of actual content
    metadata_hash: str  # SHA-256 of metadata
    combined_hash: str  # Hash of content + metadata
    
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'content_hash': self.content_hash,
            'metadata_hash': self.metadata_hash,
            'combined_hash': self.combined_hash,
            'created_at': self.created_at
        }


@dataclass
class ContextChunk:
    """
    A chunk of context with full provenance
    
    Before re-use, passes through trustscore gate:
    truth × governance × sovereignty × workflow_integrity
    """
    
    chunk_id: str
    content: str
    
    # Provenance
    source_id: str  # Where did this come from
    source_type: str  # "retrieval", "user_input", "external", "generated"
    author: Optional[str] = None
    lineage: List[str] = field(default_factory=list)  # Chain of transformations
    
    # Trust
    confidence: float = 0.0  # 0-1, how confident in accuracy
    freshness: FreshnessLevel = FreshnessLevel.RECENT
    freshness_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Verification
    verified: bool = False
    trust_score: Optional[float] = None
    verification_chain: List[str] = field(default_factory=list)
    
    # Hashing
    provenance_hash: Optional[ProvenanceHash] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_used: Optional[str] = None
    use_count: int = 0
    
    # Flags
    can_reuse: bool = True
    requires_refresh: bool = False
    
    def __post_init__(self):
        # Generate provenance hash
        self.provenance_hash = self._generate_hash()
    
    def _generate_hash(self) -> ProvenanceHash:
        """Generate provenance hashes"""
        
        # Content hash
        content_hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        
        # Metadata hash
        metadata = {
            'source_id': self.source_id,
            'source_type': self.source_type,
            'author': self.author,
            'lineage': self.lineage
        }
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode('utf-8')).hexdigest()
        
        # Combined hash
        combined = f"{content_hash}{metadata_hash}"
        combined_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return ProvenanceHash(
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            combined_hash=combined_hash
        )
    
    def calculate_freshness(self) -> FreshnessLevel:
        """Calculate freshness based on timestamp"""
        
        try:
            timestamp = datetime.fromisoformat(self.freshness_timestamp)
            age = datetime.utcnow() - timestamp
            
            if age < timedelta(hours=1):
                return FreshnessLevel.REAL_TIME
            elif age < timedelta(days=1):
                return FreshnessLevel.FRESH
            elif age < timedelta(days=7):
                return FreshnessLevel.RECENT
            elif age < timedelta(days=30):
                return FreshnessLevel.STALE
            else:
                return FreshnessLevel.OUTDATED
        
        except:
            return FreshnessLevel.RECENT
    
    def to_dict(self) -> Dict:
        return {
            'chunk_id': self.chunk_id,
            'content': self.content[:200],  # Truncate for logging
            'provenance': {
                'source_id': self.source_id,
                'source_type': self.source_type,
                'author': self.author,
                'lineage': self.lineage
            },
            'trust': {
                'confidence': self.confidence,
                'freshness': self.freshness.value,
                'verified': self.verified,
                'trust_score': self.trust_score,
                'verification_chain': self.verification_chain
            },
            'hashes': self.provenance_hash.to_dict() if self.provenance_hash else {},
            'metadata': {
                'created_at': self.created_at,
                'last_used': self.last_used,
                'use_count': self.use_count
            },
            'flags': {
                'can_reuse': self.can_reuse,
                'requires_refresh': self.requires_refresh
            }
        }


class TrustscoreGate:
    """
    Gate that validates context chunks before re-use
    
    Formula: truth × governance × sovereignty × workflow_integrity
    Below threshold → retrieval refresh or human escalation
    """
    
    def __init__(
        self,
        min_truth: float = 0.6,
        min_governance: float = 0.7,
        min_sovereignty: float = 0.8,
        min_workflow: float = 0.7,
        min_composite: float = 0.7
    ):
        self.min_truth = min_truth
        self.min_governance = min_governance
        self.min_sovereignty = min_sovereignty
        self.min_workflow = min_workflow
        self.min_composite = min_composite
        
        # Statistics
        self.total_checks = 0
        self.passed_checks = 0
        self.refresh_triggered = 0
        self.escalations = 0
    
    async def check(self, chunk: ContextChunk) -> Dict[str, Any]:
        """
        Check if chunk passes trustscore gate
        
        Returns:
        - passed: bool
        - action: "allow", "refresh", "escalate"
        - details: Dict
        """
        
        self.total_checks += 1
        
        # Update freshness
        chunk.freshness = chunk.calculate_freshness()
        
        # Calculate component scores
        truth = self._calculate_truth_score(chunk)
        governance = self._calculate_governance_score(chunk)
        sovereignty = self._calculate_sovereignty_score(chunk)
        workflow = self._calculate_workflow_score(chunk)
        
        # Composite
        composite = truth * governance * sovereignty * workflow
        chunk.trust_score = composite
        
        # Check thresholds
        failed_components = []
        
        if truth < self.min_truth:
            failed_components.append(f"truth ({truth:.2f} < {self.min_truth})")
        if governance < self.min_governance:
            failed_components.append(f"governance ({governance:.2f} < {self.min_governance})")
        if sovereignty < self.min_sovereignty:
            failed_components.append(f"sovereignty ({sovereignty:.2f} < {self.min_sovereignty})")
        if workflow < self.min_workflow:
            failed_components.append(f"workflow ({workflow:.2f} < {self.min_workflow})")
        
        # Determine action
        if composite >= self.min_composite and not failed_components:
            # Passed - allow re-use
            chunk.can_reuse = True
            chunk.last_used = datetime.utcnow().isoformat()
            chunk.use_count += 1
            
            self.passed_checks += 1
            
            return {
                'passed': True,
                'action': 'allow',
                'composite_score': composite,
                'components': {
                    'truth': truth,
                    'governance': governance,
                    'sovereignty': sovereignty,
                    'workflow': workflow
                }
            }
        
        elif composite >= 0.5:
            # Marginal - trigger refresh
            chunk.requires_refresh = True
            self.refresh_triggered += 1
            
            logger.warning(
                f"[TRUSTSCORE-GATE] Chunk {chunk.chunk_id} requires refresh "
                f"(score: {composite:.2f}, failed: {', '.join(failed_components)})"
            )
            
            return {
                'passed': False,
                'action': 'refresh',
                'composite_score': composite,
                'failed_components': failed_components,
                'reason': 'below_threshold'
            }
        
        else:
            # Critical - escalate to human
            chunk.can_reuse = False
            self.escalations += 1
            
            logger.error(
                f"[TRUSTSCORE-GATE] Chunk {chunk.chunk_id} ESCALATED "
                f"(score: {composite:.2f}, failed: {', '.join(failed_components)})"
            )
            
            return {
                'passed': False,
                'action': 'escalate',
                'composite_score': composite,
                'failed_components': failed_components,
                'reason': 'critical_trust_failure'
            }
    
    def _calculate_truth_score(self, chunk: ContextChunk) -> float:
        """Calculate truth component"""
        
        score = chunk.confidence  # Base on confidence
        
        # Reduce based on freshness
        if chunk.freshness == FreshnessLevel.STALE:
            score *= 0.8
        elif chunk.freshness == FreshnessLevel.OUTDATED:
            score *= 0.5
        
        # Boost if verified
        if chunk.verified:
            score = min(1.0, score + 0.2)
        
        return score
    
    def _calculate_governance_score(self, chunk: ContextChunk) -> float:
        """Calculate governance component"""
        
        score = 0.5  # Default
        
        # Has provenance
        if chunk.source_id and chunk.source_type:
            score += 0.2
        
        # Has lineage
        if chunk.lineage:
            score += 0.1
        
        # Verified
        if chunk.verified:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_sovereignty_score(self, chunk: ContextChunk) -> float:
        """Calculate sovereignty component"""
        
        # Check if from internal/local source
        if chunk.source_type in ['internal', 'local', 'generated']:
            return 1.0
        elif chunk.source_type in ['retrieval', 'external']:
            return 0.7
        else:
            return 0.5
    
    def _calculate_workflow_score(self, chunk: ContextChunk) -> float:
        """Calculate workflow integrity component"""
        
        score = 0.5  # Default
        
        # Has verification chain
        if chunk.verification_chain:
            score += 0.3
        
        # Used before successfully
        if chunk.use_count > 0:
            score += 0.2
        
        return min(1.0, score)
    
    def get_stats(self) -> Dict:
        """Get gate statistics"""
        
        pass_rate = self.passed_checks / max(1, self.total_checks)
        
        return {
            'total_checks': self.total_checks,
            'passed': self.passed_checks,
            'pass_rate': pass_rate,
            'refresh_triggered': self.refresh_triggered,
            'escalations': self.escalations,
            'thresholds': {
                'truth': self.min_truth,
                'governance': self.min_governance,
                'sovereignty': self.min_sovereignty,
                'workflow': self.min_workflow,
                'composite': self.min_composite
            }
        }


# Global gate
trustscore_gate = TrustscoreGate()
