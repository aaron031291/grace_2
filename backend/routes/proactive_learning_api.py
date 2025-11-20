"""
Proactive Learning API
Monitor and control Grace's always-on autonomous learning
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(
    prefix="/api/proactive-learning",
    tags=["Proactive Learning"]
)


@router.get("/status")
async def get_proactive_learning_status():
    """Get current status of proactive learning agent"""
    from backend.autonomy.proactive_learning_agent import proactive_learning_agent
    
    return proactive_learning_agent.get_status()


@router.get("/live-feed")
async def get_live_learning_feed(limit: int = 20):
    """
    Get live feed of what Grace is learning right now
    Shows recent knowledge ingestion from the internet
    """
    from backend.models.knowledge_models import KnowledgeArtifact
    from backend.models.base_models import async_session
    from sqlalchemy import select
    
    async with async_session() as session:
        # Get recent autonomous learning artifacts
        result = await session.execute(
            select(KnowledgeArtifact).where(
                KnowledgeArtifact.ingested_by == "proactive_learning_agent"
            ).order_by(KnowledgeArtifact.created_at.desc()).limit(limit)
        )
        
        artifacts = result.scalars().all()
        
        feed = []
        for artifact in artifacts:
            feed.append({
                "id": artifact.id,
                "title": artifact.title,
                "source_url": artifact.source,
                "domain": artifact.domain,
                "size_bytes": artifact.size_bytes,
                "learned_at": artifact.created_at.isoformat() if artifact.created_at else None,
                "preview": artifact.content[:300] + "..." if len(artifact.content) > 300 else artifact.content
            })
        
        return {
            "feed": feed,
            "total_items": len(feed),
            "last_updated": datetime.utcnow().isoformat()
        }


@router.post("/pause")
async def pause_learning():
    """Temporarily pause proactive learning"""
    from backend.autonomy.proactive_learning_agent import proactive_learning_agent
    
    await proactive_learning_agent.stop()
    
    return {
        "paused": True,
        "message": "Proactive learning paused. Call /resume to restart."
    }


@router.post("/resume")
async def resume_learning():
    """Resume proactive learning"""
    from backend.autonomy.proactive_learning_agent import proactive_learning_agent
    
    await proactive_learning_agent.start()
    
    return {
        "resumed": True,
        "message": "Proactive learning resumed."
    }


@router.get("/stats")
async def get_learning_stats():
    """Get detailed learning statistics"""
    from backend.autonomy.proactive_learning_agent import proactive_learning_agent
    from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
    
    agent_status = proactive_learning_agent.get_status()
    curriculum_status = learning_whitelist_manager.get_learning_status()
    
    return {
        "agent": agent_status,
        "curriculum": curriculum_status,
        "performance": {
            "pages_per_session": agent_status['total_pages_learned'] / max(agent_status['learning_sessions'], 1),
            "avg_bytes_per_page": agent_status['total_bytes_ingested'] / max(agent_status['total_pages_learned'], 1),
            "error_rate": agent_status['errors_encountered'] / max(agent_status['learning_sessions'], 1)
        }
    }
