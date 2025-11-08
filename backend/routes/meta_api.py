from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from typing import List
from ..auth import get_current_user
from ..meta_loop import MetaAnalysis, MetaMetaEvaluation, MetaLoopConfig
from ..meta_loop_approval import approval_queue, RecommendationQueue
from ..meta_loop_engine import AppliedRecommendation
from ..models import async_session
from ..schemas import MetaAnalysisResponse, MetaMetaEvaluationResponse, MetaRecommendationResponse, SuccessResponse
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/meta", tags=["meta_loops"])

@router.post("/test/create-samples")
async def create_sample_data():
    """Create sample recommendations for UI testing"""
    from ..meta_loop import MetaAnalysis
    
    async with async_session() as session:
        analysis = MetaAnalysis(
            analysis_type="performance_threshold",
            subject="reflection_loop",
            findings="Sample test data for UI",
            recommendation="Test recommendation",
            confidence=0.85,
            applied=False
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        
        rec1_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="interval_adjustment",
            target="reflection_loop.check_interval",
            current_value=300,
            proposed_value=120,
            recommendation_text="Reduce reflection interval from 300s to 120s",
            confidence=0.85,
            risk_level="low",
            payload={
                "component": "Reflection Loop",
                "predicted_impact": 35.5,
                "reasoning": "Current 5-minute interval causes delayed insights. Reducing to 2 minutes will improve real-time pattern detection."
            }
        )
        
        rec2_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="threshold_change",
            target="task_executor.priority_threshold",
            current_value=0.7,
            proposed_value=0.6,
            recommendation_text="Lower priority threshold to process more tasks",
            confidence=0.65,
            risk_level="medium",
            payload={
                "component": "Task Executor",
                "predicted_impact": 22.3,
                "reasoning": "Current threshold of 0.7 is filtering out potentially valuable tasks."
            }
        )
        
        rec3_id = await approval_queue.submit_for_approval(
            meta_analysis_id=analysis.id,
            recommendation_type="timeout_adjustment",
            target="api_client.request_timeout",
            current_value=30,
            proposed_value=15,
            recommendation_text="Reduce API timeout to fail faster",
            confidence=0.55,
            risk_level="high",
            payload={
                "component": "API Client",
                "predicted_impact": 12.5,
                "reasoning": "30-second timeout is too long, but reducing may cause false timeouts."
            }
        )
        
        return {
            "success": True,
            "created": [rec1_id, rec2_id, rec3_id],
            "message": "Sample recommendations created"
        }

@router.get("/analyses", response_model=List[MetaAnalysisResponse])
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

@router.get("/evaluations", response_model=List[MetaMetaEvaluationResponse])
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

@router.get("/recommendations/pending", response_model=List[MetaRecommendationResponse])
async def get_pending_recommendations():
    """Get all pending recommendations awaiting approval"""
    return await approval_queue.get_pending_recommendations()

@router.post("/recommendations/{rec_id}/approve", response_model=SuccessResponse)
async def approve_recommendation(
    rec_id: int, 
    user = Depends(get_current_user),
    reason: str = "Approved for deployment"
):
    """Approve and apply a recommendation"""
    result = await approval_queue.approve_recommendation(rec_id, user["username"], reason)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to approve"))
    return result

@router.post("/recommendations/{rec_id}/reject", response_model=SuccessResponse)
async def reject_recommendation(
    rec_id: int,
    user = Depends(get_current_user),
    reason: str = "Rejected by admin"
):
    """Reject a recommendation"""
    result = await approval_queue.reject_recommendation(rec_id, user["username"], reason)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to reject"))
    return result

@router.get("/recommendations/applied", response_model=List[MetaRecommendationResponse])
async def get_applied_recommendations(limit: int = 20):
    """Show history of applied recommendations with effectiveness metrics"""
    return await approval_queue.get_applied_recommendations(limit)

@router.post("/recommendations/{applied_id}/rollback", response_model=SuccessResponse)
async def rollback_recommendation(
    applied_id: int,
    user = Depends(get_current_user),
    reason: str = "Manual rollback requested"
):
    """Rollback an applied recommendation"""
    from ..meta_loop_engine import recommendation_applicator
    result = await recommendation_applicator.rollback_change(applied_id, reason)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to rollback"))
    return result

@router.post("/recommendations/{applied_id}/measure")
async def measure_effectiveness(applied_id: int):
    """Measure effectiveness of applied recommendation"""
    from ..meta_loop_engine import recommendation_applicator
    return await recommendation_applicator.measure_after_metrics(applied_id)

@router.get("/recommendations/stats")
async def get_recommendation_stats():
    """Get statistics about recommendations"""
    async with async_session() as session:
        pending_result = await session.execute(
            select(func.count()).select_from(RecommendationQueue).where(
                RecommendationQueue.status == "pending"
            )
        )
        pending_count = pending_result.scalar()
        
        approved_result = await session.execute(
            select(func.count()).select_from(RecommendationQueue).where(
                RecommendationQueue.status == "approved"
            )
        )
        approved_count = approved_result.scalar()
        
        rejected_result = await session.execute(
            select(func.count()).select_from(RecommendationQueue).where(
                RecommendationQueue.status == "rejected"
            )
        )
        rejected_count = rejected_result.scalar()
        
        applied_result = await session.execute(
            select(func.count()).select_from(AppliedRecommendation)
        )
        applied_count = applied_result.scalar()
        
        rollback_result = await session.execute(
            select(func.count()).select_from(AppliedRecommendation).where(
                AppliedRecommendation.rolled_back == True
            )
        )
        rollback_count = rollback_result.scalar()
        
        avg_effectiveness = await session.execute(
            select(func.avg(AppliedRecommendation.effectiveness_score)).where(
                AppliedRecommendation.effectiveness_score != None
            )
        )
        avg_eff = avg_effectiveness.scalar() or 0
        
        return {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count,
            "applied": applied_count,
            "rolled_back": rollback_count,
            "average_effectiveness": round(avg_eff, 2)
        }

@router.get("/performance")
async def get_performance_metrics():
    """Get meta-loop performance analytics"""
    async with async_session() as session:
        total_applied = await session.execute(
            select(func.count()).select_from(AppliedRecommendation)
        )
        total_count = total_applied.scalar() or 0
        
        total_recs = await session.execute(
            select(func.count()).select_from(RecommendationQueue)
        )
        total_rec_count = total_recs.scalar() or 0
        
        avg_effectiveness = await session.execute(
            select(func.avg(AppliedRecommendation.effectiveness_score))
            .where(AppliedRecommendation.effectiveness_score != None)
        )
        avg_eff = avg_effectiveness.scalar() or 0
        
        recent_applied = await session.execute(
            select(AppliedRecommendation)
            .where(AppliedRecommendation.applied_at >= datetime.now() - timedelta(days=7))
            .order_by(AppliedRecommendation.applied_at)
        )
        recent = recent_applied.scalars().all()
        
        effectiveness_data = [
            {
                "timestamp": r.applied_at.isoformat(),
                "score": r.effectiveness_score or 50
            }
            for r in recent
        ]
        
        component_trends = {}
        for r in recent:
            comp = r.component or "unknown"
            if comp not in component_trends:
                component_trends[comp] = []
            component_trends[comp].append({
                "timestamp": r.applied_at.isoformat(),
                "value": r.new_value or 0
            })
        
        acceptance_rate = (total_count / total_rec_count * 100) if total_rec_count > 0 else 0
        
        return {
            "effectiveness_over_time": effectiveness_data,
            "acceptance_rate": acceptance_rate,
            "avg_improvement": avg_eff,
            "component_trends": component_trends
        }
