"""
Grant all pending approvals for Grace to start
"""
import sqlite3
import os
from datetime import datetime

db_path = "data/grace.db"

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for approval tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"📊 Found {len(tables)} tables in database")

# Look for approval-related tables
approval_tables = [t for t in tables if 'approval' in t.lower() or 'consent' in t.lower() or 'permission' in t.lower()]
print(f"\n🔍 Approval-related tables: {approval_tables}")

# Grant all approvals
approvals_granted = 0

for table in approval_tables:
    try:
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\n📋 Table: {table}")
        print(f"   Columns: {', '.join(columns)}")
        
        # Try to grant approvals
        if 'approved' in columns or 'status' in columns:
            if 'approved' in columns:
                cursor.execute(f"UPDATE {table} SET approved = 1 WHERE approved = 0 OR approved IS NULL")
            if 'status' in columns:
                cursor.execute(f"UPDATE {table} SET status = 'approved' WHERE status != 'approved' OR status IS NULL")
            
            conn.commit()
            approvals_granted += cursor.rowcount
            print(f"   ✅ Granted {cursor.rowcount} approvals")
            
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

conn.close()

print(f"\n✅ Total approvals granted: {approvals_granted}")
print("\n🚀 You can now run: python serve.py")
