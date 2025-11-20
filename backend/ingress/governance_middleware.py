"""
Governance Middleware - Ingress Integration
Every external request passes through Kernel 1 (Governance Gate) before processing.

Request → Ingress → GOVERNANCE_GATE → Event Bus → Processing
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import uuid

from backend.governance_system.governance_gate import (
    governance_gate,
    GovernanceRequest,
    GovernanceDecision,
    ActionRiskLevel
)


class GovernanceMiddleware:
    """
    Middleware that enforces governance on all ingress requests
    
    Flow:
    1. Request enters ingress
    2. Middleware extracts action/actor/resource
    3. Calls Governance Gate (Kernel 1)
    4. If approved → continue to event bus
    5. If rejected → return 403 Forbidden
    6. If requires_approval → return 202 Accepted (pending)
    """
    
    def __init__(self):
        self.gate = governance_gate
        self.blocked_requests = 0
        self.passed_requests = 0
    
    async def process_request(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Dict[str, Any],
        risk_level: str = "medium",
        is_autonomous: bool = False
    ) -> Dict[str, Any]:
        """
        Process request through governance gate
        
        Args:
            actor: Who is making the request
            action: What action is being requested
            resource: What resource is being affected
            context: Additional context
            risk_level: Risk assessment (low/medium/high/critical)
            is_autonomous: Whether this is an autonomous action
            
        Returns:
            {
                'allowed': bool,
                'response': GovernanceResponse or error dict
            }
        """
        
        # Map risk level string to enum
        risk_map = {
            'low': ActionRiskLevel.LOW,
            'medium': ActionRiskLevel.MEDIUM,
            'high': ActionRiskLevel.HIGH,
            'critical': ActionRiskLevel.CRITICAL
        }
        risk_enum = risk_map.get(risk_level, ActionRiskLevel.MEDIUM)
        
        # Create governance request
        gov_request = GovernanceRequest(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            actor=actor,
            action=action,
            resource=resource,
            context=context,
            risk_level=risk_enum,
            source="ingress",
            is_autonomous=is_autonomous
        )
        
        # Validate through governance gate
        response = await self.gate.validate(gov_request)
        
        # Emit governance event
        await self._emit_governance_event(gov_request, response)
        
        # Handle decision
        if response.decision == GovernanceDecision.APPROVED:
            self.passed_requests += 1
            return {
                'allowed': True,
                'response': response.to_dict()
            }
        
        elif response.decision == GovernanceDecision.REJECTED:
            self.blocked_requests += 1
            return {
                'allowed': False,
                'response': response.to_dict(),
                'status_code': 403,
                'error': 'Governance rejected request'
            }
        
        elif response.decision == GovernanceDecision.REQUIRES_PARLIAMENT:
            return {
                'allowed': False,
                'response': response.to_dict(),
                'status_code': 202,
                'message': 'Request pending parliament approval',
                'approval_id': response.approval_id
            }
        
        else:  # REQUIRES_APPROVAL
            return {
                'allowed': False,
                'response': response.to_dict(),
                'status_code': 202,
                'message': 'Request pending approval'
            }
    
    async def _emit_governance_event(
        self,
        request: GovernanceRequest,
        response
    ):
        """Emit GOVERNANCE_VALIDATION event to trigger mesh"""
        
        try:
            from backend.routing.trigger_mesh_enhanced import trigger_mesh, TriggerEvent
            
            # Determine event type based on decision
            if response.decision == GovernanceDecision.APPROVED:
                event_type = "governance.approved"
            elif response.decision == GovernanceDecision.REJECTED:
                event_type = "governance.rejected"
            else:
                event_type = "governance.approval_required"
            
            event = TriggerEvent(
                event_type=event_type,
                source="governance_gate",
                actor=request.actor,
                resource=request.resource,
                payload={
                    'request_id': request.request_id,
                    'action': request.action,
                    'decision': response.decision.value,
                    'reasoning': response.reasoning,
                    'trust_score': response.trust_score,
                    'violated_policies': response.violated_policies,
                    'constitutional_compliant': response.constitutional_compliant
                },
                trust_score=response.trust_score
            )
            
            await trigger_mesh.emit(event)
        
        except Exception as e:
            print(f"⚠ Failed to emit governance event: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        total = self.passed_requests + self.blocked_requests
        
        return {
            'total_requests': total,
            'passed': self.passed_requests,
            'blocked': self.blocked_requests,
            'pass_rate': self.passed_requests / max(1, total),
            'gate_stats': self.gate.get_stats()
        }


# Global middleware instance
governance_middleware = GovernanceMiddleware()


# ============================================================================
# Decorator for automatic governance enforcement
# ============================================================================

def require_governance(
    action: str,
    resource_param: str = 'resource',
    risk_level: str = 'medium',
    is_autonomous: bool = False
):
    """
    Decorator to enforce governance on API endpoints
    
    Usage:
        @require_governance(action='deploy_model', risk_level='high')
        async def deploy_model(actor: str, resource: str):
            # This will only execute if governance approves
            pass
    
    Args:
        action: The action being performed
        resource_param: Name of the parameter containing the resource
        risk_level: Risk level (low/medium/high/critical)
        is_autonomous: Whether this is an autonomous action
    """
    
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Extract actor and resource from function parameters
            actor = kwargs.get('actor', 'unknown')
            resource = kwargs.get(resource_param, 'unknown')
            
            # Build context from all kwargs
            context = {k: v for k, v in kwargs.items() if k not in ['actor', resource_param]}
            
            # Check governance
            result = await governance_middleware.process_request(
                actor=actor,
                action=action,
                resource=resource,
                context=context,
                risk_level=risk_level,
                is_autonomous=is_autonomous
            )
            
            if not result['allowed']:
                # Return error response
                return {
                    'success': False,
                    'error': result.get('error', 'Request not approved'),
                    'governance_response': result['response']
                }
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
