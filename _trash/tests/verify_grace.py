"""
Grace System Verification Script

Checks all layers of Grace to ensure everything is functioning correctly.
"""

import sys
import subprocess
import sqlite3
from pathlib import Path


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_python_version():
    """Verify Python version"""
    print_section("1. Python Environment")
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("⚠️  WARNING: Python 3.10+ recommended")
        return False
    return True


def check_dependencies():
    """Check critical dependencies"""
    print_section("2. Dependencies")
    
    required = ['fastapi', 'sqlalchemy', 'aiosqlite', 'uvicorn']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg} installed")
        except ImportError:
            print(f"✗ {pkg} MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Install missing: pip install {' '.join(missing)}")
        return False
    return True


def check_database():
    """Verify database status"""
    print_section("3. Database")
    
    db_path = Path("databases/grace.db")
    
    if not db_path.exists():
        print("⚠️  Database doesn't exist yet (will be created on startup)")
        return True
    
    print(f"✓ Database exists: {db_path}")
    
    # Check for lock files
    wal_file = Path("databases/grace.db-wal")
    shm_file = Path("databases/grace.db-shm")
    
    if wal_file.exists() or shm_file.exists():
        print(f"⚠️  Lock files found:")
        if wal_file.exists():
            print(f"    - {wal_file}")
        if shm_file.exists():
            print(f"    - {shm_file}")
        print("    Run: emergency_db_fix.bat")
        return False
    
    # Check WAL mode
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()
        
        if mode.upper() == "WAL":
            print(f"✓ WAL mode enabled")
            return True
        else:
            print(f"⚠️  Journal mode: {mode} (should be WAL)")
            print("    Run: emergency_db_fix.bat")
            return False
    except Exception as e:
        print(f"✗ Database check failed: {e}")
        return False


def check_running_processes():
    """Check for existing Grace processes"""
    print_section("4. Running Processes")
    
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True
        )
        
        python_processes = [
            line for line in result.stdout.split('\n')
            if 'python.exe' in line.lower()
        ]
        
        if python_processes:
            print(f"⚠️  Found {len(python_processes)} Python process(es) running:")
            for proc in python_processes[:3]:
                print(f"    {proc.strip()}")
            print("\n    If Grace is already running, stop it first:")
            print("    taskkill /F /IM python.exe")
            return False
        else:
            print("✓ No Python processes running (safe to start)")
            return True
            
    except Exception as e:
        print(f"  Could not check processes: {e}")
        return True


def check_file_structure():
    """Verify critical files exist"""
    print_section("5. File Structure")
    
    critical_files = [
        "backend/main.py",
        "backend/base_models.py",
        "backend/trigger_mesh.py",
        "backend/grace_spine_integration.py",
        "backend/routes/autonomy_routes.py",
        "backend/agentic_error_handler.py",
        "backend/input_sentinel.py",
        "frontend/src/components/GraceGPT.tsx"
    ]
    
    all_exist = True
    for file in critical_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} MISSING")
            all_exist = False
    
    return all_exist


def check_env():
    """Check environment configuration"""
    print_section("6. Environment")
    
    env_file = Path(".env")
    if env_file.exists():
        print(f"✓ .env file exists")
    else:
        print(f"⚠️  .env file not found (will use defaults)")
    
    example_file = Path(".env.example")
    if example_file.exists():
        print(f"✓ .env.example exists")
    
    return True


def main():
    """Run full verification"""
    print("""
================================================================
              GRACE SYSTEM VERIFICATION
================================================================
    """)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("Running Processes", check_running_processes),
        ("File Structure", check_file_structure),
        ("Environment", check_env)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {name}")
    
    print(f"\n{'='*60}")
    print(f"  Result: {passed_count}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if passed_count == total:
        print("✅ All checks passed! Grace is ready to start.")
        print("\nRun: START_GRACE_NOW.bat")
    elif passed_count >= total - 1:
        print("⚠️  Minor issues found. Grace may still start successfully.")
        print("\nRun: START_GRACE_NOW.bat")
    else:
        print("❌ Critical issues found. Fix before starting Grace.")
        print("\nRecommended fixes:")
        for name, passed in results:
            if not passed:
                if "Database" in name:
                    print("  - Run: emergency_db_fix.bat")
                elif "Dependencies" in name:
                    print("  - Run: pip install -r requirements.txt")
                elif "Running Processes" in name:
                    print("  - Run: taskkill /F /IM python.exe")
    
    return passed_count == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
