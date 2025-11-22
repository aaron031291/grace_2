"""Capture verification output to file"""
import asyncio
import json
import sys
import os

# Redirect output to file
sys.stdout = open("verify_log.txt", "w", encoding="utf-8")
sys.stderr = sys.stdout

sys.path.append(os.getcwd())

from backend.ingestion_services.ingestion_service import ingestion_service
from backend.models.base_models import async_session
from backend.models.knowledge_models import KnowledgeArtifact
from sqlalchemy import select

async def verify():
    print("=== Artifact Identity Verification ===\n")
    
    # Test 1: New Artifact
    print("[Test 1] Creating new artifact...")
    id1 = await ingestion_service.ingest(
        content="Version 1",
        artifact_type="text",
        title="Test Doc",
        actor="tester",
        source="test",
        domain="test"
    )
    
    async with async_session() as session:
        result = await session.execute(select(KnowledgeArtifact).where(KnowledgeArtifact.id == id1))
        art1 = result.scalar_one()
        meta1 = json.loads(art1.artifact_metadata)
        root1 = meta1.get("root_artifact_id")
        ver1 = meta1.get("version_id")
        print(f"  Root Key: {root1[:16]}...")
        print(f"  Version ID: {ver1[:16]}...")
    
    # Test 2: Update Same Artifact
    print("\n[Test 2] Updating same artifact...")
    id2 = await ingestion_service.ingest(
        content="Version 2",
        artifact_type="text",
        title="Test Doc",
        actor="tester",
        source="test",
        domain="test"
    )
    
    async with async_session() as session:
        result = await session.execute(select(KnowledgeArtifact).where(KnowledgeArtifact.id == id2))
        art2 = result.scalar_one()
        meta2 = json.loads(art2.artifact_metadata)
        root2 = meta2.get("root_artifact_id")
        ver2 = meta2.get("version_id")
        print(f"  Root Key: {root2[:16]}...")
        print(f"  Version ID: {ver2[:16]}...")
    
    # Verify
    if root1 == root2:
        print("\nSUCCESS: Root Key persisted across versions")
    else:
        print(f"\nFAILED: Root Key changed ({root1} != {root2})")
        return
    
    if ver1 != ver2:
        print("SUCCESS: Version ID changed")
    else:
        print("FAILED: Version ID did not change")
        return
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    try:
        asyncio.run(verify())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.stdout.close()

print("Check verify_log.txt for results")
