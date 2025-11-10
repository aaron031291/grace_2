from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from ..auth import get_current_user
from ..trusted_sources import TrustedSource, trust_manager
from ..models import async_session
from ..schemas_extended import (
    TrustedSourcesListResponse,
    TrustedSourceResponse,
    TrustSourceUpdateResponse,
    TrustSourceDeleteResponse,
    TrustScoreResponse
)


router = APIRouter(prefix="/api/trust", tags=["trust"])

class AddTrustedSource(BaseModel):
    domain: str
    trust_score: float
    category: str
    description: str = ""
    auto_approve_threshold: float = 70.0

class UpdateTrustedSource(BaseModel):
    trust_score: float | None = None
    category: str | None = None
    description: str | None = None
    auto_approve_threshold: float | None = None

@router.get("/sources")
async def list_trusted_sources():
    """List all trusted sources"""
    async with async_session() as session:
        result = await session.execute(select(TrustedSource))
        return [
            {
                "id": s.id,
                "domain": s.domain,
                "trust_score": s.trust_score,
                "category": s.category,
                "description": s.description,
                "auto_approve_threshold": s.auto_approve_threshold
            }
            for s in result.scalars().all()
        ]

@router.post("/sources")
async def add_trusted_source(
    req: AddTrustedSource,
    current_user: str = Depends(get_current_user)
):
    """Add new trusted source"""
    async with async_session() as session:
        source = TrustedSource(
            domain=req.domain,
            trust_score=req.trust_score,
            category=req.category,
            description=req.description,
            verified_by=current_user,
            auto_approve_threshold=req.auto_approve_threshold,
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    
    return {"id": source.id, "domain": source.domain}

@router.patch("/sources/{source_id}")
async def update_trusted_source(
    source_id: int,
    req: UpdateTrustedSource,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(select(TrustedSource).where(TrustedSource.id == source_id))
        source = result.scalar_one_or_none()
        if not source:
            raise HTTPException(status_code=404, detail="Trusted source not found")
        if req.trust_score is not None:
            source.trust_score = req.trust_score
        if req.category is not None:
            source.category = req.category
        if req.description is not None:
            source.description = req.description
        if req.auto_approve_threshold is not None:
            source.auto_approve_threshold = req.auto_approve_threshold
        await session.commit()
        await session.refresh(source)
    return {"status": "updated", "id": source.id}

@router.delete("/sources/{source_id}")
async def delete_trusted_source(
    source_id: int,
    current_user: str = Depends(get_current_user)
):
    async with async_session() as session:
        result = await session.execute(select(TrustedSource).where(TrustedSource.id == source_id))
        source = result.scalar_one_or_none()
        if not source:
            raise HTTPException(status_code=404, detail="Trusted source not found")
        await session.delete(source)
        await session.commit()
    return {"status": "deleted", "id": source_id}

@router.get("/score")
async def get_trust_score(url: str):
    """Get trust score for a URL"""
    score = await trust_manager.get_trust_score(url)
    auto_approve, _ = await trust_manager.should_auto_approve(url)
    
    return {
        "url": url,
        "trust_score": score,
        "auto_approve": auto_approve,
        "recommendation": "auto" if auto_approve else "review" if score >= 40 else "block"
    }
