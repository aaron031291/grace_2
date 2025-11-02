from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from ..auth import get_current_user
from ..meta_loop import MetaAnalysis, MetaMetaEvaluation, MetaLoopConfig
from ..meta_loop_approval import approval_queue, RecommendationQueue
from ..meta_loop_engine import AppliedRecommendation
from ..models import async_session
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/meta", tags=["meta_loops"])

@router.get("/analyses")
async def list_meta_analyses(limit: int = 20):
    """View Level 1 meta-loop analyses"""
    async with async_session() as session:
        result = await session.execute(
            select(MetaAnalysis)
            .order_by(MetaAnalysis.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": a.id,
                "type": a.analysis_type,
                "subject": a.subject,
                "findings": a.findings,
                "recommendation": a.recommendation,
                "confidence": a.confidence,
                "applied": a.applied,
                "created_at": a.created_at
            }
            for a in result.scalars().all()
        ]

@router.get("/evaluations")
async def list_meta_meta_evals(limit: int = 20):
    """View Level 2 meta-meta evaluations"""
    async with async_session() as session:
        result = await session.execute(
            select(MetaMetaEvaluation)
            .order_by(MetaMetaEvaluation.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": e.id,
                "metric": e.metric_name,
                "before": e.before_value,
                "after": e.after_value,
                "improvement": e.improvement,
                "conclusion": e.conclusion,
                "created_at": e.created_at
            }
            for e in result.scalars().all()
        ]

@router.get("/config")
async def get_meta_config():
    """View meta-loop configuration"""
    async with async_session() as session:
        result = await session.execute(select(MetaLoopConfig))
        return [
            {
                "key": c.config_key,
                "value": c.config_value,
                "type": c.config_type,
                "approved": c.approved,
                "last_updated_by": c.last_updated_by
            }
            for c in result.scalars().all()
        ]
