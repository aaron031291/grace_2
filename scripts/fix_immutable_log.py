"""
Fix immutable_log sequence conflicts
"""

import sqlite3
import sys

db_path = "databases/grace.db"

print("Fixing immutable_log sequence conflicts...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("SELECT COUNT(*), MAX(sequence) FROM immutable_log")
    count, max_seq = cursor.fetchone()
    print(f"Current state: {count} entries, max sequence: {max_seq}")
    
    # Find duplicates
    cursor.execute("""
        SELECT sequence, COUNT(*) as cnt 
        FROM immutable_log 
        GROUP BY sequence 
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate sequences!")
        
        # Keep only the first entry for each sequence, delete others
        for seq, cnt in duplicates:
            cursor.execute("""
                DELETE FROM immutable_log 
                WHERE id NOT IN (
                    SELECT MIN(id) FROM immutable_log WHERE sequence = ?
                )
                AND sequence = ?
            """, (seq, seq))
            print(f"  Fixed sequence {seq} (removed {cnt-1} duplicates)")
        
        conn.commit()
        print("\n✓ Database fixed!")
    else:
        print("✓ No duplicates found - database is clean")
    
    # Verify
    cursor.execute("SELECT COUNT(*), MAX(sequence) FROM immutable_log")
    count, max_seq = cursor.fetchone()
    print(f"After fix: {count} entries, max sequence: {max_seq}")
    
    conn.close()
    
    print("\n✓ Ready to restart backend!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
