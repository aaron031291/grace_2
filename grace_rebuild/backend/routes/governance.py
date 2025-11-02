from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.sql import func
from ..governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from ..models import async_session
from ..auth import get_current_user

router = APIRouter(prefix="/api/governance", tags=["governance"])

class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    severity: str = "low"
    condition: str
    action: str = "allow"

@router.get("/policies")
async def list_policies():
    async with async_session() as session:
        result = await session.execute(select(GovernancePolicy))
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "severity": p.severity,
                "condition": p.condition,
                "action": p.action,
            }
            for p in result.scalars().all()
        ]

@router.post("/policies")
async def create_policy(data: PolicyCreate, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        policy = GovernancePolicy(
            name=data.name,
            description=data.description,
            severity=data.severity,
            condition=data.condition,
            action=data.action,
        )
        session.add(policy)
        await session.commit()
        await session.refresh(policy)
        return {"id": policy.id, "name": policy.name}

@router.get("/audit")
async def list_audit(limit: int = 100):
    async with async_session() as session:
        result = await session.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        )
        return [
            {
                "id": log.id,
                "actor": log.actor,
                "action": log.action,
                "resource": log.resource,
                "policy_checked": log.policy_checked,
                "result": log.result,
                "timestamp": log.timestamp,
            }
            for log in result.scalars().all()
        ]

@router.get("/approvals")
async def list_approvals():
    async with async_session() as session:
        result = await session.execute(select(ApprovalRequest))
        return [
            {
                "id": req.id,
                "event_id": req.event_id,
                "status": req.status,
                "requested_by": req.requested_by,
                "reason": req.reason,
                "created_at": req.created_at,
            }
            for req in result.scalars().all()
        ]

@router.post("/approvals/{request_id}/decision")
async def decide(request_id: int, decision: str, reason: str = "", current_user: str = Depends(get_current_user)):
    if decision not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid decision")
    
    async with async_session() as session:
        req = await session.get(ApprovalRequest, request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Approval not found")
        if req.status != "pending":
            raise HTTPException(status_code=400, detail="Already decided")
        
        req.status = "approved" if decision == "approve" else "rejected"
        req.decision_by = current_user
        req.decision_reason = reason
        req.decided_at = func.now()
        await session.commit()
    
    return {"status": req.status}
