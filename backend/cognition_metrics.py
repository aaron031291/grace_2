"""
Compatibility wrapper for backend.cognition_metrics
Re-exports from backend.misc.cognition_metrics
"""

from backend.misc.cognition_metrics import (
    get_metrics_engine,
    CognitionMetricsEngine,
)

__all__ = [
    'get_metrics_engine',
    'CognitionMetricsEngine',
]
