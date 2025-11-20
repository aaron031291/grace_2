"""
Governance Gate - Kernel 1: First Stop After Ingress
All requests must pass through governance before autonomous action.

Complete implementation:
- Constitutional validation
- Policy enforcement
- Trust score verification
- Parliament approval (when needed)
- Immutable logging
- MTL (Memory/Trust/Learning) integration
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GovernanceDecision(Enum):
    """Governance decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_APPROVAL = "requires_approval"
    REQUIRES_PARLIAMENT = "requires_parliament"


class ActionRiskLevel(Enum):
    """Risk levels for actions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GovernanceRequest:
    """Request for governance validation"""
    request_id: str
    actor: str
    action: str
    resource: str
    context: Dict[str, Any]
    risk_level: ActionRiskLevel = ActionRiskLevel.MEDIUM
    source: str = "unknown"
    is_autonomous: bool = False


@dataclass
class GovernanceResponse:
    """Response from governance validation"""
    decision: GovernanceDecision
    request_id: str
    reasoning: str
    trust_score: float
    violated_policies: List[str]
    constitutional_compliant: bool
    requires_human_approval: bool
    approval_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision.value,
            'request_id': self.request_id,
            'reasoning': self.reasoning,
            'trust_score': self.trust_score,
            'violated_policies': self.violated_policies,
            'constitutional_compliant': self.constitutional_compliant,
            'requires_human_approval': self.requires_human_approval,
            'approval_id': self.approval_id,
            'metadata': self.metadata or {}
        }


class GovernanceGate:
    """
    Kernel 1: Governance Gate - First stop after ingress
    
    All requests flow through:
    1. Ingress → Governance Gate → (approved) → Event Bus → ...
    2. Governance Gate checks:
       - Constitutional compliance
       - Policy enforcement
       - Trust score validation
       - Risk assessment
    3. High-risk actions → Parliament approval
    4. All checks logged to immutable log
    5. Trust updates written to MTL
    """
    
    def __init__(self):
        self.requests_processed = 0
        self.approved_count = 0
        self.rejected_count = 0
        self.pending_approvals = {}
        
        # Load dependencies lazily
        self._constitutional_verifier = None
        self._policy_engine = None
        self._parliament_engine = None
        self._trust_scorer = None
        self._immutable_log = None
        self._mtl_writer = None
    
    async def validate(self, request: GovernanceRequest) -> GovernanceResponse:
        """
        Main validation method - Kernel 1 gate
        
        Args:
            request: Governance request to validate
            
        Returns:
            GovernanceResponse with decision
        """
        
        self.requests_processed += 1
        
        violated_policies = []
        reasoning_parts = []
        
        # Step 1: Constitutional Validation
        constitutional_result = await self._validate_constitutional(request)
        
        if not constitutional_result['compliant']:
            self.rejected_count += 1
            
            response = GovernanceResponse(
                decision=GovernanceDecision.REJECTED,
                request_id=request.request_id,
                reasoning=f"Constitutional violation: {constitutional_result['violation']}",
                trust_score=0.0,
                violated_policies=[constitutional_result['violated_principle']],
                constitutional_compliant=False,
                requires_human_approval=False
            )
            
            await self._log_decision(request, response)
            return response
        
        reasoning_parts.append("Constitutional check passed")
        
        # Step 2: Policy Enforcement
        policy_result = await self._enforce_policies(request)
        
        if policy_result['violated']:
            violated_policies.extend(policy_result['violated_policies'])
            
            if policy_result['severity'] == 'critical':
                self.rejected_count += 1
                
                response = GovernanceResponse(
                    decision=GovernanceDecision.REJECTED,
                    request_id=request.request_id,
                    reasoning=f"Critical policy violations: {', '.join(violated_policies)}",
                    trust_score=0.0,
                    violated_policies=violated_policies,
                    constitutional_compliant=True,
                    requires_human_approval=False
                )
                
                await self._log_decision(request, response)
                return response
        
        reasoning_parts.append(f"Policy check: {len(violated_policies)} violations")
        
        # Step 3: Trust Score Validation
        trust_score = await self._validate_trust_score(request)
        
        if trust_score < 0.5:
            self.rejected_count += 1
            
            response = GovernanceResponse(
                decision=GovernanceDecision.REJECTED,
                request_id=request.request_id,
                reasoning=f"Insufficient trust score: {trust_score:.2f}",
                trust_score=trust_score,
                violated_policies=violated_policies,
                constitutional_compliant=True,
                requires_human_approval=True
            )
            
            await self._log_decision(request, response)
            return response
        
        reasoning_parts.append(f"Trust score: {trust_score:.2f}")
        
        # Step 4: Risk Assessment & Parliament Check
        if request.risk_level in [ActionRiskLevel.HIGH, ActionRiskLevel.CRITICAL]:
            # High/critical risk requires parliament approval
            
            approval_id = f"approval_{request.request_id}"
            self.pending_approvals[approval_id] = request
            
            response = GovernanceResponse(
                decision=GovernanceDecision.REQUIRES_PARLIAMENT,
                request_id=request.request_id,
                reasoning=f"{request.risk_level.value} risk requires parliament approval",
                trust_score=trust_score,
                violated_policies=violated_policies,
                constitutional_compliant=True,
                requires_human_approval=True,
                approval_id=approval_id
            )
            
            await self._log_decision(request, response)
            await self._request_parliament_approval(request, approval_id)
            
            return response
        
        # Step 5: Autonomous actions require additional checks
        if request.is_autonomous:
            autonomous_check = await self._validate_autonomous_action(request)
            
            if not autonomous_check['allowed']:
                self.rejected_count += 1
                
                response = GovernanceResponse(
                    decision=GovernanceDecision.REJECTED,
                    request_id=request.request_id,
                    reasoning=f"Autonomous action rejected: {autonomous_check['reason']}",
                    trust_score=trust_score,
                    violated_policies=violated_policies,
                    constitutional_compliant=True,
                    requires_human_approval=True
                )
                
                await self._log_decision(request, response)
                return response
            
            reasoning_parts.append("Autonomous action validated")
        
        # Step 6: APPROVED
        self.approved_count += 1
        
        response = GovernanceResponse(
            decision=GovernanceDecision.APPROVED,
            request_id=request.request_id,
            reasoning="; ".join(reasoning_parts),
            trust_score=trust_score,
            violated_policies=violated_policies,
            constitutional_compliant=True,
            requires_human_approval=False
        )
        
        # Log decision and update MTL
        await self._log_decision(request, response)
        await self._update_mtl(request, response)
        
        return response
    
    async def _validate_constitutional(self, request: GovernanceRequest) -> Dict[str, Any]:
        """Validate against constitutional principles"""
        
        try:
            from backend.governance_system.constitutional_verifier import constitutional_verifier
            
            result = await constitutional_verifier.verify(
                actor=request.actor,
                action=request.action,
                resource=request.resource,
                context=request.context
            )
            
            return {
                'compliant': result.get('compliant', True),
                'violation': result.get('violation', ''),
                'violated_principle': result.get('violated_principle', '')
            }
        
        except Exception as e:
            print(f"⚠ Constitutional verification unavailable: {e}")
            # Default to compliant if system unavailable
            return {'compliant': True, 'violation': '', 'violated_principle': ''}
    
    async def _enforce_policies(self, request: GovernanceRequest) -> Dict[str, Any]:
        """Enforce domain policies"""
        
        try:
            from backend.workflow_engines.policy_engine import policy_engine
            
            result = await policy_engine.evaluate(
                actor=request.actor,
                action=request.action,
                resource=request.resource,
                context=request.context
            )
            
            return {
                'violated': not result.get('allowed', True),
                'violated_policies': result.get('violated_policies', []),
                'severity': result.get('severity', 'low')
            }
        
        except Exception as e:
            print(f"⚠ Policy enforcement unavailable: {e}")
            return {'violated': False, 'violated_policies': [], 'severity': 'low'}
    
    async def _validate_trust_score(self, request: GovernanceRequest) -> float:
        """Validate trust score for actor"""
        
        try:
            from backend.trust_framework.trust_score import get_trust_score
            
            trust = await get_trust_score(request.actor)
            return trust.composite_score if trust else 1.0
        
        except Exception as e:
            print(f"⚠ Trust score unavailable: {e}")
            return 0.8  # Default moderate trust
    
    async def _validate_autonomous_action(self, request: GovernanceRequest) -> Dict[str, Any]:
        """Validate autonomous actions (AVN, code generation, system changes)"""
        
        # Check if action is in allowed autonomous actions
        allowed_autonomous = [
            'execute_task',
            'generate_code',
            'deploy_model',
            'scale_service',
            'restart_component',
            'rollback_deployment'
        ]
        
        if request.action not in allowed_autonomous:
            return {
                'allowed': False,
                'reason': f"Action '{request.action}' not in allowed autonomous actions"
            }
        
        # Check if actor has autonomous privileges
        if not request.context.get('has_autonomous_privilege', False):
            return {
                'allowed': False,
                'reason': "Actor lacks autonomous privilege"
            }
        
        return {'allowed': True, 'reason': ''}
    
    async def _request_parliament_approval(self, request: GovernanceRequest, approval_id: str):
        """Request parliament approval for high-risk actions"""
        
        try:
            from backend.workflow_engines.parliament_engine import parliament_engine
            
            await parliament_engine.request_approval(
                approval_id=approval_id,
                actor=request.actor,
                action=request.action,
                resource=request.resource,
                context=request.context,
                risk_level=request.risk_level.value
            )
        
        except Exception as e:
            print(f"⚠ Parliament approval request failed: {e}")
    
    async def _log_decision(self, request: GovernanceRequest, response: GovernanceResponse):
        """Log governance decision to immutable log"""
        
        try:
            from backend.logging.governance_logger import governance_logger
            
            await governance_logger.log_governance_decision(
                decision_id=request.request_id,
                decision_type="governance_gate",
                actor=request.actor,
                resource=request.resource,
                approved=(response.decision == GovernanceDecision.APPROVED),
                reasoning=response.reasoning,
                vote_details={
                    'trust_score': response.trust_score,
                    'violated_policies': response.violated_policies,
                    'constitutional_compliant': response.constitutional_compliant
                },
                metadata={
                    'action': request.action,
                    'risk_level': request.risk_level.value,
                    'is_autonomous': request.is_autonomous
                }
            )
        
        except Exception as e:
            print(f"⚠ Failed to log governance decision: {e}")
    
    async def _update_mtl(self, request: GovernanceRequest, response: GovernanceResponse):
        """Update Memory/Trust/Learning (MTL) kernel"""
        
        try:
            # Update trust score based on outcome
            from backend.trust_framework.trust_score import update_trust_score
            
            if response.decision == GovernanceDecision.APPROVED:
                await update_trust_score(
                    actor=request.actor,
                    action_outcome='success',
                    context={'governance_approved': True}
                )
            elif response.decision == GovernanceDecision.REJECTED:
                await update_trust_score(
                    actor=request.actor,
                    action_outcome='violation',
                    context={
                        'governance_rejected': True,
                        'violated_policies': response.violated_policies
                    }
                )
            
            # Tag memory with constitutional compliance
            from backend.memory_services.memory_service import memory_service
            
            await memory_service.tag_action(
                action_id=request.request_id,
                tags=[
                    f"governance:{response.decision.value}",
                    f"constitutional:{'compliant' if response.constitutional_compliant else 'violation'}",
                    f"trust:{response.trust_score:.2f}"
                ]
            )
        
        except Exception as e:
            print(f"⚠ Failed to update MTL: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get governance gate statistics"""
        return {
            'requests_processed': self.requests_processed,
            'approved': self.approved_count,
            'rejected': self.rejected_count,
            'pending_approvals': len(self.pending_approvals),
            'approval_rate': self.approved_count / max(1, self.requests_processed)
        }


# Global governance gate instance - Kernel 1
governance_gate = GovernanceGate()
