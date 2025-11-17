"""
World Model Hub API - Phase 1
Unified interface for World Model Hub frontend
"""

from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel

from backend.world_model import world_model_service

router = APIRouter(prefix="/api/world_model_hub", tags=["world_model_hub"])


class ChatMessage(BaseModel):
    """Chat message to Grace"""
    message: str
    user_id: str = "user"
    context: Optional[Dict[str, Any]] = None


class ApprovalAction(BaseModel):
    """Approval or decline action"""
    trace_id: str
    action: str  # "approve" or "decline"
    reason: Optional[str] = None
    user_id: str = "user"


# ============================================================================
# ============================================================================

@router.get("/context")
async def get_context(
    query: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
) -> Dict[str, Any]:
    """
    Get current context for World Model Hub
    
    Returns:
        - Recent artifacts
        - Active missions
        - Pending approvals
        - Learning jobs
        - System health
        - Relevant knowledge (if query provided)
    """
    return await world_model_service.query_context(
        user_query=query,
        limit=limit
    )


@router.post("/chat")
async def chat_with_grace(message: ChatMessage) -> Dict[str, Any]:
    """
    Send a message to Grace and get a response
    
    Args:
        message: User message with optional context
    
    Returns:
        Grace's response with trace_id and relevant knowledge
    """
    return await world_model_service.chat_with_grace(
        message=message.message,
        user_id=message.user_id,
        context=message.context
    )


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    """
    Get execution trace details
    
    Args:
        trace_id: Trace ID to retrieve
    
    Returns:
        Events, actions, and reflections for the trace
    """
    return await world_model_service.link_trace(
        message_id="",  # Not needed for retrieval
        trace_id=trace_id
    )


# ============================================================================
# ============================================================================

@router.get("/artifacts")
async def list_artifacts(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    List recent artifacts from world model
    
    Args:
        limit: Maximum number of artifacts
        category: Filter by category (self, system, user, domain, temporal)
    
    Returns:
        List of artifacts
    """
    artifacts = await world_model_service.list_recent_artifacts(
        limit=limit,
        category=category
    )
    
    return {
        "artifacts": artifacts,
        "count": len(artifacts)
    }


# ============================================================================
# ============================================================================

@router.get("/missions")
async def list_missions(
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List missions
    
    Args:
        status: Filter by status (active, completed, failed)
    
    Returns:
        List of missions
    """
    missions = await world_model_service.list_active_missions()
    
    
    return {
        "missions": missions,
        "count": len(missions)
    }


# ============================================================================
# ============================================================================

@router.get("/approvals")
async def list_approvals(
    limit: int = Query(20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    List pending approvals
    
    Args:
        limit: Maximum number of approvals
    
    Returns:
        List of pending approvals
    """
    approvals = await world_model_service.list_pending_approvals(limit=limit)
    
    return {
        "approvals": approvals,
        "count": len(approvals)
    }


@router.post("/approvals/action")
async def handle_approval(action: ApprovalAction) -> Dict[str, Any]:
    """
    Approve or decline an action
    
    Args:
        action: Approval action (approve or decline)
    
    Returns:
        Result of the action
    """
    if action.action == "approve":
        return await world_model_service.approve_action(
            trace_id=action.trace_id,
            approved_by=action.user_id
        )
    elif action.action == "decline":
        return await world_model_service.decline_action(
            trace_id=action.trace_id,
            reason=action.reason or "Declined by user",
            declined_by=action.user_id
        )
    else:
        return {
            "success": False,
            "error": f"Invalid action: {action.action}. Must be 'approve' or 'decline'"
        }


# ============================================================================
# ============================================================================

@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Get World Model Hub health status
    
    Returns:
        System health and statistics
    """
    stats = world_model_service.get_stats()
    
    return {
        "status": "operational" if stats["initialized"] else "initializing",
        "stats": stats
    }


@router.post("/initialize")
async def initialize() -> Dict[str, Any]:
    """
    Initialize World Model Hub service
    
    Returns:
        Initialization status
    """
    await world_model_service.initialize()
    
    return {
        "status": "initialized",
        "message": "World Model Hub service initialized successfully"
    }
