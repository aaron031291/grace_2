"""
Grace Log Reader
Grace's ability to read and understand her own logs and activity
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, desc, func
import logging

from .models import async_session
from .healing_models import (
    HealingAttempt, AgenticSpineLog, MetaLoopLog,
    MLLearningLog, TriggerMeshLog, ShardLog, ParallelProcessLog
)
from .healing_analytics import healing_analytics

logger = logging.getLogger(__name__)


class GraceLogReader:
    """
    Allows Grace to read and interpret her own logs
    for self-awareness and improvement
    """
    
    async def get_my_recent_activity(self, hours: int = 1) -> Dict[str, Any]:
        """Get Grace's recent autonomous activity"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        summary = {
            'period_hours': hours,
            'healing': {'attempts': 0, 'successes': 0, 'failures': 0},
            'decisions': {'made': 0, 'executed': 0},
            'learning': {'patterns_updated': 0, 'predictions_made': 0},
            'shards': {'active': 0, 'tasks_completed': 0},
            'events': {'published': 0, 'handlers_executed': 0}
        }
        
        async with async_session() as session:
            # Healing activity
            result = await session.execute(
                select(HealingAttempt)
                .where(HealingAttempt.attempted_at >= since)
            )
            healing = result.scalars().all()
            summary['healing']['attempts'] = len(healing)
            summary['healing']['successes'] = sum(1 for h in healing if h.success is True)
            summary['healing']['failures'] = sum(1 for h in healing if h.success is False)
            
            # Decisions made
            result = await session.execute(
                select(AgenticSpineLog)
                .where(AgenticSpineLog.timestamp >= since)
            )
            decisions = result.scalars().all()
            summary['decisions']['made'] = len(decisions)
            summary['decisions']['executed'] = sum(1 for d in decisions if d.status == 'completed')
            
            # Learning activity
            result = await session.execute(
                select(MLLearningLog)
                .where(MLLearningLog.timestamp >= since)
            )
            learning = result.scalars().all()
            summary['learning']['patterns_updated'] = sum(1 for l in learning if l.learning_type == 'pattern_update')
            summary['learning']['predictions_made'] = sum(1 for l in learning if l.predicted_error)
            
            # Shard activity
            result = await session.execute(
                select(ShardLog)
                .where(ShardLog.timestamp >= since)
            )
            shards = result.scalars().all()
            summary['shards']['active'] = len(set(s.shard_id for s in shards))
            summary['shards']['tasks_completed'] = sum(1 for s in shards if s.success is True)
            
            # Trigger mesh
            result = await session.execute(
                select(TriggerMeshLog)
                .where(TriggerMeshLog.timestamp >= since)
            )
            events = result.scalars().all()
            summary['events']['published'] = len(events)
            summary['events']['handlers_executed'] = sum(e.handlers_succeeded for e in events)
        
        return summary
    
    async def get_my_errors(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get errors Grace encountered"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(HealingAttempt)
                .where(HealingAttempt.attempted_at >= since)
                .where(HealingAttempt.success == False)
                .order_by(desc(HealingAttempt.attempted_at))
                .limit(limit)
            )
            
            errors = result.scalars().all()
            
            return [
                {
                    'error_type': e.error_type,
                    'error_message': e.error_message,
                    'file': e.error_file,
                    'line': e.error_line,
                    'attempted_at': e.attempted_at.isoformat() if e.attempted_at else None,
                    'fix_attempted': bool(e.fix_description),
                    'failure_reason': e.failure_reason
                }
                for e in errors
            ]
    
    async def get_my_successes(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get successful healing actions Grace performed"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(HealingAttempt)
                .where(HealingAttempt.attempted_at >= since)
                .where(HealingAttempt.success == True)
                .order_by(desc(HealingAttempt.attempted_at))
                .limit(limit)
            )
            
            successes = result.scalars().all()
            
            return [
                {
                    'error_type': s.error_type,
                    'fix_description': s.fix_description,
                    'file': s.error_file,
                    'line': s.error_line,
                    'applied_at': s.applied_at.isoformat() if s.applied_at else None,
                    'confidence': s.confidence
                }
                for s in successes
            ]
    
    async def get_my_learning_progress(self) -> Dict[str, Any]:
        """Get Grace's learning progress metrics"""
        
        async with async_session() as session:
            # Total patterns learned
            result = await session.execute(
                select(func.count(func.distinct(MLLearningLog.pattern_name)))
                .where(MLLearningLog.pattern_name.isnot(None))
            )
            patterns_learned = result.scalar() or 0
            
            # Total predictions made
            result = await session.execute(
                select(func.count(MLLearningLog.id))
                .where(MLLearningLog.predicted_error.isnot(None))
            )
            predictions_made = result.scalar() or 0
            
            # Average pattern success rate
            result = await session.execute(
                select(func.avg(MLLearningLog.pattern_success_rate))
                .where(MLLearningLog.pattern_success_rate.isnot(None))
            )
            avg_success_rate = result.scalar() or 0.0
            
            return {
                'patterns_learned': patterns_learned,
                'predictions_made': predictions_made,
                'average_pattern_success_rate': avg_success_rate,
                'learning_status': 'active' if patterns_learned > 0 else 'initializing'
            }
    
    async def generate_self_report(self, hours: int = 24) -> str:
        """Generate natural language self-report for Grace"""
        
        activity = await self.get_my_recent_activity(hours)
        errors = await self.get_my_errors(hours, limit=5)
        successes = await self.get_my_successes(hours, limit=5)
        learning = await self.get_my_learning_progress()
        
        report = f"📊 My Activity Report (Last {hours}h)\n\n"
        
        # Healing
        report += f"🔧 Healing:\n"
        report += f"   • Attempted {activity['healing']['attempts']} fixes\n"
        report += f"   • ✅ {activity['healing']['successes']} successful\n"
        report += f"   • ❌ {activity['healing']['failures']} failed\n"
        
        if activity['healing']['attempts'] > 0:
            rate = activity['healing']['successes'] / activity['healing']['attempts'] * 100
            report += f"   • Success rate: {rate:.1f}%\n"
        
        report += "\n"
        
        # Decisions
        report += f"🎯 Autonomous Decisions:\n"
        report += f"   • Made {activity['decisions']['made']} decisions\n"
        report += f"   • Executed {activity['decisions']['executed']} actions\n\n"
        
        # Learning
        report += f"🧠 Learning:\n"
        report += f"   • Patterns learned: {learning['patterns_learned']}\n"
        report += f"   • Predictions made: {learning['predictions_made']}\n"
        report += f"   • Avg success rate: {learning['average_pattern_success_rate']:.1%}\n\n"
        
        # Recent successes
        if successes:
            report += "✅ Recent Successes:\n"
            for s in successes[:3]:
                report += f"   • Fixed {s['error_type']} in {s['file']}\n"
            report += "\n"
        
        # Recent errors (for learning)
        if errors:
            report += "❌ Recent Challenges:\n"
            for e in errors[:3]:
                report += f"   • {e['error_type']} - {e['failure_reason'] or 'Still analyzing'}\n"
            report += "\n"
        
        # Shards & Parallel
        report += f"🔀 Parallel Execution:\n"
        report += f"   • Active shards: {activity['shards']['active']}\n"
        report += f"   • Tasks completed: {activity['shards']['tasks_completed']}\n"
        report += f"   • Events published: {activity['events']['published']}\n"
        
        return report


# Global instance
grace_log_reader = GraceLogReader()
