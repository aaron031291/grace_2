"""
Autonomous Web Navigator API
Exposes Grace's autonomous web navigation capabilities
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/web-navigator", tags=["Autonomous Navigation"])


class NavigationRequest(BaseModel):
    query: str
    confidence: float = 0.5
    knowledge_match: float = 0.5
    force_search: bool = False


@router.post("/auto-navigate")
async def auto_navigate(request: NavigationRequest):
    """
    Grace autonomously decides if she should search the web
    and executes appropriate strategy
    """
    try:
        from backend.agents.autonomous_web_navigator import autonomous_web_navigator
        
        if request.force_search:
            # Force search regardless of decision logic
            result = await autonomous_web_navigator.execute_search_strategy(
                strategy_name='basic_search',
                topic=request.query
            )
            return {
                "searched": True,
                "reason": "Forced search",
                "strategy": "basic_search",
                "result": result
            }
        
        # Let Grace decide autonomously
        result = await autonomous_web_navigator.auto_navigate(
            user_query=request.query,
            grace_confidence=request.confidence,
            knowledge_match=request.knowledge_match
        )
        
        if result:
            return {
                "searched": True,
                "reason": "Autonomous decision to search",
                "result": result
            }
        else:
            return {
                "searched": False,
                "reason": "Grace decided search not needed",
                "grace_says": "I can answer this from existing knowledge"
            }
    
    except Exception as e:
        logger.error(f"[WEB-NAVIGATOR-API] Auto-navigate failed: {e}")
        return {
            "searched": False,
            "error": str(e)
        }


@router.get("/should-search")
async def should_search(
    query: str,
    confidence: float = 0.5,
    knowledge_match: float = 0.5
):
    """
    Ask Grace if she thinks she should search the web for this query
    (Decision only, doesn't execute search)
    """
    try:
        from backend.agents.autonomous_web_navigator import autonomous_web_navigator
        
        context = {
            'query': query,
            'confidence': confidence,
            'knowledge_match': knowledge_match,
            'error_occurred': 'error' in query.lower(),
            'task_type': 'question'
        }
        
        should_search, reason, strategy = await autonomous_web_navigator.should_search_web(context)
        
        return {
            "should_search": should_search,
            "reason": reason,
            "recommended_strategy": strategy,
            "confidence_threshold": 0.6,
            "knowledge_match_threshold": 0.3
        }
    
    except Exception as e:
        logger.error(f"[WEB-NAVIGATOR-API] Should-search check failed: {e}")
        return {
            "error": str(e)
        }


@router.get("/metrics")
async def get_navigator_metrics():
    """Get autonomous navigation metrics"""
    try:
        from backend.agents.autonomous_web_navigator import autonomous_web_navigator
        
        metrics = await autonomous_web_navigator.get_metrics()
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


@router.get("/playbook")
async def get_playbook():
    """Get the web navigation playbook (what Grace knows)"""
    try:
        from backend.agents.autonomous_web_navigator import autonomous_web_navigator
        
        if not autonomous_web_navigator.playbook:
            return {
                "loaded": False,
                "message": "Playbook not loaded"
            }
        
        return {
            "loaded": True,
            "playbook": {
                "name": autonomous_web_navigator.playbook.get('name'),
                "version": autonomous_web_navigator.playbook.get('version'),
                "triggers": len(autonomous_web_navigator.playbook.get('triggers', [])),
                "strategies": list(autonomous_web_navigator.playbook.get('strategies', {}).keys()),
                "decision_trees": list(autonomous_web_navigator.playbook.get('decision_trees', {}).keys()),
                "examples": len(autonomous_web_navigator.playbook.get('examples', []))
            }
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "loaded": False
        }
