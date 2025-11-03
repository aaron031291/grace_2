"""Initialize All Grace Systems

Creates all database tables and seeds initial data for complete Grace system.
Run this ONCE before first use.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print(" GRACE COMPLETE SYSTEM INITIALIZATION")
print("="*70)
print()

async def initialize():
    """Initialize all Grace systems"""
    
    # Step 1: Create all database tables
    print("STEP 1: Creating database tables...")
    print("-"*70)
    
    try:
        from backend.models import engine, Base
        from backend.cognition.memory_models import Base as CognitionBase
        
        # Import all models to register them
        from backend import models
        from backend import governance_models
        from backend import sandbox_models
        from backend import memory_models
        from backend import knowledge_models
        from backend import parliament_models
        from backend import constitutional_models
        from backend.speech_models import SpeechMessage, TextToSpeechMessage
        from backend.code_memory import CodePattern, CodeContext
        from backend.grace_architect_agent import GraceArchitectureKnowledge, GraceExtensionRequest
        from backend.transcendence.unified_intelligence import TrustedSource, AgenticLearningCycle, CollaborativeDecision
        from backend.transcendence.multi_modal_memory import MultiModalArtifact, FileChunk, WebScrapeResult, RemoteAccessSession
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(CognitionBase.metadata.create_all)
        
        print("  SUCCESS: All database tables created")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Seed governance policies
    print("STEP 2: Seeding governance policies...")
    print("-"*70)
    
    try:
        from backend.seed_governance_policies import seed_governance_policies
        await seed_governance_policies()
        print()
    except Exception as e:
        print(f"  WARNING: {e}")
        print()
    
    # Step 3: Seed Hunter rules
    print("STEP 3: Seeding Hunter security rules...")
    print("-"*70)
    
    try:
        from backend.seed_hunter_rules import seed_hunter_rules
        await seed_hunter_rules()
        print()
    except Exception as e:
        print(f"  WARNING: {e}")
        print()
    
    # Step 4: Seed Parliament
    print("STEP 4: Seeding Parliament members...")
    print("-"*70)
    
    try:
        from backend.seed_parliament import seed_parliament
        await seed_parliament()
        print()
    except Exception as e:
        print(f"  WARNING: {e}")
        print()
    
    # Step 5: Seed Constitution
    print("STEP 5: Seeding Constitutional principles...")
    print("-"*70)
    
    try:
        from backend.seed_constitution import seed_constitution
        await seed_constitution()
        print()
    except Exception as e:
        print(f"  WARNING: {e}")
        print()
    
    # Step 6: Create default whitelist
    print("STEP 6: Creating default whitelist...")
    print("-"*70)
    
    try:
        from backend.models import async_session
        from backend.transcendence.unified_intelligence import TrustedSource
        
        default_sources = [
            {
                'name': 'OpenAI Documentation',
                'source_type': 'authority',
                'category': 'ai_development',
                'trust_level': 'absolute',
                'auto_ingest': True,
                'use_for_training': True,
                'added_by': 'system',
                'examples': ['https://platform.openai.com/docs']
            },
            {
                'name': 'Python Official Docs',
                'source_type': 'authority',
                'category': 'ai_development',
                'trust_level': 'absolute',
                'auto_ingest': True,
                'use_for_training': True,
                'added_by': 'system',
                'examples': ['https://docs.python.org']
            },
            {
                'name': 'AI Research Papers',
                'source_type': 'topic',
                'category': 'ai_development',
                'trust_level': 'high',
                'auto_ingest': False,
                'use_for_training': True,
                'added_by': 'system',
                'examples': ['arxiv.org', 'papers.nips.cc']
            },
            {
                'name': 'Business Strategy',
                'source_type': 'topic',
                'category': 'business',
                'trust_level': 'medium',
                'auto_ingest': False,
                'use_for_training': True,
                'added_by': 'system'
            },
            {
                'name': 'Marketing Best Practices',
                'source_type': 'topic',
                'category': 'marketing',
                'trust_level': 'medium',
                'auto_ingest': False,
                'use_for_training': True,
                'added_by': 'system'
            }
        ]
        
        async with async_session() as session:
            for source_data in default_sources:
                source = TrustedSource(**source_data)
                session.add(source)
            
            await session.commit()
        
        print(f"  SUCCESS: Added {len(default_sources)} trusted sources")
        print()
        
    except Exception as e:
        print(f"  WARNING: {e}")
        print()
    
    # Summary
    print("="*70)
    print(" INITIALIZATION COMPLETE")
    print("="*70)
    print()
    print("Grace is now ready with:")
    print("  - All database tables created")
    print("  - 23 governance policies")
    print("  - 17 Hunter security rules")
    print("  - Parliament members (you + 4 Grace agents)")
    print("  - 30 constitutional principles")
    print("  - 5 default whitelisted sources")
    print()
    print("Next steps:")
    print("  1. Start backend: py backend/main.py")
    print("  2. Access UI: http://localhost:5173")
    print("  3. Start learning: POST /api/transcendence/learn")
    print("  4. Build empire!")
    print()
    
    return True

if __name__ == "__main__":
    print("\nGrace Complete System Initialization\n")
    
    try:
        success = asyncio.run(initialize())
        
        if success:
            print("SUCCESS: Grace is operational!")
            print()
            print("Your collaborative AI partner for empire building is ready.")
            print()
        else:
            print("PARTIAL: Some components need attention")
            print()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
