"""
Metrics Snapshot Aggregator - Creates time-window aggregations
Consumes MetricEvents and produces MetricsSnapshots for dashboards
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import logging

from .telemetry_schemas import (
    MetricEvent, MetricsSnapshot, MetricStats, 
    MetricBandCounts, DerivedAction, MetricBand
)
from .trigger_mesh import trigger_mesh
from .models import async_session
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from .base_models import Base

logger = logging.getLogger(__name__)


class MetricsSnapshotTable(Base):
    """Persistent storage for metrics snapshots"""
    __tablename__ = "metrics_snapshots"
    
    id = Column(Integer, primary_key=True)
    snapshot_id = Column(String(256), unique=True, nullable=False, index=True)
    metric_id = Column(String(128), nullable=False, index=True)
    resource_scope = Column(String(64), nullable=False)
    resource_id = Column(String(128), nullable=False)
    
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Statistics
    stats_json = Column(JSON, nullable=False)  # MetricStats
    bands_json = Column(JSON, nullable=False)  # MetricBandCounts
    latest_band = Column(String(32), nullable=False, index=True)
    
    # Actions
    derived_actions_json = Column(JSON)  # List[DerivedAction]
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MetricsSnapshotAggregator:
    """
    Aggregates metrics over time windows
    
    Subscribes to metrics.* events from trigger mesh
    Creates periodic snapshots for dashboards and anomaly detection
    """
    
    def __init__(self, window_minutes: int = 5):
        self.window_minutes = window_minutes
        self.running = False
        self.aggregation_task: Optional[asyncio.Task] = None
        
        # In-memory buffer for current window
        self.current_window: Dict[str, List[MetricEvent]] = defaultdict(list)
        self.window_start: Optional[datetime] = None
    
    async def start(self):
        """Start snapshot aggregation"""
        if self.running:
            return
        
        # Subscribe to all metrics events
        trigger_mesh.subscribe("metrics.*", self._handle_metric_event)
        
        self.running = True
        self.window_start = datetime.now(timezone.utc)
        self.aggregation_task = asyncio.create_task(self._aggregation_loop())
        
        logger.info(f"[METRICS-SNAPSHOT] ✅ Aggregator started ({self.window_minutes}min windows)")
    
    async def stop(self):
        """Stop aggregation"""
        self.running = False
        if self.aggregation_task:
            self.aggregation_task.cancel()
            try:
                await self.aggregation_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[METRICS-SNAPSHOT] Aggregator stopped")
    
    async def _handle_metric_event(self, event: Any):
        """Handle incoming metric event"""
        try:
            # Buffer event for current window
            metric_id = event.payload.get("metric_id")
            if metric_id:
                # Store simplified version
                self.current_window[metric_id].append({
                    "value": event.payload.get("value"),
                    "band": event.payload.get("computed_band"),
                    "resource_id": event.resource,
                    "resource_scope": event.subsystem,
                    "timestamp": event.timestamp
                })
        except Exception as e:
            logger.error(f"[METRICS-SNAPSHOT] Error buffering event: {e}")
    
    async def _aggregation_loop(self):
        """Periodically aggregate buffered metrics"""
        while self.running:
            try:
                # Wait for window duration
                await asyncio.sleep(self.window_minutes * 60)
                
                # Aggregate current window
                await self._aggregate_window()
                
                # Start new window
                self.current_window.clear()
                self.window_start = datetime.now(timezone.utc)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[METRICS-SNAPSHOT] Aggregation error: {e}")
                await asyncio.sleep(60)
    
    async def _aggregate_window(self):
        """Aggregate buffered metrics and create snapshots"""
        window_end = datetime.now(timezone.utc)
        
        for metric_id, events in self.current_window.items():
            if not events:
                continue
            
            try:
                # Extract values and bands
                values = [e["value"] for e in events if e.get("value") is not None]
                bands = [e["band"] for e in events if e.get("band")]
                
                if not values:
                    continue
                
                # Compute statistics
                stats = MetricStats(
                    min=min(values),
                    max=max(values),
                    avg=sum(values) / len(values),
                    p95=self._percentile(values, 95) if len(values) > 1 else values[0],
                    sample_count=len(values)
                )
                
                # Count bands
                band_counts = MetricBandCounts(
                    good_samples=bands.count("good"),
                    warning_samples=bands.count("warning"),
                    critical_samples=bands.count("critical")
                )
                
                # Latest band
                latest_band = MetricBand(bands[-1]) if bands else MetricBand.GOOD
                
                # Derive actions if critical
                derived_actions = []
                if latest_band == MetricBand.CRITICAL:
                    # Get playbooks from catalog
                    from .metrics_collector import metrics_collector
                    catalog_entry = metrics_collector.catalog.get(metric_id)
                    
                    if catalog_entry and catalog_entry.playbooks:
                        for playbook_id in catalog_entry.playbooks:
                            derived_actions.append(DerivedAction(
                                action_type="playbook_recommendation",
                                playbook_id=playbook_id,
                                confidence=0.8,
                                reason=f"{metric_id} in critical band"
                            ))
                
                # Get resource info from first event
                resource_id = events[0].get("resource_id", "unknown")
                resource_scope = events[0].get("resource_scope", "subsystem")
                
                # Create snapshot
                snapshot = MetricsSnapshot(
                    snapshot_id=f"{resource_id}:{window_end.isoformat()}:{metric_id}",
                    metric_id=metric_id,
                    resource_scope=resource_scope,
                    resource_id=resource_id,
                    window_start=self.window_start,
                    window_end=window_end,
                    stats=stats,
                    bands=band_counts,
                    latest_band=latest_band,
                    derived_actions=derived_actions
                )
                
                # Persist to database
                await self._persist_snapshot(snapshot)
                
                # If critical with actions, publish to trigger mesh
                if derived_actions:
                    await self._publish_action_recommendations(snapshot)
            
            except Exception as e:
                logger.error(f"[METRICS-SNAPSHOT] Error aggregating {metric_id}: {e}")
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    async def _persist_snapshot(self, snapshot: MetricsSnapshot):
        """Save snapshot to database"""
        try:
            async with async_session() as session:
                db_snapshot = MetricsSnapshotTable(
                    snapshot_id=snapshot.snapshot_id,
                    metric_id=snapshot.metric_id,
                    resource_scope=snapshot.resource_scope,
                    resource_id=snapshot.resource_id,
                    window_start=snapshot.window_start,
                    window_end=snapshot.window_end,
                    stats_json=snapshot.stats.model_dump(),
                    bands_json=snapshot.bands.model_dump(),
                    latest_band=snapshot.latest_band.value,
                    derived_actions_json=[a.model_dump() for a in snapshot.derived_actions]
                )
                
                session.add(db_snapshot)
                await session.commit()
                
                logger.info(f"[METRICS-SNAPSHOT] Saved {snapshot.metric_id} snapshot: {snapshot.latest_band.value}")
        
        except Exception as e:
            logger.error(f"[METRICS-SNAPSHOT] Error persisting snapshot: {e}")
    
    async def _publish_action_recommendations(self, snapshot: MetricsSnapshot):
        """Publish action recommendations to proactive intelligence"""
        for action in snapshot.derived_actions:
            if action.playbook_id:
                # Publish to trigger mesh for proactive intelligence to consume
                await trigger_mesh.publish(TriggerEvent(
                    event_type="metrics.action_recommended",
                    source="metrics_snapshot_aggregator",
                    actor="metrics_system",
                    resource=snapshot.resource_id,
                    subsystem="proactive_intelligence",
                    payload={
                        "metric_id": snapshot.metric_id,
                        "playbook_id": action.playbook_id,
                        "confidence": action.confidence,
                        "reason": action.reason,
                        "metric_value": snapshot.stats.avg,
                        "band": snapshot.latest_band.value
                    }
                ))
                
                logger.warning(
                    f"[METRICS-SNAPSHOT] 🎯 Recommending playbook '{action.playbook_id}' "
                    f"for {snapshot.metric_id} ({snapshot.latest_band.value})"
                )


# Global instance
snapshot_aggregator = MetricsSnapshotAggregator(window_minutes=5)
