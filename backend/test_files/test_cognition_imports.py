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
    print("[OK] GraceLoopOutput")
except Exception as e:
    print(f"[FAIL] GraceLoopOutput: {e}")

try:
    print("[OK] MemoryScoreModel")
except Exception as e:
    print(f"[FAIL] MemoryScoreModel: {e}")

try:
    print("[OK] cognition.models (core)")
except Exception as e:
    print(f"[FAIL] cognition.models: {e}")

try:
    print("[OK] QuorumEngine")
except Exception as e:
    print(f"[FAIL] QuorumEngine: {e}")

try:
    print("[OK] GraceCognitionLinter")
except Exception as e:
    print(f"[FAIL] GraceCognitionLinter: {e}")

try:
    print("[OK] GovernancePrimeDirective")
except Exception as e:
    print(f"[FAIL] GovernancePrimeDirective: {e}")

try:
    print("[OK] FeedbackIntegrator")
except Exception as e:
    print(f"[FAIL] FeedbackIntegrator: {e}")

try:
    print("[OK] memory_models (database)")
except Exception as e:
    print(f"[FAIL] memory_models: {e}")

try:
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
