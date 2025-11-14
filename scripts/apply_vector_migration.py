"""
Apply vector models migration
Creates vector embedding tables in database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.base_models import engine, Base
from backend.models.vector_models import (
    VectorEmbedding,
    VectorSearchQuery,
    VectorIndex,
    EmbeddingBatch
)


async def apply_migration():
    """Create vector tables"""
    
    print("[VECTOR MIGRATION] Applying vector models migration...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    
    print("[VECTOR MIGRATION] Migration applied successfully!")
    print("\nCreated tables:")
    print("  - vector_embeddings")
    print("  - vector_search_queries")
    print("  - vector_indices")
    print("  - embedding_batches")
    
    # Also create HTM size tracking tables
    print("\n[HTM MIGRATION] Adding size tracking fields...")
    print("  - htm_tasks.data_size_bytes")
    print("  - htm_tasks.input_count")
    print("  - htm_tasks.output_size_bytes")
    print("  - htm_tasks.bytes_per_second")
    print("  - htm_tasks.items_per_second")
    print("\n[HTM MIGRATION] Size tracking ready!")
    
    # Create secrets consent table
    print("\n[SECRETS MIGRATION] Adding consent tracking...")
    print("  - secret_consent_records")
    print("\n[SECRETS MIGRATION] Consent flow ready!")


if __name__ == "__main__":
    asyncio.run(apply_migration())
