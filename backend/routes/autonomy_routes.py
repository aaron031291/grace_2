"""
Autonomy & Shard Orchestration API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..autonomy_tiers import autonomy_manager, AutonomyTier
from ..shard_orchestrator import shard_orchestrator
from ..auth import get_current_user
from ..schemas import (
    AutonomyStatusResponse, AutonomyPoliciesResponse, AutonomyCheckResponse,
    AutonomyApprovalListResponse, AutonomyApprovalResponse, ShardTaskSubmitResponse, 
    ShardQueueResponse, AutonomyTaskStatusResponse, ShardStatusResponse
)

router = APIRouter(prefix="/api/autonomy", tags=["autonomy"])


# ==================== REQUEST MODELS ====================

class ActionRequest(BaseModel):
    action: str
    context: Dict
    approval_id: Optional[str] = None


class ApprovalDecision(BaseModel):
    approval_id: str
    approved: bool
    reason: str = ""


class TaskSubmission(BaseModel):
    domain: str
    action: str
    payload: Dict
    priority: int = 5
    dependencies: List[str] = []


# ==================== AUTONOMY ENDPOINTS ====================

@router.get("/status", response_model=AutonomyStatusResponse)
async def get_autonomy_status():
    """Get current autonomy configuration"""
    tier_counts = {
        "operational": len(autonomy_manager.TIER_1_ACTIONS),
        "code_touching": len(autonomy_manager.TIER_2_ACTIONS),
        "governance": len(autonomy_manager.TIER_3_ACTIONS)
    }
    
    return {
        "tiers": tier_counts,
        "pending_approvals": len(autonomy_manager.get_pending_approvals()),
        "total_policies": sum(tier_counts.values())
    }


@router.get("/policies", response_model=AutonomyPoliciesResponse)
async def list_policies():
    """List all action policies"""
    return {
        "tier_1_operational": [
            {
                "name": p.name,
                "description": p.description,
                "auto_approved": not p.approval_required,
                "impact": p.max_impact
            }
            for p in autonomy_manager.TIER_1_ACTIONS.values()
        ],
        "tier_2_code_touching": [
            {
                "name": p.name,
                "description": p.description,
                "approval_required": p.approval_required,
                "impact": p.max_impact
            }
            for p in autonomy_manager.TIER_2_ACTIONS.values()
        ],
        "tier_3_governance": [
            {
                "name": p.name,
                "description": p.description,
                "approval_required": p.approval_required,
                "impact": p.max_impact
            }
            for p in autonomy_manager.TIER_3_ACTIONS.values()
        ]
    }


@router.post("/check", response_model=AutonomyCheckResponse)
async def check_action(request: ActionRequest, user=Depends(get_current_user)):
    """Check if an action can be executed"""
    can_execute, approval_id = await autonomy_manager.can_execute(
        request.action,
        request.context
    )
    
    policy = autonomy_manager.all_policies.get(request.action)
    
    return {
        "can_execute": can_execute,
        "approval_id": approval_id,
        "requires_approval": policy.approval_required if policy else None,
        "tier": policy.tier.name if policy else None
    }


@router.get("/approvals", response_model=List[AutonomyApprovalListResponse])
async def get_pending_approvals(user=Depends(get_current_user)):
    """Get all pending approval requests"""
    return autonomy_manager.get_pending_approvals()


@router.post("/approve", response_model=AutonomyApprovalResponse)
async def approve_action(decision: ApprovalDecision, user=Depends(get_current_user)):
    """Approve or reject a pending action"""
    try:
        if decision.approved:
            await autonomy_manager.approve_action(
                decision.approval_id,
                user["username"],
                decision.reason
            )
            return {"status": "approved", "approval_id": decision.approval_id}
        else:
            await autonomy_manager.reject_action(
                decision.approval_id,
                user["username"],
                decision.reason
            )
            return {"status": "rejected", "approval_id": decision.approval_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== SHARD ORCHESTRATION ENDPOINTS ====================

@router.post("/tasks/submit", response_model=ShardTaskSubmitResponse)
async def submit_task(task: TaskSubmission, user=Depends(get_current_user)):
    """Submit a task to the shard orchestrator"""
    task_id = await shard_orchestrator.submit_task(
        domain=task.domain,
        action=task.action,
        payload=task.payload,
        priority=task.priority,
        dependencies=task.dependencies
    )
    
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a submitted task"""
    status = await shard_orchestrator.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


@router.get("/shards/status")
async def get_shards_status():
    """Get status of all shards"""
    return await shard_orchestrator.get_shard_status()


@router.get("/queue", response_model=ShardQueueResponse)
async def get_task_queue():
    """Get current task queue"""
    return {
        "queued": len(shard_orchestrator.task_queue),
        "completed": len(shard_orchestrator.completed_tasks),
        "tasks": [
            {
                "id": t.id,
                "domain": t.domain,
                "action": t.action,
                "priority": t.priority,
                "status": t.status
            }
            for t in shard_orchestrator.task_queue[:20]
        ]
    }
