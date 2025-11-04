from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..auth import get_current_user
from ..security import require_roles
from ..ingestion_service import ingestion_service
from ..trusted_sources import trust_manager
from ..verification import verification_engine
from ..verification_middleware import verify_action

router = APIRouter(
    prefix="/api/ingest",
    tags=["ingestion"],
    dependencies=[Depends(require_roles("admin", "analyst"))],
)

class IngestText(BaseModel):
    content: str
    title: str
    artifact_type: str = "text"
    domain: str = "general"
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None

class IngestURL(BaseModel):
    url: str
    domain: str = "external"

@router.post("/text")
@verify_action("data_ingest", lambda data: data.get("title", "unknown"))
async def ingest_text(
    req: IngestText,
    current_user: str = Depends(get_current_user)
):
    """Ingest text content"""
    try:
        artifact_id = await ingestion_service.ingest(
            content=req.content,
            artifact_type=req.artifact_type,
            title=req.title,
            actor=current_user,
            domain=req.domain,
            tags=req.tags,
            metadata=req.metadata
        )
        return {"status": "ingested", "artifact_id": artifact_id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url")
async def ingest_url(
    req: IngestURL,
    current_user: str = Depends(get_current_user)
):
    """Ingest content from URL (trust-scored)"""
    
    auto_approve, trust_score = await trust_manager.should_auto_approve(req.url)
    
    if trust_score < 40:
        raise HTTPException(status_code=403, detail=f"Low trust source (score: {trust_score}). Blocked.")
    
    if not auto_approve:
        from ..governance_models import ApprovalRequest
        from ..models import async_session
        
        async with async_session() as session:
            approval = ApprovalRequest(
                event_id=0,
                requested_by=current_user,
                reason=f"URL ingestion requires approval: {req.url} (trust: {trust_score})",
                status="pending"
            )
            session.add(approval)
            await session.commit()
            await session.refresh(approval)
        
        return {
            "status": "pending_approval",
            "approval_id": approval.id,
            "trust_score": trust_score,
            "message": f"Medium trust source ({trust_score}). Approval required."
        }
    
    try:
        artifact_id = await ingestion_service.ingest_url(req.url, current_user)
        
        import uuid
        action_id = str(uuid.uuid4())
        await verification_engine.log_verified_action(
            action_id=action_id,
            actor=current_user,
            action_type="knowledge_ingest_url",
            resource=req.url,
            input_data={"url": req.url, "trust_score": trust_score},
            output_data={"artifact_id": artifact_id},
            criteria_met=True
        )
        
        return {
            "status": "ingested",
            "artifact_id": artifact_id,
            "url": req.url,
            "trust_score": trust_score,
            "verified": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
@verify_action("file_ingest", lambda data: data.get("filename", "unknown"))
async def ingest_file(
    file: UploadFile = File(...),
    domain: str = Form("uploads"),
    current_user: str = Depends(get_current_user)
):
    """Ingest uploaded file (supports txt, md, pdf, images, audio, video)"""
    try:
        file_content = await file.read()
        
        artifact_id = await ingestion_service.ingest_file(
            file_content=file_content,
            filename=file.filename,
            actor=current_user
        )
        
        return {
            "status": "ingested",
            "artifact_id": artifact_id,
            "filename": file.filename,
            "size": len(file_content)
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/artifacts")
async def list_artifacts(
    domain: str = None,
    artifact_type: str = None,
    limit: int = 50,
    current_user: str = Depends(get_current_user)
):
    """List ingested knowledge artifacts"""
    from sqlalchemy import select
    from ..knowledge_models import KnowledgeArtifact
    from ..models import async_session
    
    async with async_session() as session:
        query = select(KnowledgeArtifact).order_by(KnowledgeArtifact.created_at.desc())
        
        if domain:
            query = query.where(KnowledgeArtifact.domain == domain)
        if artifact_type:
            query = query.where(KnowledgeArtifact.artifact_type == artifact_type)
        
        query = query.limit(limit)
        result = await session.execute(query)
        
        return [
            {
                "id": a.id,
                "path": a.path,
                "title": a.title,
                "type": a.artifact_type,
                "domain": a.domain,
                "source": a.source,
                "size_bytes": a.size_bytes,
                "created_at": a.created_at
            }
            for a in result.scalars().all()
        ]
