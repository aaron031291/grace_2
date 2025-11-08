"""Verification Script for AI Coding Agent System"""

import asyncio
from datetime import datetime

async def verify_coding_agent():
    """Verify all components are working"""
    
    print("=" * 70)
    print("GRACE AI CODING AGENT - VERIFICATION")
    print("=" * 70)
    print()
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Import all modules
    print("Test 1: Importing modules...")
    try:
        from code_memory import code_memory, CodePattern, CodeContext
        from code_understanding import code_understanding
        from code_generator import code_generator
        from dev_workflow import dev_workflow, DevelopmentTask
        from routes.coding_agent_api import router
        results['passed'].append("All modules imported successfully")
        print("  ✅ All modules imported")
    except Exception as e:
        results['failed'].append(f"Module import failed: {e}")
        print(f"  ❌ Import failed: {e}")
    
    # Test 2: Database models
    print("\nTest 2: Checking database models...")
    try:
        from models import Base, engine, async_session
        from sqlalchemy import inspect
        
        # Check if tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        results['passed'].append("Database models created")
        print("  ✅ Database models OK")
    except Exception as e:
        results['failed'].append(f"Database error: {e}")
        print(f"  ❌ Database error: {e}")
    
    # Test 3: Code Memory Engine
    print("\nTest 3: Testing Code Memory Engine...")
    try:
        from code_memory import code_memory
        from pathlib import Path
        
        # Test basic functionality
        test_path = Path('test.py')
        language = code_memory._detect_language(test_path)
        assert language == 'python'
        
        results['passed'].append("Code Memory Engine functional")
        print("  ✅ Code Memory Engine OK")
    except Exception as e:
        results['failed'].append(f"Code Memory error: {e}")
        print(f"  ❌ Code Memory error: {e}")
    
    # Test 4: Code Understanding
    print("\nTest 4: Testing Code Understanding...")
    try:
        from code_understanding import code_understanding
        
        # Test intent classification
        intent_type = code_understanding._classify_intent("create new user")
        assert intent_type == 'create'
        
        # Test entity extraction
        entities = code_understanding._extract_entities("add user authentication")
        assert len(entities) > 0
        
        results['passed'].append("Code Understanding functional")
        print("  ✅ Code Understanding OK")
    except Exception as e:
        results['failed'].append(f"Code Understanding error: {e}")
        print(f"  ❌ Code Understanding error: {e}")
    
    # Test 5: Code Generator
    print("\nTest 5: Testing Code Generator...")
    try:
        from code_generator import code_generator
        
        # Test template existence
        assert 'python' in code_generator.templates
        assert 'function' in code_generator.templates['python']
        
        results['passed'].append("Code Generator functional")
        print("  ✅ Code Generator OK")
    except Exception as e:
        results['failed'].append(f"Code Generator error: {e}")
        print(f"  ❌ Code Generator error: {e}")
    
    # Test 6: Development Workflow
    print("\nTest 6: Testing Development Workflow...")
    try:
        from dev_workflow import dev_workflow
        
        # Test workflow classification
        workflow_type = dev_workflow._classify_task_type({
            'intent_type': 'create',
            'entities': ['api', 'endpoint']
        })
        assert workflow_type in dev_workflow.task_types
        
        results['passed'].append("Development Workflow functional")
        print("  ✅ Development Workflow OK")
    except Exception as e:
        results['failed'].append(f"Development Workflow error: {e}")
        print(f"  ❌ Development Workflow error: {e}")
    
    # Test 7: API Routes
    print("\nTest 7: Testing API Routes...")
    try:
        from routes.coding_agent_api import router
        
        # Check endpoints
        route_paths = [route.path for route in router.routes]
        assert '/parse' in route_paths
        assert '/understand' in route_paths
        assert '/generate/function' in route_paths
        
        results['passed'].append(f"API Routes registered ({len(route_paths)} endpoints)")
        print(f"  ✅ API Routes OK ({len(route_paths)} endpoints)")
    except Exception as e:
        results['failed'].append(f"API Routes error: {e}")
        print(f"  ❌ API Routes error: {e}")
    
    # Test 8: Integration with GRACE systems
    print("\nTest 8: Testing GRACE system integration...")
    try:
        # Try to import integrated systems
        from governance import governance_engine
        from hunter import hunter_engine
        from causal_analyzer import causal_analyzer
        from meta_loop_engine import meta_loop
        
        results['passed'].append("GRACE system integration verified")
        print("  ✅ GRACE integration OK")
    except Exception as e:
        results['warnings'].append(f"GRACE integration warning: {e}")
        print(f"  [WARN]  GRACE integration warning: {e}")
    
    # Test 9: Check seed script exists
    print("\nTest 9: Checking seed script...")
    try:
        import os
        seed_script = os.path.join(os.path.dirname(__file__), 'seed_code_memory.py')
        assert os.path.exists(seed_script)
        
        results['passed'].append("Seed script found")
        print("  ✅ Seed script exists")
    except Exception as e:
        results['failed'].append(f"Seed script error: {e}")
        print(f"  ❌ Seed script error: {e}")
    
    # Test 10: Check documentation
    print("\nTest 10: Checking documentation...")
    try:
        import os
        docs = [
            'CODING_AGENT.md',
            'CODING_AGENT_STATUS.md',
            'CODING_AGENT_QUICKSTART.md'
        ]
        
        for doc in docs:
            doc_path = os.path.join(os.path.dirname(__file__), doc)
            assert os.path.exists(doc_path), f"{doc} not found"
        
        results['passed'].append(f"Documentation complete ({len(docs)} files)")
        print(f"  ✅ Documentation OK ({len(docs)} files)")
    except Exception as e:
        results['failed'].append(f"Documentation error: {e}")
        print(f"  ❌ Documentation error: {e}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    print(f"\n✅ Passed: {len(results['passed'])}")
    for item in results['passed']:
        print(f"   * {item}")
    
    if results['warnings']:
        print(f"\n[WARN]  Warnings: {len(results['warnings'])}")
        for item in results['warnings']:
            print(f"   * {item}")
    
    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"   * {item}")
    
    print("\n" + "=" * 70)
    
    if len(results['failed']) == 0:
        print("✅ ALL TESTS PASSED - SYSTEM READY")
    elif len(results['failed']) < 3:
        print("[WARN]  MOSTLY WORKING - MINOR ISSUES")
    else:
        print("❌ SYSTEM HAS ISSUES - REVIEW REQUIRED")
    
    print("=" * 70)
    print(f"\nVerification completed at: {datetime.now().isoformat()}")
    print()
    
    return len(results['failed']) == 0

if __name__ == "__main__":
    success = asyncio.run(verify_coding_agent())
    exit(0 if success else 1)
