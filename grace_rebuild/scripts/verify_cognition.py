"""Verify Cognition System - Proper Module Import Testing

Tests imports using proper Python module structure (not sys.path hacks)
"""

import subprocess
import sys

print("=" * 70)
print(" GRACE COGNITION VERIFICATION (Proper Module Structure)")
print("=" * 70)
print()

# Test imports as modules (the correct way)
tests = [
    ("GraceLoopOutput", "python -m backend.cognition.GraceLoopOutput"),
    ("MemoryScoreModel", "python -c \"from backend.cognition.MemoryScoreModel import MemoryScoreModel; print('OK')\""),
    ("LoopMemoryBank", "python -c \"from backend.cognition.LoopMemoryBank import LoopMemoryBank; print('OK')\""),
    ("GovernancePrimeDirective", "python -c \"from backend.cognition.GovernancePrimeDirective import governance_prime_directive; print('OK')\""),
    ("FeedbackIntegrator", "python -c \"from backend.cognition.FeedbackIntegrator import feedback_integrator; print('OK')\""),
    ("QuorumEngine", "python -c \"from backend.cognition.QuorumEngine import QuorumEngine; print('OK')\""),
    ("GraceCognitionLinter", "python -c \"from backend.cognition.GraceCognitionLinter import GraceCognitionLinter; print('OK')\""),
]

print("Testing imports (as proper Python modules)...")
print("-" * 70)

passed = 0
failed = 0

for name, cmd in tests:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"  SUCCESS: {name}")
            passed += 1
        else:
            print(f"  FAILED: {name}")
            if result.stderr:
                print(f"    Error: {result.stderr.strip()[:100]}")
            failed += 1
    except Exception as e:
        print(f"  ERROR: {name} - {e}")
        failed += 1

print()
print("=" * 70)
print(f" RESULTS: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print()
    print("SUCCESS: All cognition classes import correctly!")
    print()
    print("Next steps:")
    print("  1. Create tables: py -m backend.cognition.migrate_all_tables")
    print("  2. Test integration: py -m pytest backend/tests/test_cognition_integration.py")
    print("  3. Start Grace: py backend/main.py")
    sys.exit(0)
else:
    print()
    print(f"ISSUES: {failed} import failures detected")
    print("These need fixing before cognition system is fully operational.")
    print()
    sys.exit(1)
