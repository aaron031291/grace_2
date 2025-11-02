"""Grace Cognition System

Advanced decision-making and quality assurance for Grace AI.

Components:
- QuorumEngine: Trust-weighted specialist consensus
- GraceCognitionLinter: Contradiction and drift detection
- GovernancePrimeDirective: Constitutional validation
- FeedbackIntegrator: Learning from outcomes
- LoopMemoryBank: Memory storage with trust scoring
- MemoryScoreModel: Trust/decay scoring logic
- GraceLoopOutput: Standardized output format
- Models: Data models for cognition system
"""

from .GraceLoopOutput import (
    GraceLoopOutput, 
    OutputType, 
    ConfidenceLevel,
    Citation,
    PolicyTag,
    Diagnostic
)
from .MemoryScoreModel import MemoryScoreModel
from .LoopMemoryBank import LoopMemoryBank
from .GovernancePrimeDirective import GovernancePrimeDirective
from .FeedbackIntegrator import FeedbackIntegrator
from .QuorumEngine import QuorumEngine
from .GraceCognitionLinter import GraceCognitionLinter
from .models import (
    DecisionTask,
    ConsensusDecision,
    SpecialistProposal,
    LintReport,
    Violation,
    Patch,
    DecisionStrategy,
    RiskLevel,
    ViolationSeverity,
    GovernanceVerdict,
    GovernanceDecision,
    RemediationAction,
    MemoryArtifact,
    TrustEvent,
    MemoryIndex,
    GarbageCollectionLog
)

__all__ = [
    # Core components
    'MemoryScoreModel',
    'LoopMemoryBank',
    'GovernancePrimeDirective',
    'FeedbackIntegrator',
    'QuorumEngine',
    'GraceCognitionLinter',
    
    # Output format
    'GraceLoopOutput',
    'OutputType',
    'ConfidenceLevel',
    'Citation',
    'PolicyTag',
    'Diagnostic',
    
    # Consensus models
    'DecisionTask',
    'ConsensusDecision',
    'SpecialistProposal',
    'DecisionStrategy',
    'RiskLevel',
    
    # Linting models
    'LintReport',
    'Violation',
    'Patch',
    'ViolationSeverity',
    
    # Governance models
    'GovernanceVerdict',
    'GovernanceDecision',
    'RemediationAction',
    
    # Memory models
    'MemoryArtifact',
    'TrustEvent',
    'MemoryIndex',
    'GarbageCollectionLog'
]

__version__ = '1.0.0'
