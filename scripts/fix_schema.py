"""Fix database schema - add missing columns"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "backend" / "grace.db"
conn = sqlite3.connect(str(db_path))

print("Fixing schema...")

# Check and add verification_events.passed
try:
    cursor = conn.execute("PRAGMA table_info(verification_events)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "passed" not in columns:
        print("  [FIX] Adding verification_events.passed column...")
        conn.execute("ALTER TABLE verification_events ADD COLUMN passed BOOLEAN NOT NULL DEFAULT 0")
        print("  [OK] Added")
    else:
        print("  [OK] verification_events.passed exists")
except Exception as e:
    print(f"  [SKIP] verification_events: {e}")

# Check and add playbooks.risk_level and autonomy_tier
try:
    cursor = conn.execute("PRAGMA table_info(playbooks)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "risk_level" not in columns:
        print("  [FIX] Adding playbooks.risk_level column...")
        conn.execute("ALTER TABLE playbooks ADD COLUMN risk_level VARCHAR(16) NOT NULL DEFAULT 'medium'")
        print("  [OK] Added")
    else:
        print("  [OK] playbooks.risk_level exists")
    
    if "autonomy_tier" not in columns:
        print("  [FIX] Adding playbooks.autonomy_tier column...")
        conn.execute("ALTER TABLE playbooks ADD COLUMN autonomy_tier VARCHAR(16) NOT NULL DEFAULT 'tier_1'")
        print("  [OK] Added")
    else:
        print("  [OK] playbooks.autonomy_tier exists")
except Exception as e:
    print(f"  [SKIP] playbooks: {e}")

conn.commit()
conn.close()

print("\n[OK] Schema fixed!")
