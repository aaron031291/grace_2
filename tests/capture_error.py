"""Capture full error to file"""
import asyncio
import sys
import os
sys.path.append(os.getcwd())

async def test_with_error_capture():
    try:
        from backend.ingestion_services.ingestion_service import ingestion_service
        
        artifact_id = await ingestion_service.ingest(
            content="Test content",
            artifact_type="text",
            title="Error Capture Test",
            actor="tester",
            source="test",
            domain="test"
        )
        print(f"SUCCESS: {artifact_id}")
    except Exception as e:
        import traceback
        with open("error_full.txt", "w") as f:
            f.write(f"Exception: {str(e)}\n\n")
            f.write(traceback.format_exc())
        print(f"Error written to error_full.txt")
        raise

if __name__ == "__main__":
    asyncio.run(test_with_error_capture())
