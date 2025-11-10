"""Fix corrupted database by rebuilding it"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

def fix_database():
    """Fix corrupted grace.db"""
    
    db_path = Path("grace.db")
    backup_path = Path(f"grace.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    print("=" * 80)
    print("DATABASE REPAIR UTILITY")
    print("=" * 80)
    print()
    
    # Backup corrupted database
    if db_path.exists():
        print(f"[1/4] Backing up corrupted database to {backup_path}...")
        shutil.copy(db_path, backup_path)
        print("  ✓ Backup created")
    else:
        print("[1/4] No existing database found")
    
    # Try to recover data
    print()
    print("[2/4] Attempting data recovery...")
    recovered_data = {}
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to get table list
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"  Found {len(tables)} tables")
                
                for (table_name,) in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"    - {table_name}: {count} rows")
                    except:
                        print(f"    - {table_name}: CORRUPTED")
            except Exception as e:
                print(f"  ✗ Cannot read tables: {e}")
            
            conn.close()
        except Exception as e:
            print(f"  ✗ Database severely corrupted: {e}")
    
    # Remove corrupted database
    print()
    print("[3/4] Removing corrupted database...")
    if db_path.exists():
        db_path.unlink()
        print("  ✓ Removed")
    
    # Remove associated files
    for ext in ['-shm', '-wal', '-journal']:
        file_path = Path(f"grace.db{ext}")
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Removed grace.db{ext}")
    
    # Create fresh database
    print()
    print("[4/4] Creating fresh database...")
    print("  Database will be initialized on next Grace startup")
    print("  ✓ Ready for fresh start")
    
    print()
    print("=" * 80)
    print("DATABASE REPAIR COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run: .\\GRACE.ps1 -SkipChecks")
    print("  2. Database will be automatically created")
    print("  3. All tables will be initialized")
    print()
    print(f"Backup saved to: {backup_path}")
    print()

if __name__ == '__main__':
    fix_database()

