"""Database models for Grace's telemetry and cognition metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, UniqueConstraint

from .models import Base


class MetricSample(Base):
    """Raw metric datapoint emitted by any Grace subsystem."""

    __tablename__ = "metric_samples"

    id = Column(Integer, primary_key=True)
    collected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    domain = Column(String(64), nullable=False, index=True)
    metric = Column(String(128), nullable=False, index=True)
    value = Column(Float, nullable=False)
    metadata = Column(JSON, nullable=True)


class MetricRollup(Base):
    """Aggregated metric statistics over a sliding window."""

    __tablename__ = "metric_rollups"

    id = Column(Integer, primary_key=True)
    domain = Column(String(64), nullable=False, index=True)
    metric = Column(String(128), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    average = Column(Float, nullable=False)
    minimum = Column(Float, nullable=False)
    maximum = Column(Float, nullable=False)
    samples = Column(Integer, nullable=False, default=0)
    confidence = Column(Float, nullable=False, default=0.0)
    threshold_met = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("domain", "metric", "window_start", name="metric_rollup_unique"),
    )


__all__ = ["MetricSample", "MetricRollup"]
