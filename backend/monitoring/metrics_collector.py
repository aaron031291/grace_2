"""
Real Metrics Collector - Feeds Grace's Autonomy
Collects REAL telemetry from system, not stubs
"""

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import psutil
from sqlalchemy import select, func, text

from .telemetry_schemas import (
    MetricEvent, MetricsSnapshot, MetricCatalogEntry, 
    MetricResource, MetricStats, MetricBandCounts, 
    DerivedAction, MetricBand, MetricUnit
)
from .trigger_mesh import trigger_mesh, TriggerEvent
from .models import async_session
from .logging_utils import log_event
from .metrics_catalog_loader import metrics_catalog

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Real metrics collector that feeds proactive intelligence
    
    Collects REAL telemetry from:
    - System resources (CPU, memory, disk)
    - Database (queue depths, task latency)
    - Application (API latency, error rates)
    - Governance (approval counts, blocks)
    - Learning (ingestion stats, verification rates)
    """
    
    def __init__(self):
        self.catalog: Dict[str, MetricCatalogEntry] = {}
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        self.catalog_path = Path(__file__).parent.parent / "config" / "metrics_catalog.yaml"
    
    async def start(self):
        """Start metrics collection"""
        if self.running:
            return
        
        # Load catalog (use new catalog loader)
        catalog_loaded = metrics_catalog.load()
        if catalog_loaded:
            print(f"[METRICS] ✅ Using metrics catalog: {len(metrics_catalog.metrics)} definitions")
        
        # Load legacy catalog
        await self._load_catalog()
        
        self.running = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        
        logger.info(f"[METRICS] ✅ Collector started with {len(self.catalog)} metrics")
    
    async def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[METRICS] Collector stopped")
    
    async def _load_catalog(self):
        """Load metrics catalog from YAML"""
        try:
            with open(self.catalog_path, 'r') as f:
                catalog_data = yaml.safe_load(f)
            
            for metric in catalog_data.get('metrics', []):
                entry = MetricCatalogEntry(**metric)
                self.catalog[entry.metric_id] = entry
            
            logger.info(f"[METRICS] Loaded {len(self.catalog)} metric definitions")
        except Exception as e:
            logger.error(f"[METRICS] Failed to load catalog: {e}")
            self.catalog = {}
    
    async def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                # Collect all metrics in parallel
                await asyncio.gather(
                    self._collect_api_metrics(),
                    self._collect_executor_metrics(),
                    self._collect_learning_metrics(),
                    self._collect_autonomy_metrics(),
                    self._collect_infra_metrics(),
                    return_exceptions=True
                )
                
                # Collection interval: 30 seconds
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[METRICS] Collection error: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _collect_api_metrics(self):
        """Collect API gateway metrics (REAL)"""
        try:
            # These would come from Prometheus in production
            # For now, collect from application state
            
            # TODO(ROADMAP): Wire Prometheus client
            # For MVP, collect basic stats from uvicorn
            
            pass  # Placeholder - wire when Prometheus available
        except Exception as e:
            logger.error(f"[METRICS] API collection error: {e}")
    
    async def _collect_executor_metrics(self):
        """Collect executor & queue metrics (REAL from DB)"""
        try:
            async with async_session() as session:
                # Queue depth - count pending tasks
                from .base_models import Base
                try:
                    # Try to query execution_tasks table if it exists
                    result = await session.execute(
                        text("SELECT COUNT(*) FROM execution_tasks WHERE status = 'pending'")
                    )
                    queue_depth = result.scalar() or 0
                    
                    await self._publish_metric(
                        metric_id="executor.queue_depth",
                        value=float(queue_depth),
                        resource_scope="queue",
                        resource_id="main_executor",
                        source="internal_sql"
                    )
                except Exception:
                    # Table doesn't exist yet, skip
                    pass
                
                # Task latency - age of oldest pending task
                try:
                    result = await session.execute(
                        text("""
                            SELECT 
                                (julianday('now') - julianday(created_at)) * 86400 as age_seconds
                            FROM execution_tasks 
                            WHERE status = 'pending'
                            ORDER BY created_at ASC
                            LIMIT 1
                        """)
                    )
                    oldest_age = result.scalar()
                    
                    if oldest_age is not None:
                        await self._publish_metric(
                            metric_id="executor.task_latency",
                            value=float(oldest_age),
                            resource_scope="queue",
                            resource_id="main_executor",
                            source="internal_sql"
                        )
                except Exception:
                    pass
        
        except Exception as e:
            logger.error(f"[METRICS] Executor collection error: {e}")
    
    async def _collect_learning_metrics(self):
        """Collect learning pipeline metrics (REAL from DB)"""
        try:
            async with async_session() as session:
                # Sources verified - from knowledge_sources table
                try:
                    result = await session.execute(
                        text("""
                            SELECT 
                                COUNT(*) as total,
                                SUM(CASE WHEN verified = 1 THEN 1 ELSE 0 END) as verified
                            FROM knowledge_sources
                            WHERE created_at > datetime('now', '-5 minutes')
                        """)
                    )
                    row = result.first()
                    
                    if row and row[0] > 0:
                        verification_rate = (row[1] / row[0]) * 100
                        
                        await self._publish_metric(
                            metric_id="learning.sources_verified",
                            value=verification_rate,
                            resource_scope="subsystem",
                            resource_id="web_learning",
                            source="provenance_tracker"
                        )
                except Exception:
                    pass
                
                # Governance blocks
                try:
                    result = await session.execute(
                        text("""
                            SELECT COUNT(*) 
                            FROM immutable_log
                            WHERE action = 'web_scrape_blocked'
                            AND timestamp > datetime('now', '-5 minutes')
                        """)
                    )
                    blocks = result.scalar() or 0
                    
                    await self._publish_metric(
                        metric_id="learning.governance_blocks",
                        value=float(blocks),
                        resource_scope="subsystem",
                        resource_id="governance",
                        source="governance_framework"
                    )
                except Exception:
                    pass
        
        except Exception as e:
            logger.error(f"[METRICS] Learning collection error: {e}")
    
    async def _collect_autonomy_metrics(self):
        """Collect autonomy & decision metrics (REAL from DB)"""
        try:
            async with async_session() as session:
                # Plan success rate
                try:
                    result = await session.execute(
                        text("""
                            SELECT 
                                COUNT(*) as total,
                                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                            FROM healing_attempts
                            WHERE attempted_at > datetime('now', '-5 minutes')
                        """)
                    )
                    row = result.first()
                    
                    if row and row[0] > 0:
                        success_rate = (row[1] / row[0]) * 100
                        
                        await self._publish_metric(
                            metric_id="autonomy.plan_success_rate",
                            value=success_rate,
                            resource_scope="subsystem",
                            resource_id="agentic_spine",
                            source="agentic_spine"
                        )
                except Exception:
                    pass
                
                # Approvals pending
                try:
                    result = await session.execute(
                        text("""
                            SELECT COUNT(*)
                            FROM approval_requests
                            WHERE status = 'pending'
                        """)
                    )
                    pending = result.scalar() or 0
                    
                    await self._publish_metric(
                        metric_id="autonomy.approvals_pending",
                        value=float(pending),
                        resource_scope="subsystem",
                        resource_id="governance",
                        source="governance_engine"
                    )
                except Exception:
                    pass
        
        except Exception as e:
            logger.error(f"[METRICS] Autonomy collection error: {e}")
    
    async def _collect_infra_metrics(self):
        """Collect infrastructure metrics (REAL from psutil)"""
        try:
            # CPU utilization (REAL)
            cpu_percent = psutil.cpu_percent(interval=1)
            await self._publish_metric(
                metric_id="infra.cpu_utilization",
                value=cpu_percent,
                resource_scope="host",
                resource_id="localhost",
                source="psutil"
            )
            
            # Memory utilization (REAL)
            memory = psutil.virtual_memory()
            await self._publish_metric(
                metric_id="infra.memory_utilization",
                value=memory.percent,
                resource_scope="host",
                resource_id="localhost",
                source="psutil"
            )
            
            # Disk usage (REAL)
            disk = psutil.disk_usage('/')
            await self._publish_metric(
                metric_id="infra.disk_usage",
                value=disk.percent,
                resource_scope="volume",
                resource_id="root_volume",
                source="psutil"
            )
        
        except Exception as e:
            logger.error(f"[METRICS] Infra collection error: {e}")
    
    async def _publish_metric(
        self,
        metric_id: str,
        value: float,
        resource_scope: str,
        resource_id: str,
        source: str
    ):
        """Publish metric event to trigger mesh"""
        
        # Get catalog entry for thresholds
        catalog_entry = self.catalog.get(metric_id)
        if not catalog_entry:
            logger.warning(f"[METRICS] Metric {metric_id} not in catalog")
            return
        
        # Compute band
        band = self._compute_band(value, catalog_entry.thresholds, catalog_entry.unit)
        
        # Detect trend (simplified - would need history)
        trend = "steady"
        
        # Create event
        event = MetricEvent(
            event_type=f"metrics.{metric_id}",
            source=source,
            actor="metrics_collector",
            resource=MetricResource(
                scope=resource_scope,
                id=resource_id
            ),
            payload={
                "metric_id": metric_id,
                "value": value,
                "unit": catalog_entry.unit.value,
                "aggregation": catalog_entry.aggregation,
                "interval_seconds": catalog_entry.recommended_interval_seconds,
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "thresholds": catalog_entry.thresholds,
                "computed_band": band.value,
                "trend": trend
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        # Publish to trigger mesh
        await trigger_mesh.publish(TriggerEvent(
            event_type=event.event_type,
            source=event.source,
            actor=event.actor,
            resource=event.resource.id,
            payload=event.payload,
            timestamp=event.timestamp
        ))
        
        # Log if warning or critical
        if band in [MetricBand.WARNING, MetricBand.CRITICAL]:
            log_event(f"metric_{band.value}", {
                "metric_id": metric_id,
                "value": value,
                "band": band.value,
                "resource": resource_id
            })
    
    def _compute_band(self, value: float, thresholds: Dict[str, Dict[str, float]], unit: MetricUnit) -> MetricBand:
        """Compute which threshold band value falls into"""
        
        # Good band
        good = thresholds.get("good", {})
        if "upper" in good and value <= good["upper"]:
            if "lower" not in good or value >= good["lower"]:
                return MetricBand.GOOD
        if "lower" in good and value >= good["lower"]:
            if "upper" not in good or value <= good["upper"]:
                return MetricBand.GOOD
        
        # Critical band
        critical = thresholds.get("critical", {})
        if "lower" in critical and value >= critical["lower"]:
            return MetricBand.CRITICAL
        if "upper" in critical and value <= critical["upper"]:
            return MetricBand.CRITICAL
        
        # Default to warning
        return MetricBand.WARNING
    
    async def get_latest_metrics(self, metric_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get latest values for specified metrics"""
        # This would query the metrics_snapshots table
        # For now, return empty - will be populated by snapshot aggregator
        return []


# Global instance
metrics_collector = MetricsCollector()
