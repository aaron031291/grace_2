"""
Search Books with Natural Language Queries

Enables semantic search across all ingested books.
"""

import sys
import io
import sqlite3
import json
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "databases/memory_tables.db"


def create_query_embedding(query: str) -> list:
    """Create embedding for search query (stub)"""
    
    hash_obj = hashlib.sha256(query.encode())
    hash_bytes = hash_obj.digest()
    
    vector = []
    for i in range(0, len(hash_bytes), 2):
        if i + 1 < len(hash_bytes):
            val = (hash_bytes[i] * 256 + hash_bytes[i+1]) / 65535.0
            vector.append(val)
    
    while len(vector) < 384:
        vector.append(0.0)
    
    return vector[:384]


def simple_search(query: str, top_k: int = 5) -> list:
    """
    Simple keyword search across book chunks
    (Will be replaced with vector similarity when embeddings are ready)
    """
    
    conn = sqlite3.connect(DB_PATH)
    
    # Keyword search for now
    cursor = conn.execute("""
        SELECT c.content, c.word_count, c.chunk_index, d.title, d.authors
        FROM memory_document_chunks c
        LEFT JOIN memory_documents d ON c.document_id = d.id
        WHERE c.content LIKE ? OR c.content LIKE ?
        ORDER BY c.chunk_index
        LIMIT ?
    """, (f"%{query}%", f"%{query.title()}%", top_k))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def search_books(query: str, top_k: int = 5):
    """Search books and display results"""
    
    print(f"\n🔍 Searching: '{query}'")
    print("="*60)
    
    results = simple_search(query, top_k)
    
    if not results:
        print(f"\n❌ No results found for '{query}'")
        print("\nTry different keywords or check book topics:")
        print("  - sales, closing, objections")
        print("  - traffic, marketing, ads")
        print("  - customer success, churn, retention")
        print("  - lean startup, mvp, pivot")
        print("  - team, trust, accountability")
        print("  - finance, valuation, NPV")
        return
    
    print(f"\n📚 Found {len(results)} relevant passages:\n")
    
    for i, result in enumerate(results, 1):
        content, word_count, chunk_idx, title, authors = result
        
        # Extract relevant excerpt (around the keyword)
        query_lower = query.lower()
        content_lower = content.lower()
        
        pos = content_lower.find(query_lower)
        if pos == -1:
            # Try title case
            pos = content_lower.find(query.title().lower())
        
        if pos != -1:
            # Extract context around keyword
            start = max(0, pos - 200)
            end = min(len(content), pos + 400)
            excerpt = content[start:end]
            
            # Add ellipsis if truncated
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(content):
                excerpt = excerpt + "..."
        else:
            # Just show beginning
            excerpt = content[:600] + "..."
        
        print(f"{'='*60}")
        print(f"Result {i}:")
        print(f"  📖 Book: {title or 'Unknown'}")
        if authors:
            try:
                author_list = json.loads(authors)
                print(f"  ✍️ Author: {author_list[0] if author_list else 'Unknown'}")
            except:
                pass
        print(f"  📄 Chunk: #{chunk_idx} ({word_count} words)")
        print(f"\n  📝 Excerpt:")
        print(f"  {excerpt}")
        print()
    
    print("="*60)
    print(f"\n💡 Tip: Refine your search with more specific terms")
    print()


def main():
    if len(sys.argv) < 2:
        print("\n❌ Usage: python search_books.py <query> [top_k]")
        print("\nExamples:")
        print('  python search_books.py "Build-Measure-Learn"')
        print('  python search_books.py "objection handling" 10')
        print('  python search_books.py "traffic temperature"')
        print('  python search_books.py "customer churn"')
        print('  python search_books.py "pricing strategy"')
        print()
        sys.exit(1)
    
    query = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else " ".join(sys.argv[1:])
    top_k = int(sys.argv[-1]) if len(sys.argv) > 2 and sys.argv[-1].isdigit() else 5
    
    search_books(query, top_k)


if __name__ == "__main__":
    main()
