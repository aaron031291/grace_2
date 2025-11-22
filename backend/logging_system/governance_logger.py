"""
Governance Integration for Immutable Log
Logs all governance decisions, approvals, and rejections with full audit trail
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .immutable_log import immutable_log


class GovernanceLogger:
    """
    Specialized logger for governance decisions
    Ensures all governance actions are logged to immutable audit trail
    """
    
    def __init__(self):
        self.log = immutable_log
    
    async def log_governance_decision(
        self,
        decision_id: str,
        decision_type: str,
        actor: str,
        resource: str,
        approved: bool,
        reasoning: str,
        vote_details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log a governance decision
        
        Args:
            decision_id: Unique decision identifier
            decision_type: Type of decision (policy_change, resource_allocation, etc.)
            actor: Who made or requested the decision
            resource: What resource the decision affects
            approved: Whether decision was approved
            reasoning: Why the decision was made
            vote_details: Voting breakdown if applicable
            metadata: Additional context
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "decision_id": decision_id,
            "decision_type": decision_type,
            "approved": approved,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if vote_details:
            payload["vote_details"] = vote_details
        
        if metadata:
            payload["metadata"] = metadata
        
        action = "GOVERNANCE_APPROVED" if approved else "GOVERNANCE_REJECTED"
        result = "approved" if approved else "rejected"
        
        return await self.log.append(
            actor=actor,
            action=action,
            resource=resource,
            subsystem="governance",
            payload=payload,
            result=result
        )
    
    async def log_policy_change(
        self,
        policy_id: str,
        actor: str,
        old_policy: Dict[str, Any],
        new_policy: Dict[str, Any],
        change_reason: str
    ) -> int:
        """
        Log a policy change
        
        Args:
            policy_id: Policy identifier
            actor: Who changed the policy
            old_policy: Previous policy state
            new_policy: New policy state
            change_reason: Why policy was changed
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "policy_id": policy_id,
            "old_policy": old_policy,
            "new_policy": new_policy,
            "change_reason": change_reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="POLICY_CHANGED",
            resource=f"policy:{policy_id}",
            subsystem="governance",
            payload=payload,
            result="completed"
        )
    
    async def log_constitutional_violation(
        self,
        violation_id: str,
        actor: str,
        violated_principle: str,
        violation_details: str,
        action_taken: str
    ) -> int:
        """
        Log a constitutional violation and response
        
        Args:
            violation_id: Violation identifier
            actor: Who attempted the violating action
            violated_principle: Which constitutional principle was violated
            violation_details: Details of the violation
            action_taken: How the violation was handled
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "violation_id": violation_id,
            "violated_principle": violated_principle,
            "violation_details": violation_details,
            "action_taken": action_taken,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="CONSTITUTIONAL_VIOLATION",
            resource=f"principle:{violated_principle}",
            subsystem="governance",
            payload=payload,
            result="blocked"
        )
    
    async def log_approval_request(
        self,
        request_id: str,
        actor: str,
        action_requested: str,
        resource: str,
        justification: str,
        approval_level: str
    ) -> int:
        """
        Log a request for approval
        
        Args:
            request_id: Request identifier
            actor: Who is requesting approval
            action_requested: What action needs approval
            resource: What resource will be affected
            justification: Why approval is requested
            approval_level: Required approval level (low/medium/high/critical)
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "request_id": request_id,
            "action_requested": action_requested,
            "justification": justification,
            "approval_level": approval_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="APPROVAL_REQUESTED",
            resource=resource,
            subsystem="governance",
            payload=payload,
            result="pending"
        )
    
    async def log_escalation(
        self,
        escalation_id: str,
        actor: str,
        issue_type: str,
        severity: str,
        escalation_reason: str,
        escalated_to: str
    ) -> int:
        """
        Log an escalation to higher authority
        
        Args:
            escalation_id: Escalation identifier
            actor: Who initiated the escalation
            issue_type: Type of issue being escalated
            severity: Severity level
            escalation_reason: Why escalation was needed
            escalated_to: Who/what it was escalated to
            
        Returns:
            Log entry ID
        """
        
        payload = {
            "escalation_id": escalation_id,
            "issue_type": issue_type,
            "severity": severity,
            "escalation_reason": escalation_reason,
            "escalated_to": escalated_to,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log.append(
            actor=actor,
            action="ESCALATED",
            resource=f"escalation:{escalation_id}",
            subsystem="governance",
            payload=payload,
            result="escalated"
        )
    
    async def get_governance_history(
        self,
        hours_back: int = 168,  # 7 days
        limit: int = 100
    ) -> list:
        """
        Get governance decision history
        
        Args:
            hours_back: How many hours to look back
            limit: Maximum number of entries to return
            
        Returns:
            List of governance log entries
        """
        
        return await self.log.get_entries(
            subsystem="governance",
            limit=limit
        )
    
    async def get_violation_history(
        self,
        limit: int = 50
    ) -> list:
        """
        Get history of constitutional violations
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of violation log entries
        """
        
        entries = await self.log.get_entries(
            subsystem="governance",
            limit=limit * 2  # Get more to filter
        )
        
        # Filter for violations
        violations = [
            entry for entry in entries
            if entry['action'] == 'CONSTITUTIONAL_VIOLATION'
        ]
        
        return violations[:limit]


governance_logger = GovernanceLogger()
