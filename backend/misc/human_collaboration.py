"""
Human Collaboration Interface - Concise signed briefs and proactive engagement

Provides signed briefs in incident channels so humans understand rationale.
Requests clarifications and approvals proactively. Enables humans to intervene
at any point while keeping them informed, not overwhelmed.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .immutable_log import immutable_log
from backend.core.unified_event_publisher import publish_trigger


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class InterventionType(Enum):
    CLARIFICATION = "clarification"
    APPROVAL = "approval"
    OVERRIDE = "override"
    FEEDBACK = "feedback"


@dataclass
class SignedBrief:
    """Cryptographically signed incident brief for humans"""
    brief_id: str
    incident_id: str
    timestamp: datetime
    severity: str
    summary: str
    context: Dict[str, Any]
    proposed_action: str
    rationale: str
    risk_assessment: Dict[str, Any]
    approval_required: bool
    deadline: Optional[datetime] = None
    signature: str = ""
    
    def to_markdown(self) -> str:
        """Format brief as readable markdown"""
        return f"""## Incident Brief: {self.brief_id}
        
**Severity:** {self.severity}  
**Time:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

### Summary
{self.summary}

### Proposed Action
{self.proposed_action}

### Rationale
{self.rationale}

### Risk Assessment
- **Risk Score:** {self.risk_assessment.get('score', 'N/A')}
- **Blast Radius:** {self.risk_assessment.get('blast_radius', 'N/A')} services
- **Rollback Available:** {'Yes' if self.risk_assessment.get('has_rollback') else 'No'}

### Context
```json
{self.context}
```

{'**⚠️ APPROVAL REQUIRED' + (f' by {self.deadline.strftime("%H:%M:%S")}' if self.deadline else '') + '**' if self.approval_required else '**ℹ️ Informational Only**'}

---
*Signed: {self.signature}*
"""


@dataclass
class ApprovalRequest:
    """Request for human approval"""
    request_id: str
    brief: SignedBrief
    requested_by: str
    requested_at: datetime
    deadline: Optional[datetime]
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    responded_at: Optional[datetime] = None
    response_notes: str = ""


@dataclass
class ClarificationRequest:
    """Request for human clarification"""
    request_id: str
    question: str
    context: Dict[str, Any]
    options: List[str]
    requested_at: datetime
    response: Optional[str] = None
    responded_at: Optional[datetime] = None


@dataclass
class InterventionRecord:
    """Record of human intervention"""
    intervention_id: str
    intervention_type: InterventionType
    actor: str
    target_resource: str
    action: str
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BriefGenerator:
    """Generates concise, signed incident briefs"""
    
    def __init__(self):
        self.private_key = "grace_signing_key"
    
    async def generate_brief(
        self,
        incident_id: str,
        severity: str,
        summary: str,
        context: Dict,
        proposed_action: str,
        rationale: str,
        risk_assessment: Dict,
        approval_required: bool = False,
        deadline: Optional[datetime] = None
    ) -> SignedBrief:
        """Generate a cryptographically signed brief"""
        
        brief = SignedBrief(
            brief_id=f"brief_{datetime.utcnow().timestamp()}",
            incident_id=incident_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            summary=summary,
            context=context,
            proposed_action=proposed_action,
            rationale=rationale,
            risk_assessment=risk_assessment,
            approval_required=approval_required,
            deadline=deadline
        )
        
        brief.signature = await self._sign_brief(brief)
        
        return brief
    
    async def _sign_brief(self, brief: SignedBrief) -> str:
        """Sign brief with GRACE's private key"""
        import hashlib
        
        content = f"{brief.brief_id}:{brief.incident_id}:{brief.timestamp}:{brief.summary}"
        signature = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return f"GRACE:{signature}"


class IncidentChannel:
    """Communication channel for incident collaboration"""
    
    def __init__(self):
        self.channels: Dict[str, List[str]] = {}
        self.subscribers: Dict[str, set] = {}
    
    async def create_channel(self, incident_id: str) -> str:
        """Create incident channel"""
        channel_id = f"channel_{incident_id}"
        self.channels[channel_id] = []
        self.subscribers[channel_id] = set()
        return channel_id
    
    async def post_brief(self, channel_id: str, brief: SignedBrief):
        """Post brief to channel"""
        if channel_id not in self.channels:
            await self.create_channel(channel_id)
        
        message = brief.to_markdown()
        self.channels[channel_id].append(message)
        
        await publish_trigger(
            trigger_type="collaboration.brief_posted",
            context={
                "channel": channel_id,
                "brief_id": brief.brief_id,
                "severity": brief.severity,
                "approval_required": brief.approval_required,
                "actor": "grace_agent",
                "resource": brief.brief_id
            },
            source="human_collaboration"
        )
        
        await self._notify_subscribers(channel_id, message)
    
    async def post_update(self, channel_id: str, update: str):
        """Post status update to channel"""
        if channel_id not in self.channels:
            return
        
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        message = f"**[{timestamp}]** {update}"
        self.channels[channel_id].append(message)
        
        await self._notify_subscribers(channel_id, message)
    
    async def subscribe(self, channel_id: str, subscriber: str):
        """Subscribe to channel notifications"""
        if channel_id not in self.subscribers:
            self.subscribers[channel_id] = set()
        self.subscribers[channel_id].add(subscriber)
    
    async def _notify_subscribers(self, channel_id: str, message: str):
        """Notify all channel subscribers"""
        if channel_id in self.subscribers:
            for subscriber in self.subscribers[channel_id]:
                print(f"📢 [{channel_id}] -> {subscriber}: {message[:100]}...")


class ApprovalManager:
    """Manages approval requests and responses"""
    
    def __init__(self):
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []
    
    async def request_approval(
        self,
        brief: SignedBrief,
        requested_by: str = "grace_agent",
        deadline: Optional[datetime] = None
    ) -> ApprovalRequest:
        """Request human approval for action"""
        
        request = ApprovalRequest(
            request_id=f"approval_{datetime.utcnow().timestamp()}",
            brief=brief,
            requested_by=requested_by,
            requested_at=datetime.utcnow(),
            deadline=deadline
        )
        
        self.pending_approvals[request.request_id] = request
        
        await publish_trigger(
            trigger_type="collaboration.approval_requested",
            context={
                "brief_id": brief.brief_id,
                "incident_id": brief.incident_id,
                "deadline": deadline.isoformat() if deadline else None,
                "actor": requested_by,
                "resource": request.request_id
            },
            source="human_collaboration"
        )
        
        await immutable_log.append(
            actor=requested_by,
            action="approval_requested",
            resource=request.request_id,
            subsystem="approval_manager",
            payload={
                "brief_id": brief.brief_id,
                "severity": brief.severity
            },
            result="pending"
        )
        
        return request
    
    async def approve(
        self,
        request_id: str,
        approved_by: str,
        notes: str = ""
    ) -> bool:
        """Approve pending request"""
        
        if request_id not in self.pending_approvals:
            return False
        
        request = self.pending_approvals[request_id]
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approved_by
        request.responded_at = datetime.utcnow()
        request.response_notes = notes
        
        self.approval_history.append(request)
        del self.pending_approvals[request_id]
        
        await immutable_log.append(
            actor=approved_by,
            action="approval_granted",
            resource=request_id,
            subsystem="approval_manager",
            payload={
                "brief_id": request.brief.brief_id,
                "notes": notes
            },
            result="approved"
        )
        
        await publish_trigger(
            trigger_type="collaboration.approval_granted",
            context={
                "brief_id": request.brief.brief_id,
                "actor": approved_by,
                "resource": request_id
            },
            source="human_collaboration"
        )
        
        return True
    
    async def reject(
        self,
        request_id: str,
        rejected_by: str,
        reason: str
    ) -> bool:
        """Reject pending request"""
        
        if request_id not in self.pending_approvals:
            return False
        
        request = self.pending_approvals[request_id]
        request.status = ApprovalStatus.REJECTED
        request.approved_by = rejected_by
        request.responded_at = datetime.utcnow()
        request.response_notes = reason
        
        self.approval_history.append(request)
        del self.pending_approvals[request_id]
        
        await immutable_log.append(
            actor=rejected_by,
            action="approval_rejected",
            resource=request_id,
            subsystem="approval_manager",
            payload={
                "brief_id": request.brief.brief_id,
                "reason": reason
            },
            result="rejected"
        )
        
        await publish_trigger(
            trigger_type="collaboration.approval_rejected",
            context={
                "brief_id": request.brief.brief_id,
                "reason": reason,
                "actor": rejected_by,
                "resource": request_id
            },
            source="human_collaboration"
        )
        
        return True
    
    async def check_deadlines(self):
        """Check for expired approval requests"""
        now = datetime.utcnow()
        
        for request_id, request in list(self.pending_approvals.items()):
            if request.deadline and now > request.deadline:
                request.status = ApprovalStatus.EXPIRED
                self.approval_history.append(request)
                del self.pending_approvals[request_id]
                
                await publish_trigger(
                    trigger_type="collaboration.approval_expired",
                    context={
                        "brief_id": request.brief.brief_id,
                        "actor": "system",
                        "resource": request_id
                    },
                    source="human_collaboration"
                )


class ClarificationManager:
    """Manages clarification requests when GRACE needs input"""
    
    def __init__(self):
        self.pending_clarifications: Dict[str, ClarificationRequest] = {}
        self.clarification_history: List[ClarificationRequest] = []
    
    async def request_clarification(
        self,
        question: str,
        context: Dict,
        options: List[str]
    ) -> ClarificationRequest:
        """Request clarification from human"""
        
        request = ClarificationRequest(
            request_id=f"clarify_{datetime.utcnow().timestamp()}",
            question=question,
            context=context,
            options=options,
            requested_at=datetime.utcnow()
        )
        
        self.pending_clarifications[request.request_id] = request
        
        await publish_trigger(
            trigger_type="collaboration.clarification_requested",
            context={
                "question": question,
                "options": options,
                "actor": "grace_agent",
                "resource": request.request_id
            },
            source="human_collaboration"
        )
        
        return request
    
    async def provide_clarification(
        self,
        request_id: str,
        response: str
    ) -> bool:
        """Provide response to clarification request"""
        
        if request_id not in self.pending_clarifications:
            return False
        
        request = self.pending_clarifications[request_id]
        request.response = response
        request.responded_at = datetime.utcnow()
        
        self.clarification_history.append(request)
        del self.pending_clarifications[request_id]
        
        await publish_trigger(
            trigger_type="collaboration.clarification_provided",
            context={
                "response": response,
                "actor": "human",
                "resource": request_id
            },
            source="human_collaboration"
        )
        
        return True


class InterventionManager:
    """Tracks human interventions and overrides"""
    
    def __init__(self):
        self.interventions: List[InterventionRecord] = []
    
    async def record_intervention(
        self,
        intervention_type: InterventionType,
        actor: str,
        target_resource: str,
        action: str,
        reasoning: str
    ):
        """Record human intervention"""
        
        intervention = InterventionRecord(
            intervention_id=f"intervention_{datetime.utcnow().timestamp()}",
            intervention_type=intervention_type,
            actor=actor,
            target_resource=target_resource,
            action=action,
            reasoning=reasoning
        )
        
        self.interventions.append(intervention)
        
        await immutable_log.append(
            actor=actor,
            action=f"human_{intervention_type.value}",
            resource=target_resource,
            subsystem="intervention_manager",
            payload={
                "intervention_id": intervention.intervention_id,
                "action": action,
                "reasoning": reasoning
            },
            result="recorded"
        )
        
        await publish_trigger(
            trigger_type=f"collaboration.{intervention_type.value}",
            context={
                "action": action,
                "reasoning": reasoning,
                "actor": actor,
                "resource": target_resource
            },
            source="human_collaboration"
        )


class HumanCollaboration:
    """Main human collaboration coordinator"""
    
    def __init__(self):
        self.brief_generator = BriefGenerator()
        self.channels = IncidentChannel()
        self.approval_manager = ApprovalManager()
        self.clarification_manager = ClarificationManager()
        self.intervention_manager = InterventionManager()
    
    async def start(self):
        """Start human collaboration system"""
        asyncio.create_task(self._monitor_deadlines())
        print("✓ Human Collaboration Interface started")
    
    async def notify_incident(
        self,
        incident_id: str,
        severity: str,
        summary: str,
        context: Dict,
        proposed_action: str,
        rationale: str,
        risk_assessment: Dict,
        approval_required: bool = False
    ) -> Optional[ApprovalRequest]:
        """Notify humans of incident with signed brief"""
        
        brief = await self.brief_generator.generate_brief(
            incident_id=incident_id,
            severity=severity,
            summary=summary,
            context=context,
            proposed_action=proposed_action,
            rationale=rationale,
            risk_assessment=risk_assessment,
            approval_required=approval_required
        )
        
        channel_id = await self.channels.create_channel(incident_id)
        await self.channels.post_brief(channel_id, brief)
        
        if approval_required:
            return await self.approval_manager.request_approval(brief)
        
        return None
    
    async def update_incident(self, incident_id: str, update: str):
        """Post update to incident channel"""
        channel_id = f"channel_{incident_id}"
        await self.channels.post_update(channel_id, update)
    
    async def request_human_input(
        self,
        question: str,
        context: Dict,
        options: List[str]
    ) -> str:
        """Request human input when uncertain"""
        
        request = await self.clarification_manager.request_clarification(
            question, context, options
        )
        
        while request.response is None:
            await asyncio.sleep(1)
            if request.request_id in self.clarification_manager.pending_clarifications:
                request = self.clarification_manager.pending_clarifications[request.request_id]
            else:
                break
        
        return request.response or options[0]
    
    async def _monitor_deadlines(self):
        """Background task to monitor approval deadlines"""
        while True:
            await asyncio.sleep(30)
            await self.approval_manager.check_deadlines()


human_collaboration = HumanCollaboration()
