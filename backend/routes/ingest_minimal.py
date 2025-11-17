"""
Minimal Ingestion - Zero Dependencies
For testing and Grace autonomous operation
"""

from fastapi import APIRouter
from pydantic import BaseModel
import hashlib

router = APIRouter(prefix="/api/ingest/minimal", tags=["minimal_ingestion"])

class MinimalIngest(BaseModel):
    content: str
    title: str
    domain: str = "general"

@router.post("/text")
async def minimal_ingest_text(req: MinimalIngest):
    """
    Ultra-minimal text ingestion
    - No auth
    - No governance  
    - No hunter
    - No verification
    - Just store to database
    """
    try:
        from ..models import async_session
        from ..knowledge_models import KnowledgeArtifact
        from sqlalchemy import select
        
        content_hash = hashlib.sha256(req.content.encode()).hexdigest()
        
        async with async_session() as session:
            # Quick duplicate check
            result = await session.execute(
                select(KnowledgeArtifact).where(KnowledgeArtifact.content_hash == content_hash).limit(1)
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                return {
                    "status": "duplicate",
                    "artifact_id": existing.id,
                    "message": "Content already exists"
                }
            
            # Create artifact
            artifact = KnowledgeArtifact(
                path=f"{req.domain}/{req.title.replace(' ', '_').lower()}",
                title=req.title,
                artifact_type="text",
                content=req.content,
                content_hash=content_hash,
                artifact_metadata="{}",
                source="minimal_ingest",
                ingested_by="grace_system",
                domain=req.domain,
                tags="[]",
                size_bytes=len(req.content)
            )
            
            session.add(artifact)
            await session.commit()
            await session.refresh(artifact)
            
            return {
                "status": "success",
                "artifact_id": artifact.id,
                "message": f"Ingested '{req.title}' ({len(req.content)} bytes)"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/status")
async def minimal_ingest_status():
    """Check if minimal ingestion is working"""
    return {
        "status": "active",
        "features": {
            "auth": False,
            "governance": False,
            "hunter": False,
            "verification": False,
            "snapshot": False
        },
        "purpose": "Testing and autonomous operation"
    }
