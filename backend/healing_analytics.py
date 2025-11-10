"""
Healing Analytics Engine
Query and analyze healing data from tables + data cube
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
import logging

from .models import async_session
from .healing_models import (
    HealingAttempt, AgenticSpineLog, MetaLoopLog,
    MLLearningLog, TriggerMeshLog, DataCubeEntry
)

logger = logging.getLogger(__name__)


class HealingAnalytics:
    """Query and analyze healing system performance"""
    
    async def get_healing_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of healing activity"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            # Healing attempts
            result = await session.execute(
                select(HealingAttempt)
                .where(HealingAttempt.attempted_at >= since)
            )
            attempts = result.scalars().all()
            
            total_attempts = len(attempts)
            successful = sum(1 for a in attempts if a.success is True)
            failed = sum(1 for a in attempts if a.success is False)
            pending = sum(1 for a in attempts if a.status == 'pending')
            
            # By severity
            by_severity = {}
            for attempt in attempts:
                sev = attempt.severity
                by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # By error type
            by_error_type = {}
            for attempt in attempts:
                et = attempt.error_type
                by_error_type[et] = by_error_type.get(et, 0) + 1
            
            return {
                'period_hours': hours,
                'total_attempts': total_attempts,
                'successful': successful,
                'failed': failed,
                'pending': pending,
                'success_rate': successful / total_attempts if total_attempts > 0 else 0.0,
                'by_severity': by_severity,
                'by_error_type': by_error_type
            }
    
    async def get_ml_learning_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get ML/DL learning statistics"""
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            result = await session.execute(
                select(MLLearningLog)
                .where(MLLearningLog.timestamp >= since)
            )
            logs = result.scalars().all()
            
            total_learning_cycles = len(logs)
            pattern_updates = sum(1 for l in logs if l.learning_type == 'pattern_update')
            model_trainings = sum(1 for l in logs if l.learning_type == 'model_training')
            predictions = sum(1 for l in logs if l.learning_type == 'prediction')
            
            # Average confidence
            confidences = [l.pattern_confidence for l in logs if l.pattern_confidence]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'period_hours': hours,
                'total_learning_cycles': total_learning_cycles,
                'pattern_updates': pattern_updates,
                'model_trainings': model_trainings,
                'predictions_made': predictions,
                'average_confidence': avg_confidence
            }
    
    async def get_data_cube_analytics(
        self,
        dimension: str = 'subsystem',
        metric: str = 'count',
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Query data cube for multi-dimensional analytics
        
        Args:
            dimension: Which dimension to group by (subsystem, actor, action)
            metric: Which metric to aggregate (count, success_rate, duration)
            hours: Time window
        """
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with async_session() as session:
            if dimension == 'subsystem':
                group_col = DataCubeEntry.dimension_subsystem
            elif dimension == 'actor':
                group_col = DataCubeEntry.dimension_actor
            elif dimension == 'action':
                group_col = DataCubeEntry.dimension_action
            else:
                group_col = DataCubeEntry.dimension_subsystem
            
            # Query based on metric
            if metric == 'count':
                result = await session.execute(
                    select(
                        group_col,
                        func.count(DataCubeEntry.id).label('value')
                    )
                    .where(DataCubeEntry.dimension_time >= since)
                    .group_by(group_col)
                )
            elif metric == 'success_rate':
                result = await session.execute(
                    select(
                        group_col,
                        func.avg(func.cast(DataCubeEntry.metric_success, Integer)).label('value')
                    )
                    .where(DataCubeEntry.dimension_time >= since)
                    .group_by(group_col)
                )
            elif metric == 'duration':
                result = await session.execute(
                    select(
                        group_col,
                        func.avg(DataCubeEntry.metric_duration).label('value')
                    )
                    .where(DataCubeEntry.dimension_time >= since)
                    .where(DataCubeEntry.metric_duration.isnot(None))
                    .group_by(group_col)
                )
            else:
                result = await session.execute(
                    select(
                        group_col,
                        func.count(DataCubeEntry.id).label('value')
                    )
                    .where(DataCubeEntry.dimension_time >= since)
                    .group_by(group_col)
                )
            
            rows = result.all()
            
            analytics = {}
            for row in rows:
                analytics[row[0]] = row[1]
            
            return {
                'dimension': dimension,
                'metric': metric,
                'period_hours': hours,
                'data': analytics
            }
    
    async def get_crypto_verification_report(self) -> Dict[str, Any]:
        """Verify cryptographic chain integrity for all tables"""
        
        report = {
            'tables': {},
            'overall_integrity': True
        }
        
        tables = [
            ('healing_attempts', HealingAttempt),
            ('agentic_spine_logs', AgenticSpineLog),
            ('meta_loop_logs', MetaLoopLog),
            ('ml_learning_logs', MLLearningLog)
        ]
        
        async with async_session() as session:
            for table_name, model_class in tables:
                result = await session.execute(
                    select(model_class).order_by(model_class.id)
                )
                entries = result.scalars().all()
                
                verified = 0
                broken = 0
                
                for i, entry in enumerate(entries):
                    if i == 0:
                        # Genesis entry
                        if not entry.previous_hash or entry.previous_hash == "":
                            verified += 1
                        else:
                            broken += 1
                    else:
                        # Check chain
                        prev_entry = entries[i-1]
                        if entry.previous_hash == prev_entry.hash:
                            verified += 1
                        else:
                            broken += 1
                
                table_integrity = broken == 0
                report['tables'][table_name] = {
                    'total_entries': len(entries),
                    'verified_links': verified,
                    'broken_links': broken,
                    'integrity': 'INTACT' if table_integrity else 'COMPROMISED'
                }
                
                if not table_integrity:
                    report['overall_integrity'] = False
        
        return report


# Global instance
healing_analytics = HealingAnalytics()
