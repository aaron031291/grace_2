"""
Autonomous Action Governance Wiring
All autonomous actions MUST go through governance gate before execution.

Categories:
1. Business Operations (marketplace, payments, consulting)
2. AVN Restarts & Self-Healing
3. System-Level Changes (scaling, deployment)
4. Code Generation & Deployment
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from backend.governance_system.governance_gate import (
    governance_gate,
    GovernanceRequest,
    GovernanceDecision,
    ActionRiskLevel
)


class AutonomousGovernanceWiring:
    """
    Ensures all autonomous actions go through governance
    
    Usage:
        # Before executing autonomous action:
        approved = await autonomous_governance.check_and_wait(
            actor='avn_healer',
            action='restart_service',
            resource='api_service',
            context={'anomaly_id': 'anom_123'}
        )
        
        if approved:
            # Execute action
            await restart_service()
    """
    
    def __init__(self):
        self.gate = governance_gate
        self.actions_checked = 0
        self.actions_blocked = 0
    
    async def check_and_wait(
        self,
        actor: str,
        action: str,
        resource: str,
        context: Dict[str, Any],
        timeout_seconds: int = 300
    ) -> bool:
        """
        Check governance and wait for approval (if needed)
        
        Args:
            actor: Who is requesting the action
            action: What action
            resource: What resource
            context: Additional context
            timeout_seconds: How long to wait for approval
            
        Returns:
            True if approved, False if rejected/timeout
        """
        
        self.actions_checked += 1
        
        # Determine risk level based on action type
        risk_level = self._assess_risk_level(action, context)
        
        # Create governance request
        gov_request = GovernanceRequest(
            request_id=f"auto_{datetime.utcnow().timestamp()}",
            actor=actor,
            action=action,
            resource=resource,
            context=context,
            risk_level=risk_level,
            source="autonomous",
            is_autonomous=True
        )
        
        # Validate through governance
        response = await self.gate.validate(gov_request)
        
        # Handle decision
        if response.decision == GovernanceDecision.APPROVED:
            return True
        
        elif response.decision == GovernanceDecision.REJECTED:
            self.actions_blocked += 1
            print(f"⚠ Autonomous action blocked: {action} - {response.reasoning}")
            return False
        
        elif response.decision in [GovernanceDecision.REQUIRES_PARLIAMENT, GovernanceDecision.REQUIRES_APPROVAL]:
            # Wait for approval
            print(f"⏳ Waiting for approval: {action} (approval_id: {response.approval_id})")
            
            approved = await self._wait_for_approval(
                response.approval_id,
                timeout_seconds
            )
            
            if not approved:
                self.actions_blocked += 1
            
            return approved
        
        self.actions_blocked += 1
        return False
    
    async def _wait_for_approval(
        self,
        approval_id: str,
        timeout_seconds: int
    ) -> bool:
        """Wait for parliament/human approval"""
        
        try:
            # Listen for approval event via trigger mesh
            from backend.routing.trigger_mesh_enhanced import trigger_mesh
            
            approval_received = False
            
            async def handle_approval(event):
                nonlocal approval_received
                if event.payload.get('approval_id') == approval_id:
                    if event.payload.get('approved'):
                        approval_received = True
            
            # Subscribe to approval events
            await trigger_mesh.subscribe("governance.decision_made", handle_approval)
            
            # Wait for approval or timeout
            start_time = datetime.utcnow()
            while not approval_received:
                if (datetime.utcnow() - start_time).total_seconds() > timeout_seconds:
                    print(f"⏱ Approval timeout: {approval_id}")
                    return False
                
                await asyncio.sleep(1)
            
            return True
        
        except Exception as e:
            print(f"⚠ Error waiting for approval: {e}")
            return False
    
    def _assess_risk_level(self, action: str, context: Dict[str, Any]) -> ActionRiskLevel:
        """Assess risk level for autonomous action"""
        
        # Critical risk actions
        critical_actions = [
            'delete_database',
            'shutdown_system',
            'deploy_to_production',
            'modify_governance_policy'
        ]
        
        if action in critical_actions:
            return ActionRiskLevel.CRITICAL
        
        # High risk actions
        high_risk_actions = [
            'restart_service',
            'rollback_deployment',
            'scale_down',
            'deploy_model',
            'execute_code'
        ]
        
        if action in high_risk_actions:
            return ActionRiskLevel.HIGH
        
        # Medium risk actions
        medium_risk_actions = [
            'generate_code',
            'create_task',
            'send_email',
            'process_payment'
        ]
        
        if action in medium_risk_actions:
            return ActionRiskLevel.MEDIUM
        
        # Default to medium
        return ActionRiskLevel.MEDIUM
    
    def get_stats(self) -> Dict[str, Any]:
        """Get wiring statistics"""
        return {
            'actions_checked': self.actions_checked,
            'actions_blocked': self.actions_blocked,
            'block_rate': self.actions_blocked / max(1, self.actions_checked)
        }


# Global wiring instance
autonomous_governance = AutonomousGovernanceWiring()


# ============================================================================
# Pre-wired helpers for common autonomous actions
# ============================================================================

async def check_business_operation(
    operation: str,
    actor: str,
    resource: str,
    context: Dict[str, Any]
) -> bool:
    """
    Check governance for business operations
    (marketplace, payments, consulting)
    """
    return await autonomous_governance.check_and_wait(
        actor=actor,
        action=f"business:{operation}",
        resource=resource,
        context=context
    )


async def check_avn_action(
    action: str,
    component: str,
    anomaly_id: str,
    severity: str
) -> bool:
    """
    Check governance for AVN self-healing actions
    (restarts, rollbacks, scaling)
    """
    return await autonomous_governance.check_and_wait(
        actor="avn_healer",
        action=f"avn:{action}",
        resource=component,
        context={
            'anomaly_id': anomaly_id,
            'severity': severity,
            'autonomous_healing': True
        }
    )


async def check_system_change(
    change_type: str,
    target_system: str,
    actor: str,
    details: Dict[str, Any]
) -> bool:
    """
    Check governance for system-level changes
    (scaling, deployment, configuration)
    """
    return await autonomous_governance.check_and_wait(
        actor=actor,
        action=f"system:{change_type}",
        resource=target_system,
        context={
            **details,
            'system_level_change': True
        }
    )


async def check_code_deployment(
    code_id: str,
    deployment_target: str,
    actor: str,
    verification_passed: bool
) -> bool:
    """
    Check governance for code generation & deployment
    """
    return await autonomous_governance.check_and_wait(
        actor=actor,
        action="deploy_generated_code",
        resource=deployment_target,
        context={
            'code_id': code_id,
            'verification_passed': verification_passed,
            'autonomous_deployment': True
        }
    )


# ============================================================================
# Example integrations
# ============================================================================

"""
# Business Operations Example:
from backend.autonomous.governance_wiring import check_business_operation

async def process_marketplace_order(order_id: str, actor: str):
    approved = await check_business_operation(
        operation='process_order',
        actor=actor,
        resource=f"order:{order_id}",
        context={'order_id': order_id, 'amount': 99.99}
    )
    
    if not approved:
        return {'error': 'Governance rejected order processing'}
    
    # Process order...


# AVN Self-Healing Example:
from backend.autonomous.governance_wiring import check_avn_action

async def avn_restart_service(component: str, anomaly_id: str):
    approved = await check_avn_action(
        action='restart_service',
        component=component,
        anomaly_id=anomaly_id,
        severity='high'
    )
    
    if not approved:
        print(f"⚠ Governance blocked restart of {component}")
        return
    
    # Restart service...


# System Change Example:
from backend.autonomous.governance_wiring import check_system_change

async def auto_scale_service(service_name: str, target_replicas: int):
    approved = await check_system_change(
        change_type='scale',
        target_system=service_name,
        actor='auto_scaler',
        details={
            'current_replicas': 2,
            'target_replicas': target_replicas,
            'reason': 'high_load'
        }
    )
    
    if not approved:
        print(f"⚠ Governance blocked scaling of {service_name}")
        return
    
    # Scale service...


# Code Deployment Example:
from backend.autonomous.governance_wiring import check_code_deployment

async def deploy_generated_code(code_id: str, target: str):
    # First verify code
    from backend.verification_system.verification_api import verification_api
    
    verification = await verification_api.verify_security(code)
    
    # Then check governance
    approved = await check_code_deployment(
        code_id=code_id,
        deployment_target=target,
        actor='code_generator',
        verification_passed=verification['safe_to_execute']
    )
    
    if not approved:
        print(f"⚠ Governance blocked deployment of {code_id}")
        return
    
    # Deploy code...
"""
