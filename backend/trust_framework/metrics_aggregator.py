"""
Metrics Aggregation System - PRODUCTION
Collects, aggregates, and analyzes metrics from all TRUST framework systems

Provides:
- Time-series data for trending
- Aggregated statistics
- Cross-system correlation
- Capacity planning insights
"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    
    metric_name: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'metric': self.metric_name,
            'value': self.value,
            'tags': self.tags,
            'timestamp': self.timestamp
        }


@dataclass
class AggregatedMetric:
    """Aggregated metric with statistics"""
    
    metric_name: str
    
    # Statistics
    count: int
    sum: float
    mean: float
    min: float
    max: float
    stddev: float
    
    # Percentiles
    p50: float
    p95: float
    p99: float
    
    # Time range
    start_time: float
    end_time: float
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'metric': self.metric_name,
            'statistics': {
                'count': self.count,
                'sum': self.sum,
                'mean': self.mean,
                'min': self.min,
                'max': self.max,
                'stddev': self.stddev
            },
            'percentiles': {
                'p50': self.p50,
                'p95': self.p95,
                'p99': self.p99
            },
            'time_range': {
                'start': self.start_time,
                'end': self.end_time,
                'duration_seconds': self.end_time - self.start_time
            },
            'tags': self.tags
        }


class MetricsCollector:
    """
    Collects metrics from all TRUST framework systems
    
    Metrics collected:
    - Model health (perplexity, entropy, latency)
    - HTM anomaly scores
    - Verification pass rates
    - Hallucination counts
    - Data hygiene pass rates
    - Guardrail triggers
    - System performance
    """
    
    def __init__(
        self,
        storage_path: str = "databases/metrics",
        retention_days: int = 30
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.retention_days = retention_days
        
        # Time-series storage (in-memory for speed)
        self.metrics: Dict[str, deque] = {}  # metric_name -> deque of DataPoints
        self.max_points_per_metric = 10000
        
        # Running state
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.total_metrics_collected = 0
        self.collection_cycles = 0
        
        logger.info("[METRICS] Collector initialized")
    
    async def start(self, interval_seconds: int = 60):
        """Start metrics collection"""
        
        if self.running:
            return
        
        self.running = True
        self.collection_task = asyncio.create_task(self._collection_loop(interval_seconds))
        
        logger.info(f"[METRICS] Collection started (interval: {interval_seconds}s)")
    
    async def stop(self):
        """Stop metrics collection"""
        
        if not self.running:
            return
        
        self.running = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[METRICS] Collection stopped")
    
    async def _collection_loop(self, interval: int):
        """Main collection loop"""
        
        while self.running:
            try:
                await self._collect_all_metrics()
                self.collection_cycles += 1
                
                # Persist periodically
                if self.collection_cycles % 10 == 0:
                    await self._persist_metrics()
                
                await asyncio.sleep(interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[METRICS] Collection error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_all_metrics(self):
        """Collect metrics from all systems"""
        
        # Collect from each system
        await self._collect_model_health_metrics()
        await self._collect_htm_metrics()
        await self._collect_verification_metrics()
        await self._collect_hallucination_metrics()
        await self._collect_data_hygiene_metrics()
        await self._collect_system_metrics()
    
    async def _collect_model_health_metrics(self):
        """Collect model health metrics"""
        
        from .model_health_telemetry import model_health_registry
        
        snapshots = model_health_registry.get_all_snapshots()
        
        for model_name, snapshot in snapshots.items():
            snapshot_dict = snapshot.to_dict()
            
            # Perplexity
            self.record_metric(
                "model.perplexity",
                snapshot_dict['metrics']['avg_perplexity'],
                {'model': model_name}
            )
            
            # Entropy
            self.record_metric(
                "model.entropy",
                snapshot_dict['metrics']['avg_entropy'],
                {'model': model_name}
            )
            
            # Latency
            self.record_metric(
                "model.latency_ms",
                snapshot_dict['metrics']['avg_latency_ms'],
                {'model': model_name}
            )
            
            # Health score (numeric)
            health_scores = {
                'healthy': 1.0,
                'degraded': 0.7,
                'grey_zone': 0.4,
                'critical': 0.2,
                'quarantined': 0.0
            }
            
            health_score = health_scores.get(snapshot_dict['status'], 0.5)
            self.record_metric(
                "model.health_score",
                health_score,
                {'model': model_name}
            )
    
    async def _collect_htm_metrics(self):
        """Collect HTM anomaly detection metrics"""
        
        from .htm_anomaly_detector import htm_detector_pool
        
        all_stats = htm_detector_pool.get_all_stats()
        
        for model_name, stats in all_stats.items():
            # Anomaly rate
            self.record_metric(
                "htm.anomaly_rate",
                stats.get('anomaly_rate', 0.0),
                {'model': model_name}
            )
            
            # Total sequences
            self.record_metric(
                "htm.sequences_analyzed",
                float(stats.get('total_sequences', 0)),
                {'model': model_name}
            )
    
    async def _collect_verification_metrics(self):
        """Collect verification mesh metrics"""
        
        from .verification_mesh import verification_mesh
        
        stats = verification_mesh.get_stats()
        
        # Pass rate
        self.record_metric(
            "verification.pass_rate",
            stats.get('pass_rate', 0.0),
            {}
        )
        
        # Total verifications
        self.record_metric(
            "verification.total",
            float(stats.get('total_verifications', 0)),
            {}
        )
    
    async def _collect_hallucination_metrics(self):
        """Collect hallucination tracking metrics"""
        
        from .hallucination_ledger import hallucination_ledger
        
        summary = hallucination_ledger.get_ledger_summary()
        
        # Total hallucinations
        self.record_metric(
            "hallucinations.total",
            float(summary.get('total_hallucinations', 0)),
            {}
        )
        
        # Models needing retraining
        self.record_metric(
            "hallucinations.models_need_retraining",
            float(len(summary.get('models_needing_retraining', []))),
            {}
        )
    
    async def _collect_data_hygiene_metrics(self):
        """Collect data hygiene metrics"""
        
        from .data_hygiene_pipeline import data_hygiene_pipeline
        
        stats = data_hygiene_pipeline.get_stats()
        
        # Pass rate
        self.record_metric(
            "data_hygiene.pass_rate",
            stats.get('pass_rate', 0.0),
            {}
        )
        
        # Quarantined items
        self.record_metric(
            "data_hygiene.quarantined",
            float(stats.get('quarantined', 0)),
            {}
        )
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        
        import psutil
        
        # CPU
        self.record_metric("system.cpu_percent", psutil.cpu_percent(), {})
        
        # Memory
        mem = psutil.virtual_memory()
        self.record_metric("system.memory_percent", mem.percent, {})
        self.record_metric("system.memory_mb", mem.used / 1024 / 1024, {})
        
        # Disk
        disk = psutil.disk_usage('/')
        self.record_metric("system.disk_percent", disk.percent, {})
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """Record a metric data point"""
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque(maxlen=self.max_points_per_metric)
        
        data_point = MetricDataPoint(
            metric_name=metric_name,
            value=value,
            tags=tags or {}
        )
        
        self.metrics[metric_name].append(data_point)
        self.total_metrics_collected += 1
    
    def query(
        self,
        metric_name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[MetricDataPoint]:
        """Query metrics"""
        
        if metric_name not in self.metrics:
            return []
        
        points = list(self.metrics[metric_name])
        
        # Filter by time range
        if start_time:
            points = [p for p in points if p.timestamp >= start_time]
        
        if end_time:
            points = [p for p in points if p.timestamp <= end_time]
        
        # Filter by tags
        if tags:
            points = [
                p for p in points
                if all(p.tags.get(k) == v for k, v in tags.items())
            ]
        
        return points
    
    def aggregate(
        self,
        metric_name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[AggregatedMetric]:
        """Aggregate metrics over time range"""
        
        points = self.query(metric_name, start_time, end_time, tags)
        
        if not points:
            return None
        
        values = [p.value for p in points]
        
        return AggregatedMetric(
            metric_name=metric_name,
            count=len(values),
            sum=float(np.sum(values)),
            mean=float(np.mean(values)),
            min=float(np.min(values)),
            max=float(np.max(values)),
            stddev=float(np.std(values)),
            p50=float(np.percentile(values, 50)),
            p95=float(np.percentile(values, 95)),
            p99=float(np.percentile(values, 99)),
            start_time=points[0].timestamp,
            end_time=points[-1].timestamp,
            tags=tags or {}
        )
    
    async def _persist_metrics(self):
        """Persist metrics to disk"""
        
        metrics_file = self.storage_path / f"metrics_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        
        try:
            # Append new metrics
            with open(metrics_file, 'a') as f:
                for metric_name, points in self.metrics.items():
                    # Only persist recent points (last collection cycle)
                    recent = [p for p in points if time.time() - p.timestamp < 120]
                    
                    for point in recent:
                        f.write(json.dumps(point.to_dict()) + '\n')
            
            logger.debug(f"[METRICS] Persisted to {metrics_file}")
        
        except Exception as e:
            logger.error(f"[METRICS] Failed to persist: {e}")
    
    def get_stats(self) -> Dict:
        """Get collector statistics"""
        
        return {
            'total_metrics_collected': self.total_metrics_collected,
            'collection_cycles': self.collection_cycles,
            'unique_metrics': len(self.metrics),
            'total_data_points': sum(len(points) for points in self.metrics.values()),
            'running': self.running
        }


# Global collector
metrics_collector = MetricsCollector()
