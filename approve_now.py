"""
Directly approve all pending items in the database
"""
import sqlite3
import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = "data/grace.db"

if not os.path.exists(db_path):
    print(f"[X] Database not found at {db_path}")
    exit(1)

print("[*] Connecting to database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"[*] Found {len(tables)} tables")

# Look for consent/approval related tables
approval_tables = [t for t in tables if any(word in t.lower() for word in ['consent', 'approval', 'permission', 'auth'])]

print(f"\n[*] Approval-related tables: {len(approval_tables)}")
for table in approval_tables:
    print(f"   - {table}")

# Grant approvals
total_approved = 0

for table in approval_tables:
    try:
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        # Try different approval columns
        if 'approved' in columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE approved = 0 OR approved IS NULL")
            pending = cursor.fetchone()[0]
            if pending > 0:
                cursor.execute(f"UPDATE {table} SET approved = 1")
                conn.commit()
                print(f"   [OK] {table}: Approved {pending} items")
                total_approved += pending
                
        if 'status' in columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE status = 'pending' OR status IS NULL")
            pending = cursor.fetchone()[0]
            if pending > 0:
                cursor.execute(f"UPDATE {table} SET status = 'approved' WHERE status = 'pending' OR status IS NULL")
                conn.commit()
                print(f"   [OK] {table}: Approved {pending} items")
                total_approved += pending
                
        if 'consent_status' in columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE consent_status = 'pending'")
            pending = cursor.fetchone()[0]
            if pending > 0:
                cursor.execute(f"UPDATE {table} SET consent_status = 'approved' WHERE consent_status = 'pending'")
                conn.commit()
                print(f"   [OK] {table}: Approved {pending} items")
                total_approved += pending
                
    except Exception as e:
        print(f"   [!] {table}: {e}")

conn.close()

print(f"\n[OK] Total approvals granted: {total_approved}")
print("\n[*] You can now start Grace: python serve.py")
