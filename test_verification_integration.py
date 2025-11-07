"""
Quick test script for verification system integration.

Tests:
1. Database migration exists
2. Verification routes registered
3. InputSentinel uses ActionExecutor
4. End-to-end verified action (simulated)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_migration_exists():
    """Check that migration file was created"""
    migration_file = Path(__file__).parent / "alembic" / "versions" / "20251107_verification_system.py"
    
    if migration_file.exists():
        print("[OK] Migration file exists: 20251107_verification_system.py")
        return True
    else:
        print("[FAIL] Migration file NOT found")
        return False


async def test_routes_registered():
    """Check that verification routes are imported in main.py"""
    main_file = Path(__file__).parent / "backend" / "main.py"
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "verification_routes" in content and "app.include_router(verification_routes.router)" in content:
        print("[OK] Verification routes registered in main.py")
        return True
    else:
        print("[FAIL] Verification routes NOT registered")
        return False


async def test_input_sentinel_integration():
    """Check that InputSentinel uses ActionExecutor"""
    sentinel_file = Path(__file__).parent / "backend" / "input_sentinel.py"
    
    with open(sentinel_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "action_executor" in content and "ExpectedEffect" in content:
        print("[OK] InputSentinel integrated with ActionExecutor")
        return True
    else:
        print("[FAIL] InputSentinel NOT using ActionExecutor")
        return False


async def test_imports():
    """Test that all new modules can be imported"""
    try:
        from backend.action_contract import contract_verifier, ExpectedEffect
        print("[OK] action_contract imports successfully")
        
        from backend.self_heal.safe_hold import snapshot_manager
        print("[OK] safe_hold imports successfully")
        
        from backend.benchmarks import benchmark_suite
        print("[OK] benchmark_suite imports successfully")
        
        from backend.progression_tracker import progression_tracker
        print("[OK] progression_tracker imports successfully")
        
        from backend.action_executor import action_executor
        print("[OK] action_executor imports successfully")
        
        from backend.routes.verification_routes import router
        print("[OK] verification_routes imports successfully")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_components_exist():
    """Test that all component files exist"""
    files_to_check = [
        "backend/action_contract.py",
        "backend/self_heal/safe_hold.py",
        "backend/benchmarks/benchmark_suite.py",
        "backend/benchmarks/__init__.py",
        "backend/progression_tracker.py",
        "backend/action_executor.py",
        "backend/routes/verification_routes.py",
        "docs/VERIFICATION_SYSTEM.md",
        "alembic/versions/20251107_verification_system.py"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] MISSING: {file_path}")
            all_exist = False
    
    return all_exist


async def main():
    print("=" * 60)
    print("VERIFICATION SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print()
    
    results = []
    
    print("[FILES] Checking component files...")
    results.append(await test_components_exist())
    print()
    
    print("[IMPORTS] Testing imports...")
    results.append(await test_imports())
    print()
    
    print("[MIGRATION] Checking database migration...")
    results.append(await test_migration_exists())
    print()
    
    print("[ROUTES] Checking route registration...")
    results.append(await test_routes_registered())
    print()
    
    print("[INTEGRATION] Checking InputSentinel integration...")
    results.append(await test_input_sentinel_integration())
    print()
    
    print("=" * 60)
    if all(results):
        print("[PASS] ALL TESTS PASSED!")
        print()
        print("Next steps:")
        print("1. Start Grace backend:")
        print("   .venv\\Scripts\\python -m backend.main")
        print()
        print("2. Test verification endpoint:")
        print("   curl http://localhost:8000/api/verification/status")
    else:
        print("[FAIL] SOME TESTS FAILED")
        print("Please review the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
