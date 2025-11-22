"""
Parliament - Voting subsystem for governance decisions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Vote(Enum):
    """Voting options"""
    APPROVE = "approve"
    DENY = "deny"
    ABSTAIN = "abstain"
    ESCALATE = "escalate"


class Parliamentarian:
    """A member of parliament with voting power"""

    def __init__(self, member_id: str, name: str, specialty: str, trust_score: float = 0.8):
        self.member_id = member_id
        self.name = name
        self.specialty = specialty
        self.trust_score = trust_score
        self.voting_power = trust_score  # Voting power based on trust

    async def vote_on_proposal(self, proposal: Dict[str, Any]) -> Vote:
        """
        Vote on a governance proposal

        This is a simplified implementation. In practice, this would use
        more sophisticated decision-making based on the parliamentarian's
        specialty and the proposal details.
        """
        # Simple voting logic based on proposal type and specialty
        proposal_type = proposal.get("type", "unknown")
        risk_level = proposal.get("risk_level", "medium")

        # Security specialists are more conservative
        if self.specialty == "security" and risk_level == "high":
            return Vote.DENY

        # Innovation specialists are more approving for new features
        if self.specialty == "innovation" and proposal_type == "feature":
            return Vote.APPROVE

        # Default: approve low-risk, abstain on medium, deny high-risk
        if risk_level == "low":
            return Vote.APPROVE
        elif risk_level == "high":
            return Vote.ESCALATE
        else:
            return Vote.ABSTAIN


@dataclass
class Proposal:
    """A governance proposal for voting"""

    proposal_id: str
    title: str
    description: str
    proposer: str
    proposal_type: str
    risk_level: str
    details: Dict[str, Any]
    created_at: datetime
    voting_deadline: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if voting deadline has passed"""
        if self.voting_deadline:
            return datetime.now(timezone.utc) > self.voting_deadline
        return False


@dataclass
class VoteResult:
    """Result of a parliamentary vote"""

    proposal_id: str
    total_votes: int
    approve_votes: int
    deny_votes: int
    abstain_votes: int
    escalate_votes: int
    weighted_approve: float
    weighted_deny: float
    decision: str
    confidence: float
    voting_time: datetime


class Parliament:
    """
    Parliament - Democratic voting system for governance decisions

    Members vote on proposals with weighted voting based on trust scores.
    Provides consensus-based decision making for complex governance issues.
    """

    def __init__(self):
        self.component_id = "parliament"
        self.running = False

        # Parliament members
        self.members: Dict[str, Parliamentarian] = {}
        self._initialize_members()

        # Active proposals
        self.active_proposals: Dict[str, Proposal] = {}
        self.completed_votes: List[VoteResult] = []

        # Voting settings
        self.quorum_required = 0.5  # 50% of members must vote
        self.approval_threshold = 0.6  # 60% weighted approval needed
        self.voting_timeout_hours = 24

        # Statistics
        self.voting_stats = {
            "total_proposals": 0,
            "approved_proposals": 0,
            "denied_proposals": 0,
            "escalated_proposals": 0,
            "average_voting_time": 0
        }

    def _initialize_members(self) -> None:
        """Initialize parliament members"""
        # Create diverse parliament with different specialties
        members_data = [
            ("security_expert", "Security Expert", "security", 0.9),
            ("ethics_officer", "Ethics Officer", "ethics", 0.85),
            ("innovation_lead", "Innovation Lead", "innovation", 0.8),
            ("risk_analyst", "Risk Analyst", "risk", 0.85),
            ("compliance_officer", "Compliance Officer", "compliance", 0.9),
            ("user_advocate", "User Advocate", "usability", 0.75),
            ("performance_expert", "Performance Expert", "performance", 0.8)
        ]

        for member_id, name, specialty, trust in members_data:
            self.members[member_id] = Parliamentarian(member_id, name, specialty, trust)

        logger.info(f"[PARLIAMENT] Initialized {len(self.members)} parliament members")

    async def initialize(self) -> None:
        """Initialize parliament"""
        logger.info("[PARLIAMENT] Parliament initializing")

        # Load any persisted state if needed
        await self._load_persisted_state()

        logger.info("[PARLIAMENT] Parliament initialized")

    async def start(self) -> None:
        """Start parliament operations"""
        if self.running:
            return

        self.running = True
        logger.info("[PARLIAMENT] Parliament started")

    async def stop(self) -> None:
        """Stop parliament operations"""
        if not self.running:
            return

        self.running = False
        logger.info("[PARLIAMENT] Parliament stopped")

    async def _load_persisted_state(self) -> None:
        """Load persisted parliament state"""
        # In a full implementation, this would load from database
        # For now, just initialize fresh
        pass

    async def submit_proposal(
        self,
        title: str,
        description: str,
        proposer: str,
        proposal_type: str,
        risk_level: str = "medium",
        details: Optional[Dict[str, Any]] = None,
        voting_timeout_hours: Optional[int] = None
    ) -> str:
        """
        Submit a proposal for parliamentary voting

        Returns proposal ID
        """
        proposal_id = f"proposal_{int(datetime.now().timestamp() * 1000)}"

        timeout = voting_timeout_hours or self.voting_timeout_hours
        voting_deadline = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        # Add timeout hours
        voting_deadline = voting_deadline.replace(hour=voting_deadline.hour + timeout)

        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposer=proposer,
            proposal_type=proposal_type,
            risk_level=risk_level,
            details=details or {},
            created_at=datetime.now(timezone.utc),
            voting_deadline=voting_deadline
        )

        self.active_proposals[proposal_id] = proposal
        self.voting_stats["total_proposals"] += 1

        logger.info(f"[PARLIAMENT] Proposal submitted: {proposal_id} - {title}")

        # Start voting process
        asyncio.create_task(self._conduct_vote(proposal))

        return proposal_id

    async def _conduct_vote(self, proposal: Proposal) -> None:
        """Conduct voting on a proposal"""
        try:
            logger.info(f"[PARLIAMENT] Starting vote on proposal: {proposal.proposal_id}")

            # Collect votes from all members
            votes = await self._collect_votes(proposal)

            # Calculate result
            result = self._calculate_vote_result(proposal.proposal_id, votes)

            # Store result
            self.completed_votes.append(result)
            del self.active_proposals[proposal.proposal_id]

            # Update statistics
            if result.decision == "approved":
                self.voting_stats["approved_proposals"] += 1
            elif result.decision == "denied":
                self.voting_stats["denied_proposals"] += 1
            elif result.decision == "escalated":
                self.voting_stats["escalated_proposals"] += 1

            # Emit result event
            await self._emit_vote_result(result)

            logger.info(f"[PARLIAMENT] Vote completed: {proposal.proposal_id} -> {result.decision}")

        except Exception as e:
            logger.error(f"[PARLIAMENT] Vote failed for {proposal.proposal_id}: {e}")

    async def _collect_votes(self, proposal: Proposal) -> Dict[str, Vote]:
        """Collect votes from all parliament members"""
        votes = {}

        # Vote collection with timeout
        vote_tasks = []
        for member in self.members.values():
            task = asyncio.create_task(self._get_member_vote(member, proposal))
            vote_tasks.append((member.member_id, task))

        # Wait for votes with timeout
        timeout = self.voting_timeout_hours * 3600  # Convert to seconds
        completed_votes = await asyncio.wait_for(
            asyncio.gather(*[task for _, task in vote_tasks], return_exceptions=True),
            timeout=timeout
        )

        # Process results
        for (member_id, _), vote_result in zip(vote_tasks, completed_votes):
            if isinstance(vote_result, Exception):
                logger.warning(f"[PARLIAMENT] Vote failed for {member_id}: {vote_result}")
                votes[member_id] = Vote.ABSTAIN
            else:
                votes[member_id] = vote_result

        return votes

    async def _get_member_vote(self, member: Parliamentarian, proposal: Proposal) -> Vote:
        """Get vote from a specific member"""
        # Add some delay to simulate deliberation
        await asyncio.sleep(0.1)

        return await member.vote_on_proposal({
            "type": proposal.proposal_type,
            "risk_level": proposal.risk_level,
            "title": proposal.title,
            "description": proposal.description,
            "details": proposal.details
        })

    def _calculate_vote_result(self, proposal_id: str, votes: Dict[str, Vote]) -> VoteResult:
        """Calculate the result of a vote"""
        total_members = len(self.members)
        votes_cast = len(votes)

        # Check quorum
        quorum_met = votes_cast >= (total_members * self.quorum_required)

        if not quorum_met:
            # Not enough votes - default to escalate
            return VoteResult(
                proposal_id=proposal_id,
                total_votes=votes_cast,
                approve_votes=0,
                deny_votes=0,
                abstain_votes=votes_cast,
                escalate_votes=0,
                weighted_approve=0.0,
                weighted_deny=0.0,
                decision="escalated",
                confidence=0.5,
                voting_time=datetime.now(timezone.utc)
            )

        # Count votes with weights
        approve_weight = 0.0
        deny_weight = 0.0
        abstain_count = 0
        escalate_count = 0

        total_weight = sum(self.members[mid].voting_power for mid in votes.keys())

        for member_id, vote in votes.items():
            weight = self.members[member_id].voting_power

            if vote == Vote.APPROVE:
                approve_weight += weight
            elif vote == Vote.DENY:
                deny_weight += weight
            elif vote == Vote.ABSTAIN:
                abstain_count += 1
            elif vote == Vote.ESCALATE:
                escalate_count += 1

        # Calculate percentages
        approve_percentage = approve_weight / total_weight if total_weight > 0 else 0
        deny_percentage = deny_weight / total_weight if total_weight > 0 else 0

        # Determine decision
        if approve_percentage >= self.approval_threshold:
            decision = "approved"
            confidence = approve_percentage
        elif deny_percentage > approve_percentage:
            decision = "denied"
            confidence = deny_percentage
        elif escalate_count > votes_cast * 0.3:  # 30% want escalation
            decision = "escalated"
            confidence = escalate_count / votes_cast
        else:
            decision = "escalated"  # Default to escalation for unclear cases
            confidence = 0.5

        return VoteResult(
            proposal_id=proposal_id,
            total_votes=votes_cast,
            approve_votes=sum(1 for v in votes.values() if v == Vote.APPROVE),
            deny_votes=sum(1 for v in votes.values() if v == Vote.DENY),
            abstain_votes=abstain_count,
            escalate_votes=escalate_count,
            weighted_approve=approve_percentage,
            weighted_deny=deny_percentage,
            decision=decision,
            confidence=confidence,
            voting_time=datetime.now(timezone.utc)
        )

    async def _emit_vote_result(self, result: VoteResult) -> None:
        """Emit vote result event"""
        try:
            # Emit to event bus
            from backend.core.unified_event_publisher import get_unified_publisher
            event_bus = get_unified_publisher()

            await event_bus.publish_event(
                event_type="parliament.vote_completed",
                payload={
                    "proposal_id": result.proposal_id,
                    "decision": result.decision,
                    "confidence": result.confidence,
                    "votes": {
                        "total": result.total_votes,
                        "approve": result.approve_votes,
                        "deny": result.deny_votes,
                        "abstain": result.abstain_votes,
                        "escalate": result.escalate_votes
                    },
                    "weighted_scores": {
                        "approve": result.weighted_approve,
                        "deny": result.weighted_deny
                    }
                },
                source=self.component_id
            )

        except Exception as e:
            logger.debug(f"[PARLIAMENT] Failed to emit vote result: {e}")

    async def get_vote_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a proposal vote"""
        if proposal_id in self.active_proposals:
            proposal = self.active_proposals[proposal_id]
            return {
                "status": "voting",
                "proposal": {
                    "id": proposal.proposal_id,
                    "title": proposal.title,
                    "created_at": proposal.created_at.isoformat(),
                    "deadline": proposal.voting_deadline.isoformat() if proposal.voting_deadline else None
                }
            }

        # Check completed votes
        for result in self.completed_votes:
            if result.proposal_id == proposal_id:
                return {
                    "status": "completed",
                    "result": {
                        "decision": result.decision,
                        "confidence": result.confidence,
                        "total_votes": result.total_votes,
                        "completed_at": result.voting_time.isoformat()
                    }
                }

        return None

    async def get_parliament_stats(self) -> Dict[str, Any]:
        """Get parliament statistics"""
        return {
            "component_id": self.component_id,
            "running": self.running,
            "members": len(self.members),
            "active_proposals": len(self.active_proposals),
            "completed_votes": len(self.completed_votes),
            "voting_settings": {
                "quorum_required": self.quorum_required,
                "approval_threshold": self.approval_threshold,
                "voting_timeout_hours": self.voting_timeout_hours
            },
            "statistics": self.voting_stats.copy()
        }


# Global instance
parliament = Parliament()</code></edit_file>
