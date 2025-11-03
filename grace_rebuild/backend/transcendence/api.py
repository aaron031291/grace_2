"""Transcendence API - Unified Intelligence Interface

Single interface for ALL Grace capabilities:
- Collaborative proposals (Grace proposes, you approve)
- Agentic learning cycles (complete learning pipeline)
- Whitelist management (trusted sources)
- Memory integration (trust-scored storage)
- Business building (autonomous execution)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/transcendence", tags=["Transcendence"])

class ProposalRequest(BaseModel):
    """Grace proposes something"""
    proposal: str
    category: str
    reasoning: str
    confidence: float
    business_context: Optional[str] = None

class ApprovalRequest(BaseModel):
    """You approve/modify proposal"""
    decision_id: str
    approved: bool = True
    modifications: Optional[Dict[str, Any]] = None

class LearningCycleRequest(BaseModel):
    """Start agentic learning cycle"""
    topic: str
    domain: str
    sources: List[str]
    create_training_data: bool = True

class WhitelistRequest(BaseModel):
    """Add to whitelist"""
    name: str
    source_type: str  # topic, domain, authority
    category: str
    trust_level: str = "high"
    use_for_training: bool = True

@router.post("/propose")
async def grace_proposes(request: ProposalRequest):
    """
    Grace proposes an action/idea/change to you
    
    Returns:
        Decision ID awaiting your approval
    """
    
    from .unified_intelligence import transcendence
    
    try:
        result = await transcendence.collaborative_propose(
            proposal=request.proposal,
            category=request.category,
            reasoning=request.reasoning,
            confidence=request.confidence,
            business_context=request.business_context
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve/{decision_id}")
async def approve_proposal(decision_id: str, request: ApprovalRequest):
    """
    You approve Grace's proposal
    
    Returns:
        Execution result
    """
    
    from .unified_intelligence import transcendence
    
    try:
        if request.approved:
            result = await transcendence.approve_proposal(
                decision_id=decision_id,
                modifications=request.modifications
            )
            return result
        else:
            # Rejection handling
            return {"status": "rejected", "decision_id": decision_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learn")
async def start_learning_cycle(request: LearningCycleRequest):
    """
    Start complete agentic learning cycle
    
    Full pipeline:
    Ingest → Understand → Interpret → Intent → Apply → Create → Manage → Adapt
    
    Each stage verified and stored in memory
    
    Returns:
        Complete learning cycle results
    """
    
    from .unified_intelligence import transcendence
    
    try:
        result = await transcendence.agentic_learning_cycle(
            topic=request.topic,
            domain=request.domain,
            sources=request.sources,
            create_training_data=request.create_training_data
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whitelist")
async def add_to_whitelist(request: WhitelistRequest):
    """
    Add topic/domain/authority to whitelist
    
    Whitelisted sources:
    - Automatically trusted
    - Used for training data
    - Aligned with your standards
    
    Returns:
        Whitelist entry
    """
    
    from ..models import async_session
    from .unified_intelligence import TrustedSource
    
    async with async_session() as session:
        source = TrustedSource(
            source_type=request.source_type,
            name=request.name,
            category=request.category,
            trust_level=request.trust_level,
            whitelist_status="approved",
            use_for_training=request.use_for_training,
            auto_ingest=True,
            added_by="aaron"
        )
        
        session.add(source)
        await session.commit()
        await session.refresh(source)
        
        return {
            "id": source.id,
            "name": source.name,
            "category": source.category,
            "status": "whitelisted",
            "use_for_training": source.use_for_training
        }

@router.get("/whitelist")
async def get_whitelist(
    category: Optional[str] = None,
    source_type: Optional[str] = None
):
    """Get whitelisted sources"""
    
    from ..models import async_session
    from .unified_intelligence import TrustedSource
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(TrustedSource).where(
            TrustedSource.whitelist_status == "approved"
        )
        
        if category:
            query = query.where(TrustedSource.category == category)
        if source_type:
            query = query.where(TrustedSource.source_type == source_type)
        
        result = await session.execute(query)
        sources = result.scalars().all()
        
        return {
            "sources": [
                {
                    "name": s.name,
                    "category": s.category,
                    "type": s.source_type,
                    "trust_level": s.trust_level,
                    "use_for_training": s.use_for_training
                }
                for s in sources
            ],
            "count": len(sources)
        }

@router.get("/cycles")
async def get_learning_cycles(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get learning cycles"""
    
    from ..models import async_session
    from .unified_intelligence import AgenticLearningCycle
    from sqlalchemy import select
    
    async with async_session() as session:
        query = select(AgenticLearningCycle).order_by(
            AgenticLearningCycle.created_at.desc()
        )
        
        if domain:
            query = query.where(AgenticLearningCycle.domain == domain)
        if status:
            query = query.where(AgenticLearningCycle.status == status)
        
        query = query.limit(limit)
        
        result = await session.execute(query)
        cycles = result.scalars().all()
        
        return {
            "cycles": [
                {
                    "cycle_id": c.cycle_id,
                    "topic": c.topic,
                    "domain": c.domain,
                    "status": c.status,
                    "success": c.success,
                    "revenue_impact": c.revenue_impact,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in cycles
            ]
        }

@router.get("/proposals/pending")
async def get_pending_proposals():
    """Get proposals awaiting your approval"""
    
    from ..models import async_session
    from .unified_intelligence import CollaborativeDecision
    from sqlalchemy import select
    
    async with async_session() as session:
        result = await session.execute(
            select(CollaborativeDecision).where(
                CollaborativeDecision.status == "pending"
            ).order_by(CollaborativeDecision.created_at.desc())
        )
        proposals = result.scalars().all()
        
        return {
            "proposals": [
                {
                    "decision_id": p.decision_id,
                    "proposal": p.grace_proposal,
                    "reasoning": p.grace_reasoning,
                    "confidence": p.grace_confidence,
                    "category": p.proposal_type,
                    "business_context": p.business_context,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in proposals
            ],
            "count": len(proposals)
        }
