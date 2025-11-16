"""
Initialize Book System Database Tables
Creates all required tables with proper schemas
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import get_db


async def create_tables():
    """Create all tables required for book system"""
    
    db = await get_db()
    
    print("Creating book system tables...")
    
    # 1. memory_documents
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_documents (
            document_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            source_type TEXT NOT NULL,
            file_path TEXT,
            trust_score REAL DEFAULT 0.5,
            metadata JSON,
            verification_results JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✓ Created memory_documents")
    
    # 2. memory_document_chunks
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_document_chunks (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata JSON,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES memory_documents(document_id)
        )
    """)
    print("✓ Created memory_document_chunks")
    
    # 3. memory_insights
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_insights (
            insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            insight_type TEXT NOT NULL,
            content TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES memory_documents(document_id)
        )
    """)
    print("✓ Created memory_insights")
    
    # 4. memory_verification_suites
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_verification_suites (
            verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            verification_type TEXT NOT NULL,
            results JSON,
            trust_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES memory_documents(document_id)
        )
    """)
    print("✓ Created memory_verification_suites")
    
    # 5. memory_librarian_log
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_librarian_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            target_path TEXT,
            details JSON,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created memory_librarian_log")
    
    # 6. memory_sub_agents
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_sub_agents (
            agent_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            mission TEXT,
            capabilities JSON,
            constraints JSON,
            status TEXT DEFAULT 'idle',
            current_task TEXT,
            tasks_completed INTEGER DEFAULT 0,
            tasks_failed INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            trust_score REAL DEFAULT 0.5,
            last_active_at TIMESTAMP,
            heartbeat_interval_sec INTEGER DEFAULT 30,
            governance_stamp JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created memory_sub_agents")
    
    # 7. memory_file_operations
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_file_operations (
            operation_id TEXT PRIMARY KEY,
            operation_type TEXT NOT NULL,
            source_path TEXT,
            target_path TEXT,
            backup_path TEXT,
            can_undo BOOLEAN DEFAULT TRUE,
            undone BOOLEAN DEFAULT FALSE,
            undone_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details JSON
        )
    """)
    print("✓ Created memory_file_operations")
    
    # 8. memory_file_organization_rules
    await db.execute("""
        CREATE TABLE IF NOT EXISTS memory_file_organization_rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_pattern TEXT NOT NULL,
            target_folder TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            learned_from_user BOOLEAN DEFAULT FALSE,
            times_applied INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✓ Created memory_file_organization_rules")
    
    # Create indexes
    print("\nCreating indexes...")
    
    await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_source_type ON memory_documents(source_type)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_trust_score ON memory_documents(trust_score)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON memory_document_chunks(document_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_insights_document_id ON memory_insights(document_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_verifications_document_id ON memory_verification_suites(document_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_librarian_log_timestamp ON memory_librarian_log(timestamp)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_file_ops_timestamp ON memory_file_operations(timestamp)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_org_rules_pattern ON memory_file_organization_rules(file_pattern)")
    
    print("✓ Created indexes")
    
    await db.commit()
    
    print("\n✓ All tables created successfully!")
    
    # Verify tables
    print("\nVerifying tables...")
    tables = await db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    
    for table in tables:
        count = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table['name']}")
        print(f"  {table['name']}: {count['count']} rows")
    
    print("\n✓ Database initialization complete!")


async def create_directories():
    """Create required directory structure"""
    
    print("\nCreating directory structure...")
    
    directories = [
        "grace_training/documents/books",
        "grace_training/business",
        "grace_training/technical",
        "grace_training/finance",
        "grace_training/research",
        "grace_training/media",
        "grace_training/governance",
        "grace_training/learning",
        ".librarian_backups"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}/")
    
    # Create README in books folder
    books_readme = Path("grace_training/documents/books/README.md")
    if not books_readme.exists():
        with open(books_readme, 'w', encoding='utf-8') as f:
            f.write("# Books Library\n\n")
            f.write("Drop PDF/EPUB books here for Grace to learn from.\n\n")
            f.write("The Librarian will automatically:\n")
            f.write("- Extract text and metadata\n")
            f.write("- Create chunks and embeddings\n")
            f.write("- Generate summaries and flashcards\n")
            f.write("- Verify quality and assign trust scores\n")
        print("✓ Created books/README.md")
    
    print("\n✓ Directory structure created!")


if __name__ == "__main__":
    print("Initializing Grace Book System...\n")
    asyncio.run(create_tables())
    asyncio.run(create_directories())
    print("\n🚀 System ready! You can now:")
    print("   1. Drop books into grace_training/documents/books/")
    print("   2. Run E2E test: python tests/test_book_ingestion_e2e.py")
    print("   3. Start backend: python serve.py")
    print("   4. Start frontend: cd frontend && npm run dev")
