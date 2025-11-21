"""
Orchestrator API - Multi-agent system monitoring
Provides status, metrics, and control endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from backend.agents.multi_agent_orchestrator import multi_agent_orchestrator

router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_orchestrator_status():
    """
    Get current orchestrator status.
    
    Returns:
    - Running state
    - Active agents count
    - Queue size
    - Knowledge gaps detected
    """
    return multi_agent_orchestrator.get_status()


@router.get("/agents")
async def get_active_agents():
    """
    List all active builder agents.
    
    Returns:
        Dictionary of active agents with their task IDs
    """
    return {
        "active_agents": list(multi_agent_orchestrator.active_agents.keys()),
        "count": len(multi_agent_orchestrator.active_agents),
        "max_agents": multi_agent_orchestrator.max_agents
    }


@router.get("/knowledge-gaps")
async def get_knowledge_gaps():
    """
    Get list of detected knowledge gaps.
    
    These are concepts/libraries that builds failed on,
    triggering automatic learning.
    """
    return {
        "gaps": multi_agent_orchestrator.knowledge_gaps,
        "total": len(multi_agent_orchestrator.knowledge_gaps),
        "recent": multi_agent_orchestrator.knowledge_gaps[-10:] if multi_agent_orchestrator.knowledge_gaps else []
    }


@router.get("/queue")
async def get_queue_status():
    """
    Get build queue status.
    
    Returns:
        Number of tasks waiting in queue
    """
    return {
        "queue_size": multi_agent_orchestrator.task_queue.qsize(),
        "active_agents": len(multi_agent_orchestrator.active_agents),
        "available_slots": multi_agent_orchestrator.max_agents - len(multi_agent_orchestrator.active_agents)
    }


@router.post("/config")
async def update_orchestrator_config(max_agents: int = None):
    """
    Update orchestrator configuration.
    
    Args:
        max_agents: Maximum number of parallel agents (1-20)
    """
    if max_agents is not None:
        if max_agents < 1 or max_agents > 20:
            raise HTTPException(status_code=400, detail="max_agents must be between 1 and 20")
        
        multi_agent_orchestrator.max_agents = max_agents
        logger.info(f"[ORCHESTRATOR-API] Updated max_agents to {max_agents}")
    
    return {
        "success": True,
        "config": {
            "max_agents": multi_agent_orchestrator.max_agents
        }
    }


@router.get("/metrics")
async def get_orchestrator_metrics():
    """
    Get orchestrator performance metrics.
    
    Returns:
    - Total tasks processed
    - Success rate
    - Average task duration
    - Knowledge gaps discovered
    """
    # Note: Would need to add metrics tracking to orchestrator
    # For now, return basic stats
    return {
        "knowledge_gaps_discovered": len(multi_agent_orchestrator.knowledge_gaps),
        "active_agents": len(multi_agent_orchestrator.active_agents),
        "queue_size": multi_agent_orchestrator.task_queue.qsize()
    }
