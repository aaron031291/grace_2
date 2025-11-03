"""Test cognition imports"""

import sys
import os

# Add parent directory to path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print("Testing cognition imports...")
print("="*60)

# Test individual imports
try:
    from cognition.GraceLoopOutput import GraceLoopOutput, OutputType, ConfidenceLevel
    print("[OK] GraceLoopOutput")
except Exception as e:
    print(f"[FAIL] GraceLoopOutput: {e}")

try:
    from cognition.MemoryScoreModel import MemoryScoreModel
    print("[OK] MemoryScoreModel")
except Exception as e:
    print(f"[FAIL] MemoryScoreModel: {e}")

try:
    from cognition.models import (
        DecisionTask, ConsensusDecision, SpecialistProposal,
        LintReport, Violation, Patch,
        GovernanceVerdict, GovernanceDecision, RemediationAction
    )
    print("[OK] cognition.models (core)")
except Exception as e:
    print(f"[FAIL] cognition.models: {e}")

try:
    from cognition.QuorumEngine import QuorumEngine
    print("[OK] QuorumEngine")
except Exception as e:
    print(f"[FAIL] QuorumEngine: {e}")

try:
    from cognition.GraceCognitionLinter import GraceCognitionLinter
    print("[OK] GraceCognitionLinter")
except Exception as e:
    print(f"[FAIL] GraceCognitionLinter: {e}")

try:
    from cognition.GovernancePrimeDirective import GovernancePrimeDirective
    print("[OK] GovernancePrimeDirective")
except Exception as e:
    print(f"[FAIL] GovernancePrimeDirective: {e}")

try:
    from cognition.FeedbackIntegrator import FeedbackIntegrator
    print("[OK] FeedbackIntegrator")
except Exception as e:
    print(f"[FAIL] FeedbackIntegrator: {e}")

try:
    from cognition.memory_models import MemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog
    print("[OK] memory_models (database)")
except Exception as e:
    print(f"[FAIL] memory_models: {e}")

try:
    from cognition.LoopMemoryBank import LoopMemoryBank
    print("[OK] LoopMemoryBank")
except Exception as e:
    print(f"[FAIL] LoopMemoryBank: {e}")

print("\n" + "="*60)
try:
    from cognition import __all__
    print("[OK] FULL IMPORT SUCCESS - All cognition components loaded!")
    print(f"\nExported symbols: {len(__all__)} items")
except Exception as e:
    print(f"[FAIL] Full import failed: {e}")

print("="*60)
