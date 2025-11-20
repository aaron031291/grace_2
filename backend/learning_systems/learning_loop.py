"""
Learning Loop - Continuous Improvement from Action Outcomes

Captures outcomes from verified actions and updates:
- Playbook success rates
- Action confidence scores
- Pattern recognition
- Future recommendations

Feeds back into the agentic system for continuous improvement.
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, String, JSON, DateTime, Float, Boolean, Integer, select, func

from backend.models.base_models import Base, async_session
from backend.logging.immutable_log import immutable_log


class OutcomeRecord(Base):
    """Records outcome of an agentic action for learning"""
    __tablename__ = "outcome_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Action identification
    contract_id = Column(String(128), nullable=True)
    playbook_id = Column(String(128), nullable=True)
    action_type = Column(String(128), nullable=False)
    
    # Problem context
    error_pattern = Column(String(256), nullable=True)
    diagnosis_code = Column(String(128), nullable=True)
    
    # Outcome
    success = Column(Boolean, nullable=False)
    confidence_score = Column(Float, nullable=True)  # From verification
    execution_time_seconds = Column(Float, nullable=True)
    
    # Impact
    problem_resolved = Column(Boolean, nullable=True)
    rollback_occurred = Column(Boolean, default=False)
    
    # Metadata
    tier = Column(String(32), nullable=True)
    triggered_by = Column(String(256), nullable=True)
    context = Column(JSON, nullable=True)
    
    # Timing
    created_at = Column(DateTime, nullable=False)


class PlaybookStatistics(Base):
    """Aggregated statistics for playbooks"""
    __tablename__ = "playbook_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    playbook_id = Column(String(128), unique=True, nullable=False)
    
    # Success tracking
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    rollbacks = Column(Integer, default=0)
    
    # Performance
    avg_confidence_score = Column(Float, default=0.0)
    avg_execution_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)  # 0.0-1.0
    
    # Learning
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    
    # Recommendations
    recommended_for_patterns = Column(JSON, nullable=True)  # List of error patterns
    
    # Timing
    updated_at = Column(DateTime, nullable=False)


class LearningLoop:
    """
    Continuous learning system that improves Grace from experience.
    Updates playbook statistics, confidence scores, and recommendations.
    """
    
    async def record_outcome(
        self,
        action_type: str,
        success: bool,
        error_pattern: Optional[str] = None,
        diagnosis_code: Optional[str] = None,
        contract_id: Optional[str] = None,
        playbook_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
        execution_time: Optional[float] = None,
        problem_resolved: bool = False,
        rolled_back: bool = False,
        tier: str = "tier_1",
        triggered_by: Optional[str] = None,
        context: Optional[Dict] = None
    ):
        """
        Record an action outcome for learning.
        Called after every verified action execution.
        """
        
        async with async_session() as session:
            # Create outcome record
            outcome = OutcomeRecord(
                contract_id=contract_id,
                playbook_id=playbook_id,
                action_type=action_type,
                error_pattern=error_pattern,
                diagnosis_code=diagnosis_code,
                success=success,
                confidence_score=confidence_score,
                execution_time_seconds=execution_time,
                problem_resolved=problem_resolved,
                rollback_occurred=rolled_back,
                tier=tier,
                triggered_by=triggered_by,
                context=context,
                created_at=datetime.now(timezone.utc)
            )
            session.add(outcome)
            await session.commit()
            
            # Update playbook statistics if applicable
            if playbook_id:
                await self._update_playbook_stats(playbook_id, success, confidence_score, execution_time, rolled_back)
                
                # NEW: Notify brain of learning insights
                await self._notify_brain_of_insights(playbook_id)
            
            # Log to immutable ledger
            await immutable_log.append(
                actor="learning_loop",
                action="outcome_recorded",
                resource=playbook_id or action_type,
                subsystem="learning",
                payload={
                    "action_type": action_type,
                    "success": success,
                    "confidence": confidence_score,
                    "rolled_back": rolled_back
                },
                result="success" if success else "failed"
            )
    
    async def _update_playbook_stats(
        self,
        playbook_id: str,
        success: bool,
        confidence_score: Optional[float],
        execution_time: Optional[float],
        rolled_back: bool
    ):
        """Update aggregated playbook statistics"""
        
        async with async_session() as session:
            # Get or create stats record
            result = await session.execute(
                select(PlaybookStatistics)
                .where(PlaybookStatistics.playbook_id == playbook_id)
            )
            stats = result.scalar_one_or_none()
            
            if not stats:
                stats = PlaybookStatistics(
                    playbook_id=playbook_id,
                    total_executions=0,
                    successful_executions=0,
                    failed_executions=0,
                    rollbacks=0,
                    avg_confidence_score=0.0,
                    avg_execution_time=0.0,
                    success_rate=0.0,
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(stats)
            
            # Update counts
            stats.total_executions = (stats.total_executions or 0) + 1
            if success:
                stats.successful_executions += 1
                stats.last_success_at = datetime.now(timezone.utc)
            else:
                stats.failed_executions += 1
                stats.last_failure_at = datetime.now(timezone.utc)
            
            if rolled_back:
                stats.rollbacks += 1
            
            # Update averages
            if confidence_score is not None:
                # Rolling average of confidence scores
                n = stats.total_executions
                stats.avg_confidence_score = (
                    (stats.avg_confidence_score * (n - 1) + confidence_score) / n
                )
            
            if execution_time is not None:
                n = stats.total_executions
                stats.avg_execution_time = (
                    (stats.avg_execution_time * (n - 1) + execution_time) / n
                )
            
            # Update success rate
            stats.success_rate = stats.successful_executions / stats.total_executions
            stats.updated_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            # Send execution time telemetry to HTM
            if execution_time is not None:
                try:
                    from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
                    # Tokenize duration (100ms buckets)
                    duration_ms = int(execution_time * 1000)
                    token = min(duration_ms // 100, 10000)
                    htm_detector_pool.detect_for_model(
                        "action_duration",
                        [token],
                        [1.0]
                    )
                except Exception:
                    pass
    
    async def get_playbook_stats(self, playbook_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific playbook"""
        
        async with async_session() as session:
            result = await session.execute(
                select(PlaybookStatistics)
                .where(PlaybookStatistics.playbook_id == playbook_id)
            )
            stats = result.scalar_one_or_none()
            
            if not stats:
                return None
            
            return {
                "playbook_id": stats.playbook_id,
                "total_executions": stats.total_executions,
                "successful_executions": stats.successful_executions,
                "failed_executions": stats.failed_executions,
                "rollbacks": stats.rollbacks,
                "success_rate": stats.success_rate,
                "avg_confidence_score": stats.avg_confidence_score,
                "avg_execution_time": stats.avg_execution_time,
                "last_success_at": stats.last_success_at.isoformat() if stats.last_success_at else None,
                "last_failure_at": stats.last_failure_at.isoformat() if stats.last_failure_at else None
            }
    
    async def _notify_brain_of_insights(self, playbook_id: str):
        """
        NEW: Feed learning insights back to agentic brain
        Called after updating playbook stats to close the learning loop
        """
        try:
            # Get current stats
            async with async_session() as session:
                result = await session.execute(
                    select(PlaybookStatistics)
                    .where(PlaybookStatistics.playbook_id == playbook_id)
                )
                stats = result.scalar_one_or_none()
                
                if not stats:
                    return
                
                # Emit insight event if success rate drops below threshold
                if stats.success_rate < 0.6 and stats.total_executions >= 3:
                    from backend.core.message_bus import message_bus, MessagePriority
                    
                    await message_bus.publish(
                        source="learning_loop",
                        topic="agentic.learning.insight",
                        payload={
                            "insight_type": "low_success_rate",
                            "playbook_id": playbook_id,
                            "success_rate": stats.success_rate,
                            "total_executions": stats.total_executions,
                            "recommendation": "consider_alternative_playbook",
                            "reason": f"Success rate {stats.success_rate:.1%} below 60% threshold",
                            "severity": "high" if stats.success_rate < 0.4 else "medium"
                        },
                        priority=MessagePriority.HIGH
                    )
                    
                    print(f"[LEARNING] Insight emitted: {playbook_id} success rate at {stats.success_rate:.1%}")
                
                # Emit positive insight for high performers
                elif stats.success_rate > 0.9 and stats.total_executions >= 5:
                    from backend.core.message_bus import message_bus, MessagePriority
                    
                    await message_bus.publish(
                        source="learning_loop",
                        topic="agentic.learning.insight",
                        payload={
                            "insight_type": "high_success_rate",
                            "playbook_id": playbook_id,
                            "success_rate": stats.success_rate,
                            "total_executions": stats.total_executions,
                            "recommendation": "prioritize_this_playbook",
                            "reason": f"Success rate {stats.success_rate:.1%} exceeds 90%"
                        },
                        priority=MessagePriority.NORMAL
                    )
        except Exception as e:
            print(f"[LEARNING] Failed to notify brain: {e}")
    
    async def get_top_playbooks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-performing playbooks by success rate"""
        
        async with async_session() as session:
            result = await session.execute(
                select(PlaybookStatistics)
                .where(PlaybookStatistics.total_executions >= 3)  # Min 3 executions
                .order_by(PlaybookStatistics.success_rate.desc())
                .limit(limit)
            )
            stats_list = result.scalars().all()
            
            return [
                {
                    "playbook_id": s.playbook_id,
                    "success_rate": s.success_rate,
                    "total_executions": s.total_executions,
                    "avg_confidence": s.avg_confidence_score
                }
                for s in stats_list
            ]
    
    async def get_recommendations_for_pattern(
        self,
        error_pattern: str,
        diagnosis_code: Optional[str] = None
    ) -> List[str]:
        """
        Get recommended playbooks for an error pattern based on historical success.
        Returns list of playbook IDs ordered by success rate.
        """
        
        async with async_session() as session:
            # Get successful outcomes for this pattern
            result = await session.execute(
                select(OutcomeRecord.playbook_id, func.count().label('count'))
                .where(OutcomeRecord.error_pattern == error_pattern)
                .where(OutcomeRecord.success == True)
                .where(OutcomeRecord.playbook_id.isnot(None))
                .group_by(OutcomeRecord.playbook_id)
                .order_by(func.count().desc())
                .limit(5)
            )
            
            recommendations = [row[0] for row in result.fetchall()]
            return recommendations
    
    async def get_learning_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of learning over the past N days"""
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        async with async_session() as session:
            # Total outcomes
            total_result = await session.execute(
                select(func.count())
                .select_from(OutcomeRecord)
                .where(OutcomeRecord.created_at >= cutoff)
            )
            total = total_result.scalar() or 0
            
            # Successful outcomes
            success_result = await session.execute(
                select(func.count())
                .select_from(OutcomeRecord)
                .where(OutcomeRecord.created_at >= cutoff)
                .where(OutcomeRecord.success == True)
            )
            successes = success_result.scalar() or 0
            
            # Rollbacks
            rollback_result = await session.execute(
                select(func.count())
                .select_from(OutcomeRecord)
                .where(OutcomeRecord.created_at >= cutoff)
                .where(OutcomeRecord.rollback_occurred == True)
            )
            rollbacks = rollback_result.scalar() or 0
            
            # Average confidence
            avg_confidence_result = await session.execute(
                select(func.avg(OutcomeRecord.confidence_score))
                .select_from(OutcomeRecord)
                .where(OutcomeRecord.created_at >= cutoff)
                .where(OutcomeRecord.confidence_score.isnot(None))
            )
            avg_confidence = avg_confidence_result.scalar() or 0.0
            
            return {
                "period_days": days,
                "total_actions": total,
                "successful_actions": successes,
                "failed_actions": total - successes,
                "rollbacks": rollbacks,
                "success_rate": (successes / total) if total > 0 else 0.0,
                "avg_confidence_score": avg_confidence,
                "learning_active": total > 0
            }


# Singleton instance
learning_loop = LearningLoop()
