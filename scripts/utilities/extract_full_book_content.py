"""
Extract FULL text content from PDFs and store in database

Reads every page of each PDF and stores complete content.
"""

import sys
import io
from pathlib import Path
import sqlite3
import json
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from pypdf import PdfReader
    print("✅ Using pypdf for extraction")
except ImportError:
    try:
        from PyPDF2 import PdfReader
        print("✅ Using PyPDF2 for extraction")
    except ImportError:
        print("❌ No PDF library found. Install: pip install pypdf")
        sys.exit(1)


def extract_pdf_text(pdf_path: Path) -> dict:
    """Extract full text from PDF"""
    
    print(f"\n📄 Extracting: {pdf_path.name}")
    print(f"   Size: {pdf_path.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        reader = PdfReader(str(pdf_path))
        
        total_pages = len(reader.pages)
        print(f"   Pages: {total_pages}")
        
        # Extract text from all pages
        full_text = ""
        for i, page in enumerate(reader.pages, 1):
            try:
                text = page.extract_text()
                full_text += text + "\n\n"
                
                if i % 50 == 0:  # Progress every 50 pages
                    print(f"   Progress: {i}/{total_pages} pages...")
            except Exception as e:
                print(f"   ⚠️ Page {i} extraction failed: {e}")
        
        # Get metadata
        metadata = {}
        if reader.metadata:
            metadata = {
                "pdf_title": reader.metadata.get('/Title', ''),
                "pdf_author": reader.metadata.get('/Author', ''),
                "pdf_subject": reader.metadata.get('/Subject', ''),
                "pdf_creator": reader.metadata.get('/Creator', ''),
            }
        
        word_count = len(full_text.split())
        char_count = len(full_text)
        
        print(f"   ✅ Extracted: {word_count:,} words, {char_count:,} characters")
        
        return {
            "success": True,
            "full_text": full_text,
            "total_pages": total_pages,
            "word_count": word_count,
            "char_count": char_count,
            "metadata": metadata
        }
        
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Chunk text into overlapping segments"""
    
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        chunks.append({
            "text": chunk_text,
            "start_word": i,
            "end_word": i + len(chunk_words),
            "word_count": len(chunk_words)
        })
    
    return chunks


def store_full_content(pdf_path: Path, extraction_result: dict, db_path: str = "databases/memory_tables.db"):
    """Store full content and chunks in database"""
    
    if not extraction_result["success"]:
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find the document ID for this PDF
    cursor.execute(
        "SELECT id, title FROM memory_documents WHERE file_path LIKE ?",
        (f"%{pdf_path.name}%",)
    )
    
    result = cursor.fetchone()
    if not result:
        print(f"   ⚠️ Document not found in database")
        conn.close()
        return False
    
    doc_id, title = result
    
    print(f"\n💾 Storing full content for: {title}")
    
    # Create chunks table if doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            word_count INTEGER,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Store chunks
    full_text = extraction_result["full_text"]
    chunks = chunk_text(full_text, chunk_size=2000, overlap=200)
    
    print(f"   Creating {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks):
        cursor.execute("""
            INSERT INTO memory_document_chunks 
            (document_id, chunk_index, content, word_count, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc_id,
            i,
            chunk["text"],
            chunk["word_count"],
            json.dumps({
                "start_word": chunk["start_word"],
                "end_word": chunk["end_word"],
                "extraction_timestamp": datetime.now().isoformat()
            })
        ))
    
    # Update document with full stats
    cursor.execute("""
        UPDATE memory_documents
        SET token_count = ?,
            notes = ?
        WHERE id = ?
    """, (
        extraction_result["word_count"],
        f"Full text extracted: {extraction_result['total_pages']} pages, {extraction_result['word_count']:,} words, {len(chunks)} chunks",
        doc_id
    ))
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ Stored {len(chunks)} chunks in database")
    return True


def process_all_pdfs():
    """Process all uploaded PDFs"""
    
    upload_dir = Path("storage/uploads")
    pdfs = sorted(upload_dir.glob("*.pdf"))
    
    if not pdfs:
        print("❌ No PDFs found in storage/uploads/")
        return
    
    print("\n" + "="*60)
    print(f"📚 EXTRACTING FULL CONTENT FROM {len(pdfs)} BOOKS")
    print("="*60)
    print("\nThis will:")
    print("  1. Read every page of every PDF")
    print("  2. Extract all text content")  
    print("  3. Chunk into 2000-word segments")
    print("  4. Store in memory_document_chunks table")
    print("\nEstimated time: 5-10 minutes for all books")
    print("="*60)
    
    successful = 0
    failed = 0
    total_pages = 0
    total_words = 0
    total_chunks = 0
    
    for i, pdf in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] {pdf.name}")
        print("-"*60)
        
        # Extract
        result = extract_pdf_text(pdf)
        
        if result["success"]:
            # Store
            if store_full_content(pdf, result):
                successful += 1
                total_pages += result["total_pages"]
                total_words += result["word_count"]
                chunk_count = (result["word_count"] // 1800) + 1  # Approximate
                total_chunks += chunk_count
            else:
                failed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"✅ Successful: {successful}/{len(pdfs)}")
    print(f"❌ Failed: {failed}/{len(pdfs)}")
    print(f"\n📊 Total Extracted:")
    print(f"   Pages: {total_pages:,}")
    print(f"   Words: {total_words:,}")
    print(f"   Chunks: {total_chunks:,}")
    print("\n💾 All content stored in: databases/memory_tables.db")
    print("   Table: memory_document_chunks")
    print("\n🔍 Query full content:")
    print("   python query_book.py 'Lean Startup'")
    print("   (Will now search actual book content!)")
    print("="*60)
    print()


if __name__ == "__main__":
    process_all_pdfs()
