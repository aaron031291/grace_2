"""
Compatibility wrapper for backend.metrics_service
Re-exports from backend.monitoring.metrics_service
"""

from backend.monitoring.metrics_service import (
    MetricEvent,
    MetricsCollector,
    get_metrics_collector,
    publish_metric,
    publish_batch,
    MetricPublisherMixin,
    init_metrics_collector,
    sync_to_cognition_engine,
    start_metrics_sync,
)

__all__ = [
    'MetricEvent',
    'MetricsCollector',
    'get_metrics_collector',
    'publish_metric',
    'publish_batch',
    'MetricPublisherMixin',
    'init_metrics_collector',
    'sync_to_cognition_engine',
    'start_metrics_sync',
]
