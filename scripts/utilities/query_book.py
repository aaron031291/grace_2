"""
Query Book Content from Memory Database

Shows what Grace knows about a book after ingestion.
"""

import sys
import io
import sqlite3
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def query_book(search_term=None):
    """Query book content from memory database"""
    
    db_path = Path("databases/memory_tables.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    # Get total documents
    cursor = conn.execute("SELECT COUNT(*) FROM memory_documents")
    total = cursor.fetchone()[0]
    
    print(f"\n📚 Total documents in system: {total}\n")
    print("="*60)
    
    if search_term:
        # Search for specific book
        query = """
            SELECT id, title, summary, key_topics, authors, source_type, 
                   token_count, trust_score, notes
            FROM memory_documents 
            WHERE title LIKE ? OR summary LIKE ?
            ORDER BY ROWID DESC
            LIMIT 5
        """
        cursor = conn.execute(query, (f"%{search_term}%", f"%{search_term}%"))
    else:
        # Get most recent
        query = """
            SELECT id, title, summary, key_topics, authors, source_type,
                   token_count, trust_score, notes
            FROM memory_documents 
            ORDER BY ROWID DESC 
            LIMIT 5
        """
        cursor = conn.execute(query)
    
    docs = cursor.fetchall()
    
    if not docs:
        print(f"❌ No documents found" + (f" matching '{search_term}'" if search_term else ""))
        return
    
    for i, doc in enumerate(docs, 1):
        doc_id, title, summary, key_topics, authors, source_type, token_count, trust_score, notes = doc
        
        print(f"\n{i}. {title}")
        print("-" * 60)
        print(f"ID: {doc_id}")
        print(f"Source Type: {source_type}")
        
        if authors and authors != '[]':
            try:
                authors_list = json.loads(authors)
                if authors_list:
                    print(f"Authors: {', '.join(authors_list)}")
            except:
                print(f"Authors: {authors}")
        
        if summary:
            print(f"\nSummary:")
            print(f"  {summary}")
        
        if key_topics and key_topics != '{}':
            try:
                topics = json.loads(key_topics)
                if topics:
                    print(f"\nKey Topics: {', '.join(topics.keys())}")
            except:
                pass
        
        if token_count:
            print(f"\nToken Count: {token_count:,}")
        
        if trust_score is not None:
            print(f"Trust Score: {trust_score:.2f}")
        
        if notes:
            print(f"\nNotes: {notes}")
        
        print("="*60)
    
    # Check if there's content in insights
    cursor = conn.execute("SELECT COUNT(*) FROM memory_insights")
    insights_count = cursor.fetchone()[0]
    
    if insights_count > 0:
        print(f"\n💡 Total insights in system: {insights_count}")
        
        if search_term:
            cursor = conn.execute(
                "SELECT summary FROM memory_insights WHERE summary LIKE ? LIMIT 3",
                (f"%{search_term}%",)
            )
        else:
            cursor = conn.execute(
                "SELECT summary FROM memory_insights ORDER BY ROWID DESC LIMIT 3"
            )
        
        insights = cursor.fetchall()
        if insights:
            print("\nRecent insights:")
            for insight in insights:
                print(f"  • {insight[0][:200]}...")
    
    conn.close()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
        print(f"\n🔍 Searching for: '{search_term}'")
        query_book(search_term)
    else:
        print("\n📖 Showing most recent documents:")
        query_book()
    
    print()


if __name__ == "__main__":
    main()
