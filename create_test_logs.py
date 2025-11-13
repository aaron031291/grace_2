"""
Create test log entries to demonstrate the log viewing system
"""
import asyncio
import sys
import io
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.database import get_db

async def create_test_logs():
    """Create sample log entries"""
    
    print("\n" + "="*60)
    print("  Creating Test Log Entries")
    print("="*60 + "\n")
    
    db = await get_db()
    
    # Sample log entries
    log_entries = [
        {
            "action_type": "schema_proposal",
            "target_path": "grace_training/documents/books/lean_startup.pdf",
            "details": json.dumps({"confidence": 0.92, "proposed_table": "memory_documents"})
        },
        {
            "action_type": "schema_approval",
            "target_path": "schema_001",
            "details": json.dumps({"status": "approved", "approved_by": "auto_approval"})
        },
        {
            "action_type": "ingestion_launch",
            "target_path": "lean_startup.pdf",
            "details": json.dumps({"pipeline": "book_ingestion", "priority": "high"})
        },
        {
            "action_type": "file_organization",
            "target_path": "startup_notes.txt",
            "details": json.dumps({"from": "grace_training/", "to": "grace_training/business/", "confidence": 0.88})
        },
        {
            "action_type": "ingestion_complete",
            "target_path": "book_abc123",
            "details": json.dumps({"chunks": 120, "insights": 18, "duration_sec": 45.2})
        },
        {
            "action_type": "trust_update",
            "target_path": "book_abc123",
            "details": json.dumps({"old_score": 0.5, "new_score": 0.95, "verified": True})
        },
        {
            "action_type": "folder_created",
            "target_path": "grace_training/crypto/",
            "details": json.dumps({"domain": "crypto", "auto_created": True})
        },
        {
            "action_type": "automation_rule_executed",
            "target_path": "auto_verify_books",
            "details": json.dumps({"rule": "Auto-verify after ingestion", "triggered_by": "ingestion_complete"})
        }
    ]
    
    for i, entry in enumerate(log_entries):
        await db.execute(
            """INSERT INTO memory_librarian_log 
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (entry["action_type"], entry["target_path"], entry["details"])
        )
        print(f"✓ Created log {i+1}: {entry['action_type']} -> {entry['target_path']}")
    
    await db.commit()
    
    print(f"\n✅ Created {len(log_entries)} test log entries")
    
    # Verify they exist
    print("\n" + "="*60)
    print("  Verifying Logs in Database")
    print("="*60 + "\n")
    
    logs = await db.fetch_all(
        "SELECT * FROM memory_librarian_log ORDER BY timestamp DESC LIMIT 10"
    )
    
    print(f"Total logs in database: {len(logs)}\n")
    
    for i, log in enumerate(logs):
        print(f"{i+1}. [{log.get('action_type')}] {log.get('target_path')}")
        print(f"   Time: {log.get('timestamp')}")
        if log.get('details'):
            details = log.get('details')
            print(f"   Details: {details[:80]}...")
        print()
    
    print("="*60)
    print("  ✓ Logs Created Successfully!")
    print("="*60)
    print("\nNow test the API:")
    print("  curl http://localhost:8000/api/librarian/logs/tail?lines=10")
    print("\nOr open UI:")
    print("  http://localhost:5173 → Self-Healing → Logs tab")

if __name__ == "__main__":
    asyncio.run(create_test_logs())
