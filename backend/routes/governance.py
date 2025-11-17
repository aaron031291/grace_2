from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import Optional
import os
import time
from collections import deque
from ..governance_models import GovernancePolicy, AuditLog, ApprovalRequest
from ..models import async_session
from ..auth import get_current_user
from ..verification_middleware import verify_action, verification_middleware
from ..logging_utils import log_event
from ..constitutional_verifier import constitutional_verifier
from ..governance import governance_engine
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


# Internal helpers used with verification envelopes to keep endpoint signatures FastAPI-friendly
async def _create_approval_db(*, data: ApprovalCreate, current_user: str) -> dict:
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
        return {
            "id": req.id,
            "event_id": req.event_id,
            "status": req.status,
            "requested_by": req.requested_by,
            "reason": req.reason,
            "created_at": req.created_at,
        }


async def _decide_approval_db(*, request_id: int, decision: str, reason: str, current_user: str) -> dict:
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
        await session.refresh(req)
        return {
            "id": req.id,
            "status": req.status,
            "decision_by": req.decision_by,
            "decision_reason": req.decision_reason,
            "decided_at": req.decided_at,
        }

# Simple in-module per-user limiter for decision endpoint to ensure predictable test behavior
_DECISION_EVENTS: dict[str, deque] = {}


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
async def create_approval(data: ApprovalCreate, request: Request, current_user: str = Depends(get_current_user)):
    # Build payload for verification/governance checks
    payload = data.dict()
    resource = f"event_{payload.get('event_id', 'unknown')}"

    # Constitutional + governance checks
    const_result = await constitutional_verifier.verify_action(
        actor=current_user,
        action_type="approval_create",
        resource=resource,
        payload=payload,
        confidence=payload.get("confidence", 1.0),
        context=payload.get("context", {}),
    )
    if not const_result.get("allowed", True):
        violations = const_result.get("violations", [])
        violation_msg = ", ".join([v.get("reason", "Unknown") for v in violations[:3]])
        raise HTTPException(status_code=403, detail=f"Blocked by constitutional verification: {violation_msg}")

    gov_decision = await governance_engine.check(
        actor=current_user,
        action="approval_create",
        resource=resource,
        payload=payload,
    )
    if gov_decision.get("decision") == "block":
        raise HTTPException(status_code=403, detail=f"Blocked by governance: {gov_decision.get('policy', 'unknown')}")

    # Verification envelope (sign inputs/outputs around the DB action)
    result_dict, action_id = await verification_middleware.verify_and_record(
        actor=current_user,
        action_type="approval_create",
        resource=resource,
        input_data=payload,
        action_func=_create_approval_db,
        data=data,
        current_user=current_user,
    )

    # Structured log
    req_id = request.headers.get("X-Request-ID") or os.getenv("REQUEST_ID_FALLBACK", "")
    log_event(
        action="approval_create",
        actor=current_user,
        resource=resource,
        outcome="created",
        payload={"reason": data.reason},
        extras={"approval_id": result_dict["id"], "status": result_dict["status"]},
        request_id=req_id or None,
        verification_id=action_id,
    )

    result_dict["_verification_id"] = action_id
    return result_dict

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
async def decide(request_id: int, body: ApprovalDecision, request: Request, current_user: str = Depends(get_current_user)):
    # RBAC allowlist: enforce only if APPROVAL_DECIDERS is set
    deciders = _deciders_allowlist()
    if deciders is not None and current_user not in deciders:
        raise HTTPException(status_code=403, detail="Not authorized to decide approvals")

    if body.decision not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="Invalid decision")

    # Rate limiting (per-user) — local predictable limiter for tests/dev
    try:
        capacity = int(os.getenv("APPROVAL_DECISION_RATE_PER_MIN", "10"))
    except Exception:
        capacity = 10
    if os.getenv("RATE_LIMIT_BYPASS", "").lower() not in {"1", "true", "yes", "on"}:
        window = 60
        q = _DECISION_EVENTS.setdefault(current_user, deque())
        now = time.monotonic()
        cutoff = now - window
        # purge old
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= capacity:
            # compute retry-after
            oldest = q[0]
            retry_after = max(1, int(window - (now - oldest)))
            headers = {"Retry-After": str(retry_after)}
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.", headers=headers)
        q.append(now)

    # Prepare payload and checks
    payload = {"request_id": request_id, "decision": body.decision, "reason": body.reason}
    resource = f"request_{request_id}"

    const_result = await constitutional_verifier.verify_action(
        actor=current_user,
        action_type="approval_decision",
        resource=resource,
        payload=payload,
        confidence=1.0,
        context={},
    )
    if not const_result.get("allowed", True):
        violations = const_result.get("violations", [])
        violation_msg = ", ".join([v.get("reason", "Unknown") for v in violations[:3]])
        raise HTTPException(status_code=403, detail=f"Blocked by constitutional verification: {violation_msg}")

    gov_decision = await governance_engine.check(
        actor=current_user,
        action="approval_decision",
        resource=resource,
        payload=payload,
    )
    if gov_decision.get("decision") == "block":
        raise HTTPException(status_code=403, detail=f"Blocked by governance: {gov_decision.get('policy', 'unknown')}")

    # Verification envelope around the DB update
    result_dict, action_id = await verification_middleware.verify_and_record(
        actor=current_user,
        action_type="approval_decision",
        resource=resource,
        input_data=payload,
        action_func=_decide_approval_db,
        request_id=request_id,
        decision=body.decision,
        reason=body.reason,
        current_user=current_user,
    )

    # Structured log
    req_id = request.headers.get("X-Request-ID") or os.getenv("REQUEST_ID_FALLBACK", "")
    log_event(
        action="approval_decision",
        actor=current_user,
        resource=resource,
        outcome=result_dict.get("status", "unknown"),
        payload={"reason": body.reason},
        extras={"approval_id": result_dict.get("id")},
        request_id=req_id or None,
        verification_id=action_id,
    )

    # If approved, auto-execute via execute_verified_action
    if body.decision == "approve":
        async with async_session() as session:
            approval_req = await session.get(ApprovalRequest, request_id)
            if approval_req:
                # Publish approval.granted event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="approval.granted",
                    source="governance",
                    actor=current_user,
                    resource=f"approval_{request_id}",
                    payload={
                        "approval_id": request_id,
                        "event_id": approval_req.event_id,
                        "reason": body.reason,
                        "tier": "tier_2"  # Default tier, can be enhanced
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
                
                # Execute the approved action (in background to avoid blocking response)
                # Note: In production, this should be handled by a background task
                # For now, we just publish the event for InputSentinel to pick up

    result_dict["_verification_id"] = action_id
    return result_dict

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
