"""Grace Cognition System

Advanced decision-making and quality assurance for Grace AI.

Components:
- QuorumEngine: Trust-weighted specialist consensus
- GraceCognitionLinter: Contradiction and drift detection
- GraceLoopOutput: Standardized output format
- Models: Data models for cognition system
"""

from .QuorumEngine import QuorumEngine
from .GraceCognitionLinter import GraceCognitionLinter
from .GraceLoopOutput import (
    GraceLoopOutput, 
    OutputType, 
    ConfidenceLevel,
    Citation,
    PolicyTag,
    Diagnostic
)
from .models import (
    DecisionTask,
    ConsensusDecision,
    SpecialistProposal,
    LintReport,
    Violation,
    Patch,
    DecisionStrategy,
    RiskLevel,
    ViolationSeverity
)

__all__ = [
    # Engines
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
    'ViolationSeverity'
]

__version__ = '1.0.0'
