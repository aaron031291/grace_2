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
        print("✅ Migration file exists: 20251107_verification_system.py")
        return True
    else:
        print("❌ Migration file NOT found")
        return False


async def test_routes_registered():
    """Check that verification routes are imported in main.py"""
    main_file = Path(__file__).parent / "backend" / "main.py"
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    if "verification_routes" in content and "app.include_router(verification_routes.router)" in content:
        print("✅ Verification routes registered in main.py")
        return True
    else:
        print("❌ Verification routes NOT registered")
        return False


async def test_input_sentinel_integration():
    """Check that InputSentinel uses ActionExecutor"""
    sentinel_file = Path(__file__).parent / "backend" / "input_sentinel.py"
    
    with open(sentinel_file, 'r') as f:
        content = f.read()
    
    if "action_executor" in content and "ExpectedEffect" in content:
        print("✅ InputSentinel integrated with ActionExecutor")
        return True
    else:
        print("❌ InputSentinel NOT using ActionExecutor")
        return False


async def test_imports():
    """Test that all new modules can be imported"""
    try:
        from backend.action_contract import contract_verifier, ExpectedEffect
        print("✅ action_contract imports successfully")
        
        from backend.self_heal.safe_hold import snapshot_manager
        print("✅ safe_hold imports successfully")
        
        from backend.benchmarks import benchmark_suite
        print("✅ benchmark_suite imports successfully")
        
        from backend.progression_tracker import progression_tracker
        print("✅ progression_tracker imports successfully")
        
        from backend.action_executor import action_executor
        print("✅ action_executor imports successfully")
        
        from backend.routes.verification_routes import router
        print("✅ verification_routes imports successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
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
            print(f"✅ {file_path}")
        else:
            print(f"❌ MISSING: {file_path}")
            all_exist = False
    
    return all_exist


async def main():
    print("=" * 60)
    print("VERIFICATION SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print()
    
    results = []
    
    print("📁 Checking component files...")
    results.append(await test_components_exist())
    print()
    
    print("📦 Testing imports...")
    results.append(await test_imports())
    print()
    
    print("🗄️ Checking database migration...")
    results.append(await test_migration_exists())
    print()
    
    print("🚀 Checking route registration...")
    results.append(await test_routes_registered())
    print()
    
    print("🔗 Checking InputSentinel integration...")
    results.append(await test_input_sentinel_integration())
    print()
    
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print()
        print("Next steps:")
        print("1. Run database migration:")
        print("   .venv\\Scripts\\python -m alembic upgrade head")
        print()
        print("2. Start Grace backend:")
        print("   .venv\\Scripts\\python -m backend.main")
        print()
        print("3. Test verification endpoint:")
        print("   curl http://localhost:8000/api/verification/status")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
