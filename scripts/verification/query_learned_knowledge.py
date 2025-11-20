#!/usr/bin/env python3
"""Query the knowledge that was just learned from the internet"""

import sys
import os
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(os.getcwd())))

import asyncio
from sqlalchemy import select

async def query_knowledge():
    """Query what Grace learned from the internet"""
    from backend.models.knowledge_models import KnowledgeArtifact
    from backend.models.base_models import async_session
    
    print("="*60)
    print("QUERYING LEARNED KNOWLEDGE FROM INTERNET")
    print("="*60)
    
    async with async_session() as session:
        # Get all artifacts from verification domain
        result = await session.execute(
            select(KnowledgeArtifact).where(
                KnowledgeArtifact.domain == "verification"
            ).order_by(KnowledgeArtifact.created_at.desc())
        )
        
        artifacts = result.scalars().all()
        
        print(f"\n[FOUND] {len(artifacts)} artifacts learned from the internet:")
        print()
        
        for i, artifact in enumerate(artifacts, 1):
            print(f"{i}. Artifact ID: {artifact.id}")
            print(f"   Title: {artifact.title}")
            print(f"   Source URL: {artifact.source}")
            print(f"   Type: {artifact.artifact_type}")
            print(f"   Size: {artifact.size_bytes:,} bytes")
            print(f"   Content Hash: {artifact.content_hash[:16]}...")
            print(f"   Ingested By: {artifact.ingested_by}")
            print(f"   Ingested At: {artifact.created_at}")
            print(f"   Preview: {artifact.content[:200]}...")
            print()
        
        # Show total knowledge in system
        all_result = await session.execute(select(KnowledgeArtifact))
        total = len(all_result.scalars().all())
        
        print(f"[TOTAL] Grace has {total} total knowledge artifacts in memory")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(query_knowledge())
