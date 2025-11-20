#!/usr/bin/env python3
"""
Test Ingestion Quality Pipeline
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_ingestion_quality():
    """Test complete ingestion quality pipeline"""
    print("🔍 TESTING INGESTION QUALITY PIPELINE")
    print("=" * 50)
    
    from backend.ingestion.ingestion_quality_pipeline import ingestion_quality_pipeline
    
    # Test content with various quality issues
    test_content = """
    This is a test document for the ingestion quality pipeline.
    It contains some PII like john.doe@example.com and phone 555-123-4567.
    
    This paragraph has good content that should be chunked properly.
    It has multiple sentences and provides valuable information.
    
    This is duplicate content that should be detected.
    This is duplicate content that should be detected.
    
    API key: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
    Credit card: 4532-1234-5678-9012
    """
    
    # Process through pipeline
    result = await ingestion_quality_pipeline.process_content(
        content=test_content,
        source_id="test_document_001",
        metadata={"type": "test", "created_at": "2024-01-01"}
    )
    
    print(f"✅ Pipeline Status: {result['status']}")
    print(f"📊 Chunks: {result['original_chunks']} -> {result['final_chunks']}")
    print(f"🔄 Duplicates Removed: {result['deduplication_stats']['duplicates_removed']}")
    print(f"🛡️ PII Redactions: {result['pii_stats']['total_redactions']}")
    print(f"⏱️ Processing Time: {result['processing_time']:.3f}s")
    
    # Get pipeline stats
    stats = ingestion_quality_pipeline.get_pipeline_stats()
    print(f"📈 Success Rate: {stats['success_rate']:.2%}")
    
    return result['status'] == 'success'

if __name__ == "__main__":
    success = asyncio.run(test_ingestion_quality())
    print("\n🎉 INGESTION QUALITY TESTS PASSED!" if success else "\n❌ TESTS FAILED")
    sys.exit(0 if success else 1)