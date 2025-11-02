"""Seed Grace's Code Memory by Parsing grace_2 Codebase

This script parses the entire grace_2 codebase and extracts:
- Functions with signatures and documentation
- Classes with methods
- Code patterns and idioms
- Stores them in the code_patterns table for recall
"""

import asyncio
import sys
from pathlib import Path
from code_memory import code_memory
from models import Base, engine

async def seed_grace_codebase():
    """Parse grace_2 codebase and populate code memory"""
    
    print("=" * 60)
    print("GRACE CODE MEMORY SEEDING")
    print("=" * 60)
    print()
    
    # Create tables if they don't exist
    print("📊 Creating code memory tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables ready\n")
    
    # Define paths to parse
    grace_root = Path(__file__).parent.parent.parent
    
    paths_to_parse = [
        {
            'path': grace_root / 'grace_rebuild' / 'backend',
            'project': 'grace_backend',
            'description': 'Grace backend services'
        },
        {
            'path': grace_root / 'grace_rebuild' / 'cli',
            'project': 'grace_cli',
            'description': 'Grace CLI interface'
        },
        {
            'path': grace_root / 'grace_2',
            'project': 'grace_core',
            'description': 'Grace core system'
        }
    ]
    
    total_patterns = 0
    
    for item in paths_to_parse:
        path = item['path']
        project = item['project']
        
        if not path.exists():
            print(f"⚠ Skipping {project}: Path not found - {path}")
            continue
        
        print(f"📂 Parsing {project}...")
        print(f"   Path: {path}")
        
        try:
            result = await code_memory.parse_codebase(
                root_path=str(path),
                project_name=project,
                language_filter=['python']  # Focus on Python first
            )
            
            print(f"✓ Extracted patterns from {project}:")
            for pattern_type, count in result['patterns_extracted'].items():
                if count > 0:
                    print(f"   - {pattern_type}: {count}")
            
            total_patterns += result['total']
            print()
            
        except Exception as e:
            print(f"✗ Error parsing {project}: {e}\n")
    
    print("=" * 60)
    print(f"✓ COMPLETE - Total patterns stored: {total_patterns}")
    print("=" * 60)
    print()
    print("Grace's code memory is now populated!")
    print("You can now use:")
    print("  - grace code understand <file>")
    print("  - grace code suggest --intent 'add feature'")
    print("  - grace code generate --spec 'create API endpoint'")
    print()

if __name__ == "__main__":
    print("\n🧠 Grace Code Memory Seeder\n")
    
    try:
        asyncio.run(seed_grace_codebase())
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
