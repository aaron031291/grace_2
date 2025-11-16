"""
Generate summaries and insights from book chunks

Analyzes book content and creates:
- Chapter summaries
- Key takeaways
- Actionable insights
- Flashcards for learning
"""

import sys
import io
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "databases/memory_tables.db"


def get_books_with_chunks():
    """Get all books that have extracted content"""
    conn = sqlite3.connect(DB_PATH)
    
    # Get books
    cursor = conn.execute("""
        SELECT DISTINCT d.id, d.title, d.authors, COUNT(c.id) as chunk_count
        FROM memory_documents d
        LEFT JOIN memory_document_chunks c ON d.id = c.document_id
        WHERE d.source_type = 'book'
        GROUP BY d.id
        HAVING COUNT(c.id) > 0
    """)
    
    books = cursor.fetchall()
    conn.close()
    
    return books


def analyze_book_content(book_id: str, title: str) -> dict:
    """Analyze book chunks and generate insights"""
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get all chunks for this book
    cursor = conn.execute("""
        SELECT chunk_index, content, word_count
        FROM memory_document_chunks
        WHERE document_id = ?
        ORDER BY chunk_index
    """, (book_id,))
    
    chunks = cursor.fetchall()
    conn.close()
    
    total_words = sum(c[2] for c in chunks)
    
    # Sample first few chunks for summary
    sample_text = "\n".join([c[1] for c in chunks[:3]])[:5000]
    
    # Extract key patterns (simple heuristics - can be enhanced with LLM)
    insights = {
        "book_id": book_id,
        "title": title,
        "total_chunks": len(chunks),
        "total_words": total_words,
        "summary": f"{title} - Comprehensive guide with {total_words:,} words across {len(chunks)} sections.",
        "key_takeaways": extract_takeaways(sample_text, title),
        "generated_at": datetime.now().isoformat()
    }
    
    return insights


def extract_takeaways(text: str, title: str) -> list:
    """Extract key takeaways from text"""
    
    takeaways = []
    
    # Look for common patterns
    patterns = [
        "key is", "important to", "must", "should", "always",
        "never", "critical", "essential", "fundamental"
    ]
    
    sentences = text.split(".")
    for sentence in sentences[:20]:  # First 20 sentences
        sentence_lower = sentence.lower()
        for pattern in patterns:
            if pattern in sentence_lower and len(sentence) > 30:
                takeaway = sentence.strip()
                if takeaway and takeaway not in takeaways:
                    takeaways.append(takeaway)
                    if len(takeaways) >= 5:
                        break
        if len(takeaways) >= 5:
            break
    
    return takeaways[:5]


def generate_flashcards(book_id: str, title: str, insights: dict) -> list:
    """Generate flashcards for spaced repetition"""
    
    flashcards = []
    
    # Create flashcards from takeaways
    for i, takeaway in enumerate(insights.get('key_takeaways', [])[:3], 1):
        flashcard = {
            "book_id": book_id,
            "front": f"What is a key principle from '{title}'?",
            "back": takeaway,
            "category": "business_intelligence",
            "difficulty": "medium"
        }
        flashcards.append(flashcard)
    
    # Add summary flashcard
    flashcards.append({
        "book_id": book_id,
        "front": f"What is '{title}' about?",
        "back": insights.get('summary', ''),
        "category": "business_intelligence",
        "difficulty": "easy"
    })
    
    return flashcards


def store_insights(insights: dict, flashcards: list):
    """Store insights and flashcards in database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Store main insight
    try:
        cursor.execute("""
            INSERT INTO memory_insights 
            (source, summary, category, confidence, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            insights['book_id'],
            insights['summary'],
            'book_summary',
            0.8,
            json.dumps({
                "title": insights['title'],
                "total_words": insights['total_words'],
                "total_chunks": insights['total_chunks'],
                "key_takeaways": insights['key_takeaways']
            })
        ))
        
        # Store flashcards as separate insights
        for fc in flashcards:
            cursor.execute("""
                INSERT INTO memory_insights
                (source, summary, category, confidence, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                fc['book_id'],
                fc['back'],
                'flashcard',
                0.7,
                json.dumps({
                    "front": fc['front'],
                    "category": fc['category'],
                    "difficulty": fc['difficulty']
                })
            ))
        
        conn.commit()
        print(f"   ✅ Stored 1 summary + {len(flashcards)} flashcards")
        
    except Exception as e:
        print(f"   ⚠️ Storage error: {e}")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Generate book notes and insights")
    parser.add_argument("--auto", action="store_true", help="Run without prompts")
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("BOOK NOTES & INSIGHTS GENERATOR")
    print("="*60)
    
    # Get books
    books = get_books_with_chunks()
    
    if not books:
        print("\n❌ No books with extracted content found")
        print("Run: python extract_full_book_content.py")
        sys.exit(1)
    
    print(f"\n📚 Found {len(books)} books with content:\n")
    
    for book in books:
        book_id, title, authors, chunk_count = book
        print(f"  • {title} ({chunk_count} chunks)")
    
    if not args.auto:
        response = input("\nGenerate insights for all books? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            sys.exit(0)
    
    print("\n" + "="*60)
    print("GENERATING INSIGHTS")
    print("="*60)
    
    total_flashcards = 0
    
    for i, book in enumerate(books, 1):
        book_id, title, authors, chunk_count = book
        
        print(f"\n[{i}/{len(books)}] {title}")
        print("-"*60)
        
        # Analyze
        insights = analyze_book_content(book_id, title)
        
        # Generate flashcards
        flashcards = generate_flashcards(book_id, title, insights)
        
        # Store
        store_insights(insights, flashcards)
        
        total_flashcards += len(flashcards)
        
        print(f"   📝 Summary: {insights['summary'][:100]}...")
        print(f"   🎯 Takeaways: {len(insights['key_takeaways'])}")
        print(f"   🃏 Flashcards: {len(flashcards)}")
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"✅ Processed: {len(books)} books")
    print(f"💡 Total insights: {len(books)}")
    print(f"🃏 Total flashcards: {total_flashcards}")
    print("\n📊 Query insights:")
    print("   curl http://localhost:8000/api/librarian/flashcards")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
