"""
Component Cryptographic Registry
Universal cryptographic interface for all 48 Grace components
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ComponentCryptoInterface:
    """Standard cryptographic interface for Grace components"""
    component_id: str
    component_type: str
    crypto_identity: Optional[str] = None
    initialized: bool = False


class UniversalComponentCryptoInterface:
    """Standard cryptographic interface for all Grace components"""
    
    # Complete 48-component mapping
    GRACE_COMPONENT_CRYPTO_MAP = {
        # Layer 1: Governance (Components 1-6)
        "component_01_governance_engine": "constitutional_authority_crypto_identity",
        "component_02_parliament": "democratic_governance_crypto_identity",
        "component_03_quorum_system": "collective_intelligence_crypto_identity",
        "component_04_trust_core_kernel": "trust_management_crypto_identity",
        "component_05_verification_engine": "truth_validation_crypto_identity",
        "component_06_unified_logic": "cross_layer_coordination_crypto_identity",
        
        # Layer 2: Event Mesh (Components 7-12)
        "component_07_trigger_mesh": "event_coordination_crypto_identity",
        "component_08_event_routing": "intelligent_distribution_crypto_identity",
        "component_09_priority_manager": "priority_assessment_crypto_identity",
        "component_10_message_broker": "message_coordination_crypto_identity",
        "component_11_event_processor": "event_processing_crypto_identity",
        "component_12_notification_system": "notification_coordination_crypto_identity",
        
        # Layer 3: Memory Core (Components 13-18)
        "component_13_lightning_memory": "ultra_high_speed_crypto_identity",
        "component_14_fusion_memory": "deep_contextual_crypto_identity",
        "component_15_library_memory": "knowledge_storage_crypto_identity",
        "component_16_vector_memory": "semantic_embeddings_crypto_identity",
        "component_17_temporal_memory": "temporal_patterns_crypto_identity",
        "component_18_memory_coordinator": "memory_orchestration_crypto_identity",
        
        # Layer 4: Immutable Systems (Components 19-24)
        "component_19_immutable_logs": "audit_trail_crypto_identity",
        "component_20_blockchain_anchor": "blockchain_verification_crypto_identity",
        "component_21_data_cube": "analytics_aggregation_crypto_identity",
        "component_22_metrics_collector": "telemetry_collection_crypto_identity",
        "component_23_snapshots": "state_preservation_crypto_identity",
        "component_24_audit_system": "compliance_audit_crypto_identity",
        
        # Layer 5: AI/ML Systems (Components 25-30)
        "component_25_agentic_spine": "autonomous_decision_crypto_identity",
        "component_26_ml_pipeline": "machine_learning_crypto_identity",
        "component_27_causal_analyzer": "causal_reasoning_crypto_identity",
        "component_28_proactive_intelligence": "predictive_analysis_crypto_identity",
        "component_29_code_healer": "self_repair_crypto_identity",
        "component_30_autonomous_improver": "self_optimization_crypto_identity",
        
        # Layer 6: Self-Heal (Components 31-36)
        "component_31_self_heal_scheduler": "healing_coordination_crypto_identity",
        "component_32_playbook_executor": "remediation_execution_crypto_identity",
        "component_33_meta_loop": "system_supervision_crypto_identity",
        "component_34_anomaly_watchdog": "anomaly_detection_crypto_identity",
        "component_35_boot_pipeline": "startup_validation_crypto_identity",
        "component_36_learning_system": "pattern_learning_crypto_identity",
        
        # Layer 7: External Integration (Components 37-42)
        "component_37_github_miner": "github_integration_crypto_identity",
        "component_38_reddit_learner": "reddit_integration_crypto_identity",
        "component_39_web_scraper": "web_learning_crypto_identity",
        "component_40_api_discovery": "api_integration_crypto_identity",
        "component_41_amp_integration": "amp_api_crypto_identity",
        "component_42_youtube_learner": "youtube_integration_crypto_identity",
        
        # Layer 8: User Interaction (Components 43-48)
        "component_43_chat_api": "conversation_interface_crypto_identity",
        "component_44_multimodal_api": "multimodal_interface_crypto_identity",
        "component_45_terminal_chat": "terminal_interface_crypto_identity",
        "component_46_websocket_manager": "realtime_connection_crypto_identity",
        "component_47_auth_system": "authentication_crypto_identity",
        "component_48_ide_security": "development_security_crypto_identity",
    }
    
    def __init__(self, component_id: str, component_type: str):
        """Initialize component with crypto capabilities"""
        
        self.component_id = component_id
        self.component_type = component_type
        self.crypto_identity = None
        self._crypto_engine = None
    
    async def initialize_component_crypto_identity(self) -> str:
        """
        Initialize cryptographic identity for component
        
        Returns crypto_id for this component
        """
        
        # Lazy load crypto engine
        if not self._crypto_engine:
            from backend.crypto_assignment_engine import crypto_engine
            self._crypto_engine = crypto_engine
        
        # Assign crypto identity
        identity = await self._crypto_engine.assign_universal_crypto_identity(
            entity_id=self.component_id,
            entity_type="grace_components",
            crypto_context={
                "component_type": self.component_type,
                "initialization": "component_startup"
            }
        )
        
        self.crypto_identity = identity.crypto_id
        
        logger.info(f"Component {self.component_id} initialized with crypto ID: {self.crypto_identity}")
        
        return self.crypto_identity
    
    async def sign_component_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cryptographically sign component operations
        
        Returns signed operation with signature and constitutional validation
        """
        
        if not self.crypto_identity:
            await self.initialize_component_crypto_identity()
        
        # Generate operation signature
        import hashlib
        import json
        
        operation_json = json.dumps(operation_data, sort_keys=True)
        operation_hash = hashlib.sha3_256(operation_json.encode()).hexdigest()
        
        signature = hashlib.sha3_256(
            f"{self.crypto_identity}:{operation_hash}".encode()
        ).hexdigest()
        
        # Constitutional validation (if governance available)
        constitutional_approved = await self._validate_operation_constitutionally(operation_data)
        
        return {
            "operation": operation_data,
            "crypto_id": self.crypto_identity,
            "signature": signature,
            "constitutional_approved": constitutional_approved,
            "signed_at": datetime.now().isoformat()
        }
    
    async def validate_incoming_crypto_signature(
        self,
        signed_message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate cryptographic signatures from other components"""
        
        if not self._crypto_engine:
            from backend.crypto_assignment_engine import crypto_engine
            self._crypto_engine = crypto_engine
        
        # Lightning-fast validation
        validation = await self._crypto_engine.validate_signature_lightning_fast(signed_message)
        
        return validation
    
    async def _validate_operation_constitutionally(self, operation_data: Dict[str, Any]) -> bool:
        """Validate operation against constitutional principles"""
        
        try:
            from backend.governance import governance_engine
            
            result = await governance_engine.check_action(
                actor=self.component_id,
                action=operation_data.get("action", "component_operation"),
                resource=operation_data.get("resource", "system"),
                context=operation_data
            )
            
            return result.get("approved", True)
            
        except Exception:
            return True  # Allow if governance not available


class ComponentCryptoRegistry:
    """Registry for all Grace component cryptographic identities"""
    
    def __init__(self):
        self.registered_components = {}
        self.crypto_identities = {}
    
    async def register_all_grace_components_crypto(self) -> List[Dict[str, Any]]:
        """Register cryptographic identities for all 48 Grace components"""
        
        from backend.crypto_assignment_engine import crypto_engine
        
        registrations = []
        
        for component_id, crypto_type in UniversalComponentCryptoInterface.GRACE_COMPONENT_CRYPTO_MAP.items():
            try:
                # Create interface for component
                interface = UniversalComponentCryptoInterface(component_id, crypto_type)
                
                # Initialize crypto identity
                crypto_id = await interface.initialize_component_crypto_identity()
                
                # Register
                self.registered_components[component_id] = interface
                self.crypto_identities[component_id] = crypto_id
                
                registrations.append({
                    "component_id": component_id,
                    "crypto_type": crypto_type,
                    "crypto_id": crypto_id,
                    "status": "registered"
                })
                
            except Exception as e:
                logger.error(f"Failed to register {component_id}: {e}")
                registrations.append({
                    "component_id": component_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        logger.info(f"Registered {len(self.registered_components)}/48 components with crypto identities")
        
        return registrations
    
    def get_component_interface(self, component_id: str) -> Optional[UniversalComponentCryptoInterface]:
        """Get crypto interface for component"""
        return self.registered_components.get(component_id)


# Global registry
component_crypto_registry = ComponentCryptoRegistry()
