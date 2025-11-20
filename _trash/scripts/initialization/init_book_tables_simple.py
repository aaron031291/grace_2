"""
Simple Book System Database Initialization
Creates tables directly without ORM dependencies
"""

import sqlite3
from pathlib import Path
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("Initializing Grace Book System Database...\n")
    
    # Create databases directory
    db_path = Path("databases/memory_fusion.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("Creating tables...\n")
    
    # 1. memory_documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_documents (
            document_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            source_type TEXT NOT NULL,
            file_path TEXT,
            trust_score REAL DEFAULT 0.5,
            metadata TEXT,
            verification_results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✓ Created memory_documents")
    
    # 2. memory_document_chunks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_document_chunks (
            chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES memory_documents(document_id)
        )
    """)
    print("✓ Created memory_document_chunks")
    
    # 3. memory_insights
    cursor.execute("""
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_verification_suites (
            verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            verification_type TEXT NOT NULL,
            results TEXT,
            trust_score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES memory_documents(document_id)
        )
    """)
    print("✓ Created memory_verification_suites")
    
    # 5. memory_librarian_log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_librarian_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            target_path TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created memory_librarian_log")
    
    # 6. memory_sub_agents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_sub_agents (
            agent_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            mission TEXT,
            capabilities TEXT,
            constraints TEXT,
            status TEXT DEFAULT 'idle',
            current_task TEXT,
            tasks_completed INTEGER DEFAULT 0,
            tasks_failed INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            trust_score REAL DEFAULT 0.5,
            last_active_at TIMESTAMP,
            heartbeat_interval_sec INTEGER DEFAULT 30,
            governance_stamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created memory_sub_agents")
    
    # 7. memory_file_operations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_file_operations (
            operation_id TEXT PRIMARY KEY,
            operation_type TEXT NOT NULL,
            source_path TEXT,
            target_path TEXT,
            backup_path TEXT,
            can_undo INTEGER DEFAULT 1,
            undone INTEGER DEFAULT 0,
            undone_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    """)
    print("✓ Created memory_file_operations")
    
    # 8. memory_file_organization_rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_file_organization_rules (
            rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_pattern TEXT NOT NULL,
            target_folder TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            learned_from_user INTEGER DEFAULT 0,
            times_applied INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    print("✓ Created memory_file_organization_rules")
    
    # Create indexes
    print("\nCreating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_documents_source_type ON memory_documents(source_type)",
        "CREATE INDEX IF NOT EXISTS idx_documents_trust_score ON memory_documents(trust_score)",
        "CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON memory_document_chunks(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_insights_document_id ON memory_insights(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_verifications_document_id ON memory_verification_suites(document_id)",
        "CREATE INDEX IF NOT EXISTS idx_librarian_log_timestamp ON memory_librarian_log(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_file_ops_timestamp ON memory_file_operations(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_org_rules_pattern ON memory_file_organization_rules(file_pattern)"
    ]
    
    for idx_sql in indexes:
        cursor.execute(idx_sql)
    
    print("✓ Created all indexes")
    
    conn.commit()
    
    # Verify tables
    print("\nVerifying tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  {table[0]}: {count} rows")
    
    conn.close()
    
    print("\n✓ Database initialization complete!")
    
    # Create directory structure
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
    
    print("\n" + "="*60)
    print("🚀 SYSTEM READY!")
    print("="*60)
    print("\nYou can now:")
    print("  1. Drop books into grace_training/documents/books/")
    print("  2. Run E2E test: python tests/test_book_ingestion_e2e.py")
    print("  3. Start backend: python serve.py")
    print("  4. Start frontend: cd frontend && npm run dev")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
