from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from ..auth import get_current_user
from ..trusted_sources import TrustedSource, trust_manager
from ..models import async_session

router = APIRouter(prefix="/api/trust", tags=["trust"])

class AddTrustedSource(BaseModel):
    domain: str
    trust_score: float
    category: str
    description: str = ""

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
            verified_by=current_user
        )
        session.add(source)
        await session.commit()
        await session.refresh(source)
    
    return {"id": source.id, "domain": source.domain}

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
