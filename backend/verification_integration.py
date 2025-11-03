"""Integration layer for verification audit and status checking"""

from sqlalchemy import select, desc
from .models import async_session
from .verification import VerificationEnvelope
from .hunter_integration import hunter_integration
from datetime import datetime, timedelta
from typing import List, Dict, Any

class VerificationIntegration:
    """Functions to check verification status and audit logs"""
    
    async def check_verification_status(self, action_id: str) -> Dict[str, Any]:
        """Check if a specific action was verified"""
        async with async_session() as session:
            result = await session.execute(
                select(VerificationEnvelope).where(
                    VerificationEnvelope.action_id == action_id
                )
            )
            envelope = result.scalar_one_or_none()
            
            if not envelope:
                return {"status": "not_found", "verified": False}
            
            return {
                "status": "found",
                "verified": envelope.verified,
                "action_id": envelope.action_id,
                "actor": envelope.actor,
                "action_type": envelope.action_type,
                "resource": envelope.resource,
                "criteria_met": envelope.criteria_met,
                "created_at": envelope.created_at
            }
    
    async def get_verification_audit_log(
        self, 
        limit: int = 100,
        actor: str = None,
        action_type: str = None,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent verification audit log"""
        async with async_session() as session:
            query = select(VerificationEnvelope).order_by(
                desc(VerificationEnvelope.created_at)
            )
            
            if actor:
                query = query.where(VerificationEnvelope.actor == actor)
            if action_type:
                query = query.where(VerificationEnvelope.action_type == action_type)
            
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            query = query.where(VerificationEnvelope.created_at >= cutoff_time)
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            envelopes = result.scalars().all()
            
            return [
                {
                    "action_id": e.action_id,
                    "actor": e.actor,
                    "action_type": e.action_type,
                    "resource": e.resource,
                    "verified": e.verified,
                    "criteria_met": e.criteria_met,
                    "input_hash": e.input_hash,
                    "output_hash": e.output_hash,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in envelopes
            ]
    
    async def get_failed_verifications(
        self, 
        limit: int = 50,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get verifications that failed criteria"""
        async with async_session() as session:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            result = await session.execute(
                select(VerificationEnvelope)
                .where(VerificationEnvelope.verified == False)
                .where(VerificationEnvelope.created_at >= cutoff_time)
                .order_by(desc(VerificationEnvelope.created_at))
                .limit(limit)
            )
            
            failures = result.scalars().all()
            
            for failure in failures:
                await self.flag_failed_verification_to_hunter(failure)
            
            return [
                {
                    "action_id": f.action_id,
                    "actor": f.actor,
                    "action_type": f.action_type,
                    "resource": f.resource,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in failures
            ]
    
    async def flag_failed_verification_to_hunter(self, envelope: VerificationEnvelope):
        """Flag a failed verification to Hunter for investigation"""
        await hunter_integration.flag_verification_failure(
            action_id=envelope.action_id,
            actor=envelope.actor,
            action_type=envelope.action_type,
            reason="Verification envelope check failed"
        )
    
    async def get_verification_stats(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get verification statistics"""
        async with async_session() as session:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            total_result = await session.execute(
                select(VerificationEnvelope)
                .where(VerificationEnvelope.created_at >= cutoff_time)
            )
            total = len(total_result.scalars().all())
            
            verified_result = await session.execute(
                select(VerificationEnvelope)
                .where(VerificationEnvelope.created_at >= cutoff_time)
                .where(VerificationEnvelope.verified == True)
            )
            verified = len(verified_result.scalars().all())
            
            criteria_met_result = await session.execute(
                select(VerificationEnvelope)
                .where(VerificationEnvelope.created_at >= cutoff_time)
                .where(VerificationEnvelope.criteria_met == True)
            )
            criteria_met = len(criteria_met_result.scalars().all())
            
            return {
                "total_verifications": total,
                "verified_count": verified,
                "criteria_met_count": criteria_met,
                "failed_count": total - verified,
                "success_rate": (verified / total * 100) if total > 0 else 0,
                "period_hours": hours_back
            }

verification_integration = VerificationIntegration()
