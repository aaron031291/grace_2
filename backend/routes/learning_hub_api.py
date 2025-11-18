"""
Learning Hub API - Phase 3 Unified Interface
Aggregates all Phase 3 learning systems into a single dashboard endpoint
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import os

router = APIRouter(prefix="/api/learning/hub", tags=["learning-hub"])

@router.get("/summary")
async def get_learning_hub_summary() -> Dict[str, Any]:
    """
    Get comprehensive Phase 3 learning system summary
    
    Aggregates:
    - Knowledge gap detection stats
    - Learning job queue metrics
    - Domain whitelist status
    - World model trust/versioning
    - Safe mode status
    - Approval gates status
    """
    try:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "safe_mode": os.getenv("OFFLINE_MODE", "false").lower() == "true",
            "phase_3_status": "operational"
        }
        
        try:
            from backend.learning.knowledge_gap_detector import get_gap_detector
            detector = get_gap_detector()
            summary["gap_detection"] = detector.get_stats()
        except Exception as e:
            summary["gap_detection"] = {"error": str(e), "status": "unavailable"}
        
        try:
            from backend.learning.governed_learning import GovernedLearningOrchestrator
            summary["learning_jobs"] = {
                "status": "orchestrator_available",
                "note": "Requires orchestrator instance for live metrics"
            }
        except Exception as e:
            summary["learning_jobs"] = {"error": str(e), "status": "unavailable"}
        
        try:
            from backend.learning_systems.domain_whitelists import DomainWhitelistManager
            whitelist_mgr = DomainWhitelistManager()
            summary["domain_whitelists"] = whitelist_mgr.get_domain_stats()
        except Exception as e:
            summary["domain_whitelists"] = {"error": str(e), "status": "unavailable"}
        
        try:
            from backend.learning.governed_learning import WorldModelUpdateManager
            summary["world_model"] = {
                "status": "manager_available",
                "note": "Requires manager instance for version/trust metrics"
            }
        except Exception as e:
            summary["world_model"] = {"error": str(e), "status": "unavailable"}
        
        try:
            from backend.learning.governed_learning import SafeModeLearningController
            safe_controller = SafeModeLearningController()
            summary["safe_mode_controller"] = {
                "enabled": safe_controller.enabled,
                "offline_mode": os.getenv("OFFLINE_MODE", "false")
            }
        except Exception as e:
            summary["safe_mode_controller"] = {"error": str(e), "status": "unavailable"}
        
        gap_stats = summary.get("gap_detection", {})
        summary["phase_3_success_criteria"] = {
            "gap_detection_operational": "error" not in gap_stats,
            "whitelist_governance": "error" not in summary.get("domain_whitelists", {}),
            "safe_mode_enforced": summary["safe_mode"],
            "all_systems_available": all(
                "error" not in summary.get(key, {})
                for key in ["gap_detection", "domain_whitelists", "safe_mode_controller"]
            )
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate learning hub summary: {str(e)}"
        )

@router.get("/health")
async def get_learning_hub_health() -> Dict[str, Any]:
    """Quick health check for Phase 3 learning systems"""
    try:
        health = {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        components = [
            ("gap_detector", "backend.learning.knowledge_gap_detector", "get_gap_detector"),
            ("orchestrator", "backend.learning.governed_learning", "GovernedLearningOrchestrator"),
            ("whitelist_manager", "backend.learning_systems.domain_whitelists", "DomainWhitelistManager"),
            ("safe_mode", "backend.learning.governed_learning", "SafeModeLearningController"),
        ]
        
        for name, module, cls in components:
            try:
                exec(f"from {module} import {cls}")
                health["components"][name] = "available"
            except Exception as e:
                health["components"][name] = f"unavailable: {str(e)}"
                health["status"] = "degraded"
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_learning_metrics() -> Dict[str, Any]:
    """Get detailed Phase 3 metrics for monitoring"""
    try:
        from backend.learning.knowledge_gap_detector import get_gap_detector
        
        detector = get_gap_detector()
        gaps = detector.get_prioritized_gaps()
        stats = detector.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_gaps": len(gaps),
            "critical_gaps": sum(1 for g in gaps if g.priority == 'critical'),
            "high_priority_gaps": sum(1 for g in gaps if g.priority == 'high'),
            "gap_stats": stats,
            "learning_sla": {
                "target_completion_time_minutes": 5,
                "target_success_rate": 0.95,
                "note": "Phase 3 requires 95% of learning jobs < 5 minutes"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
