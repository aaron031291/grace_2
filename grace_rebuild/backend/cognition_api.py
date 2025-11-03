"""FastAPI router scaffolding for Grace cognition and metrics status."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query

from .auth import get_current_user
from .metrics_service import metrics_service


router = APIRouter(prefix="/api/cognition", tags=["cognition"])


@router.get("/status")
async def cognition_status(current_user: str = Depends(get_current_user)) -> Dict[str, object]:
    """Return a high-level snapshot of domain health."""

    benchmark = await metrics_service.evaluate_benchmarks()
    domains: Dict[str, Dict[str, float]] = {}
    for domain in benchmark.keys():
        domains[domain] = await metrics_service.get_domain_snapshot(domain)

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "domains": domains,
        "benchmarks": benchmark,
    }


@router.get("/metrics/{domain}")
async def cognition_domain_metrics(
    domain: str,
    metric: Optional[str] = Query(default=None, description="Optional metric filter"),
    current_user: str = Depends(get_current_user),
) -> Dict[str, object]:
    """Return raw samples and rollups for a domain."""

    samples = await metrics_service.get_recent_samples(domain=domain, metric=metric)
    snapshot = await metrics_service.get_domain_snapshot(domain)

    return {
        "domain": domain,
        "metric": metric,
        "samples": [
            {
                "value": point.value,
                "collected_at": point.collected_at.isoformat(),
                "metadata": point.metadata,
            }
            for point in samples
        ],
        "snapshot": snapshot,
    }


@router.get("/report/latest")
async def cognition_readiness_report(current_user: str = Depends(get_current_user)) -> Dict[str, object]:
    """Generate a lightweight readiness report summary."""

    benchmarks = await metrics_service.evaluate_benchmarks()

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "ready": all(benchmarks.values()),
        "benchmarks": benchmarks,
        "content": "Grace readiness reporting scaffold. Detailed narrative to follow.",
    }
