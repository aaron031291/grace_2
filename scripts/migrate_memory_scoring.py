"""Database migration for Memory Scoring System

Creates tables for cognition layer memory management.
"""

import asyncio
from backend.models import engine, Base
from backend.cognition.models import MemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog


async def create_tables():
    """Create all cognition memory tables"""
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Created cognition memory tables:")
        print("  - cognition_memory_artifacts")
        print("  - cognition_trust_events")
        print("  - cognition_memory_index")
        print("  - cognition_gc_log")


async def verify_tables():
    """Verify tables were created"""
    from sqlalchemy import text
    
    async with engine.connect() as conn:
        # Check for tables
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cognition_%'"
        ))
        tables = [row[0] for row in result]
        
        print(f"\n✓ Verified {len(tables)} cognition tables:")
        for table in tables:
            print(f"  - {table}")
        
        return len(tables) == 4


async def seed_example_data():
    """Seed some example memory data for testing"""
    from backend.cognition import GraceLoopOutput, OutputType, loop_memory_bank
    
    print("\n📝 Seeding example data...")
    
    examples = [
        {
            "loop_id": "reflection_001",
            "component": "reflection",
            "output_type": OutputType.REASONING,
            "result": {"analysis": "Code quality assessment shows high maintainability"},
            "confidence": 0.92,
            "importance": 0.8
        },
        {
            "loop_id": "hunter_001",
            "component": "hunter",
            "output_type": OutputType.DECISION,
            "result": {"decision": "approve", "reasons": ["compliant", "tested"]},
            "confidence": 0.88,
            "importance": 0.9
        },
        {
            "loop_id": "meta_001",
            "component": "meta",
            "output_type": OutputType.REFLECTION,
            "result": {"reflection": "System performance within normal parameters"},
            "confidence": 0.85,
            "importance": 0.7
        },
        {
            "loop_id": "temporal_001",
            "component": "temporal",
            "output_type": OutputType.PREDICTION,
            "result": {"prediction": "Task will complete in 2.5 hours"},
            "confidence": 0.70,
            "importance": 0.6
        },
        {
            "loop_id": "observation_001",
            "component": "monitor",
            "output_type": OutputType.OBSERVATION,
            "result": {"cpu": 45, "memory": 2048, "disk": 15000},
            "confidence": 1.0,
            "importance": 0.3
        }
    ]
    
    refs = []
    for ex in examples:
        output = GraceLoopOutput(**ex)
        ref = await loop_memory_bank.store(output, domain="examples")
        refs.append(ref)
        print(f"  ✓ {ex['component']}: {ref.memory_ref} (trust={ref.trust_score:.3f})")
    
    print(f"\n✓ Seeded {len(refs)} example memories")
    
    # Simulate some usage
    print("\n🔄 Simulating usage patterns...")
    
    # Successful uses for reflection
    for _ in range(3):
        await loop_memory_bank.update_trust(refs[0].memory_ref, outcome="success")
    
    # Mixed uses for hunter
    await loop_memory_bank.update_trust(refs[1].memory_ref, outcome="success")
    await loop_memory_bank.update_trust(refs[1].memory_ref, outcome="failure")
    
    print("  ✓ Updated trust scores based on usage")
    
    return refs


async def test_queries():
    """Test some basic queries"""
    from backend.cognition import loop_memory_bank
    
    print("\n🔍 Testing queries...")
    
    # Query by component
    hits = await loop_memory_bank.read(
        query={"component": "reflection"},
        k=10
    )
    print(f"  ✓ Found {len(hits)} reflection memories")
    
    # Query by output type
    hits = await loop_memory_bank.read(
        query={"output_type": "reasoning"},
        k=10
    )
    print(f"  ✓ Found {len(hits)} reasoning outputs")
    
    # Query with filters
    hits = await loop_memory_bank.read(
        filters={"domain": "examples", "min_trust": 0.5},
        k=10
    )
    print(f"  ✓ Found {len(hits)} high-trust examples")
    
    # Show top result
    if hits:
        top = hits[0]
        print(f"\n📊 Top result:")
        print(f"  Ref: {top.memory_ref}")
        print(f"  Component: {top.output.component}")
        print(f"  Trust: {top.trust_score:.3f}")
        print(f"  Rank: {top.rank_score:.3f}")
        print(f"  Accesses: {top.access_count}")


async def main():
    """Run migration"""
    print("=" * 60)
    print("Memory Scoring System - Database Migration")
    print("=" * 60)
    
    # Create tables
    await create_tables()
    
    # Verify
    if not await verify_tables():
        print("❌ Table verification failed!")
        return
    
    # Seed example data
    refs = await seed_example_data()
    
    # Test queries
    await test_queries()
    
    print("\n" + "=" * 60)
    print("✅ Migration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run tests: pytest tests/test_memory_scoring.py -v")
    print("2. See MEMORY_SCORING.md for API documentation")
    print("3. Integrate with loops using loop_memory_bank.store(output)")


if __name__ == "__main__":
    asyncio.run(main())
