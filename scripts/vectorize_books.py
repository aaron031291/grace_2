"""
Vectorize Book Chunks for Semantic Search

Creates embeddings for all book chunks enabling natural language queries.
"""

import sys
import io
import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "databases/memory_tables.db"
VECTOR_DIR = Path("storage/embeddings/books")


def get_chunks_to_vectorize(source: str = None):
    """Get all chunks that need embeddings"""
    
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT c.id, c.document_id, c.chunk_index, c.content, c.word_count, 
               COALESCE(d.title, 'Unknown') as title
        FROM memory_document_chunks c
        LEFT JOIN memory_documents d ON c.document_id = d.id
    """
    
    if source:
        query += f" AND d.notes LIKE '%{source}%'"
    
    query += " ORDER BY c.document_id, c.chunk_index"
    
    cursor = conn.execute(query)
    chunks = cursor.fetchall()
    conn.close()
    
    return chunks


def create_embedding_stub(text: str, chunk_id: int) -> dict:
    """
    Create embedding (stub for now - will use real embeddings when OpenAI is connected)
    
    In production, this would call:
    - OpenAI embeddings API
    - Or sentence-transformers locally
    - Or custom embedding model
    """
    
    # For now, create a simple hash-based vector (deterministic)
    import hashlib
    
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert to pseudo-vector (384 dimensions like sentence-transformers)
    vector = []
    for i in range(0, len(hash_bytes), 2):
        if i + 1 < len(hash_bytes):
            val = (hash_bytes[i] * 256 + hash_bytes[i+1]) / 65535.0
            vector.append(val)
    
    # Pad to 384 dimensions
    while len(vector) < 384:
        vector.append(0.0)
    
    return {
        "chunk_id": chunk_id,
        "vector": vector[:384],
        "dimensions": 384,
        "model": "stub_hash_vector",
        "created_at": datetime.now().isoformat()
    }


def store_embeddings(embeddings: list):
    """Store embeddings in vector store"""
    
    # Create storage directory
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    
    # Store as JSONL
    output_file = VECTOR_DIR / f"embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for emb in embeddings:
            f.write(json.dumps(emb) + '\n')
    
    print(f"   💾 Saved to: {output_file}")
    
    # Also store in database (if table exists)
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Create embeddings table if needed
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunk_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id INTEGER NOT NULL,
                embedding_vector TEXT NOT NULL,
                dimensions INTEGER DEFAULT 384,
                model VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        for emb in embeddings:
            conn.execute("""
                INSERT OR REPLACE INTO chunk_embeddings 
                (chunk_id, embedding_vector, dimensions, model)
                VALUES (?, ?, ?, ?)
            """, (
                emb['chunk_id'],
                json.dumps(emb['vector']),
                emb['dimensions'],
                emb['model']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"   💾 Stored {len(embeddings)} embeddings in database")
        
    except Exception as e:
        print(f"   ⚠️ Database storage error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Vectorize book chunks")
    parser.add_argument("--source", default="business-intelligence", help="Filter by source")
    parser.add_argument("--model", default="stub", choices=["stub", "openai", "local"], help="Embedding model")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("BOOK CHUNK VECTORIZATION")
    print("="*60)
    print(f"Source: {args.source}")
    print(f"Model: {args.model}")
    print("="*60)
    
    # Get chunks
    chunks = get_chunks_to_vectorize(args.source)
    
    if not chunks:
        print("\n❌ No chunks found to vectorize")
        sys.exit(1)
    
    print(f"\n📊 Found {len(chunks)} chunks from books")
    
    # Group by book
    books = {}
    for chunk in chunks:
        chunk_id, doc_id, chunk_idx, content, word_count, title = chunk
        if title not in books:
            books[title] = []
        books[title].append(chunk)
    
    print(f"📚 Across {len(books)} books:\n")
    for title, book_chunks in books.items():
        print(f"  • {title}: {len(book_chunks)} chunks")
    
    print("\n" + "="*60)
    print("GENERATING EMBEDDINGS")
    print("="*60)
    
    if args.model == "openai":
        print("⚠️ OpenAI embeddings not implemented yet")
        print("   Using stub vectors for now")
    
    all_embeddings = []
    
    for i, chunk in enumerate(chunks, 1):
        chunk_id, doc_id, chunk_idx, content, word_count, title = chunk
        
        if i % 10 == 0:
            print(f"   Progress: {i}/{len(chunks)} chunks...")
        
        # Create embedding
        embedding = create_embedding_stub(content, chunk_id)
        all_embeddings.append(embedding)
    
    # Store embeddings
    print(f"\n💾 Storing {len(all_embeddings)} embeddings...")
    store_embeddings(all_embeddings)
    
    print("\n" + "="*60)
    print("VECTORIZATION COMPLETE")
    print("="*60)
    print(f"✅ Processed: {len(chunks)} chunks")
    print(f"📁 Storage: {VECTOR_DIR}")
    print(f"💾 Database: chunk_embeddings table")
    print("\n🔍 Next step: Build search index")
    print("   python scripts/build_search_index.py")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
