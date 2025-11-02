"""Fix Cognition Import Issues

Adds missing models to cognition/models.py
"""

from pathlib import Path

models_file = Path("backend/cognition/models.py")

# Read current content
with open(models_file, 'r') as f:
    content = f.read()

# Add missing imports and models at the end
additions = '''

@dataclass
class GovernanceVerdict:
    """Result of constitutional governance validation"""
    decision: str  # go, block, degrade, escalate
    tags: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    reason: str = ""
    constitutional_checks: List[int] = field(default_factory=list)
    compliance_score: float = 1.0
    requires_parliament: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

# Import memory models for convenience
from .memory_models import MemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog

__all__ = [
    'OutputType', 'ConfidenceLevel',
    'RiskLevel', 'DecisionStrategy', 'ViolationSeverity',
    'SpecialistProposal', 'DecisionTask', 'ConsensusDecision',
    'Violation', 'Patch', 'LintReport',
    'GovernanceVerdict',
    'MemoryArtifact', 'TrustEvent', 'MemoryIndex', 'GarbageCollectionLog'
]
'''

# Remove any existing empty quotes at end
content = content.rstrip()
if content.endswith('""'):
    content = content[:-2].rstrip()

# Append additions
with open(models_file, 'w') as f:
    f.write(content + additions)

print("SUCCESS: Fixed cognition/models.py")
print("Added: GovernanceVerdict")
print("Added: memory_models imports")
print("Added: __all__ exports")
