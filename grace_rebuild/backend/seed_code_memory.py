"""Seed Code Memory - Parse GRACE codebase into memory"""

import asyncio
from pathlib import Path
from code_memory import code_memory
from models import engine, Base
from datetime import datetime

async def seed_code_memory():
    """Parse entire GRACE codebase and store patterns"""
    
    print("🧠 Seeding Grace's Code Memory...")
    print("=" * 60)
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Get codebase root
    current_file = Path(__file__)
    grace_root = current_file.parent.parent  # grace_rebuild/
    
    print(f"\n📁 Parsing codebase: {grace_root}")
    
    # Parse Python code in backend
    backend_path = grace_root / "backend"
    
    print(f"\n🔍 Analyzing backend: {backend_path}")
    result = await code_memory.parse_codebase(
        root_path=str(backend_path),
        project_name="grace_backend",
        language_filter=["python"]
    )
    
    print(f"\n✅ Backend parsing complete:")
    print(f"   - Functions: {result['patterns_extracted']['functions']}")
    print(f"   - Classes: {result['patterns_extracted']['classes']}")
    print(f"   - Total patterns: {result['total']}")
    
    # Parse frontend if exists
    frontend_path = grace_root / "frontend"
    if frontend_path.exists():
        print(f"\n🔍 Analyzing frontend: {frontend_path}")
        frontend_result = await code_memory.parse_codebase(
            root_path=str(frontend_path),
            project_name="grace_frontend",
            language_filter=["javascript", "typescript"]
        )
        print(f"\n✅ Frontend parsing complete:")
        print(f"   - Total patterns: {frontend_result['total']}")
    
    # Generate statistics
    print("\n" + "=" * 60)
    print("📊 Code Memory Statistics")
    print("=" * 60)
    
    from sqlalchemy import select, func
    from code_memory import CodePattern
    from models import async_session
    
    async with async_session() as session:
        # Count by type
        result = await session.execute(
            select(
                CodePattern.pattern_type,
                func.count(CodePattern.id)
            ).group_by(CodePattern.pattern_type)
        )
        
        print("\nPatterns by type:")
        for pattern_type, count in result:
            print(f"   {pattern_type}: {count}")
        
        # Count by language
        result = await session.execute(
            select(
                CodePattern.language,
                func.count(CodePattern.id)
            ).group_by(CodePattern.language)
        )
        
        print("\nPatterns by language:")
        for language, count in result:
            print(f"   {language}: {count}")
        
        # Top tags
        all_patterns = await session.execute(select(CodePattern))
        all_tags = {}
        for pattern in all_patterns.scalars().all():
            if pattern.tags:
                for tag in pattern.tags:
                    all_tags[tag] = all_tags.get(tag, 0) + 1
        
        print("\nTop 10 tags:")
        for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {tag}: {count}")
    
    print("\n" + "=" * 60)
    print("✨ Code memory seeding complete!")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_code_memory())
