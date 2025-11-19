"""
Cockpit API - High-level system overview

Endpoints:
- System metrics summary
- Guardian stats
- Learning status
- Health overview
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from backend.world_model.world_model_service import world_model_service
from backend.reflection_loop import reflection_loop
from backend.action_gateway import action_gateway

router = APIRouter()


class SystemMetricsSummary(BaseModel):
    """High-level system metrics"""
    timestamp: str
    health: str
    trust_score: float
    confidence: float
    active_tasks: int
    pending_approvals: int
    learning_jobs: int
    incidents: int
    uptime_seconds: float
    memory_mb: float


class GuardianStats(BaseModel):
    """Guardian system statistics"""
    enabled: bool
    violations_blocked: int
    approvals_required: int
    auto_approved: int
    last_check: str


class LearningStatus(BaseModel):
    """Learning system status"""
    enabled: bool
    active_jobs: int
    total_ingested: int
    models_trained: int
    knowledge_base_size: int
    last_ingestion: str


@router.get("/cockpit/summary", response_model=Dict[str, Any])
async def get_cockpit_summary():
    """
    Get comprehensive system overview for cockpit
    
    Returns:
        - System metrics
        - Guardian stats
        - Learning status
        - Health overview
    """
    # Get system metrics
    import psutil
    import time
    
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    uptime = time.time() - process.create_time()
    
    # Get world model context
    context = await world_model_service.query_context(limit=10)
    
    # Calculate trust score
    trust_scores = reflection_loop.get_trust_scores()
    avg_trust = sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.8
    
    # Determine health
    if avg_trust >= 0.7:
        health = "healthy"
    elif avg_trust >= 0.5:
        health = "degraded"
    else:
        health = "offline"
    
    # System metrics
    metrics = SystemMetricsSummary(
        timestamp=datetime.utcnow().isoformat(),
        health=health,
        trust_score=avg_trust,
        confidence=context["system_health"].get("confidence", avg_trust),
        active_tasks=len(context.get("active_missions", [])),
        pending_approvals=len(context.get("pending_approvals", [])),
        learning_jobs=len(context.get("learning_jobs", [])),
        incidents=0,
        uptime_seconds=uptime,
        memory_mb=memory_mb
    )
    
    # Guardian stats
    action_log = action_gateway.get_action_log()
    guardian = GuardianStats(
        enabled=True,
        violations_blocked=sum(1 for a in action_log if a.get("declined")),
        approvals_required=sum(1 for a in action_log if a.get("governance_tier") == "approval_required"),
        auto_approved=sum(1 for a in action_log if a.get("approved") and a.get("governance_tier") != "approval_required"),
        last_check=datetime.utcnow().isoformat()
    )
    
    # Learning status
    from backend.memory.memory_catalog import memory_catalog
    catalog_stats = memory_catalog.get_stats()
    
    learning = LearningStatus(
        enabled=True,
        active_jobs=len(context.get("learning_jobs", [])),
        total_ingested=catalog_stats.get("total_assets", 0),
        models_trained=0,
        knowledge_base_size=len(context.get("relevant_knowledge", [])),
        last_ingestion=datetime.utcnow().isoformat()
    )
    
    return {
        "metrics": metrics.dict(),
        "guardian": guardian.dict(),
        "learning": learning.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/cockpit/health")
async def get_health_overview():
    """Get detailed health breakdown by subsystem"""
    trust_scores = reflection_loop.get_trust_scores()
    
    subsystems = {
        "memory": trust_scores.get("memory", 0.8),
        "governance": trust_scores.get("governance", 0.9),
        "learning": trust_scores.get("learning", 0.7),
        "action_gateway": trust_scores.get("action_gateway", 0.85),
        "world_model": trust_scores.get("world_model", 0.8),
    }
    
    overall_health = sum(subsystems.values()) / len(subsystems)
    
    return {
        "overall_health": overall_health,
        "status": "healthy" if overall_health >= 0.7 else "degraded",
        "subsystems": subsystems,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/cockpit/alerts")
async def get_active_alerts():
    """Get active system alerts and warnings"""
    alerts = []
    
    # Check trust scores
    trust_scores = reflection_loop.get_trust_scores()
    for system, score in trust_scores.items():
        if score < 0.5:
            alerts.append({
                "severity": "critical",
                "system": system,
                "message": f"{system} trust score critically low: {score:.2f}",
                "timestamp": datetime.utcnow().isoformat()
            })
        elif score < 0.7:
            alerts.append({
                "severity": "warning",
                "system": system,
                "message": f"{system} trust score below threshold: {score:.2f}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    # Check pending approvals
    context = await world_model_service.query_context()
    pending = len(context.get("pending_approvals", []))
    if pending > 5:
        alerts.append({
            "severity": "warning",
            "system": "governance",
            "message": f"{pending} pending approvals require attention",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "alerts": alerts,
        "total": len(alerts),
        "critical": sum(1 for a in alerts if a["severity"] == "critical"),
        "warnings": sum(1 for a in alerts if a["severity"] == "warning")
    }
