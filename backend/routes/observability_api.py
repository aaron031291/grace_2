"""
Observability API
Exposes stress test metrics, auto-remediation status, and system telemetry

Endpoints:
- GET /api/observability/stress/current - Current stress test status
- GET /api/observability/stress/trends - Historical trends
- GET /api/observability/remediation/stats - Auto-remediation statistics
- GET /api/observability/dashboard - Complete dashboard data
"""

from fastapi import APIRouter
from typing import Dict, Any

from backend.monitoring.stress_metrics_aggregator import stress_metrics_aggregator
from backend.core.auto_remediation import auto_remediation
from backend.core.intent_api import intent_api
from backend.kernels.kernel_registry import kernel_registry

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("/stress/current")
async def get_current_stress_status() -> Dict[str, Any]:
    """
    Get current stress test status
    
    Returns active tests, recent metrics, and real-time performance
    """
    return stress_metrics_aggregator.get_dashboard_metrics()


@router.get("/stress/trends")
async def get_stress_trends(hours: int = 24) -> Dict[str, Any]:
    """
    Get stress test trends over time
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        Hourly aggregated statistics with boot times, failures, trends
    """
    return stress_metrics_aggregator.get_trend_data(hours=hours)


@router.get("/remediation/stats")
async def get_remediation_stats() -> Dict[str, Any]:
    """
    Get auto-remediation statistics
    
    Returns:
        - Number of remediations created
        - Success rate
        - Failure patterns
        - Active remediations
    """
    stats = auto_remediation.get_stats()
    
    # Add active remediation intents
    active_intents = await intent_api.get_active_intents()
    remediation_intents = [
        intent for intent in active_intents
        if intent.get("context", {}).get("source") == "auto_remediation"
    ]
    
    stats["active_remediation_intents"] = len(remediation_intents)
    stats["active_intents"] = remediation_intents[:5]  # First 5
    
    return stats


@router.get("/dashboard")
async def get_observability_dashboard() -> Dict[str, Any]:
    """
    Get complete observability dashboard data
    
    Returns comprehensive system status for UI dashboards:
    - Layer 1: Kernel health
    - Layer 2: Intent/HTM status
    - Layer 3: Brain telemetry
    - Stress test metrics
    - Auto-remediation stats
    """
    
    # Layer 1: Kernel health
    kernel_status = kernel_registry.get_status()
    
    # Layer 2: Intent API metrics
    intent_metrics = await intent_api.get_intent_metrics()
    
    # Stress metrics
    stress_metrics = stress_metrics_aggregator.get_dashboard_metrics()
    
    # Remediation stats
    remediation_stats = auto_remediation.get_stats()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "layers": {
            "layer1_kernels": {
                "total_kernels": kernel_status["total_kernels"],
                "domain_kernels": kernel_status["domain_kernels"],
                "clarity_kernels": kernel_status["clarity_kernels"],
                "health": kernel_status["health"],
                "status": "operational" if kernel_status["initialized"] else "degraded"
            },
            "layer2_orchestration": {
                "intent_api": {
                    "total_intents": intent_metrics["total_intents"],
                    "active": intent_metrics["active"],
                    "completed": intent_metrics["completed"],
                    "success_rate": intent_metrics["success_rate"]
                }
            },
            "layer3_brain": {
                "telemetry_available": True,
                "learning_loop_active": True
            }
        },
        "stress_testing": stress_metrics,
        "auto_remediation": remediation_stats,
        "overall_health": {
            "status": "operational",
            "score": _calculate_health_score(kernel_status, stress_metrics, remediation_stats)
        }
    }


@router.get("/alerts")
async def get_active_alerts() -> Dict[str, Any]:
    """
    Get active alerts from stress tests and auto-remediation
    
    Returns alerts that require attention
    """
    alerts = []
    
    # Check for recent failures
    stress_metrics = stress_metrics_aggregator.get_dashboard_metrics()
    failures_last_hour = stress_metrics["reliability"]["failures_last_hour"]
    
    if failures_last_hour > 0:
        alerts.append({
            "severity": "high",
            "type": "stress_test_failures",
            "message": f"{failures_last_hour} stress test failures in last hour",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # Check boot time regression
    recent_avg = stress_metrics["performance"]["avg_boot_time_ms"]
    if recent_avg > 500:  # Baseline threshold
        alerts.append({
            "severity": "medium",
            "type": "performance_degradation",
            "message": f"Average boot time {recent_avg:.0f}ms exceeds 500ms baseline",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # Check kernel health
    kernel_status = kernel_registry.get_status()
    unhealthy_kernels = [
        name for name, health in kernel_status["health"].items()
        if health.get("status") == "error"
    ]
    
    if unhealthy_kernels:
        alerts.append({
            "severity": "critical",
            "type": "kernel_errors",
            "message": f"{len(unhealthy_kernels)} kernels in error state",
            "affected_kernels": unhealthy_kernels,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {
        "alert_count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def _calculate_health_score(
    kernel_status: Dict,
    stress_metrics: Dict,
    remediation_stats: Dict
) -> float:
    """Calculate overall system health score (0.0 - 1.0)"""
    
    # Kernel health (40% weight)
    total_kernels = kernel_status.get("total_kernels", 0)
    healthy_kernels = sum(
        1 for health in kernel_status.get("health", {}).values()
        if health.get("status") != "error"
    )
    kernel_score = healthy_kernels / total_kernels if total_kernels > 0 else 0.5
    
    # Stress test success (30% weight)
    stress_score = stress_metrics.get("reliability", {}).get("success_rate", 0.5)
    
    # Performance (20% weight)
    avg_boot_time = stress_metrics.get("performance", {}).get("avg_boot_time_ms", 500)
    perf_score = max(0, 1.0 - (avg_boot_time - 100) / 1000)  # Penalize slow boots
    
    # Remediation effectiveness (10% weight)
    remediation_score = remediation_stats.get("success_rate", 0.5) if remediation_stats.get("remediations_created", 0) > 0 else 0.5
    
    # Weighted average
    health_score = (
        kernel_score * 0.4 +
        stress_score * 0.3 +
        perf_score * 0.2 +
        remediation_score * 0.1
    )
    
    return round(health_score, 3)


# Export router for FastAPI app
__all__ = ['router']
