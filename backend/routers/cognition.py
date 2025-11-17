"""
Cognition API Router
Exposes Grace's cognitive metrics for CLI and monitoring
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

try:
    from ..cognition_metrics import get_metrics_engine
    from ..metrics_service import get_metrics_collector, publish_metric
except ImportError:
    # Fallback for different import contexts
    from backend.cognition_metrics import get_metrics_engine
    from backend.metrics_service import get_metrics_collector

router = APIRouter(prefix="/api/cognition", tags=["cognition"])


@router.get("/status")
async def get_cognition_status() -> Dict[str, Any]:
    """
    Get real-time cognition status across all 10 domains
    Used by CLI for live dashboard display
    """
    collector = get_metrics_collector()
    engine = get_metrics_engine()
    
    # Sync latest metrics from collector to engine
    for domain, kpis in collector.aggregates.items():
        if domain in engine.domains:
            engine.update_domain(domain, kpis)
    
    return engine.get_status()


@router.get("/readiness")
async def get_saas_readiness() -> Dict[str, Any]:
    """
    Get detailed SaaS readiness report
    Shows benchmark status, gaps, and next steps
    """
    engine = get_metrics_engine()
    return engine.get_readiness_report()


@router.post("/domain/{domain_id}/update")
async def update_domain_metrics(
    domain_id: str,
    kpis: Dict[str, Any]
) -> Dict[str, str]:
    """
    Update KPIs for a specific domain
    Called by domain systems to report metrics
    """
    engine = get_metrics_engine()
    
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
    metric_name: str
) -> Dict[str, Any]:
    """
    Get detailed status for a specific benchmark metric
    """
    engine = get_metrics_engine()
    
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


@router.get("/alerts")
async def get_cognition_alerts(limit: int = 10) -> Dict[str, Any]:
    """Get recent cognition alerts"""
    try:
        from ..cognition_alerts import get_alert_manager
        
        alert_manager = get_alert_manager()
        alerts = alert_manager.get_recent_alerts(limit)
        
        return {
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        return {"alerts": [], "count": 0}


@router.post("/report/generate")
async def generate_readiness_report() -> Dict[str, Any]:
    """Generate and save SaaS readiness report"""
    try:
        from ..readiness_report import get_report_generator
        from datetime import datetime
        
        generator = get_report_generator()
        report_path = await generator.generate_and_save()
        
        return {
            "status": "generated",
            "report_path": str(report_path),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/latest")
async def get_latest_report() -> Dict[str, Any]:
    """Get the latest readiness report content"""
    try:
        from ..readiness_report import get_report_generator
        from datetime import datetime
        
        generator = get_report_generator()
        report_content = generator.generate_markdown_report()
        
        return {
            "status": "generated",
            "content": report_content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
