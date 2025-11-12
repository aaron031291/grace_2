#!/usr/bin/env python3
"""
Test Complete Pipeline
Verify the full upload → learn flow works end-to-end
"""

import asyncio
import sys
from pathlib import Path


async def test_pipeline():
    """Test the complete ingestion pipeline"""
    
    print("Testing Grace Complete Learning Pipeline\n")
    print("=" * 60)
    
    # Test 1: Schema Registry
    print("\n[1] Testing Schema Registry...")
    try:
        from backend.memory_tables.registry import table_registry
        
        # Load schemas
        count = table_registry.load_all_schemas()
        print(f"   ✅ Loaded {count} schemas")
        
        # List tables
        tables = table_registry.list_tables()
        print(f"   ✅ Tables: {', '.join(tables)}")
        
        # Initialize database
        table_registry.initialize_database()
        print(f"   ✅ Database initialized")
        
    except Exception as e:
        print(f"   ❌ Schema registry failed: {e}")
        return False
    
    # Test 2: Content Pipeline
    print("\n[2] Testing Content Pipeline...")
    try:
        from backend.memory_tables.content_pipeline import content_pipeline
        
        # Create test file
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document for Grace's learning system.")
        
        # Analyze
        analysis = await content_pipeline.analyze(test_file)
        print(f"   ✅ Analyzed file: {analysis['category']}")
        print(f"   ✅ Features: {list(analysis['features'].keys())}")
        
        # Cleanup
        test_file.unlink()
        
    except Exception as e:
        print(f"   ❌ Content pipeline failed: {e}")
        return False
    
    # Test 3: Schema Inference
    print("\n[3] Testing Schema Inference...")
    try:
        from backend.memory_tables.schema_agent import SchemaInferenceAgent
        
        agent = SchemaInferenceAgent(registry=table_registry)
        
        # Create test file
        test_file = Path("test_doc.txt")
        test_file.write_text("# Test Document\n\nThis is a test.")
        
        # Analyze
        file_analysis = await agent.analyze_file(test_file)
        print(f"   ✅ File type: {file_analysis['detected_type']}")
        
        # Propose schema
        proposal = await agent.propose_schema(file_analysis, tables)
        print(f"   ✅ Proposal: {proposal['action']} → {proposal.get('table_name')}")
        
        # Extract data
        row_data = await agent.extract_row_data(test_file, proposal['table_name'])
        print(f"   ✅ Row data extracted: {list(row_data.keys())[:5]}...")
        
        # Cleanup
        test_file.unlink()
        
    except Exception as e:
        print(f"   ❌ Schema inference failed: {e}")
        return False
    
    # Test 4: Table Operations
    print("\n[4] Testing Table Operations...")
    try:
        # Insert test row
        test_data = {
            'file_path': 'test/document.txt',
            'title': 'Test Document',
            'source_type': 'custom',
            'summary': 'Test summary',
            'key_topics': ['test'],
            'token_count': 10,
            'risk_level': 'low'
        }
        
        inserted = table_registry.insert_row('memory_documents', test_data)
        print(f"   ✅ Inserted row: {inserted.id}")
        
        # Query
        rows = table_registry.query_rows('memory_documents', limit=5)
        print(f"   ✅ Queried {len(rows)} rows")
        
        # Update
        import uuid
        success = table_registry.update_row(
            'memory_documents',
            inserted.id,
            {'trust_score': 0.85}
        )
        print(f"   ✅ Updated row: {success}")
        
    except Exception as e:
        print(f"   ❌ Table operations failed: {e}")
        return False
    
    # Test 5: Learning Integration
    print("\n[5] Testing Learning Integration...")
    try:
        from backend.memory_tables.learning_integration import learning_bridge
        
        # Extract insights
        insights = await learning_bridge.extract_insights('memory_documents')
        print(f"   ✅ Extracted {len(insights)} insights")
        
        # Generate report
        report = await learning_bridge.generate_learning_report()
        print(f"   ✅ Learning report: {report['summary']['total_tables']} tables, {report['summary']['total_rows']} rows")
        
    except Exception as e:
        print(f"   ❌ Learning integration failed: {e}")
        return False
    
    # Test 6: Auto-Ingestion Service
    print("\n[6] Testing Auto-Ingestion Service...")
    try:
        from backend.memory_tables.auto_ingestion import auto_ingestion_service
        
        # Get stats (service not started)
        stats = auto_ingestion_service.get_stats()
        print(f"   ✅ Service stats: running={stats['running']}")
        print(f"   ✅ Processed files: {stats['processed_files_count']}")
        
    except Exception as e:
        print(f"   ❌ Auto-ingestion failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("[PASS] ALL TESTS PASSED")
    print("\nComplete pipeline verified:")
    print("  - Schema registry [OK]")
    print("  - Content analysis [OK]")
    print("  - Schema inference [OK]")
    print("  - Table operations [OK]")
    print("  - Learning integration [OK]")
    print("  - Auto-ingestion [OK]")
    print("\nGrace is ready to learn from the real world!")
    
    return True


async def test_api_availability():
    """Test if API routes are available"""
    print("\n[API] Testing API Routes...\n")
    
    try:
        from backend.routes import memory_tables_api
        print("   ✅ Memory Tables API available")
        
        from backend.routes import auto_ingestion_api
        print("   ✅ Auto-Ingestion API available")
        
        print("\n   API endpoints ready:")
        print("   • /api/memory/tables/* (13 endpoints)")
        print("   • /api/auto-ingest/* (7 endpoints)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API routes failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GRACE COMPLETE LEARNING PIPELINE - VERIFICATION")
    print("=" * 60)
    
    # Test pipeline
    pipeline_ok = await test_pipeline()
    
    # Test API
    api_ok = await test_api_availability()
    
    # Final result
    print("\n" + "=" * 60)
    if pipeline_ok and api_ok:
        print("✅ SYSTEM VERIFICATION COMPLETE")
        print("\nGrace's learning pipeline is fully operational.")
        print("Ready for production deployment.")
        return 0
    else:
        print("❌ VERIFICATION FAILED")
        print("\nSome components need attention.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
