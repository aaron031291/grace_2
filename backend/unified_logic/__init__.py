"""
Unified Logic - The Brain That Stitches Everything Together
Complete implementation of decision synthesis from all subsystems
"""

from .unified_decision_engine import (
    UnifiedDecisionEngine,
    UnifiedDecision,
    DecisionAction,
    ConflictType,
    GovernanceInput,
    AVNInput,
    MLDLQuorumInput,
    LearningInput,
    MemoryInput,
    unified_decision_engine
)

from .decision_router import (
    DecisionRouter,
    decision_router
)

from .complete_integration import (
    UnifiedLogicIntegration,
    unified_logic
)

__all__ = [
    # Engine
    'UnifiedDecisionEngine',
    'unified_decision_engine',
    
    # Decision types
    'UnifiedDecision',
    'DecisionAction',
    'ConflictType',
    
    # Input types
    'GovernanceInput',
    'AVNInput',
    'MLDLQuorumInput',
    'LearningInput',
    'MemoryInput',
    
    # Router
    'DecisionRouter',
    'decision_router',
    
    # Integration
    'UnifiedLogicIntegration',
    'unified_logic',
]
