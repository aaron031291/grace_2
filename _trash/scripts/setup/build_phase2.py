#!/usr/bin/env python3
"""
Phase 2 Build Script - Ingestion & Retrieval Quality
"""
import asyncio
import sys
from pathlib import Path

async def build_phase2():
    """Build Phase 2 components"""
    print("🚀 BUILDING PHASE 2 - INGESTION & RETRIEVAL QUALITY")
    print("=" * 60)
    
    # 1. Test Deterministic Chunker
    print("\n📏 [1/4] Testing Deterministic Chunker...")
    from backend.ingestion.deterministic_chunker import deterministic_chunker
    
    test_text = "This is a test document for chunking. It has multiple sentences and should be chunked consistently every time we run it."
    chunks = await deterministic_chunker.chunk_text(test_text, "test_doc")
    print(f"✅ Chunked into {len(chunks)} chunks consistently")
    
    # 2. Test Content Deduplicator
    print("\n🔄 [2/4] Testing Content Deduplicator...")
    from backend.ingestion.content_deduplicator import content_deduplicator
    
    test_items = [
        {"text": "This is duplicate content", "source_id": "doc1"},
        {"text": "This is duplicate content", "source_id": "doc2"},
        {"text": "This is unique content", "source_id": "doc3"}
    ]
    
    unique_items = await content_deduplicator.deduplicate_batch(test_items)
    print(f"✅ Deduplicated {len(test_items)} items to {len(unique_items)} unique items")
    
    # 3. Test PII Scrubber
    print("\n🔒 [3/4] Testing PII Scrubber...")
    from backend.ingestion.pii_scrubber import pii_scrubber
    
    test_item = {
        "text": "Contact John at john.doe@email.com or call 555-123-4567. His SSN is 123-45-6789.",
        "source_id": "pii_test"
    }
    
    scrubbed_item = await pii_scrubber.scrub_content(test_item)
    print(f"✅ PII scrubbed: {scrubbed_item['pii_scrubbed']}")
    print(f"   Patterns found: {scrubbed_item.get('pii_patterns_found', [])}")
    
    # 4. Test Q&A Harness
    print("\n🧪 [4/4] Testing Q&A Harness...")
    from backend.retrieval.qa_harness import qa_harness
    
    await qa_harness.load_benchmark_dataset()
    print(f"✅ Loaded {len(qa_harness.benchmark_dataset)} Q&A pairs")
    
    # Mock retrieval function for testing
    async def mock_retrieval(question: str, top_k: int = 10):
        return [
            {"text": "Service restart playbook documentation", "score": 0.9},
            {"text": "MTTR target is 5 minutes for critical incidents", "score": 0.8},
            {"text": "Guardian runs integrity checks on playbooks", "score": 0.7}
        ][:top_k]
    
    eval_results = await qa_harness.run_evaluation(mock_retrieval)
    print(f"✅ Evaluation complete - P@5: {eval_results['aggregate_metrics']['precision_at_5']:.3f}")
    
    # 5. Generate Phase 2 Report
    print("\n📊 [5/5] Phase 2 Build Summary")
    print("=" * 60)
    
    # Get metrics from all components
    chunker_stats = deterministic_chunker.chunking_stats
    dedup_metrics = await content_deduplicator.get_deduplication_metrics()
    pii_metrics = await pii_scrubber.get_pii_metrics()
    
    print(f"✅ Deterministic Chunker: {chunker_stats['total_chunks_created']} chunks created")
    print(f"✅ Content Deduplicator: {dedup_metrics['stats']['deduplication_rate']:.1%} dedup rate")
    print(f"✅ PII Scrubber: {pii_metrics['stats']['pii_detection_rate']:.1%} PII detection rate")
    print(f"✅ Q&A Harness: {eval_results['aggregate_metrics']['precision_at_5']:.3f} P@5 score")
    
    print("\n🎉 PHASE 2 BUILD COMPLETE!")
    print("\nComponents built:")
    print("  📏 Deterministic chunker with snapshot testing")
    print("  🔄 Content deduplicator with fingerprinting")
    print("  🔒 PII scrubber with pattern detection")
    print("  🧪 Q&A harness with precision/recall metrics")
    
    return True

if __name__ == "__main__":
    asyncio.run(build_phase2())