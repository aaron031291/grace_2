"""Check book ingestion progress"""

import sys
import io
import sqlite3
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Check uploads folder
uploads = list(Path("storage/uploads").glob("*.pdf"))
print(f"📤 Files uploaded: {len(uploads)}")

# Check database
conn = sqlite3.connect("databases/memory_tables.db")

# Check documents
cursor = conn.execute("SELECT COUNT(*) FROM memory_documents WHERE source_type='book'")
books_in_db = cursor.fetchone()[0]
print(f"📚 Books in database: {books_in_db}")

# Check chunks
try:
    cursor = conn.execute("SELECT COUNT(*) FROM memory_document_chunks")
    chunks = cursor.fetchone()[0]
    print(f"📊 Chunks created: {chunks}")
except:
    print(f"📊 Chunks created: 0 (table may not exist)")

# Check insights  
cursor = conn.execute("SELECT COUNT(*) FROM memory_insights")
insights = cursor.fetchone()[0]
print(f"💡 Insights generated: {insights}")

# Check recent activity
cursor = conn.execute("SELECT id, title, source_type FROM memory_documents ORDER BY ROWID DESC LIMIT 5")
recent = cursor.fetchall()

if recent:
    print(f"\n📖 Recent documents:")
    for doc in recent:
        print(f"   - {doc[1]} ({doc[2]})")

print(f"\n{'✅ Processing complete!' if books_in_db >= len(uploads) else '⏳ Still processing...'}")
print(f"\nExpected: {len(uploads)} books | Current: {books_in_db} books")
