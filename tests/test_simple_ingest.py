"""Simple test to verify ingestion works"""
import asyncio
import sys
import os
sys.path.append(os.getcwd())

async def test_simple_ingest():
    from backend.ingestion_services.ingestion_service import ingestion_service
    
    print("Testing simple ingestion...")
    try:
        artifact_id = await ingestion_service.ingest(
            content="Test content",
            artifact_type="text",
            title="Simple Test",
            actor="tester",
            source="test",
            domain="test"
        )
        print(f"✅ SUCCESS: Ingested artifact ID: {artifact_id}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_ingest())
