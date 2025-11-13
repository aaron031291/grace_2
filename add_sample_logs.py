"""Add sample logs to demonstrate log viewing"""
import sqlite3
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = sqlite3.connect('databases/memory_fusion.db')
c = db.cursor()

print("\nAdding sample log entries...\n")

logs = [
    ("schema_proposal", "lean_startup.pdf", '{"confidence": 0.92, "table": "memory_documents"}'),
    ("schema_approval", "schema_001", '{"status": "approved", "auto": true}'),
    ("ingestion_launch", "lean_startup.pdf", '{"pipeline": "book_ingestion"}'),
    ("text_extraction", "lean_startup.pdf", '{"pages": 200, "method": "pypdf"}'),
    ("chunking", "book_abc123", '{"chunks_created": 120, "chunk_size": 1024}'),
    ("ingestion_complete", "book_abc123", '{"chunks": 120, "insights": 18}'),
    ("trust_update", "book_abc123", '{"old": 0.5, "new": 0.95}'),
    ("file_organization", "startup_notes.txt", '{"moved_to": "business/"}'),
]

for action, target, details in logs:
    c.execute(
        "INSERT INTO memory_librarian_log (action_type, target_path, details, timestamp) VALUES (?, ?, ?, datetime('now'))",
        (action, target, details)
    )
    print(f"✓ {action} -> {target}")

db.commit()

# Show what we created
c.execute("SELECT COUNT(*) FROM memory_librarian_log")
count = c.fetchone()[0]
print(f"\nTotal logs in database: {count}")

print("\n=== Recent Logs ===\n")
c.execute("SELECT action_type, target_path, timestamp FROM memory_librarian_log ORDER BY timestamp DESC LIMIT 10")
for i, row in enumerate(c.fetchall(), 1):
    print(f"{i}. [{row[0]}] {row[1]} at {row[2]}")

db.close()

print("\n✅ Sample logs created!")
print("\nNow test the API:")
print("  curl http://localhost:8000/api/librarian/logs/tail?lines=10")
print("\nOr view in UI:")
print("  http://localhost:5173 → Self-Healing → Logs tab")
