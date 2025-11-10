"""Parliament Engine - Distributed Governance System

Manages multi-agent voting, quorum consensus, and distributed decision-making.
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session

from .models import async_session
from .parliament_models import (
    GovernanceMember, GovernanceSession, GovernanceVote,
    CommitteeDefinition, ParliamentConfig
)
from .verification import VerificationEngine
from .immutable_log import ImmutableLog as ImmutableLogger
from .metric_publishers import ParliamentMetrics

class ParliamentEngine:
    """Multi-agent voting and consensus system"""
    
    def __init__(self):
        self.verification = VerificationEngine()
        self.audit = ImmutableLogger()
    
    async def create_member(
        self,
        member_id: str,
        member_type: str,
        display_name: str,
        role: str = "member",
        committees: List[str] = None,
        vote_weight: float = 1.0
    ) -> Dict[str, Any]:
        """
        Create a new parliament member
        
        Args:
            member_id: Unique identifier (username, agent_name, etc.)
            member_type: Type (human, agent, grace_reflection, etc.)
            display_name: Human-readable name
            role: Role (member, admin, observer)
            committees: List of committee names
            vote_weight: Voting power (1.0 = standard vote)
        
        Returns:
            Member details
        """
        
        async with async_session() as session:
            member = GovernanceMember(
                member_id=member_id,
                member_type=member_type,
                display_name=display_name,
                role=role,
                committees=committees or [],
                vote_weight=vote_weight,
                active=True
            )
            
            session.add(member)
            await session.commit()
            await session.refresh(member)
            
            # Log to audit
            await self.audit.log_event(
                actor="parliament_engine",
                action="member_created",
                resource=f"member_{member.id}",
                result="success",
                details={
                    "member_id": member_id,
                    "type": member_type,
                    "role": role
                }
            )
            
            return {
                "id": member.id,
                "member_id": member.member_id,
                "display_name": member.display_name,
                "type": member_type,
                "role": role,
                "vote_weight": vote_weight
            }
    
    async def create_session(
        self,
        policy_name: str,
        action_type: str,
        action_payload: Dict[str, Any],
        actor: str,
        category: Optional[str] = None,
        resource: Optional[str] = None,
        committee: str = "general",
        quorum_required: int = 3,
        approval_threshold: float = 0.5,
        expires_in_hours: int = 24,
        hunter_alerts: List[Dict] = None,
        risk_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Create a new governance session for voting
        
        Args:
            policy_name: Name of governance policy triggering vote
            action_type: Type of action (execute, approve, modify, reject)
            action_payload: Full action details
            actor: Who initiated the action
            category: Category (file_access, execution, etc.)
            resource: Resource being acted upon
            committee: Which committee should vote
            quorum_required: Minimum votes needed
            approval_threshold: Percentage needed to approve (0.5 = majority)
            expires_in_hours: Hours until session expires
            hunter_alerts: Attached security alerts
            risk_level: Risk level (low, medium, high, critical)
        
        Returns:
            Session details with voting instructions
        """
        
        session_id = str(uuid.uuid4())
        
        # Create verification envelope
        action_hash = hashlib.sha256(str(action_payload).encode()).hexdigest()
        verification_id = self.verification.create_envelope(
            action_id=session_id,
            actor=actor,
            action_type=f"governance_session_{action_type}",
            resource=resource or "unknown",
            input_data={
                "policy": policy_name,
                "action_hash": action_hash,
                "committee": committee
            }
        )
        
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        async with async_session() as session:
            gov_session = GovernanceSession(
                session_id=session_id,
                policy_name=policy_name,
                action_type=action_type,
                action_payload=action_payload,
                category=category,
                resource=resource,
                actor=actor,
                committee=committee,
                quorum_required=quorum_required,
                approval_threshold=approval_threshold,
                status="pending",
                hunter_alerts=hunter_alerts or [],
                verification_envelope_id=verification_id,
                risk_level=risk_level,
                expires_at=expires_at
            )
            
            session.add(gov_session)
            await session.commit()
            await session.refresh(gov_session)
            
            db_id = gov_session.id
        
        # Log to audit
        audit_id = await self.audit.log_event(
            actor="parliament_engine",
            action="session_created",
            resource=f"session_{session_id}",
            result="pending",
            details={
                "policy": policy_name,
                "action_type": action_type,
                "committee": committee,
                "quorum": quorum_required,
                "risk_level": risk_level
            }
        )
        
        # Update with audit ID
        async with async_session() as session:
            await session.execute(
                update(GovernanceSession)
                .where(GovernanceSession.id == db_id)
                .values(audit_log_id=audit_id, status="voting", voting_started_at=datetime.utcnow())
            )
            await session.commit()
        
        # Notify committee members (TODO: integrate with notification system)
        await self._notify_committee(committee, session_id, policy_name, risk_level)
        
        return {
            "session_id": session_id,
            "status": "voting",
            "committee": committee,
            "quorum_required": quorum_required,
            "approval_threshold": approval_threshold,
            "expires_at": expires_at.isoformat(),
            "verification_id": verification_id,
            "message": f"Session created. Quorum requires {quorum_required} votes with {approval_threshold*100}% approval."
        }
    
    async def cast_vote(
        self,
        session_id: str,
        member_id: str,
        vote: str,  # approve, reject, abstain
        reason: Optional[str] = None,
        automated: bool = False,
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Cast a vote in a session
        
        Args:
            session_id: Session identifier
            member_id: Member casting vote
            vote: Vote choice (approve, reject, abstain)
            reason: Explanation for vote
            automated: True if cast by agent/Grace
            confidence: Confidence level (0.0-1.0) for automated votes
        
        Returns:
            Vote confirmation and updated session status
        """
        
        vote = vote.lower()
        if vote not in ["approve", "reject", "abstain"]:
            raise ValueError(f"Invalid vote: {vote}. Must be approve, reject, or abstain.")
        
        # Get session
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceSession).where(GovernanceSession.session_id == session_id)
            )
            gov_session = result.scalar_one_or_none()
            
            if not gov_session:
                raise ValueError(f"Session not found: {session_id}")
            
            if gov_session.status not in ["pending", "voting"]:
                raise ValueError(f"Session is {gov_session.status}, cannot vote")
            
            # Check if expired
            if gov_session.expires_at and datetime.utcnow() > gov_session.expires_at:
                await self._expire_session(gov_session.id)
                raise ValueError("Session has expired")
            
            # Get member
            member_result = await session.execute(
                select(GovernanceMember).where(GovernanceMember.member_id == member_id)
            )
            member = member_result.scalar_one_or_none()
            
            if not member:
                raise ValueError(f"Member not found: {member_id}")
            
            if not member.active or member.suspended:
                raise ValueError(f"Member is not active: {member_id}")
            
            # Check if already voted
            existing_vote = await session.execute(
                select(GovernanceVote).where(
                    and_(
                        GovernanceVote.session_id == gov_session.id,
                        GovernanceVote.member_id == member.id
                    )
                )
            )
            if existing_vote.scalar_one_or_none():
                raise ValueError(f"Member {member_id} has already voted in this session")
            
            # Create vote signature
            vote_data = f"{session_id}:{member_id}:{vote}:{reason or ''}"
            vote_signature = hashlib.sha256(vote_data.encode()).hexdigest()
            
            # Record vote
            gov_vote = GovernanceVote(
                session_id=gov_session.id,
                member_id=member.id,
                vote=vote,
                vote_weight=member.vote_weight,
                reason=reason,
                automated=automated,
                confidence=confidence,
                vote_signature=vote_signature,
                verification_status="verified"
            )
            
            session.add(gov_vote)
            
            # Update tallies
            if vote == "approve":
                gov_session.votes_approve += 1
                gov_session.weighted_approve += member.vote_weight
                member.votes_approved += 1
                # Publish metrics for approval vote
                await ParliamentMetrics.publish_vote_completed(1.0)
            elif vote == "reject":
                gov_session.votes_reject += 1
                gov_session.weighted_reject += member.vote_weight
                member.votes_rejected += 1
                # Publish metrics for rejection vote
                await ParliamentMetrics.publish_vote_completed(0.0)
            else:  # abstain
                gov_session.votes_abstain += 1
                gov_session.weighted_abstain += member.vote_weight
                member.votes_abstained += 1
                # Publish metrics for abstention
                await ParliamentMetrics.publish_vote_completed(0.5)

            gov_session.total_votes += 1
            gov_session.total_weighted += member.vote_weight
            member.total_votes += 1
            member.last_vote_at = datetime.utcnow()

            await session.commit()
            
            vote_id = gov_vote.id
            session_db_id = gov_session.id
        
        # Log to audit
        await self.audit.log_event(
            actor=member_id,
            action=f"vote_{vote}",
            resource=f"session_{session_id}",
            result="recorded",
            details={
                "vote": vote,
                "reason": reason,
                "automated": automated,
                "signature": vote_signature
            }
        )
        
        # Check if decision can be made
        decision = await self._check_decision(session_db_id)
        
        return {
            "vote_id": vote_id,
            "session_id": session_id,
            "vote": vote,
            "member": member_id,
            "decision": decision
        }
    
    async def _check_decision(self, session_db_id: int) -> Dict[str, Any]:
        """Check if session has reached quorum and make decision"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceSession).where(GovernanceSession.id == session_db_id)
            )
            gov_session = result.scalar_one()
            
            # Check if quorum reached
            if gov_session.total_votes < gov_session.quorum_required:
                return {
                    "status": "voting",
                    "votes_needed": gov_session.quorum_required - gov_session.total_votes,
                    "approve": gov_session.votes_approve,
                    "reject": gov_session.votes_reject,
                    "abstain": gov_session.votes_abstain
                }
            
            # Quorum reached, calculate outcome
            total_decisive = gov_session.votes_approve + gov_session.votes_reject
            if total_decisive == 0:
                # All abstained
                outcome = "tie"
                decision_reason = "All votes abstained"
            else:
                approval_rate = gov_session.votes_approve / total_decisive
                
                if approval_rate >= gov_session.approval_threshold:
                    outcome = "approved"
                    decision_reason = f"Approved with {approval_rate*100:.1f}% support"
                else:
                    outcome = "rejected"
                    decision_reason = f"Rejected with {approval_rate*100:.1f}% support (threshold: {gov_session.approval_threshold*100}%)"
            
            # Update session
            gov_session.status = outcome
            gov_session.outcome = outcome
            gov_session.decision_reason = decision_reason
            gov_session.decided_at = datetime.utcnow()
            
            await session.commit()
        
        # Log decision
        await self.audit.log_event(
            actor="parliament_engine",
            action=f"session_{outcome}",
            resource=f"session_{gov_session.session_id}",
            result=outcome,
            details={
                "votes_approve": gov_session.votes_approve,
                "votes_reject": gov_session.votes_reject,
                "votes_abstain": gov_session.votes_abstain,
                "reason": decision_reason
            }
        )
        
        return {
            "status": outcome,
            "outcome": outcome,
            "reason": decision_reason,
            "votes_approve": gov_session.votes_approve,
            "votes_reject": gov_session.votes_reject,
            "votes_abstain": gov_session.votes_abstain,
            "decided_at": gov_session.decided_at.isoformat() if gov_session.decided_at else None
        }
    
    async def _expire_session(self, session_db_id: int):
        """Mark session as expired"""
        
        async with async_session() as session:
            await session.execute(
                update(GovernanceSession)
                .where(GovernanceSession.id == session_db_id)
                .values(
                    status="expired",
                    outcome="expired",
                    decision_reason="Session expired without reaching quorum",
                    decided_at=datetime.utcnow()
                )
            )
            await session.commit()
    
    async def _notify_committee(
        self,
        committee: str,
        session_id: str,
        policy_name: str,
        risk_level: str
    ):
        """Notify committee members of new session (TODO: implement notifications)"""
        
        # TODO: Send notifications via:
        # - CLI notifications
        # - WebSocket events
        # - Email/Slack for critical decisions
        # - Task creation for human members
        
        print(f"📢 Notification: Committee '{committee}' has new session {session_id}")
        print(f"   Policy: {policy_name} | Risk: {risk_level}")
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details with votes"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceSession).where(GovernanceSession.session_id == session_id)
            )
            gov_session = result.scalar_one_or_none()
            
            if not gov_session:
                return None
            
            # Get votes
            votes_result = await session.execute(
                select(GovernanceVote, GovernanceMember)
                .join(GovernanceMember)
                .where(GovernanceVote.session_id == gov_session.id)
            )
            votes_data = votes_result.all()
            
            votes = [
                {
                    "member_id": member.member_id,
                    "display_name": member.display_name,
                    "vote": vote.vote,
                    "reason": vote.reason,
                    "automated": vote.automated,
                    "confidence": vote.confidence,
                    "created_at": vote.created_at.isoformat() if vote.created_at else None
                }
                for vote, member in votes_data
            ]
            
            return {
                "session_id": gov_session.session_id,
                "policy_name": gov_session.policy_name,
                "action_type": gov_session.action_type,
                "action_payload": gov_session.action_payload,
                "category": gov_session.category,
                "resource": gov_session.resource,
                "actor": gov_session.actor,
                "committee": gov_session.committee,
                "quorum_required": gov_session.quorum_required,
                "approval_threshold": gov_session.approval_threshold,
                "status": gov_session.status,
                "votes_approve": gov_session.votes_approve,
                "votes_reject": gov_session.votes_reject,
                "votes_abstain": gov_session.votes_abstain,
                "total_votes": gov_session.total_votes,
                "outcome": gov_session.outcome,
                "decision_reason": gov_session.decision_reason,
                "hunter_alerts": gov_session.hunter_alerts,
                "risk_level": gov_session.risk_level,
                "created_at": gov_session.created_at.isoformat() if gov_session.created_at else None,
                "decided_at": gov_session.decided_at.isoformat() if gov_session.decided_at else None,
                "expires_at": gov_session.expires_at.isoformat() if gov_session.expires_at else None,
                "votes": votes
            }
    
    async def list_sessions(
        self,
        status: Optional[str] = None,
        committee: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List governance sessions"""
        
        async with async_session() as session:
            query = select(GovernanceSession).order_by(GovernanceSession.created_at.desc())
            
            if status:
                query = query.where(GovernanceSession.status == status)
            if committee:
                query = query.where(GovernanceSession.committee == committee)
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            sessions = result.scalars().all()
            
            return [
                {
                    "session_id": s.session_id,
                    "policy_name": s.policy_name,
                    "action_type": s.action_type,
                    "status": s.status,
                    "committee": s.committee,
                    "votes": f"{s.total_votes}/{s.quorum_required}",
                    "outcome": s.outcome,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in sessions
            ]
    
    async def list_members(self) -> List[Dict[str, Any]]:
        """List all parliament members"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceMember).order_by(GovernanceMember.created_at.desc())
            )
            members = result.scalars().all()
            
            return [
                {
                    "id": m.id,
                    "member_id": m.member_id,
                    "display_name": m.display_name,
                    "type": m.member_type,
                    "role": m.role,
                    "committees": m.committees,
                    "vote_weight": m.vote_weight,
                    "active": m.active,
                    "suspended": m.suspended,
                    "total_votes": m.total_votes
                }
                for m in members
            ]
    
    async def get_member(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member details with voting history"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceMember).where(GovernanceMember.member_id == member_id)
            )
            member = result.scalar_one_or_none()
            
            if not member:
                return None
            
            return {
                "id": member.id,
                "member_id": member.member_id,
                "display_name": member.display_name,
                "type": member.member_type,
                "role": member.role,
                "committees": member.committees,
                "vote_weight": member.vote_weight,
                "active": member.active,
                "suspended": member.suspended,
                "total_votes": member.total_votes,
                "votes_approved": member.votes_approved,
                "votes_rejected": member.votes_rejected,
                "votes_abstained": member.votes_abstained,
                "last_vote_at": member.last_vote_at.isoformat() if member.last_vote_at else None,
                "created_at": member.created_at.isoformat() if member.created_at else None
            }
    
    async def create_committee(
        self,
        committee_name: str,
        display_name: str,
        description: Optional[str] = None,
        responsibilities: List[str] = None,
        min_members: int = 3,
        max_members: int = 10,
        default_quorum: int = 3,
        default_threshold: float = 0.5,
        auto_assign_categories: List[str] = None,
        auto_assign_risk_levels: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new committee"""
        
        async with async_session() as session:
            committee = CommitteeDefinition(
                committee_name=committee_name,
                display_name=display_name,
                description=description,
                responsibilities=responsibilities or [],
                min_members=min_members,
                max_members=max_members,
                default_quorum=default_quorum,
                default_threshold=default_threshold,
                auto_assign_categories=auto_assign_categories or [],
                auto_assign_risk_levels=auto_assign_risk_levels or []
            )
            
            session.add(committee)
            await session.commit()
            await session.refresh(committee)
            
            return {
                "id": committee.id,
                "committee_name": committee.committee_name,
                "display_name": committee.display_name,
                "description": committee.description,
                "responsibilities": committee.responsibilities
            }
    
    async def list_committees(self) -> List[Dict[str, Any]]:
        """List all committees"""
        
        async with async_session() as session:
            result = await session.execute(
                select(CommitteeDefinition).where(CommitteeDefinition.active == True)
            )
            committees = result.scalars().all()
            
            return [
                {
                    "committee_name": c.committee_name,
                    "display_name": c.display_name,
                    "description": c.description,
                    "member_count": len(c.member_ids),
                    "default_quorum": c.default_quorum
                }
                for c in committees
            ]
    
    async def get_committee(self, committee_name: str) -> Optional[Dict[str, Any]]:
        """Get committee details"""
        
        async with async_session() as session:
            result = await session.execute(
                select(CommitteeDefinition).where(CommitteeDefinition.committee_name == committee_name)
            )
            committee = result.scalar_one_or_none()
            
            if not committee:
                return None
            
            return {
                "committee_name": committee.committee_name,
                "display_name": committee.display_name,
                "description": committee.description,
                "responsibilities": committee.responsibilities,
                "member_ids": committee.member_ids,
                "default_quorum": committee.default_quorum,
                "default_threshold": committee.default_threshold
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get parliament-wide statistics"""
        
        async with async_session() as session:
            # Total sessions
            sessions_result = await session.execute(select(GovernanceSession))
            sessions = sessions_result.scalars().all()
            
            # Total members
            members_result = await session.execute(select(GovernanceMember))
            members = members_result.scalars().all()
            
            # Calculate stats
            total_sessions = len(sessions)
            approved = sum(1 for s in sessions if s.outcome == "approved")
            rejected = sum(1 for s in sessions if s.outcome == "rejected")
            expired = sum(1 for s in sessions if s.outcome == "expired")
            pending = sum(1 for s in sessions if s.status in ["pending", "voting"])
            
            return {
                "total_members": len(members),
                "active_members": sum(1 for m in members if m.active),
                "total_sessions": total_sessions,
                "sessions_approved": approved,
                "sessions_rejected": rejected,
                "sessions_expired": expired,
                "sessions_pending": pending,
                "total_votes_cast": sum(s.total_votes for s in sessions),
                "approval_rate": approved / total_sessions if total_sessions > 0 else 0
            }
    
    async def get_member_statistics(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member-specific statistics"""
        
        async with async_session() as session:
            result = await session.execute(
                select(GovernanceMember).where(GovernanceMember.member_id == member_id)
            )
            member = result.scalar_one_or_none()
            
            if not member:
                return None
            
            total_votes = member.total_votes
            approval_rate = member.votes_approved / total_votes if total_votes > 0 else 0
            
            return {
                "member_id": member.member_id,
                "display_name": member.display_name,
                "total_votes": total_votes,
                "votes_approved": member.votes_approved,
                "votes_rejected": member.votes_rejected,
                "votes_abstained": member.votes_abstained,
                "approval_rate": approval_rate,
                "last_vote_at": member.last_vote_at.isoformat() if member.last_vote_at else None
            }

parliament_engine = ParliamentEngine()
