"""
Curriculum Management API
View and control Grace's learning from curricula
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/curriculum", tags=["Curriculum Learning"])


class TriggerLearningRequest(BaseModel):
    curriculum_name: str = "all"
    intensive: bool = False


@router.get("/status")
async def get_learning_status():
    """
    See what curricula Grace discovered and what she's learning
    Shows active learning sessions and progress
    """
    try:
        from backend.agents.curriculum_orchestrator import curriculum_orchestrator
        
        status = await curriculum_orchestrator.get_learning_status()
        return status
    
    except Exception as e:
        logger.error(f"[CURRICULUM-API] Status check failed: {e}")
        return {
            "error": str(e),
            "status": "degraded"
        }


@router.post("/trigger-learning")
async def trigger_learning(request: TriggerLearningRequest):
    """
    Trigger Grace to start learning from specific curriculum or all
    
    This makes Grace:
    1. Load the curriculum
    2. Extract all search terms
    3. Search and download real data
    4. Test in sandbox
    5. Build mastery
    """
    try:
        from backend.agents.curriculum_orchestrator import curriculum_orchestrator
        
        logger.info(f"[CURRICULUM-API] Triggering learning: {request.curriculum_name}")
        
        result = await curriculum_orchestrator.trigger_learning_now(
            curriculum_name=request.curriculum_name,
            intensive=request.intensive
        )
        
        return {
            "success": True,
            "message": f"Grace is now learning from {len(result['curricula_triggered'])} curricula",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"[CURRICULUM-API] Trigger learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discovered")
async def get_discovered_curricula():
    """
    List all curricula Grace discovered
    Shows what she knows she needs to learn
    """
    try:
        from backend.agents.curriculum_orchestrator import curriculum_orchestrator
        
        return {
            "curricula": curriculum_orchestrator.discovered_curricula,
            "total": len(curriculum_orchestrator.discovered_curricula),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": str(e)
        }


@router.get("/metrics")
async def get_orchestrator_metrics():
    """Get curriculum orchestration metrics"""
    try:
        from backend.agents.curriculum_orchestrator import curriculum_orchestrator
        
        metrics = await curriculum_orchestrator.get_metrics()
        return {
            **metrics,
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "degraded"
        }
