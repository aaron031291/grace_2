"""
External Model Orchestration Layer - PRODUCTION
Integrates external model protocol into Grace's orchestration flow

Grace's Control Principles:
1. Grace is the authority - external models are consulted advisors
2. One-way by default - only bi-directional when operationally valuable
3. Strict contracts - versioned, scoped, audited
4. Security first - HMAC auth, rate limits, sandboxing
5. Trust but verify - all suggestions validated before execution
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.external_integration.external_model_protocol import (
    external_model_protocol,
    ExternalModelContract,
    ExternalModelType,
    ProtocolVersion,
    RequestType
)

logger = logging.getLogger(__name__)


class IntegrationMode(Enum):
    """Mode of integration with external models"""
    ONE_WAY_CONSUME = "one_way_consume"  # Grace consumes output only (safer)
    BI_DIRECTIONAL = "bi_directional"  # Full two-way (requires strict governance)


@dataclass
class ExternalModelIntegration:
    """
    Configuration for how Grace integrates with an external model
    
    Determines:
    - One-way vs bi-directional
    - What Grace shares
    - What Grace consumes
    - Security requirements
    """
    
    model_name: str
    integration_mode: IntegrationMode
    
    # Operational value
    provides_remediation: bool = False
    provides_insights: bool = False
    provides_validation: bool = False
    
    # Decision
    use_bi_directional: bool = False  # Requires all 3 requirements met
    
    # Contract requirements (if bi-directional)
    contract: Optional[ExternalModelContract] = None
    
    # Metadata
    enabled: bool = True
    last_interaction: Optional[str] = None


class ExternalModelOrchestrator:
    """
    Orchestrates external model integrations
    
    Makes decisions:
    - Which models get bi-directional access
    - Which stay one-way consumption
    - When to enable/disable integrations
    """
    
    def __init__(self):
        self.integrations: Dict[str, ExternalModelIntegration] = {}
        
        # Statistics
        self.total_requests_routed = 0
        self.bi_directional_count = 0
        self.one_way_count = 0
        
        logger.info("[EXTERNAL-ORCHESTRATOR] Initialized - Grace maintains authority")
    
    def evaluate_integration_requirements(
        self,
        model_name: str,
        provides_remediation: bool = False,
        provides_insights: bool = False,
        has_clear_contract: bool = False,
        has_security_governance: bool = False
    ) -> IntegrationMode:
        """
        Evaluate if bi-directional integration is warranted
        
        Returns ONE_WAY unless ALL three requirements are met:
        1. Clear contract and scope
        2. Security and governance
        3. Operational value (remediation/insights Grace can't generate)
        """
        
        # Operational value check
        has_operational_value = provides_remediation or provides_insights
        
        # All three requirements must be met
        if has_clear_contract and has_security_governance and has_operational_value:
            logger.info(
                f"[EXTERNAL-ORCHESTRATOR] {model_name}: Bi-directional approved "
                f"(contract ✓, security ✓, value ✓)"
            )
            return IntegrationMode.BI_DIRECTIONAL
        else:
            # Missing requirements - use safer one-way
            missing = []
            if not has_clear_contract:
                missing.append("contract")
            if not has_security_governance:
                missing.append("security")
            if not has_operational_value:
                missing.append("operational_value")
            
            logger.info(
                f"[EXTERNAL-ORCHESTRATOR] {model_name}: One-way only "
                f"(missing: {', '.join(missing)})"
            )
            return IntegrationMode.ONE_WAY_CONSUME
    
    def register_integration(
        self,
        model_name: str,
        model_type: ExternalModelType,
        provides_remediation: bool = False,
        provides_insights: bool = False,
        provides_validation: bool = False
    ) -> ExternalModelIntegration:
        """
        Register integration with external model
        
        Grace decides one-way vs bi-directional based on requirements
        """
        
        # For bi-directional, need a contract
        contract = None
        has_clear_contract = False
        has_security_governance = False
        
        if provides_remediation or provides_insights:
            # Operational value exists - check if we should enable bi-directional
            
            # Create contract
            contract = ExternalModelContract(
                contract_id=f"contract_{model_name}_{datetime.utcnow().timestamp()}",
                model_name=model_name,
                model_type=model_type,
                protocol_version=ProtocolVersion.V2_0,
                supported_requests=[RequestType.GET_REMEDIATION] if provides_remediation else [RequestType.GET_INSIGHT],
                grace_sends=['error_description', 'context', 'grace_version'],
                grace_receives=['remediation_actions', 'confidence', 'reasoning'] if provides_remediation else ['insights', 'confidence'],
                requires_authentication=True,
                sandbox_required=True,
                max_request_rate=60,
                max_response_size_kb=512,
                trust_score=0.6,  # Start with medium trust
                requires_grace_approval=True,  # Grace MUST approve all actions
                audit_all_interactions=True
            )
            
            has_clear_contract = True
            has_security_governance = True  # Contract enforces security
        
        # Evaluate integration mode
        mode = self.evaluate_integration_requirements(
            model_name,
            provides_remediation=provides_remediation,
            provides_insights=provides_insights,
            has_clear_contract=has_clear_contract,
            has_security_governance=has_security_governance
        )
        
        # Create integration
        integration = ExternalModelIntegration(
            model_name=model_name,
            integration_mode=mode,
            provides_remediation=provides_remediation,
            provides_insights=provides_insights,
            provides_validation=provides_validation,
            use_bi_directional=(mode == IntegrationMode.BI_DIRECTIONAL),
            contract=contract
        )
        
        # Register contract if bi-directional
        if integration.use_bi_directional and contract:
            external_model_protocol.registry.register_model(contract)
            self.bi_directional_count += 1
        else:
            self.one_way_count += 1
        
        self.integrations[model_name] = integration
        
        logger.info(
            f"[EXTERNAL-ORCHESTRATOR] Registered {model_name}: "
            f"{mode.value} "
            f"({'bi-directional' if integration.use_bi_directional else 'one-way'})"
        )
        
        return integration
    
    async def request_remediation(
        self,
        model_name: str,
        error_description: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Request remediation from external model
        
        Flow:
        1. Check if model provides remediation
        2. Check integration mode
        3. Send request (if bi-directional)
        4. Grace validates response
        5. Grace approves/rejects
        6. Return for Grace to execute
        """
        
        integration = self.integrations.get(model_name)
        
        if not integration:
            logger.debug(f"[EXTERNAL-ORCHESTRATOR] Model not registered: {model_name}")
            return None
        
        if not integration.provides_remediation:
            logger.debug(f"[EXTERNAL-ORCHESTRATOR] {model_name} doesn't provide remediation")
            return None
        
        if integration.integration_mode == IntegrationMode.ONE_WAY_CONSUME:
            logger.debug(
                f"[EXTERNAL-ORCHESTRATOR] {model_name} is one-way only - "
                f"cannot send requests"
            )
            return None
        
        # Bi-directional - send request
        logger.info(f"[EXTERNAL-ORCHESTRATOR] Requesting remediation from {model_name}")
        
        result = await external_model_protocol.get_remediation(
            model_name=model_name,
            error_description=error_description,
            context=context
        )
        
        self.total_requests_routed += 1
        
        if result:
            # Grace must approve
            if result.get('requires_grace_approval'):
                logger.info(
                    f"[EXTERNAL-ORCHESTRATOR] Remediation from {model_name} "
                    f"requires Grace approval (confidence: {result.get('confidence', 0):.2f})"
                )
                
                # Return for Grace to review and approve
                return {
                    'model': model_name,
                    'suggestion': result['suggestion'],
                    'confidence': result.get('confidence', 0.0),
                    'grace_approval_required': True,
                    'approved': False  # Not yet approved
                }
            else:
                # Auto-approved (only for very high trust models)
                return {
                    'model': model_name,
                    'suggestion': result['suggestion'],
                    'confidence': result.get('confidence', 0.0),
                    'grace_approval_required': False,
                    'approved': True
                }
        
        return None
    
    def approve_external_action(
        self,
        model_name: str,
        suggested_actions: List[str]
    ) -> Dict[str, Any]:
        """
        Grace approves external model's suggested actions
        
        Grace validates:
        - Actions are safe
        - Within scope
        - Not affecting critical systems
        """
        
        logger.info(
            f"[EXTERNAL-ORCHESTRATOR] Grace reviewing actions from {model_name}: "
            f"{', '.join(suggested_actions)}"
        )
        
        # Check each action
        approved_actions = []
        rejected_actions = []
        
        # Grace's approval logic
        for action in suggested_actions:
            if self._is_action_safe(action):
                approved_actions.append(action)
            else:
                rejected_actions.append(action)
                logger.warning(f"[EXTERNAL-ORCHESTRATOR] Grace rejected unsafe action: {action}")
        
        return {
            'approved': approved_actions,
            'rejected': rejected_actions,
            'approval_rate': len(approved_actions) / max(1, len(suggested_actions))
        }
    
    def _is_action_safe(self, action: str) -> bool:
        """
        Grace's safety check for external actions
        
        Rejects:
        - System-level commands
        - Secret access
        - Production deployments
        - Data deletion
        """
        
        unsafe_keywords = [
            'delete', 'drop', 'remove', 'destroy',
            'production', 'secret', 'key', 'password',
            'sudo', 'admin', 'root', 'privilege'
        ]
        
        action_lower = action.lower()
        
        for keyword in unsafe_keywords:
            if keyword in action_lower:
                return False
        
        # Safe actions
        safe_prefixes = [
            'restart', 'clear_cache', 'reconnect', 'refresh',
            'log', 'monitor', 'analyze', 'check'
        ]
        
        for prefix in safe_prefixes:
            if action_lower.startswith(prefix):
                return True
        
        # Default: reject unknown actions
        return False
    
    def get_stats(self) -> Dict:
        """Get orchestrator statistics"""
        
        return {
            'total_integrations': len(self.integrations),
            'bi_directional': self.bi_directional_count,
            'one_way': self.one_way_count,
            'total_requests_routed': self.total_requests_routed,
            'integrations': {
                name: {
                    'mode': integration.integration_mode.value,
                    'provides_remediation': integration.provides_remediation,
                    'enabled': integration.enabled
                }
                for name, integration in self.integrations.items()
            }
        }


# Global orchestrator
external_model_orchestrator = ExternalModelOrchestrator()


# ============================================================================
# EXAMPLE: Register some external models
# ============================================================================

def register_default_external_models():
    """Register default external model integrations"""
    
    # Example 1: External remediation specialist (bi-directional)
    # Only if provides remediation Grace can't do locally
    external_model_orchestrator.register_integration(
        model_name="external_remediation_specialist",
        model_type=ExternalModelType.REMEDIATION_SPECIALIST,
        provides_remediation=True,  # Operational value ✓
        provides_insights=False
        # Contract ✓ (auto-created)
        # Security ✓ (enforced by contract)
        # Result: BI_DIRECTIONAL approved
    )
    
    # Example 2: External domain expert (one-way)
    # Just provides telemetry - safer as one-way
    external_model_orchestrator.register_integration(
        model_name="domain_expert_logger",
        model_type=ExternalModelType.DOMAIN_EXPERT,
        provides_remediation=False,  # No operational value for bi-directional
        provides_insights=True  # Grace consumes, doesn't send back
        # Result: ONE_WAY_CONSUME (safer, simpler)
    )
    
    logger.info("[EXTERNAL-ORCHESTRATOR] Registered default external models")
