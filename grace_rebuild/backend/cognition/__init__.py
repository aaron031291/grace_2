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

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "GraceLoopOutput":
        from .GraceLoopOutput import GraceLoopOutput
        return GraceLoopOutput
    elif name == "OutputType":
        from .GraceLoopOutput import OutputType
        return OutputType
    elif name == "ConfidenceLevel":
        from .GraceLoopOutput import ConfidenceLevel
        return ConfidenceLevel
    elif name == "Citation":
        from .GraceLoopOutput import Citation
        return Citation
    elif name == "PolicyTag":
        from .GraceLoopOutput import PolicyTag
        return PolicyTag
    elif name == "Diagnostic":
        from .GraceLoopOutput import Diagnostic
        return Diagnostic
    elif name == "MemoryScoreModel":
        from .MemoryScoreModel import MemoryScoreModel
        return MemoryScoreModel
    elif name == "LoopMemoryBank":
        from .LoopMemoryBank import LoopMemoryBank
        return LoopMemoryBank
    elif name == "GovernancePrimeDirective":
        from .GovernancePrimeDirective import GovernancePrimeDirective
        return GovernancePrimeDirective
    elif name == "FeedbackIntegrator":
        from .FeedbackIntegrator import FeedbackIntegrator
        return FeedbackIntegrator
    elif name == "QuorumEngine":
        from .QuorumEngine import QuorumEngine
        return QuorumEngine
    elif name == "GraceCognitionLinter":
        from .GraceCognitionLinter import GraceCognitionLinter
        return GraceCognitionLinter
    elif name in ["DecisionTask", "ConsensusDecision", "SpecialistProposal", "LintReport",
                  "Violation", "Patch", "DecisionStrategy", "RiskLevel", "ViolationSeverity",
                  "GovernanceVerdict", "GovernanceDecision", "RemediationAction"]:
        from . import models
        return getattr(models, name)
    elif name in ["MemoryArtifact", "TrustEvent", "MemoryIndex", "GarbageCollectionLog"]:
        from . import memory_models
        return getattr(memory_models, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

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
