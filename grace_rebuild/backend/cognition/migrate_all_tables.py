"""Create all cognition system database tables"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, init_db, SessionLocal
from models import Base
from sqlalchemy import inspect

# Import all models to register them with Base
from cognition.memory_models import MemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog

def migrate():
    """Create all cognition tables"""
    print("🔧 Cognition System Migration")
    print("=" * 60)
    
    # Create all tables
    print("\n📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Verify tables
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    
    cognition_tables = [t for t in all_tables if 'cognition_' in t]
    
    print(f"\n✅ Created {len(cognition_tables)} cognition tables:")
    for table in sorted(cognition_tables):
        print(f"   - {table}")
    
    # Verify each expected table
    expected = [
        'cognition_memory_artifacts',
        'cognition_trust_events',
        'cognition_memory_index',
        'cognition_gc_log'
    ]
    
    missing = [t for t in expected if t not in all_tables]
    if missing:
        print(f"\n⚠️  Missing tables: {missing}")
        return False
    
    print(f"\n✅ All {len(expected)} expected tables verified")
    print(f"📊 Total tables in database: {len(all_tables)}")
    
    return True

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
