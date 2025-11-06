from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import Optional
import os
from ..governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from ..models import async_session
from ..auth import get_current_user
from ..verification_middleware import verify_action
from ..logging_utils import log_event
from ..rate_limit import rate_limited

router = APIRouter(prefix="/api/governance", tags=["governance"])

class PolicyCreate(BaseModel):
    name: str
    description: str = ""
    severity: str = "low"
    condition: str
    action: str = "allow"

class ApprovalCreate(BaseModel):
    event_id: int
    reason: str = ""

class ApprovalDecision(BaseModel):
    decision: str  # "approve" | "reject"
    reason: str = ""


def _deciders_allowlist() -> Optional[set]:
    """Parse APPROVAL_DECIDERS env var into a set of usernames.
    If unset or empty, returns None meaning "no enforcement" (allow all).
    """
    raw = os.getenv("APPROVAL_DECIDERS", "").strip()
    if not raw:
        return None
    return {u.strip() for u in raw.split(",") if u.strip()}

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
@verify_action("policy_create", lambda data: data.get("name", "unknown"))
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

@router.post("/approvals")
@verify_action("approval_create", lambda data: f"event_{data.get('event_id', 'unknown')}")
async def create_approval(data: ApprovalCreate, request: Request, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        req = ApprovalRequest(
            event_id=data.event_id,
            status="pending",
            requested_by=current_user,
            reason=data.reason,
        )
        session.add(req)
        await session.commit()
        await session.refresh(req)
        # Structured log (verification_id is added to response by verify_action wrapper)
        req_id = request.headers.get("X-Request-ID") or os.getenv("REQUEST_ID_FALLBACK", "")
        log_event(
            action="approval_create",
            actor=current_user,
            resource=f"event_{data.event_id}",
            outcome="created",
            payload={"reason": data.reason},
            extras={"approval_id": req.id, "status": req.status},
            request_id=req_id or None,
        )
        return {
            "id": req.id,
            "event_id": req.event_id,
            "status": req.status,
            "requested_by": req.requested_by,
            "reason": req.reason,
            "created_at": req.created_at,
        }

@router.get("/approvals/stats")
async def approvals_stats(current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        # Simple counts by status
        result = await session.execute(select(ApprovalRequest.status))
        statuses = [s for s, in result.all()]
        counts = {"pending": 0, "approved": 0, "rejected": 0}
        for s in statuses:
            counts[s] = counts.get(s, 0) + 1
        return counts

@router.get("/approvals/{request_id}")
async def get_approval(request_id: int, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        req = await session.get(ApprovalRequest, request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Approval not found")
        return {
            "id": req.id,
            "event_id": req.event_id,
            "status": req.status,
            "requested_by": req.requested_by,
            "reason": req.reason,
            "decision_by": req.decision_by,
            "decision_reason": req.decision_reason,
            "created_at": req.created_at,
            "decided_at": req.decided_at,
        }

@router.get("/approvals")
async def list_approvals(status: Optional[str] = None, requested_by: Optional[str] = None, limit: int = 50, current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        stmt = select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc()).limit(limit)
        if status:
            stmt = stmt.where(ApprovalRequest.status == status)
        if requested_by:
            stmt = stmt.where(ApprovalRequest.requested_by == requested_by)
        result = await session.execute(stmt)
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
@rate_limited("approval_decision")
@verify_action("approval_decision", lambda data: f"request_{data.get('request_id', 'unknown')}")
async def decide(request_id: int, body: ApprovalDecision, request: Request, current_user: str = Depends(get_current_user)):
    # RBAC allowlist: enforce only if APPROVAL_DECIDERS is set
    deciders = _deciders_allowlist()
    if deciders is not None and current_user not in deciders:
        raise HTTPException(status_code=403, detail="Not authorized to decide approvals")

    if body.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid decision")

    async with async_session() as session:
        req = await session.get(ApprovalRequest, request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Approval not found")
        if req.status != "pending":
            raise HTTPException(status_code=400, detail="Already decided")

        req.status = "approved" if body.decision == "approve" else "rejected"
        req.decision_by = current_user
        req.decision_reason = body.reason
        req.decided_at = func.now()
        await session.commit()
        await session.refresh(req)
        # Structured log
        req_id = request.headers.get("X-Request-ID") or os.getenv("REQUEST_ID_FALLBACK", "")
        log_event(
            action="approval_decision",
            actor=current_user,
            resource=f"request_{request_id}",
            outcome=req.status,
            payload={"reason": body.reason},
            extras={"approval_id": req.id},
            request_id=req_id or None,
        )
        return {
            "id": req.id,
            "status": req.status,
            "decision_by": req.decision_by,
            "decision_reason": req.decision_reason,
            "decided_at": req.decided_at,
        }

@router.get("/approvals/stats")
async def approvals_stats(current_user: str = Depends(get_current_user)):
    async with async_session() as session:
        # Simple counts by status
        result = await session.execute(select(ApprovalRequest.status))
        statuses = [s for s, in result.all()]
        counts = {"pending": 0, "approved": 0, "rejected": 0}
        for s in statuses:
            counts[s] = counts.get(s, 0) + 1
        return counts
