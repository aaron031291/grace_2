#!/usr/bin/env python3
"""
Run Complete CI Test Suite - Phase 0 & Phase 1
Simulates GitHub Actions CI locally
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(name: str, cmd: list, env: dict = None) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}\n")
    
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    
    result = subprocess.run(cmd, env=full_env)
    
    if result.returncode == 0:
        print(f"\n✅ {name}: PASSED")
        return True
    else:
        print(f"\n❌ {name}: FAILED")
        return False

def main():
    """Run all CI tests"""
    os.chdir(Path(__file__).parent.parent)
    
    print("="*80)
    print("GRACE CI TEST SUITE")
    print("="*80)
    print()
    
    results = {}
    
    # Test 1: Import tests
    results['imports'] = run_command(
        "Import Tests",
        [sys.executable, "scripts/test_imports.py"]
    )
    
    # Test 2: Boot probe
    results['boot_probe'] = run_command(
        "Boot Probe",
        [sys.executable, "scripts/test_boot_probe.py"],
        env={"OFFLINE_MODE": "true", "DRY_RUN": "true", "CI": "true"}
    )
    
    # Test 3: Syntax check (compile all)
    print(f"\n{'='*80}")
    print("Running: Syntax Check")
    print(f"{'='*80}\n")
    
    result = subprocess.run([
        sys.executable, "-m", "compileall", "-q",
        "backend", "scripts", "tests", "cli"
    ])
    results['syntax'] = result.returncode == 0
    print(f"\n{'✅' if results['syntax'] else '❌'} Syntax Check: {'PASSED' if results['syntax'] else 'FAILED'}")
    
    # Test 4: Guardian playbook tests
    results['guardian'] = run_command(
        "Guardian Playbook Tests",
        [sys.executable, "-m", "pytest", "tests/test_guardian_playbooks.py", "-v", "--tb=short"]
    )
    
    # Test 5: Lint check (non-blocking)
    print(f"\n{'='*80}")
    print("Running: Lint Check (non-blocking)")
    print(f"{'='*80}\n")
    
    result = subprocess.run([
        "ruff", "check", "backend",
        "--select", "F,E",
        "--ignore", "E501,E722",
        "--exit-zero"
    ])
    results['lint'] = True  # Always pass (exit-zero)
    print(f"\n✅ Lint Check: PASSED (non-blocking)")
    
    # Summary
    print("\n" + "="*80)
    print("CI TEST SUITE SUMMARY")
    print("="*80)
    print()
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test:20s} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("="*80)
        print("✅ ALL CI TESTS PASSED")
        print("="*80)
        return 0
    else:
        print("="*80)
        print(f"❌ {total - passed} CI TEST(S) FAILED")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())
