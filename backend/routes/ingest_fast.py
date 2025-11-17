"""
Fast Ingestion Routes - Grace System Access (No Auth/Governance Delays)
For autonomous operation with snapshot protection
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import hashlib
import json

from ..models import async_session
from ..knowledge_models import KnowledgeArtifact, KnowledgeRevision
from ..auto_snapshot import auto_snapshot_system
from ..schemas_extended import IngestTextResponse

router = APIRouter(prefix="/api/ingest/fast", tags=["fast_ingestion"])

class FastIngestText(BaseModel):
    content: str
    title: str
    domain: str = "general"
    artifact_type: str = "text"
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

@router.post("/text", response_model=IngestTextResponse)
async def fast_ingest_text(req: FastIngestText):
    """
    Fast text ingestion for Grace system use
    - No auth required
    - Minimal governance (basic safety only)
    - Auto-snapshot before action
    - Auto-rollback on failure
    """
    
    # Create snapshot before ingestion
    snapshot_id = await auto_snapshot_system.snapshot_before_action(
        action_type="fast_ingest_text",
        context={"title": req.title, "domain": req.domain}
    )
    
    try:
        # Compute hash for deduplication
        content_hash = hashlib.sha256(req.content.encode()).hexdigest()
        
        async with async_session() as session:
            # Check for duplicate
            from sqlalchemy import select
            existing = await session.execute(
                select(KnowledgeArtifact).where(KnowledgeArtifact.content_hash == content_hash)
            )
            existing_artifact = existing.scalar_one_or_none()
            
            if existing_artifact:
                return IngestTextResponse(
                    status="duplicate",
                    artifact_id=existing_artifact.id
                )
            
            # Create artifact
            path = f"{req.domain}/{req.artifact_type}/{req.title.replace(' ', '_').lower()}"
            
            artifact = KnowledgeArtifact(
                path=path,
                title=req.title,
                artifact_type=req.artifact_type,
                content=req.content,
                content_hash=content_hash,
                artifact_metadata=json.dumps(req.metadata or {}),
                source="grace_system",
                ingested_by="grace_system",
                domain=req.domain,
                tags=json.dumps(req.tags or []),
                size_bytes=len(req.content)
            )
            session.add(artifact)
            await session.commit()
            await session.refresh(artifact)
            
            # Create revision
            revision = KnowledgeRevision(
                artifact_id=artifact.id,
                revision_number=1,
                edited_by="grace_system",
                change_summary="fast_ingest"
            )
            session.add(revision)
            await session.commit()
            
            return IngestTextResponse(
                status="ingested",
                artifact_id=artifact.id
            )
    
    except Exception as e:
        # Auto-rollback on error
        if snapshot_id:
            await auto_snapshot_system.immediate_rollback(snapshot_id, "fast_ingest_text")
        raise

@router.get("/status")
async def get_fast_ingest_status():
    """Get fast ingestion system status"""
    return {
        "status": "active",
        "auth_required": False,
        "governance": "minimal",
        "snapshot_protection": True,
        "auto_rollback": True
    }
