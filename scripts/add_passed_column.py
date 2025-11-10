"""Add passed column to verification_events table"""
import sqlite3
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate():
    db_path = "databases/grace.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(verification_events)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'passed' not in columns:
        print("[MIGRATION] Adding 'passed' column to verification_events...")
        cursor.execute("""
            ALTER TABLE verification_events 
            ADD COLUMN passed BOOLEAN DEFAULT 0
        """)
        
        # Update existing rows based on result column
        cursor.execute("""
            UPDATE verification_events 
            SET passed = CASE 
                WHEN result = 'pass' THEN 1 
                ELSE 0 
            END
        """)
        
        conn.commit()
        print("[MIGRATION] ✅ Column added and existing data migrated")
    else:
        print("[MIGRATION] Column 'passed' already exists")
    
    conn.close()

if __name__ == "__main__":
    migrate()
