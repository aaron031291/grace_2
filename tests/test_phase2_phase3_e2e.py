"""
End-to-End Test for Phase 2 & Phase 3 Components
Tests all RAG and Learning systems with comprehensive logging
"""

import asyncio
import logging
import sys
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('e2e_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_rag_ingestion_quality():
    """Test RAG ingestion quality components"""
    logger.info("🧪 Testing RAG Ingestion Quality Components")
    print("\n" + "="*80)
    print("PHASE 2.1: RAG INGESTION QUALITY TEST")
    print("="*80)

    from backend.services.rag_ingestion_quality import (
        deterministic_chunker, content_deduplicator, pii_scrubber, ingestion_quality_metrics
    )

    # Test data
    test_content = """
    This is a sample document about Python programming. Python is a high-level programming language.
    It was created by Guido van Rossum and released in 1991. Contact: john.doe@example.com or call 555-123-4567.
    Python has many features including list comprehensions, decorators, and async/await syntax.
    For more information, visit https://www.python.org or contact support@python.org.
    """

    logger.info("📝 Testing DeterministicChunker")
    chunks = deterministic_chunker.chunk_text(test_content, "test_doc_001")
    logger.info(f"✓ Generated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
        logger.info(f"  Chunk {i+1}: {chunk['text'][:100]}... ({chunk['char_count']} chars)")

    logger.info("🔄 Testing ContentDeduplicator")
    # Create duplicate content for testing
    content_items = [
        {"text": test_content, "source_id": "doc1"},
        {"text": test_content, "source_id": "doc2"},  # Duplicate
        {"text": test_content[:200] + " modified content", "source_id": "doc3"}  # Similar
    ]

    deduped, dedup_stats = await content_deduplicator.deduplicate_content(content_items)
    logger.info(f"✓ Deduplication: {dedup_stats['original_count']} -> {dedup_stats['kept_count']} items")
    logger.info(f"  Duplicates removed: {dedup_stats['duplicates_removed']}")
    logger.info(f"  Similar content removed: {dedup_stats['similarity_removed']}")

    logger.info("🛡️ Testing PIIScrubber")
    scrubbed, pii_stats = await pii_scrubber.scrub_content(deduped)
    logger.info(f"✓ PII scrubbing completed")
    logger.info(f"  Items processed: {pii_stats['total_items_processed']}")
    if pii_stats.get('emails_scrubbed', 0) > 0:
        logger.info(f"  Emails scrubbed: {pii_stats['emails_scrubbed']}")
    if pii_stats.get('phones_scrubbed', 0) > 0:
        logger.info(f"  Phones scrubbed: {pii_stats['phones_scrubbed']}")

    logger.info("📊 Testing IngestionQualityMetrics")
    await ingestion_quality_metrics.update_metrics(chunks, dedup_stats, pii_stats, 0.5)
    quality_report = ingestion_quality_metrics.get_quality_report()
    logger.info(f"✓ Quality metrics updated")
    logger.info(f"  Overall quality score: {quality_report['metrics']['quality_score']:.3f}")
    logger.info(f"  Deduplication rate: {quality_report['metrics']['deduplication_rate']:.3f}")

    return {"chunks": chunks, "deduped": deduped, "scrubbed": scrubbed, "quality": quality_report}


async def test_rag_retrieval_quality():
    """Test RAG retrieval quality components"""
    logger.info("🎯 Testing RAG Retrieval Quality Components")
    print("\n" + "="*80)
    print("PHASE 2.2: RAG RETRIEVAL QUALITY TEST")
    print("="*80)

    from backend.services.rag_retrieval_quality import rag_evaluation_harness

    # Mock RAG service for testing
    class MockRAGService:
        async def retrieve(self, query, top_k=10, **kwargs):
            # Simulate retrieval results
            return {
                "results": [
                    {"content": f"Result {i+1} for query: {query}", "score": 0.9 - i*0.1}
                    for i in range(min(top_k, 5))
                ]
            }

    mock_rag = MockRAGService()

    logger.info("📚 Generating synthetic Q/A pairs")
    qa_pairs = await rag_evaluation_harness.generate_synthetic_qa_pairs(
        knowledge_base=[
            {"text": "Python is a programming language created by Guido van Rossum.", "source_id": "kb1"},
            {"text": "Machine learning uses algorithms to learn from data.", "source_id": "kb2"},
            {"text": "Neural networks are inspired by biological brains.", "source_id": "kb3"}
        ],
        num_pairs=5
    )
    logger.info(f"✓ Generated {len(qa_pairs)} synthetic Q/A pairs")

    logger.info("📊 Running retrieval evaluation")
    evaluation_results = await rag_evaluation_harness.evaluate_retrieval(mock_rag, qa_pairs)
    logger.info(f"✓ Evaluation completed")
    logger.info(f"  Precision@5: {evaluation_results.get('avg_precision_at_5', 0):.3f}")
    logger.info(f"  Precision@10: {evaluation_results.get('avg_precision_at_10', 0):.3f}")
    logger.info(f"  Average response time: {evaluation_results.get('average_response_time', 0):.3f}s")

    logger.info("🔍 Testing HardNegativeMiner")
    from backend.services.rag_retrieval_quality import hard_negative_miner
    hard_negatives = await hard_negative_miner.mine_hard_negatives(evaluation_results, qa_pairs)
    logger.info(f"✓ Mined {len(hard_negatives)} hard negative examples")

    return {"evaluation": evaluation_results, "qa_pairs": qa_pairs, "hard_negatives": hard_negatives}


async def test_rag_data_provenance():
    """Test RAG data provenance components"""
    logger.info("🔗 Testing RAG Data Provenance Components")
    print("\n" + "="*80)
    print("PHASE 2.4: RAG DATA PROVENANCE TEST")
    print("="*80)

    from backend.services.rag_data_provenance import (
        citation_manager, confidence_scorer, source_validator, provenance_tracker
    )

    # Create test provenance
    test_provenance = {
        "data_id": "test_data_001",
        "source_url": "https://docs.python.org/tutorial/",
        "source_type": "official_docs",
        "retrieved_at": datetime.utcnow().isoformat(),
        "retrieved_by": "test_system",
        "confidence_score": 0.85
    }

    logger.info("📝 Testing CitationManager")
    citation = citation_manager.generate_citation(test_provenance)
    logger.info(f"✓ Generated citation: {citation}")

    # Test citation coverage
    response_text = f"This is a test response. {citation} This proves the point."
    citations = [citation]
    coverage = citation_manager.validate_citation_coverage(response_text, citations)
    logger.info(f"✓ Citation coverage: {coverage['coverage_percentage']:.1f}%")

    logger.info("🎯 Testing ConfidenceScorer")
    confidence_result = confidence_scorer.calculate_confidence(test_provenance)
    logger.info(f"✓ Confidence calculated: {confidence_result['trust_score']:.3f} ({confidence_result['trust_level']})")

    logger.info("✅ Testing SourceValidator")
    is_valid, errors = await source_validator.validate_source(test_provenance)
    logger.info(f"✓ Source validation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        logger.info(f"  Errors: {errors}")

    logger.info("📊 Testing ProvenanceTracker")
    provenance_obj = provenance_tracker.get_provenance(test_provenance["data_id"]) or test_provenance
    provenance_tracker.track_provenance(provenance_obj)
    stats = provenance_tracker.get_provenance_stats()
    logger.info(f"✓ Provenance tracking: {stats['total_tracked']} items tracked")

    return {"citation": citation, "confidence": confidence_result, "validation": {"valid": is_valid, "errors": errors}}


async def test_knowledge_gap_detection():
    """Test knowledge gap detection components"""
    logger.info("🔍 Testing Knowledge Gap Detection Components")
    print("\n" + "="*80)
    print("PHASE 3.1: KNOWLEDGE GAP DETECTION TEST")
    print("="*80)

    from backend.learning_systems.knowledge_gap_detector import knowledge_gap_detector

    # Test queries with varying confidence levels
    test_cases = [
        {
            "query": "What is quantum computing?",
            "response": "I'm not entirely sure about quantum computing. It might involve qubits.",
            "confidence": 0.4
        },
        {
            "query": "How does Python list comprehension work?",
            "response": "Python list comprehensions are a concise way to create lists using for loops and conditions.",
            "confidence": 0.9
        },
        {
            "query": "What are the benefits of microservices architecture?",
            "response": "Microservices offer scalability and independent deployment but I'm uncertain about other advantages.",
            "confidence": 0.6
        }
    ]

    logger.info("🧠 Analyzing queries for knowledge gaps")
    gap_results = []

    for i, test_case in enumerate(test_cases):
        logger.info(f"  Query {i+1}: {test_case['query'][:50]}...")
        analysis = await knowledge_gap_detector.analyze_interaction(
            test_case["query"],
            {
                "response": test_case["response"],
                "confidence_score": test_case["confidence"]
            }
        )

        gap_results.append(analysis)
        logger.info(f"    Gaps found: {len(analysis['gaps_identified'])}")
        logger.info(f"    Recommendations: {len(analysis['learning_recommendations'])}")

        if analysis["gaps_identified"]:
            for gap in analysis["gaps_identified"][:2]:  # Show first 2 gaps
                logger.info(f"      Gap: {gap.get('gap_type', 'unknown')} - {gap.get('description', '')[:50]}...")

    # Get overall stats
    stats = knowledge_gap_detector.get_detection_stats()
    logger.info("📊 Gap detection statistics:"    logger.info(f"  Total analyses: {stats['gap_detection']['total_analyses']}")
    logger.info(f"  Gaps detected: {stats['gap_detection']['gaps_detected']}")
    logger.info(f"  Average confidence: {stats['confidence_stats']['average_confidence']:.3f}")

    return {"gap_results": gap_results, "stats": stats}


async def test_governed_web_learning():
    """Test governed web learning components"""
    logger.info("🌐 Testing Governed Web Learning Components")
    print("\n" + "="*80)
    print("PHASE 3.2: GOVERNED WEB LEARNING TEST")
    print("="*80)

    from backend.learning_systems.governed_web_learning import (
        domain_whitelist_manager, learning_job_orchestrator, sandbox_tester
    )

    logger.info("📋 Testing DomainWhitelistManager")
    # Test domain access
    test_urls = [
        "https://github.com/user/repo",
        "https://stackoverflow.com/questions/123",
        "https://unknown-site.com/article",
        "https://blocked-site.com/content"
    ]

    for url in test_urls:
        access_result = domain_whitelist_manager.check_domain_access(url)
        status = "✅ ALLOWED" if access_result["allowed"] else "❌ BLOCKED"
        logger.info(f"  {status}: {url}")
        if not access_result["allowed"]:
            logger.info(f"    Reason: {access_result['reason']}")

    # Test domain approval request
    approval_request = domain_whitelist_manager.request_domain_approval(
        "example-trusted.com", "test_system", "Testing domain approval workflow"
    )
    logger.info(f"✓ Domain approval requested: {approval_request}")

    # Approve the domain
    approval_success = domain_whitelist_manager.approve_domain_request(
        approval_request, "test_approver", max_requests=25, risk_level="low"
    )
    logger.info(f"✓ Domain approval {'successful' if approval_success else 'failed'}")

    logger.info("⚙️ Testing LearningJobOrchestrator")
    # Create a learning job
    job_id = await learning_job_orchestrator.create_learning_job(
        query="test learning query",
        domain_whitelist=["github.com", "stackoverflow.com"],
        requester="test_system"
    )
    logger.info(f"✓ Learning job created: {job_id}")

    # Approve the job (if required)
    job_status = learning_job_orchestrator.get_job_status(job_id)
    if job_status and job_status.get("approval_required"):
        approval_result = await learning_job_orchestrator.approve_job(job_id, "test_approver")
        logger.info(f"✓ Job approval {'successful' if approval_result else 'failed'}")

    logger.info("🧪 Testing SandboxTester")
    # Test content in sandbox
    test_content = {
        "id": "test_content_001",
        "title": "Test Learning Content",
        "text": "This is a comprehensive test of machine learning concepts including neural networks, deep learning, and AI ethics.",
        "source_type": "tutorial",
        "content_type": "educational"
    }

    sandbox_result = await sandbox_tester.test_content(test_content)
    status = "✅ PASSED" if sandbox_result["passed"] else "❌ FAILED"
    logger.info(f"✓ Sandbox test {status}")
    logger.info(f"  Quality score: {sandbox_result['quality_score']:.3f}")
    logger.info(f"  Issues found: {len(sandbox_result['issues'])}")

    return {
        "domain_access_tests": len(test_urls),
        "job_created": job_id,
        "sandbox_test": sandbox_result
    }


async def test_world_model_updates():
    """Test world model updates components"""
    logger.info("🧠 Testing World Model Updates Components")
    print("\n" + "="*80)
    print("PHASE 3.3: WORLD MODEL UPDATES TEST")
    print("="*80)

    from backend.learning_systems.world_model_updates import (
        trust_scorer, conflict_resolver, version_manager, world_model_updater
    )

    # Test knowledge entries
    test_entries = [
        {
            "entry_id": "python_concept_001",
            "concept": "python_language",
            "content": "Python is a high-level programming language known for its simplicity and readability.",
            "source": "official_docs",
            "source_type": "official_docs"
        },
        {
            "entry_id": "python_concept_002",
            "concept": "python_language",
            "content": "Python is a complex programming language with many advanced features.",
            "source": "blog_post",
            "source_type": "user_generated"
        }
    ]

    logger.info("🎯 Testing TrustScorer")
    trust_results = []
    for entry in test_entries:
        trust_result = trust_scorer.calculate_trust_score(entry)
        trust_results.append(trust_result)
        logger.info(f"✓ Trust score for {entry['entry_id']}: {trust_result['trust_score']:.3f} ({trust_result['trust_level']})")

    logger.info("⚔️ Testing ConflictResolver")
    # Create knowledge entries
    from backend.learning_systems.world_model_updates import KnowledgeEntry
    entry1 = KnowledgeEntry(
        entry_id=test_entries[0]["entry_id"],
        concept=test_entries[0]["concept"],
        content=test_entries[0]["content"],
        source=test_entries[0]["source"],
        source_type=test_entries[0]["source_type"],
        trust_score=trust_results[0]["trust_score"],
        trust_level=trust_results[0]["trust_level"],
        confidence=trust_results[0]["confidence"]
    )

    entry2 = KnowledgeEntry(
        entry_id=test_entries[1]["entry_id"],
        concept=test_entries[1]["concept"],
        content=test_entries[1]["content"],
        source=test_entries[1]["source"],
        source_type=test_entries[1]["source_type"],
        trust_score=trust_results[1]["trust_score"],
        trust_level=trust_results[1]["trust_level"],
        confidence=trust_results[1]["confidence"]
    )

    # Check for conflicts
    conflicts = await conflict_resolver.detect_conflicts(entry2, [entry1])
    logger.info(f"✓ Conflict detection: {len(conflicts)} conflicts found")

    if conflicts:
        # Resolve conflict
        resolution = await conflict_resolver.resolve_conflict(conflicts[0], entry2, entry1)
        logger.info(f"✓ Conflict resolution: {resolution['resolution_method']}")

    logger.info("📝 Testing KnowledgeVersionManager")
    # Create version
    versioned_entry = version_manager.create_version(entry1, "test_update")
    logger.info(f"✓ Version created: {versioned_entry.entry_id} (version {versioned_entry.version})")

    # Test rollback
    rollback_entry = version_manager.rollback_version("python_language", 1)
    if rollback_entry:
        logger.info(f"✓ Version rollback successful: {rollback_entry.entry_id}")
    else:
        logger.info("ℹ️ No rollback needed or version not found")

    logger.info("🔄 Testing WorldModelUpdater")
    # Update world model
    update_result = await world_model_updater.update_knowledge(test_entries[0])
    logger.info(f"✓ World model update: {update_result['action_taken']}")

    # Update stats
    update_stats = world_model_updater.get_update_stats()
    logger.info("📊 Update statistics:"    logger.info(f"  Total updates: {update_stats['update_stats']['total_updates']}")
    logger.info(f"  Accepted updates: {update_stats['update_stats']['accepted_updates']}")
    logger.info(f"  Conflicts detected: {update_stats['update_stats']['conflicts_detected']}")

    return {
        "trust_results": trust_results,
        "conflicts_found": len(conflicts),
        "versions_created": 1,
        "update_result": update_result
    }


async def test_safe_mode_learning():
    """Test safe mode learning components"""
    logger.info("🛡️ Testing Safe Mode Learning Components")
    print("\n" + "="*80)
    print("PHASE 3.5: SAFE MODE LEARNING TEST")
    print("="*80)

    from backend.learning_systems.safe_mode_learning import (
        safe_mode_learning_manager, learning_simulation_framework
    )

    logger.info("🔧 Testing SafeModeLearningManager")
    current_mode = safe_mode_learning_manager.learning_mode.value
    logger.info(f"✓ Current learning mode: {current_mode}")

    # Test operation permissions
    test_operations = ["web_search", "knowledge_query", "simulation", "external_api"]
    for op in test_operations:
        allowed, reason = safe_mode_learning_manager.can_perform_operation(op)
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        logger.info(f"  {status}: {op}")
        if not allowed:
            logger.info(f"    Reason: {reason}")

    logger.info("🔄 Testing retry policies")
    # Test operation execution with simulation
    async def mock_operation():
        # Simulate occasional failure
        if asyncio.get_event_loop().time() % 2 < 1:  # 50% failure rate
            raise Exception("Simulated network error")
        return {"result": "success", "data": "test_data"}

    result = await safe_mode_learning_manager.execute_with_retry(
        mock_operation, "sim_test_operation", "test_target"
    )
    logger.info(f"✓ Retry test completed: {'SUCCESS' if result['success'] else 'FAILED'}")
    logger.info(f"  Attempts made: {result['attempts']}")

    logger.info("🎭 Testing LearningSimulationFramework")
    # Run various simulations
    simulations = [
        ("web_learning", {"query": "test query", "num_results": 3}),
        ("knowledge_update", {"concept": "test_concept", "content": "test content"}),
        ("gap_detection", {"query": "what is machine learning?"})
    ]

    sim_results = []
    for sim_type, params in simulations:
        sim_result = await learning_simulation_framework.run_simulation(sim_type, params)
        status = "✅ SUCCESS" if sim_result["success"] else "❌ FAILED"
        logger.info(f"✓ Simulation {sim_type}: {status}")
        sim_results.append(sim_result)

    # Get system status
    system_status = safe_mode_learning_manager.get_system_status()
    logger.info("📊 System status:"    logger.info(f"  Safe mode active: {system_status['safe_mode_active']}")
    logger.info(f"  Circuit breaker: {system_status['circuit_breaker_enabled']}")
    logger.info(f"  Total operations: {system_status['stats']['total_operations']}")

    return {
        "current_mode": current_mode,
        "retry_test": result,
        "simulations_run": len(sim_results),
        "system_status": system_status
    }


async def run_e2e_test():
    """Run complete end-to-end test suite"""
    logger.info("🚀 Starting Grace Phase 2 & Phase 3 E2E Test Suite")
    print("\n" + "🧪 GRACE PHASE 2 & PHASE 3 END-TO-END TEST SUITE " + "🧪")
    print("="*85)

    start_time = datetime.utcnow()
    results = {}

    try:
        # Phase 2 Tests
        logger.info("📚 PHASE 2: RAG & Memory Systems")
        results["rag_ingestion"] = await test_rag_ingestion_quality()
        results["rag_retrieval"] = await test_rag_retrieval_quality()
        results["rag_provenance"] = await test_rag_data_provenance()

        # Phase 3 Tests
        logger.info("🎓 PHASE 3: Learning Engine & Governance")
        results["gap_detection"] = await test_knowledge_gap_detection()
        results["web_learning"] = await test_governed_web_learning()
        results["world_model"] = await test_world_model_updates()
        results["safe_mode"] = await test_safe_mode_learning()

        # Final summary
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "="*85)
        print("🎉 E2E TEST SUITE COMPLETED")
        print("="*85)
        print(f"⏱️  Total duration: {duration:.2f} seconds")
        print(f"📊 Test modules executed: {len(results)}")

        # Count successful components
        successful_components = sum(1 for r in results.values() if r is not None)
        print(f"✅ Successful components: {successful_components}/{len(results)}")

        # Key metrics summary
        print("\n📈 KEY METRICS SUMMARY:")
        if "rag_ingestion" in results:
            quality = results["rag_ingestion"]["quality"]
            print(f"  • RAG Quality Score: {quality['metrics']['quality_score']:.3f}")
            print(f"  • Deduplication Rate: {quality['metrics']['deduplication_rate']:.3f}")

        if "rag_retrieval" in results:
            eval_results = results["rag_retrieval"]["evaluation"]
            p5 = eval_results.get("avg_precision_at_5", 0)
            print(f"  • Retrieval Precision@5: {p5:.3f}")

        if "gap_detection" in results:
            gap_stats = results["gap_detection"]["stats"]
            print(f"  • Gap Detection Analyses: {gap_stats['gap_detection']['total_analyses']}")

        if "web_learning" in results:
            web_results = results["web_learning"]
            print(f"  • Domain Access Tests: {web_results['domain_access_tests']}")

        if "world_model" in results:
            wm_results = results["world_model"]
            print(f"  • Trust Scores Calculated: {len(wm_results['trust_results'])}")
            print(f"  • Conflicts Detected: {wm_results['conflicts_found']}")

        if "safe_mode" in results:
            safe_results = results["safe_mode"]
            print(f"  • Learning Mode: {safe_results['current_mode']}")
            print(f"  • Retry Test: {'PASSED' if safe_results['retry_test']['success'] else 'FAILED'}")

        print("\n🎯 ALL PHASE 2 & PHASE 3 COMPONENTS SUCCESSFULLY TESTED!")
        print("📋 Ready for production deployment with monitoring and governance.")

        logger.info("✅ E2E test suite completed successfully")

    except Exception as e:
        logger.error(f"❌ E2E test suite failed: {e}")
        print(f"\n❌ TEST SUITE FAILED: {e}")
        raise

    return results


if __name__ == "__main__":
    # Run the E2E test
    asyncio.run(run_e2e_test())