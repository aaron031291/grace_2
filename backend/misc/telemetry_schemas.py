"""
Telemetry Schemas - MetricEvent and MetricsSnapshot
Real-time metrics that feed Grace's autonomy and decision-making
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from enum import Enum


class MetricUnit(str, Enum):
    """Canonical units for metrics"""
    MILLISECONDS = "ms"
    PERCENT = "percent"
    RATIO = "ratio"
    COUNT = "count"
    REQ_PER_SEC = "req_per_sec"
    SECONDS = "seconds"


class MetricBand(str, Enum):
    """Threshold bands"""
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricTrend(str, Enum):
    """Trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STEADY = "steady"


class MetricThresholds(BaseModel):
    """Threshold definitions"""
    good: str
    warning: str
    critical: str


class MetricResource(BaseModel):
    """Resource being measured"""
    scope: Literal["service", "queue", "host", "volume", "subsystem", "worker_pool"]
    id: str


class MetricEvent(BaseModel):
    """
    Metric event published to trigger mesh
    
    Used by collectors when publishing real-time metrics
    """
    event_type: str = Field(..., description="Must be metrics.{metric_id}")
    source: str = Field(..., description="Collector identifier (prometheus, internal_sql, etc)")
    actor: str = Field(default="metrics_collector", description="Service account")
    resource: MetricResource = Field(..., description="Resource being measured")
    
    payload: Dict[str, Any] = Field(..., description="Metric data")
    # payload contains:
    # - metric_id: str
    # - value: float
    # - unit: MetricUnit
    # - aggregation: str (p95, avg, max, sum)
    # - interval_seconds: int
    # - observed_at: str (ISO timestamp)
    # - thresholds: dict
    # - computed_band: MetricBand
    # - trend: MetricTrend (optional)
    # - annotations: dict (optional)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "metrics.api.latency_p95",
                "source": "prometheus",
                "actor": "metrics_collector",
                "resource": {
                    "scope": "service",
                    "id": "grace-api"
                },
                "payload": {
                    "metric_id": "api.latency_p95",
                    "value": 412.5,
                    "unit": "ms",
                    "aggregation": "p95",
                    "interval_seconds": 60,
                    "observed_at": "2025-11-09T14:03:00Z",
                    "thresholds": {
                        "good": "<350",
                        "warning": "350-500",
                        "critical": ">500"
                    },
                    "computed_band": "warning",
                    "trend": "increasing",
                    "annotations": {
                        "prometheus_query": "histogram_quantile(0.95, ...)"
                    }
                },
                "timestamp": "2025-11-09T14:03:02Z"
            }
        }


class MetricStats(BaseModel):
    """Aggregated statistics"""
    min: float
    max: float
    avg: float
    p95: Optional[float] = None
    sample_count: int


class MetricBandCounts(BaseModel):
    """Counts per threshold band"""
    good_samples: int
    warning_samples: int
    critical_samples: int


class DerivedAction(BaseModel):
    """Action recommendation from metric analysis"""
    action_type: Literal["playbook_recommendation", "threshold_adjustment", "alert"]
    playbook_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reason: Optional[str] = None


class MetricsSnapshot(BaseModel):
    """
    Periodic aggregation for dashboards and anomaly detection
    
    Stored in metrics_snapshots table
    """
    snapshot_id: str = Field(..., description="Format: {resource_id}:{timestamp}:{metric_id}")
    metric_id: str
    resource_scope: str
    resource_id: str
    
    window_start: datetime
    window_end: datetime
    
    stats: MetricStats
    bands: MetricBandCounts
    latest_band: MetricBand
    
    derived_actions: List[DerivedAction] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "snapshot_id": "grace-api:2025-11-09T14:05:00Z:api.latency_p95",
                "metric_id": "api.latency_p95",
                "resource_scope": "service",
                "resource_id": "grace-api",
                "window_start": "2025-11-09T14:00:00Z",
                "window_end": "2025-11-09T14:05:00Z",
                "stats": {
                    "min": 280.5,
                    "max": 612.0,
                    "avg": 410.2,
                    "p95": 498.3,
                    "sample_count": 5
                },
                "bands": {
                    "good_samples": 3,
                    "warning_samples": 1,
                    "critical_samples": 1
                },
                "latest_band": "critical",
                "derived_actions": [
                    {
                        "action_type": "playbook_recommendation",
                        "playbook_id": "scale-api-shard",
                        "confidence": 0.8
                    }
                ],
                "created_at": "2025-11-09T14:05:02Z"
            }
        }


class MetricCatalogEntry(BaseModel):
    """Single metric definition from catalog"""
    metric_id: str
    category: str
    description: str
    unit: MetricUnit
    aggregation: str
    source: str
    resource_scope: str
    recommended_interval_seconds: int
    thresholds: Dict[str, Dict[str, float]]
    playbooks: List[str]
    tags: List[str]


class PlaybookDefinition(BaseModel):
    """Playbook definition from catalog"""
    playbook_id: str
    description: str
    risk_level: Literal["low", "medium", "high", "critical"]
    autonomy_tier: Literal["tier_1", "tier_2", "tier_3", "tier_4"]
    requires_approval: bool
