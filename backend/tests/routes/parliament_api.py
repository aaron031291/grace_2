"""Parliament API Routes

RESTful endpoints for distributed governance and voting.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..parliament_engine import parliament_engine
from ..auth import get_current_user

router = APIRouter(prefix="/api/parliament", tags=["parliament"])

# ==================== Pydantic Models ====================

class MemberCreate(BaseModel):
    member_id: str = Field(..., description="Unique identifier")
    member_type: str = Field(..., description="Type: human, agent, grace_*")
    display_name: str = Field(..., description="Display name")
    role: str = Field(default="member", description="member, admin, observer")
    committees: List[str] = Field(default_factory=list, description="Committee memberships")
    vote_weight: float = Field(default=1.0, description="Voting power")

class SessionCreate(BaseModel):
    policy_name: str = Field(..., description="Governance policy name")
    action_type: str = Field(..., description="execute, approve, modify, reject")
    action_payload: Dict[str, Any] = Field(..., description="Action details")
    actor: str = Field(..., description="Who initiated action")
    category: Optional[str] = Field(None, description="Action category")
    resource: Optional[str] = Field(None, description="Resource affected")
    committee: str = Field(default="general", description="Committee to vote")
    quorum_required: int = Field(default=3, description="Minimum votes")
    approval_threshold: float = Field(default=0.5, description="Approval percentage")
    expires_in_hours: int = Field(default=24, description="Expiration time")
    hunter_alerts: List[Dict] = Field(default_factory=list, description="Security alerts")
    risk_level: str = Field(default="medium", description="low, medium, high, critical")

class VoteCast(BaseModel):
    vote: str = Field(..., description="approve, reject, abstain")
    reason: Optional[str] = Field(None, description="Vote explanation")
    automated: bool = Field(default=False, description="Auto-cast by agent")
    confidence: Optional[float] = Field(None, description="Confidence 0.0-1.0")

class CommitteeCreate(BaseModel):
    committee_name: str = Field(..., description="Unique committee name")
    display_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Committee purpose")
    responsibilities: List[str] = Field(default_factory=list, description="Action types")
    min_members: int = Field(default=3, description="Minimum members")
    max_members: int = Field(default=10, description="Maximum members")
    default_quorum: int = Field(default=3, description="Default quorum")
    default_threshold: float = Field(default=0.5, description="Default threshold")
    auto_assign_categories: List[str] = Field(default_factory=list, description="Auto-assign categories")
    auto_assign_risk_levels: List[str] = Field(default_factory=list, description="Auto-assign risk levels")

# ==================== Member Endpoints ====================

@router.post("/members")
async def create_member(
    member: MemberCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new parliament member"""
    try:
        result = await parliament_engine.create_member(
            member_id=member.member_id,
            member_type=member.member_type,
            display_name=member.display_name,
            role=member.role,
            committees=member.committees,
            vote_weight=member.vote_weight
        )
        return {"success": True, "member": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/members")
async def list_members(current_user: dict = Depends(get_current_user)):
    """List all parliament members"""
    try:
        members = await parliament_engine.list_members()
        return {"success": True, "members": members}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/members/{member_id}")
async def get_member(
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get member details and voting history"""
    try:
        member = await parliament_engine.get_member(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"success": True, "member": member}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Session Endpoints ====================

@router.post("/sessions")
async def create_session(
    session: SessionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new voting session"""
    try:
        result = await parliament_engine.create_session(
            policy_name=session.policy_name,
            action_type=session.action_type,
            action_payload=session.action_payload,
            actor=session.actor,
            category=session.category,
            resource=session.resource,
            committee=session.committee,
            quorum_required=session.quorum_required,
            approval_threshold=session.approval_threshold,
            expires_in_hours=session.expires_in_hours,
            hunter_alerts=session.hunter_alerts,
            risk_level=session.risk_level
        )
        return {"success": True, "session": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions")
async def list_sessions(
    status: Optional[str] = None,
    committee: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List voting sessions with filters"""
    try:
        sessions = await parliament_engine.list_sessions(
            status=status,
            committee=committee,
            limit=limit
        )
        return {"success": True, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get session details with all votes"""
    try:
        session = await parliament_engine.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "session": session}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/vote")
async def cast_vote(
    session_id: str,
    vote_data: VoteCast,
    current_user: dict = Depends(get_current_user)
):
    """Cast a vote in a session"""
    try:
        result = await parliament_engine.cast_vote(
            session_id=session_id,
            member_id=current_user.get("username"),
            vote=vote_data.vote,
            reason=vote_data.reason,
            automated=vote_data.automated,
            confidence=vote_data.confidence
        )
        return {"success": True, "vote": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current voting status of a session"""
    try:
        session = await parliament_engine.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "status": {
                "session_id": session["session_id"],
                "status": session["status"],
                "votes_approve": session["votes_approve"],
                "votes_reject": session["votes_reject"],
                "votes_abstain": session["votes_abstain"],
                "total_votes": session["total_votes"],
                "quorum_required": session["quorum_required"],
                "quorum_met": session["total_votes"] >= session["quorum_required"],
                "outcome": session["outcome"],
                "decision_reason": session["decision_reason"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Committee Endpoints ====================

@router.post("/committees")
async def create_committee(
    committee: CommitteeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new committee"""
    try:
        result = await parliament_engine.create_committee(
            committee_name=committee.committee_name,
            display_name=committee.display_name,
            description=committee.description,
            responsibilities=committee.responsibilities,
            min_members=committee.min_members,
            max_members=committee.max_members,
            default_quorum=committee.default_quorum,
            default_threshold=committee.default_threshold,
            auto_assign_categories=committee.auto_assign_categories,
            auto_assign_risk_levels=committee.auto_assign_risk_levels
        )
        return {"success": True, "committee": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/committees")
async def list_committees(current_user: dict = Depends(get_current_user)):
    """List all committees"""
    try:
        committees = await parliament_engine.list_committees()
        return {"success": True, "committees": committees}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/committees/{committee_name}")
async def get_committee(
    committee_name: str,
    current_user: dict = Depends(get_current_user)
):
    """Get committee details and members"""
    try:
        committee = await parliament_engine.get_committee(committee_name)
        if not committee:
            raise HTTPException(status_code=404, detail="Committee not found")
        return {"success": True, "committee": committee}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Statistics Endpoints ====================

@router.get("/stats")
async def get_parliament_stats(current_user: dict = Depends(get_current_user)):
    """Get parliament-wide statistics"""
    try:
        stats = await parliament_engine.get_statistics()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/member/{member_id}")
async def get_member_stats(
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get individual member statistics"""
    try:
        stats = await parliament_engine.get_member_statistics(member_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"success": True, "stats": stats}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
