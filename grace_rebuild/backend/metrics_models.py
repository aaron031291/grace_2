"""
Metrics Database Models
Persistent storage for KPIs, aggregates, and benchmark history
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MetricEvent(Base):
    """Individual metric events (raw data points)"""
    __tablename__ = "metric_events"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), nullable=False, index=True)
    kpi = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    metadata = Column(JSON, default={})
    
    __table_args__ = (
        Index('idx_domain_kpi_timestamp', 'domain', 'kpi', 'timestamp'),
    )


class MetricsRollup(Base):
    """Aggregated metrics (hourly, daily, weekly)"""
    __tablename__ = "metrics_rollups"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), nullable=False, index=True)
    kpi = Column(String(100), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # 'hour', 'day', 'week'
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    
    avg_value = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    sum_value = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_domain_kpi_period', 'domain', 'kpi', 'period', 'period_start'),
    )


class BenchmarkHistory(Base):
    """History of benchmark evaluations"""
    __tablename__ = "benchmark_history"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    sustained = Column(Boolean, default=False)
    window_days = Column(Integer, default=7)
    sample_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    metadata = Column(JSON, default={})


class SaaSReadinessEvent(Base):
    """SaaS readiness events and triggers"""
    __tablename__ = "saas_readiness_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # 'threshold_crossed', 'elevation_ready', 'threshold_lost'
    overall_health = Column(Float, nullable=False)
    overall_trust = Column(Float, nullable=False)
    overall_confidence = Column(Float, nullable=False)
    saas_ready = Column(Boolean, default=False)
    message = Column(String(500))
    triggered_at = Column(DateTime, default=datetime.now, index=True)
    metadata = Column(JSON, default={})
    notified = Column(Boolean, default=False)


class DomainMetrics(Base):
    """Current domain metric snapshot"""
    __tablename__ = "domain_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), unique=True, nullable=False, index=True)
    health = Column(Float, default=0.0)
    trust = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    kpis = Column(JSON, default={})
    last_updated = Column(DateTime, default=datetime.now)
    
    # Trends
    health_trend = Column(String(20))  # 'improving', 'stable', 'declining'
    performance_score = Column(Float, default=0.0)
    
    # Alerts
    has_alerts = Column(Boolean, default=False)
    alert_count = Column(Integer, default=0)
