"""Telemetry aggregation service for Grace cognition metrics.

This module provides a first-pass scaffolding for collecting raw metric
events, rolling them up into time windows, and exposing lightweight
snapshots for downstream consumers such as the cognition dashboard or the
CLI. The implementation focuses on structure; optimisation and advanced
analytics will follow in later phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func, select

from .metrics_models import MetricRollup, MetricSample
from .models import async_session


DEFAULT_WINDOW_HOURS = 168  # 7 days
CRITICAL_METRICS = {
    "core": ["uptime", "governance_score"],
    "transcendence": ["task_success", "confidence"],
    "knowledge": ["trust_score", "ingestion_success"],
    "security": ["threat_detection", "response_time"],
    "ml": ["model_accuracy", "deployment_success"],
    "temporal": ["prediction_accuracy"],
    "parliament": ["recommendation_adoption"],
    "federation": ["connector_health"],
    "speech": ["recognition_accuracy"],
}


@dataclass
class MetricPoint:
    domain: str
    metric: str
    value: float
    collected_at: datetime
    metadata: Optional[Dict[str, float]] = None


class MetricsService:
    """Service responsible for ingesting and aggregating subsystem metrics."""

    async def record_metric(
        self,
        *,
        domain: str,
        metric: str,
        value: float,
        collected_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, float]] = None,
    ) -> None:
        """Persist a raw metric sample."""

        sample = MetricSample(
            domain=domain,
            metric=metric,
            value=value,
            collected_at=collected_at or datetime.utcnow(),
            metadata=metadata,
        )

        async with async_session() as session:
            session.add(sample)
            await session.commit()

    async def get_recent_samples(
        self,
        *,
        domain: Optional[str] = None,
        metric: Optional[str] = None,
        window_hours: int = DEFAULT_WINDOW_HOURS,
    ) -> List[MetricPoint]:
        """Fetch raw metric samples within the provided window."""

        cutoff = datetime.utcnow() - timedelta(hours=window_hours)

        stmt = select(MetricSample).where(MetricSample.collected_at >= cutoff)
        if domain:
            stmt = stmt.where(MetricSample.domain == domain)
        if metric:
            stmt = stmt.where(MetricSample.metric == metric)

        async with async_session() as session:
            result = await session.execute(stmt.order_by(MetricSample.collected_at.desc()))
            samples = result.scalars().all()

        return [
            MetricPoint(
                domain=s.domain,
                metric=s.metric,
                value=s.value,
                collected_at=s.collected_at,
                metadata=s.metadata,
            )
            for s in samples
        ]

    async def rollup_metrics(
        self,
        *,
        domain: Optional[str] = None,
        metric: Optional[str] = None,
        window_hours: int = DEFAULT_WINDOW_HOURS,
    ) -> None:
        """Aggregate raw metrics into rollup windows."""

        cutoff = datetime.utcnow() - timedelta(hours=window_hours)

        stmt = select(
            MetricSample.domain,
            MetricSample.metric,
            func.min(MetricSample.collected_at),
            func.max(MetricSample.collected_at),
            func.avg(MetricSample.value),
            func.min(MetricSample.value),
            func.max(MetricSample.value),
            func.count(MetricSample.id),
        ).where(MetricSample.collected_at >= cutoff)

        if domain:
            stmt = stmt.where(MetricSample.domain == domain)
        if metric:
            stmt = stmt.where(MetricSample.metric == metric)

        stmt = stmt.group_by(MetricSample.domain, MetricSample.metric)

        async with async_session() as session:
            result = await session.execute(stmt)
            aggregates = result.all()

            for row in aggregates:
                rollup = MetricRollup(
                    domain=row[0],
                    metric=row[1],
                    window_start=row[2] or datetime.utcnow(),
                    window_end=row[3] or datetime.utcnow(),
                    average=row[4] or 0.0,
                    minimum=row[5] or 0.0,
                    maximum=row[6] or 0.0,
                    samples=row[7] or 0,
                    confidence=1.0,
                    threshold_met=None,
                )
                session.merge(rollup)

            await session.commit()

    async def get_domain_snapshot(self, domain: str) -> Dict[str, Dict[str, float]]:
        """Return the latest rollup metrics for a given domain."""

        stmt = select(MetricRollup).where(MetricRollup.domain == domain)

        async with async_session() as session:
            result = await session.execute(stmt)
            rollups = result.scalars().all()

        snapshot: Dict[str, Dict[str, float]] = {}
        for rollup in rollups:
            snapshot[rollup.metric] = {
                "average": rollup.average,
                "min": rollup.minimum,
                "max": rollup.maximum,
                "samples": rollup.samples,
                "confidence": rollup.confidence,
                "threshold_met": rollup.threshold_met,
            }

        return snapshot

    async def evaluate_benchmarks(
        self, *, threshold: float = 0.9, window_hours: int = DEFAULT_WINDOW_HOURS
    ) -> Dict[str, bool]:
        """Compute which domains satisfy the benchmark threshold."""

        status: Dict[str, bool] = {}
        for domain, metrics in CRITICAL_METRICS.items():
            snapshot = await self.get_domain_snapshot(domain)
            if not metrics:
                status[domain] = False
                continue

            met = all(snapshot.get(metric, {}).get("average", 0.0) >= threshold for metric in metrics)
            status[domain] = met

        return status


metrics_service = MetricsService()


__all__ = ["MetricPoint", "MetricsService", "metrics_service"]
