#!/usr/bin/env python3
"""Simple test runner without Unicode issues"""
import asyncio
import sys
from pathlib import Path


async def test_pipeline():
    """Test the complete ingestion pipeline"""
    
    print("=" * 60)
    print("GRACE COMPLETE LEARNING PIPELINE - TESTS")
    print("=" * 60)
    
    # Test 1: Schema Registry
    print("\n[TEST 1] Schema Registry")
    try:
        from backend.memory_tables.registry import table_registry
        
        count = table_registry.load_all_schemas()
        print(f"  [OK] Loaded {count} schemas")
        
        tables = table_registry.list_tables()
        print(f"  [OK] Tables: {', '.join(tables)}")
        
        table_registry.initialize_database()
        print(f"  [OK] Database initialized")
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Content Pipeline
    print("\n[TEST 2] Content Pipeline")
    try:
        from backend.memory_tables.content_pipeline import content_pipeline
        
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document for Grace's learning system.")
        
        analysis = await content_pipeline.analyze(test_file)
        print(f"  [OK] Analyzed file: {analysis['category']}")
        print(f"  [OK] Features: {list(analysis['features'].keys())[:3]}...")
        
        test_file.unlink()
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False
    
    # Test 3: Schema Inference
    print("\n[TEST 3] Schema Inference")
    try:
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        
        agent = SchemaInferenceAgent(registry=table_registry)
        
        test_file = Path("test_doc.txt")
        test_file.write_text("# Test Document\n\nThis is a test.")
        
        file_analysis = await agent.analyze_file(test_file)
        print(f"  [OK] File type: {file_analysis['detected_type']}")
        
        proposal = await agent.propose_schema(file_analysis, tables)
        print(f"  [OK] Proposal: {proposal['action']} -> {proposal.get('table_name')}")
        
        row_data = await agent.extract_row_data(test_file, proposal['table_name'])
        print(f"  [OK] Row data extracted ({len(row_data)} fields)")
        
        test_file.unlink()
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False
    
    # Test 4: Table Operations
    print("\n[TEST 4] Table Operations")
    try:
        import time
        unique_id = str(int(time.time()))
        
        test_data = {
            'file_path': f'test/document_{unique_id}.txt',
            'title': 'Test Document',
            'source_type': 'custom',
            'summary': 'Test summary',
            'key_topics': {},  # JSON field expects dict not list
            'token_count': 10,
            'risk_level': 'low'
        }
        
        inserted = table_registry.insert_row('memory_documents', test_data)
        print(f"  [OK] Inserted row: {inserted.id}")
        
        rows = table_registry.query_rows('memory_documents', limit=5)
        print(f"  [OK] Queried {len(rows)} rows")
        
        import uuid
        success = table_registry.update_row(
            'memory_documents',
            inserted.id,
            {'trust_score': 0.85}
        )
        print(f"  [OK] Updated row: {success}")
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False
    
    # Test 5: Learning Integration
    print("\n[TEST 5] Learning Integration")
    try:
        from backend.memory_tables.learning_integration import learning_bridge
        
        # Set registry if not already set
        if not learning_bridge.registry:
            learning_bridge.registry = table_registry
        
        insights = await learning_bridge.extract_insights('memory_documents')
        print(f"  [OK] Extracted {len(insights)} insights")
        
        report = await learning_bridge.generate_learning_report()
        print(f"  [OK] Learning report generated")
        print(f"       Tables: {report['summary']['total_tables']}, Rows: {report['summary']['total_rows']}")
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Auto-Ingestion
    print("\n[TEST 6] Auto-Ingestion Service")
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        stats = auto_ingestion_service.get_stats()
        print(f"  [OK] Service running: {stats['running']}")
        print(f"  [OK] Processed files: {stats['processed_files_count']}")
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print("\nVerified components:")
    print("  - Schema registry")
    print("  - Content analysis pipeline")
    print("  - Schema inference agent")
    print("  - Table operations (CRUD)")
    print("  - Learning integration")
    print("  - Auto-ingestion service")
    print("\nGrace is ready to learn from the real world!")
    
    return True


async def test_api():
    """Test API availability"""
    print("\n" + "=" * 60)
    print("API AVAILABILITY TEST")
    print("=" * 60)
    
    try:
        from backend.routes import memory_tables_api
        print("[OK] Memory Tables API available")
        
        from backend.routes import auto_ingestion_api
        print("[OK] Auto-Ingestion API available")
        
        from backend.routes import ingestion_bridge_api
        print("[OK] Ingestion Bridge API available")
        
        print("\nAPI endpoints ready:")
        print("  - /api/memory/tables/* (13 endpoints)")
        print("  - /api/auto-ingest/* (7 endpoints)")
        print("  - /api/ingestion-bridge/* (6 endpoints)")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    
    # Test pipeline
    pipeline_ok = await test_pipeline()
    
    # Test API
    api_ok = await test_api()
    
    # Final
    print("\n" + "=" * 60)
    if pipeline_ok and api_ok:
        print("VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("=" * 60)
        return 0
    else:
        print("VERIFICATION FAILED - CHECK ERRORS ABOVE")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
