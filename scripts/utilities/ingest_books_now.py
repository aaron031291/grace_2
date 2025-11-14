"""Quick book ingestion - no prompts"""

import sys
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time

BASE_URL = "http://localhost:8000"
BOOK_DIR = Path("grace_training/buiness intellinagce")

print("\n" + "="*60)
print("GRACE - BUSINESS INTELLIGENCE BOOK INGESTION")
print("="*60)

# Find PDFs
pdfs = list(BOOK_DIR.glob("*.pdf"))
print(f"\n📚 Found {len(pdfs)} books to ingest\n")

for i, pdf in enumerate(pdfs, 1):
    print(f"\n[{i}/{len(pdfs)}] {pdf.name}")
    print(f"   Size: {pdf.stat().st_size / 1024:.1f} KB")
    
    # Extract title
    title = pdf.stem.split("-", 1)[-1] if "-" in pdf.stem else pdf.stem
    title = title.replace("-", " ").replace("_", " ")
    
    try:
        with open(pdf, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/api/books/upload",
                files={"file": (pdf.name, f, "application/pdf")},
                data={
                    "title": title,
                    "author": "Business Intelligence",
                    "trust_level": "high"
                },
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Uploaded: Job {data.get('job_id')}")
            print(f"   📊 Processing: {data.get('message', 'Started')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"      {response.text[:200]}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Delay between uploads
    if i < len(pdfs):
        print(f"   ⏸️ Waiting 5 seconds...")
        time.sleep(5)

print("\n" + "="*60)
print(f"✅ UPLOAD COMPLETE - {len(pdfs)} books submitted")
print("="*60)
print("\nProcessing in background...")
print("Check status: python query_book.py")
print()
