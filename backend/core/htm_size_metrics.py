"""
HTM Size Metrics Aggregator

Calculates and publishes data volume metrics:
- Total bytes processed
- Average/percentile sizes
- Throughput (bytes/sec, items/sec)
- Size distribution by task type
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import statistics

from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.core.message_bus import message_bus, MessagePriority
from backend.core.htm_size_tracker import format_bytes, classify_task_size, calculate_throughput
from sqlalchemy import select, and_


class HTMSizeMetricsAggregator:
    """
    Aggregates size-based metrics for HTM tasks
    
    Provides:
    - Data volume statistics
    - Throughput analysis  
    - Size distribution insights
    - Bandwidth utilization
    """
    
    def __init__(self):
        self.aggregation_interval_seconds = 300  # Aggregate every 5 min
        self.running = False
        self._task = None
        
        # Real-time stats
        self.stats = {
            "total_bytes_processed": 0,
            "total_items_processed": 0,
            "tasks_with_size_data": 0,
            "avg_task_size_bytes": 0,
            "total_throughput_bytes_per_sec": 0
        }
    
    async def start(self):
        """Start metrics aggregation loop"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._aggregation_loop())
        
        print("[HTM SIZE METRICS] Aggregator started")
    
    async def stop(self):
        """Stop aggregation loop"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("[HTM SIZE METRICS] Aggregator stopped")
    
    async def _aggregation_loop(self):
        """Main aggregation loop"""
        while self.running:
            try:
                await self._aggregate_metrics()
                await self._publish_stats()
                await asyncio.sleep(self.aggregation_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[HTM SIZE METRICS] Aggregation error: {e}")
                await asyncio.sleep(self.aggregation_interval_seconds)
    
    async def _aggregate_metrics(self):
        """Aggregate size metrics from completed tasks"""
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        async with async_session() as session:
            # Get completed tasks from last hour with size data
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status == 'completed')
                .where(HTMTask.finished_at >= one_hour_ago)
                .where(HTMTask.data_size_bytes.isnot(None))
            )
            tasks = result.scalars().all()
            
            if not tasks:
                return
            
            # Calculate aggregate stats
            total_bytes = sum(t.data_size_bytes for t in tasks if t.data_size_bytes)
            total_items = sum(t.input_count for t in tasks if t.input_count)
            
            sizes = [t.data_size_bytes for t in tasks if t.data_size_bytes]
            throughputs = [t.bytes_per_second for t in tasks if t.bytes_per_second]
            
            self.stats = {
                "total_bytes_processed": total_bytes,
                "total_items_processed": total_items or 0,
                "tasks_with_size_data": len(tasks),
                "avg_task_size_bytes": statistics.mean(sizes) if sizes else 0,
                "median_task_size_bytes": statistics.median(sizes) if sizes else 0,
                "p95_task_size_bytes": sorted(sizes)[int(len(sizes) * 0.95)] if sizes else 0,
                "p99_task_size_bytes": sorted(sizes)[int(len(sizes) * 0.99)] if sizes else 0,
                "min_task_size_bytes": min(sizes) if sizes else 0,
                "max_task_size_bytes": max(sizes) if sizes else 0,
                "avg_throughput_bytes_per_sec": statistics.mean(throughputs) if throughputs else 0,
                "p95_throughput_bytes_per_sec": sorted(throughputs)[int(len(throughputs) * 0.95)] if throughputs else 0,
                "total_data_processed_human": format_bytes(total_bytes),
                "avg_task_size_human": format_bytes(int(statistics.mean(sizes))) if sizes else "0 B",
                "p95_task_size_human": format_bytes(int(sorted(sizes)[int(len(sizes) * 0.95)])) if sizes else "0 B"
            }
            
            # Size distribution by task type
            by_type = defaultdict(list)
            for task in tasks:
                if task.data_size_bytes:
                    by_type[task.task_type].append(task.data_size_bytes)
            
            type_stats = {}
            for task_type, sizes_list in by_type.items():
                type_stats[task_type] = {
                    "count": len(sizes_list),
                    "total_bytes": sum(sizes_list),
                    "avg_bytes": statistics.mean(sizes_list),
                    "total_human": format_bytes(sum(sizes_list)),
                    "avg_human": format_bytes(int(statistics.mean(sizes_list)))
                }
            
            self.stats["by_task_type"] = type_stats
            
            # Size class distribution
            size_classes = defaultdict(int)
            for task in tasks:
                if task.data_size_bytes:
                    size_class = classify_task_size(task.data_size_bytes)
                    size_classes[size_class.value] += 1
            
            self.stats["size_distribution"] = dict(size_classes)
    
    async def _publish_stats(self):
        """Publish size metrics to message bus"""
        await message_bus.publish(
            source="htm_size_metrics",
            topic="htm.size.stats",
            payload=self.stats,
            priority=MessagePriority.LOW
        )
    
    async def get_size_analysis(
        self,
        task_type: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get detailed size analysis
        
        Args:
            task_type: Filter by specific task type
            hours: Hours of history to analyze
            
        Returns:
            Detailed size analysis with recommendations
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        async with async_session() as session:
            query = select(HTMTask).where(
                and_(
                    HTMTask.status == 'completed',
                    HTMTask.finished_at >= cutoff,
                    HTMTask.data_size_bytes.isnot(None)
                )
            )
            
            if task_type:
                query = query.where(HTMTask.task_type == task_type)
            
            result = await session.execute(query)
            tasks = result.scalars().all()
        
        if not tasks:
            return {"error": "No tasks with size data found"}
        
        # Calculate comprehensive stats
        sizes = [t.data_size_bytes for t in tasks if t.data_size_bytes]
        execution_times = [t.execution_time_ms for t in tasks if t.execution_time_ms]
        throughputs = []
        
        for task in tasks:
            if task.data_size_bytes and task.execution_time_ms and task.execution_time_ms > 0:
                throughput = calculate_throughput(task.data_size_bytes, task.execution_time_ms)
                throughputs.append(throughput)
        
        # Size statistics
        size_stats = {
            "count": len(tasks),
            "total_bytes": sum(sizes),
            "total_human": format_bytes(sum(sizes)),
            "mean_bytes": statistics.mean(sizes),
            "mean_human": format_bytes(int(statistics.mean(sizes))),
            "median_bytes": statistics.median(sizes),
            "median_human": format_bytes(int(statistics.median(sizes))),
            "stdev_bytes": statistics.stdev(sizes) if len(sizes) > 1 else 0,
            "min_bytes": min(sizes),
            "min_human": format_bytes(min(sizes)),
            "max_bytes": max(sizes),
            "max_human": format_bytes(max(sizes)),
            "p25_bytes": sorted(sizes)[len(sizes) // 4],
            "p50_bytes": sorted(sizes)[len(sizes) // 2],
            "p75_bytes": sorted(sizes)[int(len(sizes) * 0.75)],
            "p95_bytes": sorted(sizes)[int(len(sizes) * 0.95)],
            "p99_bytes": sorted(sizes)[int(len(sizes) * 0.99)]
        }
        
        # Throughput statistics
        throughput_stats = {}
        if throughputs:
            throughput_stats = {
                "mean_bytes_per_sec": statistics.mean(throughputs),
                "mean_human": f"{format_bytes(int(statistics.mean(throughputs)))}/s",
                "median_bytes_per_sec": statistics.median(throughputs),
                "median_human": f"{format_bytes(int(statistics.median(throughputs)))}/s",
                "p95_bytes_per_sec": sorted(throughputs)[int(len(throughputs) * 0.95)],
                "p95_human": f"{format_bytes(int(sorted(throughputs)[int(len(throughputs) * 0.95)]))}/s",
                "min_bytes_per_sec": min(throughputs),
                "max_bytes_per_sec": max(throughputs)
            }
        
        # Time vs size correlation
        correlation_data = []
        for task in tasks:
            if task.data_size_bytes and task.execution_time_ms:
                correlation_data.append({
                    "size_bytes": task.data_size_bytes,
                    "execution_ms": task.execution_time_ms,
                    "size_class": classify_task_size(task.data_size_bytes).value
                })
        
        # Size class distribution
        size_dist = defaultdict(int)
        for task in tasks:
            if task.data_size_bytes:
                size_class = classify_task_size(task.data_size_bytes)
                size_dist[size_class.value] += 1
        
        # Recommendations
        recommendations = []
        
        # Check for outliers
        if size_stats["max_bytes"] > size_stats["mean_bytes"] * 10:
            recommendations.append({
                "type": "outlier_detected",
                "message": f"Large size outlier detected: {format_bytes(size_stats['max_bytes'])} vs avg {format_bytes(int(size_stats['mean_bytes']))}",
                "suggestion": "Consider splitting large tasks or implementing streaming"
            })
        
        # Check throughput
        if throughput_stats and throughput_stats["mean_bytes_per_sec"] < 1024 * 1024:  # < 1 MB/s
            recommendations.append({
                "type": "low_throughput",
                "message": f"Low average throughput: {throughput_stats['mean_human']}",
                "suggestion": "Investigate bottlenecks in processing pipeline"
            })
        
        # Check size variance
        if size_stats["stdev_bytes"] > size_stats["mean_bytes"]:
            recommendations.append({
                "type": "high_variance",
                "message": "High variance in task sizes detected",
                "suggestion": "Consider size-based queue routing"
            })
        
        return {
            "analysis_period_hours": hours,
            "task_type": task_type or "all",
            "size_statistics": size_stats,
            "throughput_statistics": throughput_stats,
            "size_distribution": dict(size_dist),
            "correlation_samples": correlation_data[:20],  # First 20 for visualization
            "recommendations": recommendations
        }
    
    async def get_heavy_tasks(
        self,
        min_size_bytes: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get heaviest tasks by data volume
        
        Args:
            min_size_bytes: Minimum size threshold
            limit: Max results
            
        Returns:
            List of heavy tasks with details
        """
        async with async_session() as session:
            query = select(HTMTask).where(
                HTMTask.data_size_bytes.isnot(None)
            ).order_by(HTMTask.data_size_bytes.desc()).limit(limit)
            
            if min_size_bytes:
                query = query.where(HTMTask.data_size_bytes >= min_size_bytes)
            
            result = await session.execute(query)
            tasks = result.scalars().all()
        
        return [
            {
                "task_id": t.task_id,
                "task_type": t.task_type,
                "data_size_bytes": t.data_size_bytes,
                "data_size_human": format_bytes(t.data_size_bytes),
                "size_class": classify_task_size(t.data_size_bytes).value,
                "input_count": t.input_count,
                "execution_time_ms": t.execution_time_ms,
                "bytes_per_second": t.bytes_per_second,
                "throughput_human": f"{format_bytes(int(t.bytes_per_second))}/s" if t.bytes_per_second else None,
                "status": t.status,
                "finished_at": t.finished_at.isoformat() if t.finished_at else None
            }
            for t in tasks
        ]


# Global instance
htm_size_metrics = HTMSizeMetricsAggregator()
