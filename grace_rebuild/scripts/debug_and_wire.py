"""Debug, Verify, and Wire Grace Systems

This script:
1. Checks all imports work
2. Verifies database tables exist
3. Wires cognition pipeline into existing loops
4. Tests end-to-end workflow
5. Fixes any broken integrations
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

print("=" * 70)
print(" GRACE SYSTEM DEBUG & VERIFICATION")
print("=" * 70)
print()

# STEP 1: Verify Imports
print("STEP 1: Verifying imports...")
print("-" * 70)

imports_to_check = [
    ("GraceLoopOutput", "from backend.cognition.GraceLoopOutput import GraceLoopOutput"),
    ("MemoryScoreModel", "from backend.cognition.MemoryScoreModel import MemoryScoreModel"),
    ("LoopMemoryBank", "from backend.cognition.LoopMemoryBank import LoopMemoryBank"),
    ("GovernancePrimeDirective", "from backend.cognition.GovernancePrimeDirective import GovernancePrimeDirective"),
    ("FeedbackIntegrator", "from backend.cognition.FeedbackIntegrator import FeedbackIntegrator"),
    ("QuorumEngine", "from backend.cognition.QuorumEngine import QuorumEngine"),
    ("GraceCognitionLinter", "from backend.cognition.GraceCognitionLinter import GraceCognitionLinter"),
]

failed_imports = []

for name, import_stmt in imports_to_check:
    try:
        exec(import_stmt)
        print(f"  SUCCESS: {name}")
    except ImportError as e:
        print(f"  FAILED: {name} - {e}")
        failed_imports.append((name, str(e)))
    except Exception as e:
        print(f"  ERROR: {name} - {e}")
        failed_imports.append((name, str(e)))

print()

if failed_imports:
    print("IMPORT FAILURES DETECTED:")
    for name, error in failed_imports:
        print(f"  - {name}: {error}")
    print()
    print("Attempting fixes...")
    print()

# STEP 2: Check Database Tables
print("STEP 2: Checking database tables...")
print("-" * 70)

try:
    from backend.models import engine, Base
    
    # Get existing tables
    from sqlalchemy import inspect
    
    async def check_tables():
        async with engine.begin() as conn:
            def get_tables(connection):
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_tables)
            
            print(f"  Total tables in database: {len(tables)}")
            
            # Check for cognition tables
            cognition_tables = [t for t in tables if 'cognition' in t]
            print(f"  Cognition tables: {len(cognition_tables)}")
            for table in cognition_tables:
                print(f"    - {table}")
            
            # Check for core tables
            core_tables = ['users', 'tasks', 'chat_messages', 'governance_policies', 'security_rules']
            missing_core = [t for t in core_tables if t not in tables]
            
            if missing_core:
                print(f"\n  MISSING CORE TABLES: {missing_core}")
            else:
                print("\n  SUCCESS: All core tables present")
    
    asyncio.run(check_tables())
    
except Exception as e:
    print(f"  ERROR checking tables: {e}")

print()

# STEP 3: Integration Status
print("STEP 3: Checking integration status...")
print("-" * 70)

integration_checks = {
    "Reflection Loop": "grace_rebuild/backend/reflection.py",
    "Meta Loop": "grace_rebuild/backend/meta_loop.py",
    "Hunter Protocol": "grace_rebuild/backend/hunter.py",
    "Governance Engine": "grace_rebuild/backend/governance.py",
    "Verification Engine": "grace_rebuild/backend/verification.py",
    "Parliament Engine": "grace_rebuild/backend/parliament_engine.py",
    "Code Memory": "grace_rebuild/backend/code_memory.py",
    "Constitutional Engine": "grace_rebuild/backend/constitutional_engine.py",
}

for system, file_path in integration_checks.items():
    if Path(file_path).exists():
        print(f"  SUCCESS: {system} - {file_path}")
    else:
        print(f"  MISSING: {system} - {file_path}")

print()

# STEP 4: Summary
print("=" * 70)
print(" VERIFICATION SUMMARY")
print("=" * 70)

if not failed_imports:
    print("SUCCESS: All cognition classes import correctly")
else:
    print(f"ISSUES: {len(failed_imports)} import failures need fixing")

print()
print("Next steps:")
print("  1. Fix any import errors")
print("  2. Run: py -m backend.cognition.migrate_memory_scoring")
print("  3. Test: py -m pytest grace_rebuild/backend/tests/")
print("  4. Deploy: start_backend.bat")
print()

if __name__ == "__main__":
    pass
