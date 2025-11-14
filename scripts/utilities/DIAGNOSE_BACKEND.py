"""
Diagnose backend startup issues
"""

import sys
from pathlib import Path

print("="*70)
print("GRACE BACKEND DIAGNOSTIC")
print("="*70)
print()

# Test 1: Python path
print("+ Python executable:", sys.executable)
print("+ Python version:", sys.version)
print()

# Test 2: Import backend core
print("[1/6] Testing backend.core imports...")
try:
    sys.path.insert(0, str(Path(__file__).parent / 'backend'))
    from backend.core import message_bus
    print("  [OK] message_bus imported")
except Exception as e:
    print(f"  [FAIL] message_bus failed: {e}")

# Test 3: Import infrastructure manager
print("[2/6] Testing infrastructure manager...")
try:
    from backend.core.infrastructure_manager_kernel import infrastructure_manager
    print("  [OK] infrastructure_manager imported")
except Exception as e:
    print(f"  [FAIL] infrastructure_manager failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Import governance kernel
print("[3/6] Testing governance kernel...")
try:
    from backend.kernels.governance_kernel import governance_kernel
    print("  [OK] governance_kernel imported")
except Exception as e:
    print(f"  [FAIL] governance_kernel failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Import memory kernel
print("[4/6] Testing memory kernel...")
try:
    from backend.kernels.memory_kernel import MemoryKernel
    print("  [OK] MemoryKernel imported")
except Exception as e:
    print(f"  [FAIL] MemoryKernel failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Import app
print("[5/6] Testing FastAPI app...")
try:
    from backend.app_factory import app
    print("  [OK] FastAPI app imported")
except Exception as e:
    print(f"  [FAIL] FastAPI app failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Try basic async operation
print("[6/6] Testing async operations...")
try:
    import asyncio
    async def test():
        print("  [OK] Async working")
    asyncio.run(test())
except Exception as e:
    print(f"  [FAIL] Async failed: {e}")

print()
print("="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
print()
print("Next steps:")
print("1. If all tests pass, try: python serve.py")
print("2. If tests fail, check the error messages above")
print("3. Install missing dependencies: pip install -r backend/requirements.txt")
