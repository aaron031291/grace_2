"""
Data Pipeline Aggregation Jobs

Periodic jobs that summarize contract/benchmark outcomes and push to OLAP staging.
Stores daily aggregates for faster analytics and dashboard queries.

Benefits:
- Accelerates analytics build-out
- Reduces query load on operational DB
- Prepares data for future data cube
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import async_session
from .action_contract import ActionContract
from .benchmarks import Benchmark
from .progression_tracker import Mission
from .self_heal.safe_hold import SafeHoldSnapshot
from .event_persistence import ActionEvent
from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent


class DataAggregationService:
    """
    Periodic aggregation service for verification and execution metrics.
    """
    
    def __init__(self):
        self.running = False
        self.aggregation_task: Optional[asyncio.Task] = None
    
    async def start(self, interval_hours: int = 1):
        """
        Start periodic aggregation.
        
        Args:
            interval_hours: How often to run aggregations (default: hourly)
        """
        if self.running:
            return
        
        self.running = True
        self.aggregation_task = asyncio.create_task(
            self._aggregation_loop(interval_hours)
        )
        
        print(f"✓ Data aggregation service started (runs every {interval_hours}h)")
    
    async def stop(self):
        """Stop the aggregation service"""
        self.running = False
        if self.aggregation_task:
            self.aggregation_task.cancel()
            try:
                await self.aggregation_task
            except asyncio.CancelledError:
                pass
    
    async def _aggregation_loop(self, interval_hours: int):
        """Main aggregation loop"""
        while self.running:
            try:
                await self.run_all_aggregations()
                
                # Wait for next interval
                await asyncio.sleep(interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Aggregation error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes
    
    async def run_all_aggregations(self):
        """Run all aggregation jobs"""
        
        print("🔄 Running data aggregations...")
        start_time = datetime.now(timezone.utc)
        
        async with async_session() as session:
            # Run aggregations in parallel
            results = await asyncio.gather(
                self.aggregate_contracts(session),
                self.aggregate_benchmarks(session),
                self.aggregate_missions(session),
                self.aggregate_events(session),
                self.aggregate_daily_summary(session),
                return_exceptions=True
            )
        
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Log completion
        await immutable_log.append(
            actor="data_aggregation",
            action="aggregations_completed",
            resource="all",
            subsystem="analytics",
            payload={
                "duration_seconds": duration,
                "aggregations": len(results)
            },
            result="completed"
        )
        
        # Emit event
        await trigger_mesh.publish(TriggerEvent(
            event_type="analytics.aggregated",
            source="data_aggregation",
            actor="system",
            resource="analytics",
            payload={
                "duration_seconds": duration,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        print(f"✓ Aggregations completed in {duration:.2f}s")
    
    # ========================================================================
    # Individual Aggregation Functions
    # ========================================================================
    
    async def aggregate_contracts(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Aggregate action contract metrics.
        
        Returns summary of:
        - Total contracts by tier and status
        - Success rates
        - Violation rates
        - Rollback rates
        """
        
        # Get contract counts by tier and status
        tier_status_query = select(
            ActionContract.tier,
            ActionContract.status,
            func.count(ActionContract.id).label("count")
        ).group_by(ActionContract.tier, ActionContract.status)
        
        result = await session.execute(tier_status_query)
        tier_status_counts = {
            (row.tier, row.status): row.count
            for row in result.all()
        }
        
        # Calculate success rates by tier
        success_rates = {}
        for tier in ["tier_1", "tier_2", "tier_3"]:
            verified = tier_status_counts.get((tier, "verified"), 0)
            total = sum(
                tier_status_counts.get((tier, status), 0)
                for status in ["verified", "violated", "rolled_back"]
            )
            success_rates[tier] = verified / total if total > 0 else 0.0
        
        # Get recent violations
        violations_query = select(func.count(ActionContract.id)).where(
            and_(
                ActionContract.status == "violated",
                ActionContract.created_at >= datetime.now(timezone.utc) - timedelta(hours=24)
            )
        )
        recent_violations = await session.scalar(violations_query) or 0
        
        # Get recent rollbacks
        rollbacks_query = select(func.count(ActionContract.id)).where(
            and_(
                ActionContract.status == "rolled_back",
                ActionContract.rolled_back_at >= datetime.now(timezone.utc) - timedelta(hours=24)
            )
        )
        recent_rollbacks = await session.scalar(rollbacks_query) or 0
        
        summary = {
            "tier_status_counts": tier_status_counts,
            "success_rates": success_rates,
            "recent_violations_24h": recent_violations,
            "recent_rollbacks_24h": recent_rollbacks,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in immutable log for historical tracking
        await immutable_log.append(
            actor="data_aggregation",
            action="contracts_aggregated",
            resource="contracts",
            subsystem="analytics",
            payload=summary,
            result="completed"
        )
        
        return summary
    
    async def aggregate_benchmarks(self, session: AsyncSession) -> Dict[str, Any]:
        """Aggregate benchmark metrics"""
        
        # Get benchmark pass rates by type
        type_results_query = select(
            Benchmark.benchmark_type,
            Benchmark.passed,
            func.count(Benchmark.id).label("count"),
            func.avg(Benchmark.score).label("avg_score")
        ).group_by(Benchmark.benchmark_type, Benchmark.passed)
        
        result = await session.execute(type_results_query)
        
        benchmark_stats = {}
        for row in result.all():
            if row.benchmark_type not in benchmark_stats:
                benchmark_stats[row.benchmark_type] = {
                    "passed": 0,
                    "failed": 0,
                    "avg_score": 0.0
                }
            
            if row.passed:
                benchmark_stats[row.benchmark_type]["passed"] = row.count
            else:
                benchmark_stats[row.benchmark_type]["failed"] = row.count
            
            benchmark_stats[row.benchmark_type]["avg_score"] = float(row.avg_score or 0.0)
        
        # Calculate pass rates
        for stats in benchmark_stats.values():
            total = stats["passed"] + stats["failed"]
            stats["pass_rate"] = stats["passed"] / total if total > 0 else 0.0
        
        summary = {
            "benchmark_stats": benchmark_stats,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await immutable_log.append(
            actor="data_aggregation",
            action="benchmarks_aggregated",
            resource="benchmarks",
            subsystem="analytics",
            payload=summary,
            result="completed"
        )
        
        return summary
    
    async def aggregate_missions(self, session: AsyncSession) -> Dict[str, Any]:
        """Aggregate mission metrics"""
        
        # Count missions by status
        status_query = select(
            Mission.status,
            func.count(Mission.id).label("count"),
            func.avg(Mission.progress_percent).label("avg_progress")
        ).group_by(Mission.status)
        
        result = await session.execute(status_query)
        
        mission_stats = {
            row.status: {
                "count": row.count,
                "avg_progress": float(row.avg_progress or 0.0)
            }
            for row in result.all()
        }
        
        # Get average completion time for completed missions
        completed_query = select(
            func.avg(
                func.julianday(Mission.completed_at) - func.julianday(Mission.started_at)
            ).label("avg_duration_days")
        ).where(Mission.status == "completed")
        
        avg_duration = await session.scalar(completed_query)
        
        summary = {
            "mission_stats": mission_stats,
            "avg_completion_time_days": float(avg_duration or 0.0),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await immutable_log.append(
            actor="data_aggregation",
            action="missions_aggregated",
            resource="missions",
            subsystem="analytics",
            payload=summary,
            result="completed"
        )
        
        return summary
    
    async def aggregate_events(self, session: AsyncSession) -> Dict[str, Any]:
        """Aggregate action event metrics"""
        
        # Count events by type
        event_type_query = select(
            ActionEvent.event_type,
            func.count(ActionEvent.id).label("count")
        ).where(
            ActionEvent.triggered_at >= datetime.now(timezone.utc) - timedelta(hours=24)
        ).group_by(ActionEvent.event_type)
        
        result = await session.execute(event_type_query)
        
        event_counts = {
            row.event_type: row.count
            for row in result.all()
        }
        
        # Success rate for completed events
        completed_events = event_counts.get("agentic.problem_resolved", 0)
        failed_events = event_counts.get("agentic.action_failed", 0)
        total_outcomes = completed_events + failed_events
        
        success_rate = completed_events / total_outcomes if total_outcomes > 0 else 0.0
        
        summary = {
            "event_counts_24h": event_counts,
            "success_rate_24h": success_rate,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await immutable_log.append(
            actor="data_aggregation",
            action="events_aggregated",
            resource="events",
            subsystem="analytics",
            payload=summary,
            result="completed"
        )
        
        return summary
    
    async def aggregate_daily_summary(self, session: AsyncSession) -> Dict[str, Any]:
        """Create daily summary for dashboards"""
        
        today = datetime.now(timezone.utc).date()
        
        # Contracts created today
        contracts_today = await session.scalar(
            select(func.count(ActionContract.id)).where(
                func.date(ActionContract.created_at) == today
            )
        ) or 0
        
        # Benchmarks run today
        benchmarks_today = await session.scalar(
            select(func.count(Benchmark.id)).where(
                func.date(Benchmark.executed_at) == today
            )
        ) or 0
        
        # Missions started today
        missions_today = await session.scalar(
            select(func.count(Mission.id)).where(
                func.date(Mission.started_at) == today
            )
        ) or 0
        
        # Snapshots created today
        snapshots_today = await session.scalar(
            select(func.count(SafeHoldSnapshot.id)).where(
                func.date(SafeHoldSnapshot.created_at) == today
            )
        ) or 0
        
        summary = {
            "date": today.isoformat(),
            "contracts_created": contracts_today,
            "benchmarks_run": benchmarks_today,
            "missions_started": missions_today,
            "snapshots_created": snapshots_today,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await immutable_log.append(
            actor="data_aggregation",
            action="daily_summary_created",
            resource=f"summary_{today.isoformat()}",
            subsystem="analytics",
            payload=summary,
            result="completed"
        )
        
        return summary


# Global singleton
data_aggregation = DataAggregationService()
