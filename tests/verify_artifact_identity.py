import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

import importlib
import backend.ingestion_services.ingestion_service
print(f"DEBUG: Loaded ingestion_service from {backend.ingestion_services.ingestion_service.__file__}")
importlib.reload(backend.ingestion_services.ingestion_service)
from backend.ingestion_services.ingestion_service import ingestion_service
from backend.models.base_models import async_session
from backend.models.knowledge_models import KnowledgeArtifact
from sqlalchemy import select

async def verify_artifact_identity():
    print("=== Verifying Artifact Identity (Root Key) ===")
    
    # 1. Ingest New Artifact
    print("\n[Step 1] Ingesting new artifact...")
    path = "test/identity/doc1.txt"
    content_v1 = "Version 1 Content"
    
    artifact_id_v1 = await ingestion_service.ingest(
        content=content_v1,
        artifact_type="text",
        title="Identity Test Doc",
        actor="tester",
        source="test_script",
        domain="test",
        metadata={"origin": "verification"}
    )
    
    # Check Root Key
    async with async_session() as session:
        result = await session.execute(select(KnowledgeArtifact).where(KnowledgeArtifact.id == artifact_id_v1))
        artifact_v1 = result.scalar_one()
        meta_v1 = json.loads(artifact_v1.artifact_metadata)
        root_key_v1 = meta_v1.get("root_artifact_id")
        version_id_v1 = meta_v1.get("version_id")
        
        print(f"  Artifact ID: {artifact_id_v1}")
        print(f"  Root Key: {root_key_v1}")
        print(f"  Version ID: {version_id_v1}")
        
        if not root_key_v1:
            print("❌ FAILED: No Root Key generated")
            return
        
    # 2. Update Artifact (New Version)
    print("\n[Step 2] Updating artifact (New Version)...")
    content_v2 = "Version 2 Content (Updated)"
    
    artifact_id_v2 = await ingestion_service.ingest(
        content=content_v2,
        artifact_type="text",
        title="Identity Test Doc",
        actor="tester",
        source="test_script",
        domain="test",
        metadata={"origin": "verification"}
    )
    
    # Check Root Key Persisted
    async with async_session() as session:
        result = await session.execute(select(KnowledgeArtifact).where(KnowledgeArtifact.id == artifact_id_v2))
        artifact_v2 = result.scalar_one()
        meta_v2 = json.loads(artifact_v2.artifact_metadata)
        root_key_v2 = meta_v2.get("root_artifact_id")
        version_id_v2 = meta_v2.get("version_id")
        
        print(f"  Artifact ID: {artifact_id_v2}")
        print(f"  Root Key: {root_key_v2}")
        print(f"  Version ID: {version_id_v2}")
        
        if root_key_v1 != root_key_v2:
            print(f"❌ FAILED: Root Key changed! ({root_key_v1} -> {root_key_v2})")
            return
        
        if version_id_v1 == version_id_v2:
            print("❌ FAILED: Version ID did not change")
            return
            
        print("✅ SUCCESS: Root Key persisted, Version ID changed")

    # 3. Ingest Different Artifact
    print("\n[Step 3] Ingesting DIFFERENT artifact...")
    path_diff = "test/identity/doc2.txt"
    content_diff = "Different Document"
    
    artifact_id_diff = await ingestion_service.ingest_with_retry(
        content=content_diff,
        artifact_type="text",
        title="Different Doc",
        actor="tester",
        source="test_script",
        domain="test",
        metadata={"origin": "verification"}
    ) # Note: ingest_with_retry calls ingest internally, testing that path too
    
    async with async_session() as session:
        # We need to find it by path since ingest_with_retry returns ID
        # But wait, ingest returns ID too.
        result = await session.execute(select(KnowledgeArtifact).where(KnowledgeArtifact.id == artifact_id_diff))
        artifact_diff = result.scalar_one()
        meta_diff = json.loads(artifact_diff.artifact_metadata)
        root_key_diff = meta_diff.get("root_artifact_id")
        
        print(f"  Root Key (Diff): {root_key_diff}")
        
        if root_key_diff == root_key_v1:
             print("❌ FAILED: Different artifact has same Root Key")
             return
             
        print("✅ SUCCESS: Different artifact has unique Root Key")

if __name__ == "__main__":
    try:
        asyncio.run(verify_artifact_identity())
    except Exception:
        import traceback
        traceback.print_exc()
