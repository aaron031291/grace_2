"""
Cognition API Router
Exposes Grace's cognitive metrics for CLI and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.database import get_db
from backend.cognition_metrics import get_metrics_engine

router = APIRouter(prefix="/api/cognition", tags=["cognition"])


@router.get("/status")
async def get_cognition_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get real-time cognition status across all 10 domains
    Used by CLI for live dashboard display
    """
    engine = get_metrics_engine(db)
    return engine.get_status()


@router.get("/readiness")
async def get_saas_readiness(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get detailed SaaS readiness report
    Shows benchmark status, gaps, and next steps
    """
    engine = get_metrics_engine(db)
    return engine.get_readiness_report()


@router.post("/domain/{domain_id}/update")
async def update_domain_metrics(
    domain_id: str,
    kpis: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Update KPIs for a specific domain
    Called by domain systems to report metrics
    """
    engine = get_metrics_engine(db)
    
    if domain_id not in engine.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")
    
    engine.update_domain(domain_id, kpis)
    
    return {
        "status": "updated",
        "domain": domain_id,
        "timestamp": engine.domains[domain_id].last_updated.isoformat()
    }


@router.get("/benchmark/{metric_name}")
async def get_benchmark_status(
    metric_name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed status for a specific benchmark metric
    """
    engine = get_metrics_engine(db)
    
    if metric_name not in engine.benchmarks:
        raise HTTPException(status_code=404, detail=f"Benchmark {metric_name} not found")
    
    bench = engine.benchmarks[metric_name]
    
    return {
        "metric": metric_name,
        "sustained": bench.is_sustained(),
        "average": bench.average(),
        "threshold": bench.threshold,
        "window_days": bench.window_days,
        "sample_count": len(bench.values),
        "recent_values": [
            {"timestamp": ts.isoformat(), "value": val}
            for ts, val in list(bench.values)[-10:]
        ]
    }
