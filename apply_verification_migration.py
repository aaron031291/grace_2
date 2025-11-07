"""
Apply Verification System Migration

Applies the verification tables migration and verifies schema.
"""

import asyncio
from alembic.config import Config
from alembic import command
from pathlib import Path


def apply_migration():
    """Apply verification migration"""
    
    print("Applying verification system migration...")
    
    # Get project root
    root = Path(__file__).parent
    alembic_ini = root / "alembic.ini"
    
    if not alembic_ini.exists():
        print("ERROR: alembic.ini not found!")
        return False
    
    # Configure Alembic
    alembic_cfg = Config(str(alembic_ini))
    
    try:
        # Show current revision
        print("\nCurrent database state:")
        command.current(alembic_cfg, verbose=True)
        
        print("\nUpgrading to latest...")
        # Apply all pending migrations
        command.upgrade(alembic_cfg, "head")
        
        print("\nMigration complete!")
        
        # Show new state
        print("\nNew database state:")
        command.current(alembic_cfg, verbose=True)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_tables():
    """Verify that verification tables exist"""
    
    print("\nVerifying verification tables...")
    
    from backend.models import async_session
    from sqlalchemy import text
    
    async with async_session() as session:
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
    
    required_tables = [
        "action_contracts",
        "safe_hold_snapshots",
        "benchmark_runs",
        "mission_timelines"
    ]
    
    all_present = True
    for table in required_tables:
        if table in tables:
            print(f"  [OK] {table}")
        else:
            print(f"  [MISSING] {table}")
            all_present = False
    
    if all_present:
        print("\nAll verification tables present!")
    else:
        print("\nSome tables are missing!")
    
    return all_present


async def main():
    """Main migration application flow"""
    
    print("=" * 60)
    print("GRACE VERIFICATION SYSTEM MIGRATION")
    print("=" * 60)
    print()
    
    # Step 1: Apply migration
    success = apply_migration()
    
    if not success:
        print("\n❌ Migration failed. Please check errors above.")
        return
    
    # Step 2: Verify tables
    await verify_tables()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run: .venv\\Scripts\\python.exe test_verification_e2e.py")
    print("  2. Start backend: .venv\\Scripts\\python.exe -m backend.main")
    print("  3. Test API: curl http://localhost:8000/api/verification/contracts")


if __name__ == "__main__":
    asyncio.run(main())
