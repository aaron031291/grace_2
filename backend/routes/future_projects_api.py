"""
Future Projects Learning API
Grace's proactive learning for upcoming projects
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/future-projects", tags=["Future Projects Learning"])


class LearnDomainRequest(BaseModel):
    domain: str  # 'blockchain', 'crm', 'ecommerce', 'api_tracking_analysis', 'distributed_compute'
    intensive: bool = False


@router.get("/readiness")
async def get_readiness():
    """
    Get Grace's readiness for all future project domains
    Shows how prepared she is for each project type
    """
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        report = await future_projects_learner.get_readiness_report()
        return report
    
    except Exception as e:
        logger.error(f"[FUTURE-PROJECTS-API] Readiness check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn-domain")
async def learn_domain(request: LearnDomainRequest):
    """
    Trigger Grace to learn a specific domain now
    
    Intensive mode: Learn everything in curriculum immediately
    Normal mode: Learn incrementally (5 terms per session)
    """
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        logger.info(f"[FUTURE-PROJECTS-API] Learning domain: {request.domain}")
        
        result = await future_projects_learner.learn_domain_now(
            domain_name=request.domain,
            intensive=request.intensive
        )
        
        return {
            "success": True,
            "domain": request.domain,
            "intensive": request.intensive,
            "result": result
        }
    
    except Exception as e:
        logger.error(f"[FUTURE-PROJECTS-API] Domain learning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/learn-all")
async def learn_all_domains(intensive: bool = False):
    """
    Trigger Grace to learn ALL future project domains
    This is a comprehensive learning session across all 5 domains
    """
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        logger.info("[FUTURE-PROJECTS-API] Learning ALL future project domains")
        
        results = {}
        
        for domain in ['blockchain', 'crm', 'ecommerce', 'api_tracking_analysis', 'distributed_compute']:
            logger.info(f"[FUTURE-PROJECTS-API] Starting {domain}...")
            result = await future_projects_learner.learn_domain_now(
                domain_name=domain,
                intensive=intensive
            )
            results[domain] = result
        
        # Get updated readiness
        readiness = await future_projects_learner.get_readiness_report()
        
        return {
            "success": True,
            "message": "Learning complete for all domains",
            "domains_learned": list(results.keys()),
            "readiness": readiness,
            "intensive_mode": intensive
        }
    
    except Exception as e:
        logger.error(f"[FUTURE-PROJECTS-API] Learn all failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{domain}")
async def get_domain_progress(domain: str):
    """Get learning progress for a specific domain"""
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        progress = future_projects_learner.domain_progress.get(domain)
        
        if not progress:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
        
        return {
            "domain": domain,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FUTURE-PROJECTS-API] Get progress failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curriculum")
async def get_curriculum():
    """View the complete learning curriculum"""
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        if not future_projects_learner.curriculum:
            return {
                "loaded": False,
                "message": "Curriculum not loaded"
            }
        
        return {
            "loaded": True,
            "curriculum": {
                "name": future_projects_learner.curriculum.get('name'),
                "domains": list(future_projects_learner.curriculum.get('domains', {}).keys()),
                "learning_strategy": future_projects_learner.curriculum.get('learning_strategy'),
                "sandbox_projects": list(future_projects_learner.curriculum.get('sandbox_projects', {}).keys())
            }
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "loaded": False
        }


@router.get("/metrics")
async def get_metrics():
    """Get future projects learning metrics"""
    try:
        from backend.agents.future_projects_learner import future_projects_learner
        
        metrics = await future_projects_learner.get_metrics()
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
