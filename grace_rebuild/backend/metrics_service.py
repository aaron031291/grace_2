"""
Central Metrics Service
Collects KPIs from all 10 domains and feeds cognition dashboard
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class MetricEvent:
    """Single metric event"""
    domain: str
    kpi: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]


class MetricsCollector:
    """
    Central metrics collector for all Grace domains
    
    Domains publish metrics here, cognition system aggregates them
    """
    
    def __init__(self, db_session=None):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.aggregates: Dict[str, Dict[str, float]] = {}
        self.subscribers: List[callable] = []
        self._lock = threading.Lock()
        self.db_session = db_session
        self.persist_enabled = db_session is not None
        
        # Domain KPI definitions
        self.domain_kpis = {
            "core": ["uptime", "governance_score", "healing_actions", "verification_failures", "event_bus_latency"],
            "transcendence": ["task_success", "code_quality", "memory_recall", "planning_accuracy", "architecture_score"],
            "knowledge": ["trust_score", "ingestion_rate", "recall_accuracy", "source_diversity", "knowledge_freshness"],
            "security": ["threats_detected", "scan_coverage", "response_time", "false_positive_rate", "auto_fix_success"],
            "ml": ["model_accuracy", "deployment_success", "inference_latency", "training_efficiency", "auto_retrain_triggers"],
            "temporal": ["prediction_accuracy", "graph_completeness", "sim_quality", "event_latency", "impact_precision"],
            "parliament": ["vote_participation", "recommendation_adoption", "compliance_score", "reflection_quality", "meta_convergence"],
            "federation": ["connector_health", "api_success", "secret_rotation", "plugin_uptime", "sandbox_isolation"],
            "cognition": ["overall_health", "overall_trust", "overall_confidence", "benchmark_progress", "saas_readiness"],
            "speech": ["recognition_accuracy", "synthesis_quality", "command_success", "latency", "multi_modal_integration"]
        }
    
    async def publish(self, domain: str, kpi: str, value: float, metadata: Dict[str, Any] = None):
        """
        Publish a metric from a domain
        
        Args:
            domain: Domain name (e.g., "transcendence", "ml")
            kpi: KPI name (e.g., "task_success", "model_accuracy")
            value: Metric value (0.0 to 1.0 for percentages, any float for counts)
            metadata: Optional metadata (task_id, model_id, etc.)
        """
        try:
            metric_key = f"{domain}.{kpi}"
            
            event = MetricEvent(
                domain=domain,
                kpi=kpi,
                value=value,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            with self._lock:
                self.metrics[metric_key].append(event)
            
            # Don't let persistence failures break the app
            try:
                await self._persist_metric(event)
            except Exception as persist_error:
                logger.warning(f"Metric persistence failed (continuing): {persist_error}")
            
            await self._update_aggregates(domain, kpi)
            await self._notify_subscribers(event)
        except Exception as e:
            logger.error(f"Error publishing metric {domain}.{kpi}: {e}", exc_info=True)
            # Don't re-raise - metric failures shouldn't break the application
    
    async def _persist_metric(self, event: MetricEvent):
        """Persist metric to database if enabled"""
        if not self.persist_enabled or not self.db_session:
            return
        
        try:
            from .metrics_models import MetricEvent as MetricEventDB
            
            db_event = MetricEventDB(
                domain=event.domain,
                kpi=event.kpi,
                value=event.value,
                timestamp=event.timestamp,
                metadata=event.metadata
            )
            
            self.db_session.add(db_event)
            await self.db_session.commit()
        except ImportError as e:
            logger.warning(f"Could not import metrics models (circular import?): {e}")
        except Exception as e:
            logger.error(f"Failed to persist metric: {e}", exc_info=True)
    
    async def _update_aggregates(self, domain: str, kpi: str):
        """Update aggregated metrics"""
        metric_key = f"{domain}.{kpi}"
        events = self.metrics[metric_key]
        
        if not events:
            return
        
        recent_events = [e for e in events if e.timestamp > datetime.now() - timedelta(hours=1)]
        
        if recent_events:
            avg_value = sum(e.value for e in recent_events) / len(recent_events)
            
            if domain not in self.aggregates:
                self.aggregates[domain] = {}
            
            self.aggregates[domain][kpi] = avg_value
    
    async def _notify_subscribers(self, event: MetricEvent):
        """Notify metric subscribers"""
        for subscriber in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                print(f"Subscriber error: {e}")
    
    def subscribe(self, callback: callable):
        """Subscribe to metric events"""
        self.subscribers.append(callback)
    
    def get_domain_kpis(self, domain: str) -> Dict[str, float]:
        """Get current KPIs for a domain"""
        return self.aggregates.get(domain, {})
    
    def get_domain_health(self, domain: str) -> float:
        """Calculate domain health score"""
        kpis = self.get_domain_kpis(domain)
        
        if not kpis:
            return 0.0
        
        percentage_kpis = [v for k, v in kpis.items() if v <= 1.0 and "_rate" not in k and "success" in k or "accuracy" in k or "score" in k]
        
        if not percentage_kpis:
            return 0.8
        
        return sum(percentage_kpis) / len(percentage_kpis)
    
    def get_metric_history(self, domain: str, kpi: str, hours: int = 24) -> List[MetricEvent]:
        """Get metric history for a specific KPI"""
        metric_key = f"{domain}.{kpi}"
        cutoff = datetime.now() - timedelta(hours=hours)
        
        return [e for e in self.metrics[metric_key] if e.timestamp > cutoff]
    
    def get_all_domains_status(self) -> Dict[str, Any]:
        """Get status for all domains"""
        status = {}
        
        for domain in self.domain_kpis.keys():
            kpis = self.get_domain_kpis(domain)
            health = self.get_domain_health(domain)
            
            status[domain] = {
                "health": health,
                "trust": health * 0.95,
                "confidence": health * 0.92,
                "kpis": kpis,
                "last_updated": datetime.now().isoformat()
            }
        
        return status


_global_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _global_metrics_collector
    
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    
    return _global_metrics_collector


async def publish_metric(domain: str, kpi: str, value: float, metadata: Dict[str, Any] = None):
    """
    Convenience function to publish a metric
    
    Usage in any domain:
        from backend.metrics_service import publish_metric
        
        await publish_metric("transcendence", "task_success", 1.0, {"task_id": "123"})
    """
    collector = get_metrics_collector()
    await collector.publish(domain, kpi, value, metadata)


async def publish_batch(domain: str, kpis: Dict[str, float], metadata: Dict[str, Any] = None):
    """
    Publish multiple KPIs at once
    
    Usage:
        await publish_batch("ml", {
            "model_accuracy": 0.94,
            "deployment_success": 1.0,
            "inference_latency": 0.032
        })
    """
    collector = get_metrics_collector()
    
    for kpi, value in kpis.items():
        await collector.publish(domain, kpi, value, metadata)


class MetricPublisherMixin:
    """
    Mixin for classes that publish metrics
    
    Usage:
        class MyService(MetricPublisherMixin):
            domain = "transcendence"
            
            async def do_work(self):
                result = await some_task()
                await self.publish_success(result.success)
    """
    domain: str = "unknown"
    
    async def publish_metric(self, kpi: str, value: float, metadata: Dict[str, Any] = None):
        """Publish a metric for this service's domain"""
        await publish_metric(self.domain, kpi, value, metadata)
    
    async def publish_success(self, success: bool, kpi: str = "task_success", metadata: Dict[str, Any] = None):
        """Publish a success/failure metric"""
        await self.publish_metric(kpi, 1.0 if success else 0.0, metadata)
    
    async def publish_quality(self, score: float, kpi: str = "quality_score", metadata: Dict[str, Any] = None):
        """Publish a quality score (0.0 to 1.0)"""
        await self.publish_metric(kpi, max(0.0, min(1.0, score)), metadata)
    
    async def publish_count(self, count: int, kpi: str, metadata: Dict[str, Any] = None):
        """Publish a count metric"""
        await self.publish_metric(kpi, float(count), metadata)


# Integration with cognition metrics engine
async def sync_to_cognition_engine(db):
    """
    Sync metrics to the cognition metrics engine
    Called periodically to update rolling benchmarks
    """
    from backend.cognition_metrics import get_metrics_engine
    
    collector = get_metrics_collector()
    engine = get_metrics_engine(db)
    
    for domain, kpis in collector.aggregates.items():
        if domain in engine.domains:
            engine.update_domain(domain, kpis)


async def start_metrics_sync(db, interval: int = 60):
    """
    Start background sync from metrics collector to cognition engine
    
    Args:
        db: Database session
        interval: Sync interval in seconds
    """
    while True:
        try:
            await sync_to_cognition_engine(db)
        except Exception as e:
            print(f"Metrics sync error: {e}")
        
        await asyncio.sleep(interval)
