"""
Governance API - Approval workflow endpoints

Exposes pending actions, approvals, and rejections for frontend consumption
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.action_gateway import action_gateway, GovernanceTier
from backend.world_model.world_model_service import world_model_service
from backend.event_bus import event_bus, Event, EventType

router = APIRouter()


class ApprovalAction(BaseModel):
    """Approval or rejection of a pending action"""
    trace_id: str = Field(..., description="Trace ID of the action to approve/reject")
    approved: bool = Field(..., description="True to approve, False to reject")
    reason: Optional[str] = Field(None, description="Optional reason for rejection")
    user_id: str = Field(default="user", description="User performing the approval")


@router.get("/governance/pending")
async def get_pending_approvals(limit: int = 20) -> Dict[str, Any]:
    """
    Get all pending approval requests
    
    Returns actions that require user approval (Tier 2+) and haven't been
    approved or declined yet.
    """
    try:
        all_actions = action_gateway.get_action_log()
        
        pending = [
            action for action in all_actions
            if not action.get("approved", False) and 
            not action.get("declined", False) and
            action.get("governance_tier") in ["supervised", "approval_required"]
        ]
        
        # Sort by timestamp (most recent first)
        pending.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "pending_approvals": pending[:limit],
            "total_pending": len(pending),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch pending approvals: {str(e)}"
        )


@router.post("/governance/approve")
async def approve_action(approval: ApprovalAction) -> Dict[str, Any]:
    """
    Approve a pending action
    
    This marks the action as approved in the Action Gateway and triggers
    execution if the action handler is registered.
    """
    try:
        if not approval.approved:
            # If not approved, redirect to reject endpoint
            return await reject_action(approval)
        
        result = await world_model_service.approve_action(
            trace_id=approval.trace_id,
            approved_by=approval.user_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Action not found")
            )
        
        # Publish approval event
        await event_bus.publish(Event(
            event_type=EventType.GOVERNANCE_CHECK,
            source="governance_api",
            data={
                "action": "approved",
                "trace_id": approval.trace_id,
                "approved_by": approval.user_id
            },
            trace_id=approval.trace_id
        ))
        
        return {
            "success": True,
            "action": "approved",
            "trace_id": approval.trace_id,
            "approved_by": approval.user_id,
            "timestamp": datetime.now().isoformat(),
            "details": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Approval failed: {str(e)}"
        )


@router.post("/governance/reject")
async def reject_action(approval: ApprovalAction) -> Dict[str, Any]:
    """
    Reject a pending action
    
    This marks the action as declined in the Action Gateway and prevents
    execution.
    """
    try:
        result = await world_model_service.decline_action(
            trace_id=approval.trace_id,
            reason=approval.reason or "User rejected",
            declined_by=approval.user_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Action not found")
            )
        
        # Publish rejection event
        await event_bus.publish(Event(
            event_type=EventType.GOVERNANCE_CHECK,
            source="governance_api",
            data={
                "action": "rejected",
                "trace_id": approval.trace_id,
                "rejected_by": approval.user_id,
                "reason": approval.reason
            },
            trace_id=approval.trace_id
        ))
        
        return {
            "success": True,
            "action": "rejected",
            "trace_id": approval.trace_id,
            "rejected_by": approval.user_id,
            "reason": approval.reason or "User rejected",
            "timestamp": datetime.now().isoformat(),
            "details": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Rejection failed: {str(e)}"
        )


@router.get("/governance/history")
async def get_governance_history(
    limit: int = 50,
    include_approved: bool = True,
    include_rejected: bool = True
) -> Dict[str, Any]:
    """
    Get governance history (approved and rejected actions)
    
    Useful for audit trail and governance analytics.
    """
    try:
        all_actions = action_gateway.get_action_log()
        
        # Filter based on parameters
        filtered = []
        for action in all_actions:
            if include_approved and action.get("approved"):
                filtered.append(action)
            elif include_rejected and action.get("declined"):
                filtered.append(action)
        
        # Sort by timestamp (most recent first)
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "history": filtered[:limit],
            "total_count": len(filtered),
            "limit": limit,
            "filters": {
                "approved": include_approved,
                "rejected": include_rejected
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch governance history: {str(e)}"
        )


@router.get("/governance/stats")
async def get_governance_stats() -> Dict[str, Any]:
    """
    Get governance statistics
    
    Returns aggregated stats about approvals, rejections, and pending actions.
    """
    try:
        all_actions = action_gateway.get_action_log()
        
        stats = {
            "total_actions": len(all_actions),
            "approved": len([a for a in all_actions if a.get("approved")]),
            "rejected": len([a for a in all_actions if a.get("declined")]),
            "pending": len([
                a for a in all_actions
                if not a.get("approved") and not a.get("declined") and
                a.get("governance_tier") in ["supervised", "approval_required"]
            ]),
            "autonomous": len([
                a for a in all_actions if a.get("governance_tier") == "autonomous"
            ]),
            "by_tier": {
                "autonomous": len([a for a in all_actions if a.get("governance_tier") == "autonomous"]),
                "supervised": len([a for a in all_actions if a.get("governance_tier") == "supervised"]),
                "approval_required": len([a for a in all_actions if a.get("governance_tier") == "approval_required"]),
                "blocked": len([a for a in all_actions if a.get("governance_tier") == "blocked"])
            },
            "approval_rate": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate approval rate
        total_decisions = stats["approved"] + stats["rejected"]
        if total_decisions > 0:
            stats["approval_rate"] = stats["approved"] / total_decisions
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch governance stats: {str(e)}"
        )
