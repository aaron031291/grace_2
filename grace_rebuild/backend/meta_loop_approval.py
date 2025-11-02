"""
Meta-Loop Approval Queue System
Manages approval workflow for meta-loop recommendations
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, select
from sqlalchemy.sql import func
from .models import Base, async_session

class RecommendationQueue(Base):
    """Queue for pending meta-loop recommendations"""
    __tablename__ = "recommendation_queue"
    id = Column(Integer, primary_key=True)
    meta_analysis_id = Column(Integer, nullable=False)
    recommendation_type = Column(String(64), nullable=False)
    target = Column(String(128), nullable=False)
    current_value = Column(Text)
    proposed_value = Column(Text)
    recommendation_text = Column(Text)
    confidence = Column(Float, default=0.5)
    risk_level = Column(String(16), default="medium")
    status = Column(String(32), default="pending")
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    reviewed_by = Column(String(64))
    approval_reason = Column(Text)
    rejection_reason = Column(Text)
    auto_approved = Column(Boolean, default=False)
    payload = Column(JSON)

class ApprovalQueue:
    """Manages approval workflow for recommendations"""
    
    def __init__(self):
        self.auto_approve_thresholds = {
            "low_risk_confidence": 0.8,
            "safe_interval_min": 60
        }
    
    async def submit_for_approval(
        self, 
        meta_analysis_id: int,
        recommendation_type: str,
        target: str,
        current_value: Any,
        proposed_value: Any,
        recommendation_text: str,
        confidence: float,
        risk_level: str,
        payload: Optional[Dict] = None
    ) -> int:
        """Submit recommendation for approval"""
        
        async with async_session() as session:
            queue_item = RecommendationQueue(
                meta_analysis_id=meta_analysis_id,
                recommendation_type=recommendation_type,
                target=target,
                current_value=str(current_value) if current_value else None,
                proposed_value=str(proposed_value),
                recommendation_text=recommendation_text,
                confidence=confidence,
                risk_level=risk_level,
                payload=payload or {}
            )
            
            session.add(queue_item)
            await session.commit()
            await session.refresh(queue_item)
            
            print(f"📋 Submitted recommendation {queue_item.id} for approval: {recommendation_text}")
            
            if await self._should_auto_approve(queue_item):
                await self.approve_recommendation(queue_item.id, "auto_approval_system", "Low risk, high confidence")
                queue_item.auto_approved = True
                await session.commit()
            
            return queue_item.id
    
    async def approve_recommendation(
        self, 
        rec_id: int, 
        approver: str,
        reason: str = "Approved for deployment"
    ) -> Dict[str, Any]:
        """Approve and apply a recommendation"""
        
        async with async_session() as session:
            result = await session.execute(
                select(RecommendationQueue).where(RecommendationQueue.id == rec_id)
            )
            rec = result.scalar_one_or_none()
            
            if not rec:
                return {"success": False, "error": "Recommendation not found"}
            
            if rec.status != "pending":
                return {"success": False, "error": f"Recommendation already {rec.status}"}
            
            rec.status = "approved"
            rec.reviewed_at = datetime.utcnow()
            rec.reviewed_by = approver
            rec.approval_reason = reason
            await session.commit()
            
            print(f"✅ Approved recommendation {rec_id} by {approver}: {rec.recommendation_text}")
            
            result = await self._apply_recommendation(rec)
            
            if result.get("success"):
                from .verification import verification_service
                await verification_service.sign_event(
                    event_type="meta.recommendation_applied",
                    actor=approver,
                    resource=rec.target,
                    payload={
                        "recommendation_id": rec_id,
                        "type": rec.recommendation_type,
                        "old_value": rec.current_value,
                        "new_value": rec.proposed_value,
                        "applied_id": result.get("applied_id")
                    }
                )
                print(f"🔐 Meta-change signed and logged")
            
            return result
    
    async def reject_recommendation(
        self, 
        rec_id: int, 
        rejector: str,
        reason: str
    ) -> Dict[str, Any]:
        """Reject a recommendation"""
        
        async with async_session() as session:
            result = await session.execute(
                select(RecommendationQueue).where(RecommendationQueue.id == rec_id)
            )
            rec = result.scalar_one_or_none()
            
            if not rec:
                return {"success": False, "error": "Recommendation not found"}
            
            if rec.status != "pending":
                return {"success": False, "error": f"Recommendation already {rec.status}"}
            
            rec.status = "rejected"
            rec.reviewed_at = datetime.utcnow()
            rec.reviewed_by = rejector
            rec.rejection_reason = reason
            await session.commit()
            
            print(f"❌ Rejected recommendation {rec_id} by {rejector}: {reason}")
            
            return {"success": True, "status": "rejected"}
    
    async def auto_approve_safe_changes(self) -> int:
        """Auto-approve low-risk, high-confidence changes"""
        
        async with async_session() as session:
            result = await session.execute(
                select(RecommendationQueue).where(
                    RecommendationQueue.status == "pending",
                    RecommendationQueue.auto_approved == False
                )
            )
            pending = result.scalars().all()
            
            approved_count = 0
            for rec in pending:
                if await self._should_auto_approve(rec):
                    await self.approve_recommendation(
                        rec.id, 
                        "auto_approval_system",
                        f"Auto-approved: {rec.risk_level} risk, {rec.confidence:.2f} confidence"
                    )
                    approved_count += 1
            
            if approved_count > 0:
                print(f"🤖 Auto-approved {approved_count} low-risk recommendations")
            
            return approved_count
    
    async def _should_auto_approve(self, rec: RecommendationQueue) -> bool:
        """Determine if recommendation should be auto-approved"""
        
        if rec.risk_level == "low" and rec.confidence >= self.auto_approve_thresholds["low_risk_confidence"]:
            return True
        
        if rec.recommendation_type == "interval_change":
            proposed = float(rec.proposed_value)
            if proposed >= self.auto_approve_thresholds["safe_interval_min"]:
                return True
        
        return False
    
    async def _apply_recommendation(self, rec: RecommendationQueue) -> Dict[str, Any]:
        """Apply an approved recommendation"""
        
        from .meta_loop_engine import recommendation_applicator
        
        if rec.recommendation_type == "threshold_change":
            return await recommendation_applicator.apply_threshold_change(
                component=rec.payload.get("component", "learning"),
                threshold_name=rec.target,
                new_value=float(rec.proposed_value),
                meta_analysis_id=rec.meta_analysis_id,
                approver=rec.reviewed_by
            )
        
        elif rec.recommendation_type == "interval_change":
            return await recommendation_applicator.apply_interval_change(
                loop_name=rec.target,
                new_interval=int(rec.proposed_value),
                meta_analysis_id=rec.meta_analysis_id,
                approver=rec.reviewed_by
            )
        
        elif rec.recommendation_type == "priority_change":
            return await recommendation_applicator.apply_priority_change(
                task_type=rec.target,
                new_priority=int(rec.proposed_value),
                meta_analysis_id=rec.meta_analysis_id,
                approver=rec.reviewed_by
            )
        
        return {"success": False, "error": "Unknown recommendation type"}
    
    async def get_pending_recommendations(self) -> List[Dict[str, Any]]:
        """Get all pending recommendations"""
        
        async with async_session() as session:
            result = await session.execute(
                select(RecommendationQueue)
                .where(RecommendationQueue.status == "pending")
                .order_by(RecommendationQueue.submitted_at.desc())
            )
            pending = result.scalars().all()
            
            return [
                {
                    "id": rec.id,
                    "type": rec.recommendation_type,
                    "target": rec.target,
                    "current": rec.current_value,
                    "proposed": rec.proposed_value,
                    "text": rec.recommendation_text,
                    "confidence": rec.confidence,
                    "risk_level": rec.risk_level,
                    "submitted_at": rec.submitted_at.isoformat() if rec.submitted_at else None
                }
                for rec in pending
            ]
    
    async def get_applied_recommendations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get history of applied recommendations with metrics"""
        
        from .meta_loop_engine import AppliedRecommendation
        
        async with async_session() as session:
            result = await session.execute(
                select(AppliedRecommendation)
                .order_by(AppliedRecommendation.applied_at.desc())
                .limit(limit)
            )
            applied = result.scalars().all()
            
            return [
                {
                    "id": rec.id,
                    "type": rec.recommendation_type,
                    "target": rec.target,
                    "old_value": rec.old_value,
                    "new_value": rec.new_value,
                    "applied_by": rec.applied_by,
                    "applied_at": rec.applied_at.isoformat() if rec.applied_at else None,
                    "effectiveness": rec.effectiveness_score,
                    "rolled_back": rec.rolled_back,
                    "before_metrics": rec.before_metrics,
                    "after_metrics": rec.after_metrics
                }
                for rec in applied
            ]

approval_queue = ApprovalQueue()
