"""
Performance Optimization Engine
Grace analyzes her own performance and optimizes system parameters
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from .healing_analytics import healing_analytics
from .grace_log_reader import grace_log_reader
from .unified_logger import unified_logger
from .models import async_session
from .healing_models import DataCubeEntry, ParallelProcessLog
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Analyzes performance metrics and optimizes system parameters
    """
    
    def __init__(self):
        self.optimization_cycle_interval = 1800  # 30 minutes
        self.running = False
        self.optimizations_made = 0
        self.cycle_task = None
    
    async def start(self):
        """Start performance optimization cycles"""
        if self.running:
            return
        
        self.running = True
        self.cycle_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("[OPTIMIZER] ⚡ Performance Optimizer started")
    
    async def stop(self):
        """Stop performance optimization"""
        self.running = False
        if self.cycle_task:
            self.cycle_task.cancel()
        logger.info("[OPTIMIZER] Performance Optimizer stopped")
    
    async def _optimization_loop(self):
        """Continuous optimization cycle"""
        
        while self.running:
            try:
                await asyncio.sleep(self.optimization_cycle_interval)
                
                logger.info("[OPTIMIZER] 🔍 Analyzing performance metrics...")
                
                # Analyze various metrics
                analysis = await self._analyze_performance()
                
                # Generate optimization recommendations
                optimizations = await self._generate_optimizations(analysis)
                
                if optimizations:
                    logger.info(f"[OPTIMIZER] 💡 Generated {len(optimizations)} optimization recommendations")
                    
                    # Log optimizations
                    for opt in optimizations:
                        await self._log_optimization(opt)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[OPTIMIZER] Error in optimization cycle: {e}", exc_info=True)
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze system performance metrics"""
        
        since = datetime.utcnow() - timedelta(hours=1)
        
        analysis = {
            'period_hours': 1,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        async with async_session() as session:
            # Average task execution time
            result = await session.execute(
                select(func.avg(ParallelProcessLog.execution_time_seconds))
                .where(ParallelProcessLog.completed_at >= since)
                .where(ParallelProcessLog.success == True)
            )
            avg_exec_time = result.scalar() or 0.0
            analysis['avg_execution_time'] = avg_exec_time
            
            # Task success rate
            result = await session.execute(
                select(func.count(ParallelProcessLog.id))
                .where(ParallelProcessLog.completed_at >= since)
            )
            total_tasks = result.scalar() or 0
            
            result = await session.execute(
                select(func.count(ParallelProcessLog.id))
                .where(ParallelProcessLog.completed_at >= since)
                .where(ParallelProcessLog.success == True)
            )
            successful_tasks = result.scalar() or 0
            
            analysis['task_success_rate'] = successful_tasks / total_tasks if total_tasks > 0 else 1.0
            analysis['total_tasks'] = total_tasks
            
            # Average wait time
            result = await session.execute(
                select(func.avg(ParallelProcessLog.wait_time_seconds))
                .where(ParallelProcessLog.started_at >= since)
            )
            avg_wait = result.scalar() or 0.0
            analysis['avg_wait_time'] = avg_wait
            
            # Data cube activity rate
            result = await session.execute(
                select(func.count(DataCubeEntry.id))
                .where(DataCubeEntry.dimension_time >= since)
            )
            activity_count = result.scalar() or 0
            analysis['activity_per_hour'] = activity_count
        
        return analysis
    
    async def _generate_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        
        optimizations = []
        
        # Optimize for slow execution
        if analysis['avg_execution_time'] > 5.0:
            optimizations.append({
                'type': 'reduce_execution_time',
                'priority': 'medium',
                'current_value': analysis['avg_execution_time'],
                'target_value': 3.0,
                'recommendation': 'Optimize slow operations or increase parallelism',
                'estimated_improvement': '40% faster execution'
            })
        
        # Optimize for high wait time
        if analysis['avg_wait_time'] > 2.0:
            optimizations.append({
                'type': 'reduce_wait_time',
                'priority': 'medium',
                'current_value': analysis['avg_wait_time'],
                'target_value': 1.0,
                'recommendation': 'Increase worker count or improve task scheduling',
                'estimated_improvement': '50% less queuing'
            })
        
        # Optimize for low activity
        if analysis['activity_per_hour'] < 10:
            optimizations.append({
                'type': 'increase_activity',
                'priority': 'low',
                'current_value': analysis['activity_per_hour'],
                'target_value': 20,
                'recommendation': 'More proactive monitoring and intervention',
                'estimated_improvement': 'More autonomous actions'
            })
        
        return optimizations
    
    async def _log_optimization(self, optimization: Dict[str, Any]):
        """Log optimization recommendation"""
        
        await unified_logger.log_agentic_spine_decision(
            decision_type='optimization_recommended',
            decision_context=optimization,
            chosen_action=optimization['recommendation'],
            rationale=f"Current: {optimization['current_value']}, Target: {optimization['target_value']}",
            actor='performance_optimizer',
            confidence=0.75,
            risk_score=0.1,
            status='recommended',
            resource=optimization['type']
        )


# Global instance
performance_optimizer = PerformanceOptimizer()
