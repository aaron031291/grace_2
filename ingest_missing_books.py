"""Find and ingest missing books - TIGHT PIPELINE"""

import sys
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import sqlite3

BASE_URL = "http://localhost:8000"
BOOK_DIR = Path("grace_training/buiness intellinagce")

# Get existing books
conn = sqlite3.connect("databases/memory_tables.db")
cursor = conn.execute("SELECT file_path FROM memory_documents WHERE source_type='book'")
existing = {Path(row[0]).name for row in cursor.fetchall()}
conn.close()

print(f"\n📚 Existing books: {len(existing)}")

# Find all PDFs
all_pdfs = list(BOOK_DIR.glob("*.pdf"))
missing = [p for p in all_pdfs if p.name not in existing and not any(x in p.stem for x in ['20251113_'])]

print(f"📥 Total PDFs in folder: {len(all_pdfs)}")
print(f"❌ Missing from library: {len(missing)}\n")

if not missing:
    print("✅ All books already ingested!")
    sys.exit(0)

print("="*70)
print("MISSING BOOKS TO INGEST:")
print("="*70)

METADATA = {
    "Zig-Ziglars": {"title": "Zig Ziglar's Secrets of Closing the Sale", "author": "Zig Ziglar"},
    "Dotcom-Secrets": {"title": "Dotcom Secrets", "author": "Russell Brunson"},
    "Good-to-Great": {"title": "Good to Great", "author": "Jim Collins"},
    "Influence": {"title": "Influence: The Psychology of Persuasion", "author": "Robert Cialdini"},
    "HR-Competency": {"title": "HR Competency Models", "author": "Dave Ulrich"},
    "Final": {"title": "Final Document", "author": "Unknown"}
}

for i, pdf in enumerate(missing, 1):
    # Find metadata
    meta = None
    for key, data in METADATA.items():
        if key in pdf.stem:
            meta = data
            break
    
    if not meta:
        meta = {"title": pdf.stem.replace("-", " "), "author": "Unknown"}
    
    print(f"\n{i}. {meta['title']}")
    print(f"   File: {pdf.name}")
    print(f"   Size: {pdf.stat().st_size / (1024*1024):.2f} MB")
    print(f"   Uploading...", end=" ")
    
    try:
        with open(pdf, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/api/books/upload",
                files={"file": (pdf.name, f, "application/pdf")},
                data={
                    "title": meta["title"],
                    "author": meta["author"],
                    "trust_level": "high"
                },
                timeout=120
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'duplicate':
                print(f"⚠️ DUPLICATE (skipped)")
            else:
                print(f"✅ DONE")
                print(f"      Words: {data.get('words_extracted', 0):,}")
                print(f"      Chunks: {data.get('chunks_created', 0)}")
                print(f"      Steps: {len(data.get('steps_completed', []))}/7")
        else:
            print(f"❌ FAILED ({response.status_code})")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "="*70)
print("✅ INGESTION COMPLETE")
print("="*70)
print("\nVerifying...")

# Final count
conn = sqlite3.connect("databases/memory_tables.db")
cursor = conn.execute("SELECT COUNT(*), SUM(token_count) FROM memory_documents WHERE source_type='book'")
count, total_words = cursor.fetchone()
conn.close()

print(f"📚 Total books in library: {count}")
print(f"📝 Total words: {total_words:,}")
print("\nQuery: python scripts/search_books.py 'your-topic'")
print()
