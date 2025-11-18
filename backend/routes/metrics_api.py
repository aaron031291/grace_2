"""
Metrics API - System health and trust metrics
"""

from fastapi import APIRouter
from typing import Dict, Any
from backend.action_gateway import action_gateway
from backend.reflection_loop import reflection_loop
from backend.event_bus import event_bus

router = APIRouter()


@router.get("/metrics/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """
    Get system health and trust metrics summary
    
    Returns:
        Metrics for frontend health meter in expected format:
        { success: true, data: { health, trust, confidence, ... } }
    """
    try:
        # Get trust scores
        trust_scores = reflection_loop.get_trust_scores()
        avg_trust = sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.8
        
        # Count pending approvals
        pending = [
            a for a in action_gateway.get_action_log()
            if not a.get("approved") and 
            a.get("governance_tier") == "approval_required" and
            not a.get("declined")
        ]
        
        # Determine system status
        if avg_trust >= 0.7 and len(event_bus.event_log) > 0:
            status = "healthy"
        elif avg_trust >= 0.5:
            status = "degraded"
        else:
            status = "offline"
        
        return {
            "success": True,
            "data": {
                "health": status,
                "trust": avg_trust,
                "confidence": avg_trust,
                "trust_score": avg_trust,
                "pending_approvals": len(pending),
                "active_tasks": len(action_gateway.action_log),
                "system_status": status,
                "timestamp": event_bus.event_log[-1].timestamp if event_bus.event_log else None
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "health": "offline",
                "trust": 0.0,
                "confidence": 0.0,
                "trust_score": 0.0,
                "pending_approvals": 0,
                "active_tasks": 0,
                "system_status": "offline"
            }
        }


@router.get("/metrics/health")
async def get_health() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "grace_api"
    }
