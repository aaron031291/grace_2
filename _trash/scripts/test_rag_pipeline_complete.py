#!/usr/bin/env python3
"""
Complete RAG Pipeline & MCP Integration Test
Verifies:
- RAG Service functionality
- Vector store operations
- MCP connector
- World model integration
- E2E workflows
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class RAGPipelineTestSuite:
    """Comprehensive RAG and MCP test suite"""
    
    def __init__(self):
        self.results = {
            "start_time": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "component_status": {}
        }
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 80)
        print("RAG PIPELINE & MCP INTEGRATION TEST")
        print("=" * 80)
        print(f"Start Time: {self.results['start_time']}\n")
        
        test_suites = [
            ("1. RAG Service", self.test_rag_service),
            ("2. Vector Store", self.test_vector_store),
            ("3. Embedding Service", self.test_embedding_service),
            ("4. World Model", self.test_world_model),
            ("5. MCP Integration", self.test_mcp_integration),
            ("6. E2E RAG Workflow", self.test_e2e_rag_workflow)
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n{'='*80}")
            print(f"{suite_name}")
            print('='*80)
            
            try:
                await test_func()
                self.results["component_status"][suite_name] = "PASSED"
                self.results["tests_passed"] += 1
                print(f"[PASS] {suite_name} - PASSED")
            except Exception as e:
                self.results["component_status"][suite_name] = f"FAILED: {str(e)}"
                self.results["tests_failed"] += 1
                print(f"[FAIL] {suite_name} - FAILED: {e}")
                print(traceback.format_exc())
        
        self.results["end_time"] = datetime.now().isoformat()
        self.print_final_report()
    
    async def test_rag_service(self):
        """Test RAG service functionality"""
        print("\n-> Testing RAG Service initialization...")
        from backend.services.rag_service import rag_service
        
        await rag_service.initialize()
        assert rag_service.initialized, "RAG service not initialized"
        print("  [OK] RAG service initialized")
        
        print("\n-> Testing RAG retrieval...")
        result = await rag_service.retrieve(
            query="What is Grace?",
            top_k=5,
            similarity_threshold=0.5
        )
        print(f"  [OK] Retrieved {result['total_results']} results in {result['execution_time_ms']:.1f}ms")
        
        print("\n-> Testing RAG with citations...")
        citation_result = await rag_service.retrieve_with_citations(
            query="How does Grace work?",
            max_tokens=1000,
            top_k=5
        )
        print(f"  [OK] Generated context with {len(citation_result['citations'])} citations")
        print(f"  [OK] Total tokens: {citation_result['total_tokens']}")
        
        print("\n-> Testing hybrid search...")
        hybrid_result = await rag_service.hybrid_search(
            query="autonomous system",
            keyword_filter="Grace",
            top_k=5
        )
        print(f"  [OK] Hybrid search returned {len(hybrid_result['results'])} results")
    
    async def test_vector_store(self):
        """Test vector store operations"""
        print("\n-> Testing vector store initialization...")
        from backend.services.vector_store import vector_store
        
        await vector_store.initialize()
        print("  [OK] Vector store initialized")
        
        print("\n-> Testing vector store stats...")
        stats = await vector_store.get_stats()
        print(f"  [OK] Vector store stats: {stats}")
        
        print("\n-> Testing add text to vector store...")
        test_text = "This is a test document for RAG pipeline verification"
        result = await vector_store.add_text(
            content=test_text,
            source="test_rag_pipeline",
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        print(f"  [OK] Added text to vector store: {result}")
    
    async def test_embedding_service(self):
        """Test embedding service"""
        print("\n-> Testing embedding service...")
        from backend.services.embedding_service import embedding_service
        
        await embedding_service.initialize()
        print("  [OK] Embedding service initialized")
        
        print("\n-> Testing text embedding...")
        result = await embedding_service.embed_text(
            text="Test embedding for Grace AI system",
            source_type="test",
            source_id="test_embed_001"
        )
        print(f"  [OK] Generated embedding: {result['embedding_id']}")
        print(f"  [OK] Vector dimension: {result['dimensions']}")
        print(f"  [OK] Provider: {embedding_service.provider}")
        print(f"  [OK] Model: {embedding_service.default_model}")
        
        print("\n-> Testing batch embedding...")
        items = [
            {"text": "First test document"},
            {"text": "Second test document"},
            {"text": "Third test document"}
        ]
        batch_result = await embedding_service.embed_batch(
            items=items,
            source_type="test_batch"
        )
        print(f"  [OK] Batch embedded {batch_result['embeddings_created']} items")
    
    async def test_world_model(self):
        """Test Grace's world model"""
        print("\n-> Testing world model initialization...")
        from backend.world_model import grace_world_model
        
        await grace_world_model.initialize()
        assert grace_world_model._initialized, "World model not initialized"
        print("  [OK] World model initialized")
        
        print("\n-> Testing add knowledge...")
        knowledge_id = await grace_world_model.add_knowledge(
            category='test',
            content='This is test knowledge for RAG pipeline verification',
            source='test_suite',
            confidence=0.95,
            tags=['test', 'rag', 'pipeline']
        )
        print(f"  [OK] Added knowledge: {knowledge_id}")
        
        print("\n-> Testing world model query...")
        results = await grace_world_model.query(
            query="What is Grace?",
            top_k=5
        )
        print(f"  [OK] Query returned {len(results)} knowledge items")
        
        print("\n-> Testing ask_self...")
        answer = await grace_world_model.ask_self("What are your capabilities?")
        print(f"  [OK] Self-question answered")
        print(f"    Answer preview: {answer['answer'][:100]}...")
        print(f"    Confidence: {answer['confidence']:.2f}")
        
        print("\n-> Getting world model stats...")
        stats = grace_world_model.get_stats()
        print(f"  [OK] Total knowledge: {stats['total_knowledge']}")
        print(f"  [OK] By category: {stats['by_category']}")
    
    async def test_mcp_integration(self):
        """Test MCP (Model Context Protocol) integration"""
        print("\n-> Testing MCP initialization...")
        from backend.world_model import mcp_integration
        
        await mcp_integration.initialize()
        assert mcp_integration._initialized, "MCP not initialized"
        print("  [OK] MCP integration initialized")
        
        print("\n-> Testing MCP manifest...")
        manifest = mcp_integration.get_mcp_manifest()
        print(f"  [OK] MCP Server ID: {manifest['server']['id']}")
        print(f"  [OK] MCP Version: {manifest['server']['version']}")
        print(f"  [OK] Resources: {len(manifest['resources'])}")
        print(f"  [OK] Tools: {len(manifest['tools'])}")
        
        # List available resources
        print("\n-> Available MCP Resources:")
        for resource in manifest['resources']:
            print(f"    * {resource['uri']} - {resource['name']}")
        
        # List available tools
        print("\n-> Available MCP Tools:")
        for tool in manifest['tools']:
            print(f"    * {tool['name']} - {tool['description']}")
        
        print("\n-> Testing MCP resource request (grace://self)...")
        resource_result = await mcp_integration.handle_resource_request('grace://self')
        print(f"  [OK] Retrieved {len(resource_result['content'])} self-knowledge items")
        
        print("\n-> Testing MCP resource request (grace://system)...")
        system_result = await mcp_integration.handle_resource_request('grace://system')
        print(f"  [OK] Retrieved {len(system_result['content'])} system knowledge items")
        
        print("\n-> Testing MCP tool call (query_world_model)...")
        tool_result = await mcp_integration.handle_tool_call(
            'query_world_model',
            {'query': 'autonomous AI', 'top_k': 3}
        )
        print(f"  [OK] Tool returned {tool_result['total_results']} results")
        
        print("\n-> Testing MCP tool call (ask_grace)...")
        ask_result = await mcp_integration.handle_tool_call(
            'ask_grace',
            {'question': 'What is your purpose?'}
        )
        print(f"  [OK] Grace answered: {ask_result['answer'][:80]}...")
    
    async def test_e2e_rag_workflow(self):
        """Test end-to-end RAG workflow"""
        print("\n-> Testing E2E RAG workflow...")
        
        # 1. Add knowledge to world model
        print("\n  Step 1: Add knowledge to world model")
        from backend.world_model import grace_world_model
        
        knowledge_id = await grace_world_model.add_knowledge(
            category='domain',
            content='Grace has a complete RAG pipeline with semantic search, vector store, and MCP integration',
            source='e2e_test',
            confidence=1.0,
            tags=['rag', 'pipeline', 'mcp']
        )
        print(f"    [OK] Added knowledge: {knowledge_id}")
        
        # 2. Query via RAG service
        print("\n  Step 2: Query via RAG service")
        from backend.services.rag_service import rag_service
        
        rag_result = await rag_service.retrieve(
            query="Tell me about Grace's RAG pipeline",
            top_k=5
        )
        print(f"    [OK] RAG retrieved {rag_result['total_results']} results")
        
        # 3. Query via world model
        print("\n  Step 3: Query via world model")
        wm_results = await grace_world_model.query(
            query="RAG pipeline features",
            top_k=3
        )
        print(f"    [OK] World model returned {len(wm_results)} items")
        
        # 4. Query via MCP
        print("\n  Step 4: Query via MCP integration")
        from backend.world_model import mcp_integration
        
        mcp_result = await mcp_integration.handle_tool_call(
            'query_world_model',
            {'query': 'RAG pipeline', 'top_k': 3}
        )
        print(f"    [OK] MCP tool returned {mcp_result['total_results']} results")
        
        # 5. Get context with citations
        print("\n  Step 5: Get context with citations")
        citation_result = await rag_service.retrieve_with_citations(
            query="Explain Grace's RAG capabilities",
            max_tokens=500
        )
        print(f"    [OK] Generated context: {len(citation_result['context'])} chars")
        print(f"    [OK] Citations: {len(citation_result['citations'])}")
        print(f"    [OK] Sources: {len(citation_result['sources'])}")
        
        print("\n  [OK] Complete E2E RAG workflow verified!")
    
    def print_final_report(self):
        """Print final test report"""
        print("\n" + "=" * 80)
        print("FINAL TEST REPORT")
        print("=" * 80)
        
        total = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total * 100) if total > 0 else 0
        
        print(f"\nTest Summary:")
        print(f"  Total Suites: {total}")
        print(f"  Passed: {self.results['tests_passed']} [PASS]")
        print(f"  Failed: {self.results['tests_failed']} [FAIL]")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        print(f"\nComponent Status:")
        for component, status in self.results["component_status"].items():
            icon = "[PASS]" if status == "PASSED" else "[FAIL]"
            print(f"  {icon} {component}: {status}")
        
        print(f"\nTiming:")
        print(f"  Start: {self.results['start_time']}")
        print(f"  End: {self.results['end_time']}")
        
        print("\n" + "=" * 80)
        if self.results["tests_failed"] == 0:
            print("SUCCESS: ALL TESTS PASSED! RAG pipeline is fully operational.")
        else:
            print("WARNING: Some tests failed. Review errors above.")
        print("=" * 80)


async def main():
    """Run complete RAG pipeline test"""
    suite = RAGPipelineTestSuite()
    
    try:
        await suite.run_all_tests()
    except KeyboardInterrupt:
        print("\nWARNING: Test suite interrupted by user")
    except Exception as e:
        print(f"\nERROR: Fatal error: {e}")
        print(traceback.format_exc())
    
    return suite.results


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GRACE RAG PIPELINE & MCP INTEGRATION TEST")
    print("=" * 80)
    print("\nTesting RAG service, vector store, embeddings, world model, and MCP...\n")
    
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results["tests_failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)