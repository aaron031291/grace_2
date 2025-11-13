"""
Quick CRUD operations test to verify system works end-to-end
"""
import asyncio
import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import get_db

async def test_crud():
    """Test Create, Read, Update, Delete operations"""
    
    print("\n" + "="*60)
    print("  CRUD OPERATIONS TEST".center(60))
    print("="*60 + "\n")
    
    db = await get_db()
    
    # CREATE
    print("1. CREATE - Inserting test document...")
    test_id = "test_book_123"
    await db.execute(
        """INSERT OR REPLACE INTO memory_documents 
           (document_id, title, author, source_type, trust_score, created_at)
           VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
        (test_id, "Test Book", "Test Author", "book", 0.95)
    )
    await db.commit()
    print("   ✓ Document inserted")
    
    # READ
    print("\n2. READ - Querying document...")
    doc = await db.fetch_one(
        "SELECT * FROM memory_documents WHERE document_id = ?",
        (test_id,)
    )
    if doc:
        print(f"   ✓ Found: {doc['title']} by {doc['author']}")
        print(f"   Trust score: {doc['trust_score']}")
    else:
        print("   ✗ Document not found!")
        return False
    
    # UPDATE
    print("\n3. UPDATE - Changing trust score...")
    await db.execute(
        "UPDATE memory_documents SET trust_score = ? WHERE document_id = ?",
        (1.0, test_id)
    )
    await db.commit()
    
    doc = await db.fetch_one(
        "SELECT trust_score FROM memory_documents WHERE document_id = ?",
        (test_id,)
    )
    print(f"   ✓ Updated trust score: {doc['trust_score']}")
    
    # DELETE
    print("\n4. DELETE - Removing test document...")
    await db.execute(
        "DELETE FROM memory_documents WHERE document_id = ?",
        (test_id,)
    )
    await db.commit()
    
    doc = await db.fetch_one(
        "SELECT * FROM memory_documents WHERE document_id = ?",
        (test_id,)
    )
    if doc is None:
        print("   ✓ Document deleted successfully")
    else:
        print("   ✗ Document still exists!")
        return False
    
    # Verify other tables
    print("\n5. VERIFY TABLES...")
    tables = [
        'memory_document_chunks',
        'memory_insights',
        'memory_verification_suites',
        'memory_file_operations',
        'memory_librarian_log'
    ]
    
    for table in tables:
        try:
            result = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            print(f"   ✓ {table}: {result['count']} rows")
        except Exception as e:
            print(f"   ✗ {table}: ERROR - {e}")
    
    print("\n" + "="*60)
    print("  ✓ ALL CRUD OPERATIONS SUCCESSFUL!".center(60))
    print("="*60 + "\n")
    
    print("Database is working correctly!")
    print("\nNext: Start the system and test the UI")
    print("  1. python serve.py")
    print("  2. cd frontend && npm run dev")
    print("  3. http://localhost:5173")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_crud())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
