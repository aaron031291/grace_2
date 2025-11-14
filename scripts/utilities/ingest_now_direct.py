"""
Direct book ingestion - bypasses async issues

Directly inserts books into memory_documents for immediate access.
"""

import sys
import io
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UPLOAD_DIR = Path("storage/uploads")
DB_PATH = "databases/memory_tables.db"

# Book metadata
BOOKS = {
    "customer-success": {
        "title": "Complete Guide to Customer Success for SaaS Companies",
        "author": "Various",
        "summary": "Comprehensive guide on building and scaling customer success teams for SaaS businesses",
        "key_topics": ["customer success", "saas", "retention", "churn", "onboarding"]
    },
    "Lean-Startup": {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "summary": "Build-Measure-Learn methodology for creating successful startups through validated learning and rapid iteration",
        "key_topics": ["lean startup", "mvp", "validated learning", "pivot", "innovation"]
    },
    "Traffic-Secrets": {
        "title": "Traffic Secrets",
        "author": "Russell Brunson",
        "summary": "Proven strategies for generating targeted traffic and growing your audience through content and paid advertising",
        "key_topics": ["traffic generation", "marketing", "audience building", "paid ads", "content strategy"]
    },
    "5-Dysfunctions": {
        "title": "The Five Dysfunctions of a Team - Facilitators Guide",
        "author": "Patrick Lencioni",
        "summary": "Framework for building cohesive teams by addressing absence of trust, fear of conflict, lack of commitment, avoidance of accountability, and inattention to results",
        "key_topics": ["team building", "leadership", "trust", "accountability", "teamwork"]
    },
    "Corporate-Finance": {
        "title": "Principles of Corporate Finance (14th Edition)",
        "author": "Brealey, Myers, Allen",
        "summary": "Comprehensive textbook on corporate financial management, investment decisions, and valuation",
        "key_topics": ["corporate finance", "valuation", "capital structure", "investment", "financial markets"]
    },
    "Fast-Cash": {
        "title": "$100M Fast Cash Playbook",
        "author": "Alex Hormozi",
        "summary": "Strategies for rapid cash generation and scaling businesses to $100M through optimized sales processes",
        "key_topics": ["sales", "cash flow", "scaling", "revenue growth", "business systems"]
    },
    "Lead-Nurture": {
        "title": "$100M Lead Nurture Playbook",
        "author": "Alex Hormozi",
        "summary": "Systems and strategies for nurturing leads through the sales pipeline to maximize conversion rates",
        "key_topics": ["lead nurturing", "sales pipeline", "conversion optimization", "follow-up", "email marketing"]
    },
    "Goated-Ads": {
        "title": "$100M Goated Ads Playbook",
        "author": "Alex Hormozi",
        "summary": "Advanced advertising strategies and frameworks for creating high-converting ad campaigns at scale",
        "key_topics": ["advertising", "paid acquisition", "ad creative", "targeting", "conversion"]
    },
    "Closing": {
        "title": "$100M Closing Playbook",
        "author": "Alex Hormozi",
        "summary": "Sales closing techniques and frameworks for handling objections and converting prospects into customers",
        "key_topics": ["sales closing", "objection handling", "negotiation", "deal structure", "sales psychology"]
    }
}

def match_pdf_to_metadata(pdf_path: Path):
    """Match PDF file to metadata"""
    filename = pdf_path.stem.lower()
    
    for key, meta in BOOKS.items():
        if key.lower() in filename:
            return meta
    
    # Fallback
    return {
        "title": pdf_path.stem.replace("-", " ").replace("_", " "),
        "author": "Unknown",
        "summary": f"Business intelligence document: {pdf_path.stem}",
        "key_topics": ["business", "intelligence"]
    }

def ingest_books():
    """Ingest all uploaded PDFs directly into database"""
    
    pdfs = list(UPLOAD_DIR.glob("*.pdf"))
    
    if not pdfs:
        print("❌ No PDFs found in storage/uploads/")
        return
    
    print(f"\n📚 Ingesting {len(pdfs)} books directly to Memory Fusion...\n")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    ingested = 0
    
    for i, pdf in enumerate(pdfs, 1):
        meta = match_pdf_to_metadata(pdf)
        
        # Generate document ID
        doc_id = hashlib.md5(str(pdf).encode()).hexdigest()
        
        print(f"\n[{i}/{len(pdfs)}] {meta['title']}")
        print(f"   Author: {meta['author']}")
        print(f"   Size: {pdf.stat().st_size / (1024*1024):.2f} MB")
        
        try:
            # Insert into memory_documents
            cursor.execute("""
                INSERT OR REPLACE INTO memory_documents
                (id, file_path, title, authors, source_type, summary, key_topics, 
                 token_count, trust_score, risk_level, last_synced_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                str(pdf),
                meta['title'],
                json.dumps([meta['author']]),
                'book',
                meta['summary'],
                json.dumps({topic: 1.0 for topic in meta['key_topics']}),
                0,  # Will be updated during chunking
                0.85,  # High trust for curated business books
                'low',
                datetime.now().isoformat(),
                f"Business intelligence book - ingested {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ))
            
            conn.commit()
            print(f"   ✅ Ingested to Memory Fusion")
            ingested += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✅ INGESTION COMPLETE: {ingested}/{len(pdfs)} books")
    print("="*60)
    print("\nQuery your knowledge:")
    print("  python query_book.py")
    print("  python query_book.py 'Lean Startup'")
    print("  python query_book.py 'sales'")
    print()

if __name__ == "__main__":
    ingest_books()
