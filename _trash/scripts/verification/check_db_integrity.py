import sqlite3
import sys

def check_db(path):
    print(f"Checking {path}...")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchall()
        print(f"Result: {result}")
        conn.close()
        if result == [('ok',)]:
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Check main db and immutable log db (if separate, but logs showed verify_event table issues)
    # The error was in backend\enhanced_boot_pipeline.py _stage_schema_secrets: "database disk image is malformed"
    # It was verifying 'verification_events' table.
    
    # Let's check grace.db and databases/*.db
    import glob
    import os
    from pathlib import Path
    
    root_dir = Path(__file__).parent.parent.parent
    
    dbs = glob.glob(str(root_dir / "databases/*.db")) + glob.glob(str(root_dir / "data/*.db"))
    
    for db in dbs:
        if os.path.exists(db):
            check_db(db)
