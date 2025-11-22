"""
Parliament Domain Router
Consolidates all governance operations: proposals, votes, approvals, audits

Bounded Context: Governance and democratic decision-making
- Proposals: governance proposals and policy changes
- Votes: voting on proposals and decisions
- Approvals: approval workflows and escalations
- Audits: governance audit trails and compliance

Canonical Verbs: propose, vote, approve, audit, escalate, override
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..auth import get_current_user
from ..parliament_engine import parliament_engine
from ..governance import governance_engine
from ..human_collaboration import collaboration_manager

router = APIRouter(prefix="/api/parliament", tags=["Parliament Domain"])


class ProposalRequest(BaseModel):
    title: str
    description: str
    proposal_type: str  # "policy", "approval", "override", "constitutional"
    content: Dict[str, Any]
    voting_period_hours: int = 24
    required_quorum: float = 0.5


class VoteRequest(BaseModel):
    proposal_id: str
    vote: str  # "approve", "reject", "abstain"
    reasoning: Optional[str] = None


class ApprovalRequest(BaseModel):
    resource: str
    action: str
    risk_level: str
    justification: str
    auto_escalate: bool = True


class AuditRequest(BaseModel):
    resource: Optional[str] = None
    action: Optional[str] = None
    time_range_hours: int = 24


@router.post("/propose")
async def create_proposal(
    request: ProposalRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a governance proposal"""
    try:
        proposal = await parliament_engine.create_proposal(
            title=request.title,
            description=request.description,
            proposal_type=request.proposal_type,
            content=request.content,
            proposer=current_user,
            voting_period=request.voting_period_hours,
            quorum=request.required_quorum
        )

        return {
            "proposal_id": proposal.get("id"),
            "title": request.title,
            "type": request.proposal_type,
            "status": "proposed",
            "voting_ends": proposal.get("voting_ends")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vote")
async def cast_vote(
    request: VoteRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Cast a vote on a proposal"""
    try:
        vote = await parliament_engine.cast_vote(
            proposal_id=request.proposal_id,
            voter=current_user,
            vote=request.vote,
            reasoning=request.reasoning
        )

        return {
            "proposal_id": request.proposal_id,
            "vote": request.vote,
            "voter": current_user,
            "status": "recorded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve")
async def request_approval(
    request: ApprovalRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Request approval for an action"""
    try:
        approval = await governance_engine.create_approval_request(
            resource=request.resource,
            action=request.action,
            risk_level=request.risk_level,
            requester=current_user,
            justification=request.justification,
            auto_escalate=request.auto_escalate
        )

        return {
            "approval_id": approval.get("id"),
            "resource": request.resource,
            "action": request.action,
            "status": "pending",
            "escalated": approval.get("escalated", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audit")
async def perform_audit(
    request: AuditRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform governance audit"""
    try:
        audit = await parliament_engine.perform_audit(
            resource=request.resource,
            action=request.action,
            time_range_hours=request.time_range_hours
        )

        return {
            "audit_id": audit.get("id"),
            "resource": request.resource,
            "action": request.action,
            "time_range_hours": request.time_range_hours,
            "findings": audit.get("findings", []),
            "compliance_score": audit.get("compliance_score", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals")
async def list_proposals(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List governance proposals"""
    try:
        proposals = await parliament_engine.list_proposals(status=status)
        return {
            "proposals": proposals,
            "count": len(proposals),
            "filter": {"status": status} if status else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approvals")
async def list_approvals(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """List pending approvals"""
    try:
        approvals = await governance_engine.list_approvals(status=status)
        return {
            "approvals": approvals,
            "count": len(approvals),
            "filter": {"status": status} if status else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/votes/{proposal_id}")
async def get_proposal_votes(
    proposal_id: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get votes for a proposal"""
    try:
        votes = await parliament_engine.get_proposal_votes(proposal_id)
        return {
            "proposal_id": proposal_id,
            "votes": votes,
            "summary": {
                "approve": sum(1 for v in votes if v.get("vote") == "approve"),
                "reject": sum(1 for v in votes if v.get("vote") == "reject"),
                "abstain": sum(1 for v in votes if v.get("vote") == "abstain"),
                "total": len(votes)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalate/{approval_id}")
async def escalate_approval(
    approval_id: str,
    reason: str = "Manual escalation requested",
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Escalate an approval to higher authority"""
    try:
        escalation = await governance_engine.escalate_approval(
            approval_id=approval_id,
            reason=reason,
            escalated_by=current_user
        )

        return {
            "approval_id": approval_id,
            "status": "escalated",
            "escalation_level": escalation.get("level"),
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/override/{approval_id}")
async def override_approval(
    approval_id: str,
    justification: str,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Override an approval decision"""
    try:
        override = await governance_engine.override_approval(
            approval_id=approval_id,
            justification=justification,
            overridden_by=current_user
        )

        return {
            "approval_id": approval_id,
            "status": "overridden",
            "justification": justification,
            "overridden_by": current_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/constitution")
async def get_constitution(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current constitution/rules"""
    try:
        constitution = await parliament_engine.get_constitution()
        return {
            "constitution": constitution,
            "last_updated": constitution.get("last_updated"),
            "version": constitution.get("version")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance")
async def get_compliance_status(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get overall compliance status"""
    try:
        compliance = await parliament_engine.get_compliance_status()
        return {
            "compliance_score": compliance.get("score", 0.0),
            "violations": compliance.get("violations", []),
            "last_audit": compliance.get("last_audit"),
            "status": "compliant" if compliance.get("score", 0) > 0.8 else "non_compliant"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collaborate/{resource}")
async def initiate_collaboration(
    resource: str,
    action: str,
    context: Dict[str, Any],
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Initiate human-AI collaboration"""
    try:
        collaboration = await collaboration_manager.initiate_collaboration(
            resource=resource,
            action=action,
            context=context,
            initiator=current_user
        )

        return {
            "collaboration_id": collaboration.get("id"),
            "resource": resource,
            "action": action,
            "status": "initiated",
            "participants": collaboration.get("participants", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
