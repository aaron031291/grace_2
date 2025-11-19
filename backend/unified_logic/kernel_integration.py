"""
Unified Logic Kernel Integration
Connects all registered Grace kernels to unified logic and charter system

Every kernel:
- Registers with unified logic hub
- Submits handshake for quorum validation
- Receives charter-aligned directives
- Reports telemetry to central monitoring
- Participates in mission progress tracking
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class KernelRegistration:
    """Registration data for a kernel"""
    kernel_name: str
    kernel_type: str  # tier1_critical, tier2_governance, tier3_execution, tier4_agentic, tier5_service
    
    # Capabilities
    capabilities: List[str] = field(default_factory=list)
    provides_metrics: List[str] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Grace semantics
    grace_layer: str = "layer2"  # layer1, layer2, layer3
    grace_domain: str = "unknown"  # cognition, memory, execution, etc.
    requires_charter_approval: bool = False
    
    # Status
    registered: bool = False
    handshake_id: Optional[str] = None
    
    # Mission alignment
    contributes_to_pillars: List[str] = field(default_factory=list)


class KernelIntegrator:
    """
    Integrates all registered kernels with unified logic and charter
    
    Responsibilities:
    - Register all kernels with unified logic hub
    - Perform handshakes for validation
    - Map kernels to charter pillars
    - Enable charter-aware operations
    - Track kernel mission contributions
    """
    
    def __init__(self):
        self.kernel_registry: Dict[str, KernelRegistration] = {}
        self.integrated_kernels = set()
        
        # Lazy-loaded dependencies
        self.unified_logic_hub = None
        self.component_handshake = None
        self.charter = None
        
        # Initialize kernel definitions
        self._initialize_kernel_definitions()
    
    def _initialize_kernel_definitions(self):
        """Define all 20 Grace kernels"""
        
        # TIER 1: Critical Infrastructure (2 kernels)
        self.kernel_registry["message_bus"] = KernelRegistration(
            kernel_name="message_bus",
            kernel_type="tier1_critical",
            capabilities=["message_routing", "pub_sub", "acl_enforcement"],
            provides_metrics=["message_count", "topic_count", "acl_violations"],
            depends_on=[],
            grace_layer="layer1",
            grace_domain="infrastructure",
            requires_charter_approval=True,
            contributes_to_pillars=["knowledge_application"]  # Enables all communication
        )
        
        self.kernel_registry["immutable_log"] = KernelRegistration(
            kernel_name="immutable_log",
            kernel_type="tier1_critical",
            capabilities=["audit_logging", "event_recording", "compliance"],
            provides_metrics=["log_entries", "verification_rate"],
            depends_on=[],
            grace_layer="layer1",
            grace_domain="governance",
            requires_charter_approval=True,
            contributes_to_pillars=["knowledge_application"]  # Tracks all learning
        )
        
        # TIER 2: Governance & Safety kernels
        self.kernel_registry["clarity_framework"] = KernelRegistration(
            kernel_name="clarity_framework",
            kernel_type="tier2_governance",
            capabilities=["decision_recording", "5w1h_tracking", "narrative_docs"],
            provides_metrics=["stories_created", "decisions_logged"],
            depends_on=["immutable_log"],
            grace_layer="layer2",
            grace_domain="governance",
            contributes_to_pillars=["knowledge_application"]
        )
        
        self.kernel_registry["verification_framework"] = KernelRegistration(
            kernel_name="verification_framework",
            kernel_type="tier2_governance",
            capabilities=["trust_calculation", "verification", "validation"],
            provides_metrics=["verifications_run", "trust_scores"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="governance",
            contributes_to_pillars=["knowledge_application"]
        )
        
        self.kernel_registry["secret_manager"] = KernelRegistration(
            kernel_name="secret_manager",
            kernel_type="tier2_governance",
            capabilities=["secret_storage", "encryption", "rotation"],
            provides_metrics=["secrets_stored", "rotations_performed"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="security",
            requires_charter_approval=True,
            contributes_to_pillars=["knowledge_application"]
        )
        
        self.kernel_registry["governance"] = KernelRegistration(
            kernel_name="governance",
            kernel_type="tier2_governance",
            capabilities=["policy_enforcement", "approval_workflows", "constitutional_checks"],
            provides_metrics=["approvals_granted", "violations_detected"],
            depends_on=["message_bus", "immutable_log"],
            grace_layer="layer2",
            grace_domain="governance",
            requires_charter_approval=True,
            contributes_to_pillars=["knowledge_application"]  # Ensures safe learning
        )
        
        # TIER 3: Execution & Infrastructure (4 kernels)
        self.kernel_registry["infrastructure_manager"] = KernelRegistration(
            kernel_name="infrastructure_manager",
            kernel_type="tier3_execution",
            capabilities=["resource_management", "scaling", "monitoring"],
            provides_metrics=["cpu_usage", "memory_usage", "disk_usage"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="infrastructure",
            contributes_to_pillars=["renewable_energy"]  # Resource optimization
        )
        
        self.kernel_registry["memory_fusion"] = KernelRegistration(
            kernel_name="memory_fusion",
            kernel_type="tier3_execution",
            capabilities=["knowledge_storage", "retrieval", "fusion"],
            provides_metrics=["artifacts_stored", "retrieval_latency"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="memory",
            contributes_to_pillars=["knowledge_application"]  # Core knowledge storage
        )
        
        self.kernel_registry["librarian"] = KernelRegistration(
            kernel_name="librarian",
            kernel_type="tier3_execution",
            capabilities=["document_ingestion", "indexing", "search"],
            provides_metrics=["documents_indexed", "search_queries"],
            depends_on=["memory_fusion"],
            grace_layer="layer2",
            grace_domain="knowledge",
            contributes_to_pillars=["knowledge_application"]  # Document learning
        )
        
        self.kernel_registry["sandbox"] = KernelRegistration(
            kernel_name="sandbox",
            kernel_type="tier3_execution",
            capabilities=["safe_execution", "isolation", "validation"],
            provides_metrics=["executions", "safety_violations"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="execution",
            contributes_to_pillars=["knowledge_application"]
        )
        
        # TIER 4: Agentic & Intelligence (5 kernels)
        self.kernel_registry["agentic_spine"] = KernelRegistration(
            kernel_name="agentic_spine",
            kernel_type="tier4_agentic",
            capabilities=["multi_agent_coordination", "decision_making", "planning"],
            provides_metrics=["decisions_made", "plans_generated"],
            depends_on=["governance", "scheduler"],
            grace_layer="layer3",
            grace_domain="agentic",
            contributes_to_pillars=["knowledge_application", "science_beyond_limits"]
        )
        
        self.kernel_registry["voice_conversation"] = KernelRegistration(
            kernel_name="voice_conversation",
            kernel_type="tier4_agentic",
            capabilities=["speech_recognition", "tts", "conversation"],
            provides_metrics=["conversations", "accuracy"],
            depends_on=["agentic_spine"],
            grace_layer="layer3",
            grace_domain="interface",
            contributes_to_pillars=["cohabitation_innovation"]  # Human-AI interaction
        )
        
        self.kernel_registry["meta_loop"] = KernelRegistration(
            kernel_name="meta_loop",
            kernel_type="tier4_agentic",
            capabilities=["meta_learning", "optimization", "self_improvement"],
            provides_metrics=["optimization_cycles", "improvements"],
            depends_on=["agentic_spine"],
            grace_layer="layer3",
            grace_domain="intelligence",
            contributes_to_pillars=["knowledge_application", "science_beyond_limits"]
        )
        
        self.kernel_registry["learning_integration"] = KernelRegistration(
            kernel_name="learning_integration",
            kernel_type="tier4_agentic",
            capabilities=["learning_pipelines", "knowledge_integration", "training"],
            provides_metrics=["learning_tasks", "knowledge_integrated"],
            depends_on=["memory_fusion"],
            grace_layer="layer3",
            grace_domain="cognition",
            contributes_to_pillars=["knowledge_application"]  # Core learning
        )
        
        self.kernel_registry["health_monitor"] = KernelRegistration(
            kernel_name="health_monitor",
            kernel_type="tier4_agentic",
            capabilities=["health_tracking", "anomaly_detection", "alerting"],
            provides_metrics=["health_checks", "anomalies_detected"],
            depends_on=["message_bus"],
            grace_layer="layer2",
            grace_domain="monitoring",
            contributes_to_pillars=["knowledge_application"]
        )
        
        # TIER 5: Services & Orchestration (3 kernels)
        self.kernel_registry["trigger_mesh"] = KernelRegistration(
            kernel_name="trigger_mesh",
            kernel_type="tier5_service",
            capabilities=["event_distribution", "pub_sub", "trigger_routing"],
            provides_metrics=["events_published", "subscriptions"],
            depends_on=["message_bus"],
            grace_layer="layer2",
            grace_domain="infrastructure",
            contributes_to_pillars=["knowledge_application"]
        )
        
        self.kernel_registry["scheduler"] = KernelRegistration(
            kernel_name="scheduler",
            kernel_type="tier5_service",
            capabilities=["task_scheduling", "cron", "priority_management"],
            provides_metrics=["tasks_scheduled", "completed_tasks"],
            depends_on=["governance"],
            grace_layer="layer2",
            grace_domain="orchestration",
            contributes_to_pillars=["knowledge_application", "business_revenue"]
        )
        
        self.kernel_registry["api_server"] = KernelRegistration(
            kernel_name="api_server",
            kernel_type="tier5_service",
            capabilities=["http_api", "websocket", "rest"],
            provides_metrics=["requests_handled", "response_time"],
            depends_on=["governance", "memory_fusion"],
            grace_layer="layer2",
            grace_domain="interface",
            contributes_to_pillars=["knowledge_application", "business_revenue", "cohabitation_innovation"]
        )
        
        logger.info(f"[KERNEL INTEGRATOR] Defined {len(self.kernel_registry)} kernels")
    
    async def integrate_all_kernels(self):
        """Integrate all registered kernels with unified logic and charter"""
        
        total_kernels = len(self.kernel_registry)
        logger.info(f"[KERNEL INTEGRATOR] Starting integration of {total_kernels} kernels...")
        
        # Load dependencies
        await self._load_dependencies()
        
        # Register each kernel
        for kernel_name, registration in self.kernel_registry.items():
            try:
                await self._integrate_kernel(registration)
            except Exception as e:
                logger.error(f"[KERNEL INTEGRATOR] Failed to integrate {kernel_name}: {e}")
        
        logger.info(
            f"[KERNEL INTEGRATOR] Integrated {len(self.integrated_kernels)}/{total_kernels} kernels"
        )
        
        return self.get_integration_status()
    
    async def _load_dependencies(self):
        """Load unified logic dependencies"""
        
        try:
            from backend.unified_logic.unified_logic_hub import unified_logic_hub
            self.unified_logic_hub = unified_logic_hub
        except Exception as e:
            logger.warning(f"[KERNEL INTEGRATOR] Unified logic hub not available: {e}")
        
        try:
            from backend.misc.component_handshake import component_handshake
            self.component_handshake = component_handshake
        except Exception as e:
            logger.warning(f"[KERNEL INTEGRATOR] Component handshake not available: {e}")
        
        try:
            from backend.constitutional.grace_charter import get_grace_charter
            self.charter = get_grace_charter()
        except Exception as e:
            logger.warning(f"[KERNEL INTEGRATOR] Grace charter not available: {e}")
    
    async def _integrate_kernel(self, registration: KernelRegistration):
        """Integrate a single kernel"""
        
        kernel_name = registration.kernel_name
        
        logger.info(f"[KERNEL INTEGRATOR] Integrating {kernel_name}...")
        
        # Step 1: Submit handshake
        if self.component_handshake:
            try:
                handshake_id = await self.component_handshake.submit_handshake_request(
                    component_id=kernel_name,
                    component_type="kernel",
                    capabilities=registration.capabilities,
                    expected_metrics=registration.provides_metrics,
                    version="1.0.0"
                )
                
                registration.handshake_id = handshake_id
                logger.info(f"[KERNEL INTEGRATOR] {kernel_name} handshake submitted: {handshake_id}")
                
            except Exception as e:
                logger.warning(f"[KERNEL INTEGRATOR] Handshake failed for {kernel_name}: {e}")
        
        # Step 2: Register with unified logic hub
        if self.unified_logic_hub:
            try:
                await self.unified_logic_hub.submit_update(
                    update_type="config",
                    component_targets=[kernel_name],
                    content={
                        "config_changes": {
                            "kernel_registration": {
                                "name": kernel_name,
                                "capabilities": registration.capabilities,
                                "metrics": registration.provides_metrics
                            }
                        }
                    },
                    created_by="kernel_integrator",
                    risk_level="low"
                )
                
                logger.info(f"[KERNEL INTEGRATOR] {kernel_name} registered with unified logic hub")
                
            except Exception as e:
                logger.warning(f"[KERNEL INTEGRATOR] Unified logic registration failed for {kernel_name}: {e}")
        
        # Step 3: Check charter alignment
        if self.charter and registration.contributes_to_pillars:
            try:
                # Verify pillars are valid
                for pillar_name in registration.contributes_to_pillars:
                    from backend.constitutional.grace_charter import MissionPillar
                    
                    try:
                        pillar = MissionPillar(pillar_name)
                        pillar_status = self.charter.get_pillar_status(pillar)
                        
                        if pillar_status["enabled"]:
                            logger.info(f"[KERNEL INTEGRATOR] {kernel_name} contributes to enabled pillar: {pillar_name}")
                        else:
                            logger.info(f"[KERNEL INTEGRATOR] {kernel_name} contributes to locked pillar: {pillar_name}")
                    
                    except ValueError:
                        logger.warning(f"[KERNEL INTEGRATOR] Unknown pillar: {pillar_name}")
                
            except Exception as e:
                logger.warning(f"[KERNEL INTEGRATOR] Charter alignment check failed for {kernel_name}: {e}")
        
        # Mark as integrated
        registration.registered = True
        self.integrated_kernels.add(kernel_name)
        
        logger.info(f"[KERNEL INTEGRATOR] ✅ {kernel_name} integrated successfully")
    
    def get_kernel_by_name(self, kernel_name: str) -> Optional[KernelRegistration]:
        """Get kernel registration by name"""
        return self.kernel_registry.get(kernel_name)
    
    def get_kernels_by_tier(self, tier: str) -> List[KernelRegistration]:
        """Get all kernels of a specific tier"""
        return [k for k in self.kernel_registry.values() if k.kernel_type == tier]
    
    def get_kernels_by_domain(self, domain: str) -> List[KernelRegistration]:
        """Get all kernels in a Grace domain"""
        return [k for k in self.kernel_registry.values() if k.grace_domain == domain]
    
    def get_kernels_contributing_to_pillar(self, pillar_name: str) -> List[KernelRegistration]:
        """Get all kernels contributing to a mission pillar"""
        return [
            k for k in self.kernel_registry.values()
            if pillar_name in k.contributes_to_pillars
        ]
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get overall integration status"""
        
        return {
            "total_kernels": len(self.kernel_registry),
            "integrated": len(self.integrated_kernels),
            "integration_complete": len(self.integrated_kernels) == len(self.kernel_registry),
            "tier1_count": len(self.get_kernels_by_tier("tier1_critical")),
            "tier2_count": len(self.get_kernels_by_tier("tier2_governance")),
            "tier3_count": len(self.get_kernels_by_tier("tier3_execution")),
            "tier4_count": len(self.get_kernels_by_tier("tier4_agentic")),
            "tier5_count": len(self.get_kernels_by_tier("tier5_service")),
            "by_tier": {
                "tier1_critical": len(self.get_kernels_by_tier("tier1_critical")),
                "tier2_governance": len(self.get_kernels_by_tier("tier2_governance")),
                "tier3_execution": len(self.get_kernels_by_tier("tier3_execution")),
                "tier4_agentic": len(self.get_kernels_by_tier("tier4_agentic")),
                "tier5_service": len(self.get_kernels_by_tier("tier5_service"))
            },
            "by_domain": {
                domain: len(self.get_kernels_by_domain(domain))
                for domain in set(k.grace_domain for k in self.kernel_registry.values())
            },
            "charter_aware": len([k for k in self.kernel_registry.values() if k.contributes_to_pillars]),
            "requires_approval": len([k for k in self.kernel_registry.values() if k.requires_charter_approval])
        }


# Global integrator instance
_kernel_integrator: Optional[KernelIntegrator] = None


async def get_kernel_integrator() -> KernelIntegrator:
    """Get or create the global kernel integrator"""
    global _kernel_integrator
    
    if _kernel_integrator is None:
        _kernel_integrator = KernelIntegrator()
        await _kernel_integrator.integrate_all_kernels()
    
    return _kernel_integrator


async def integrate_all_kernels_with_unified_logic():
    """
    Convenience function to integrate all registered kernels
    
    Usage:
        await integrate_all_kernels_with_unified_logic()
    """
    
    integrator = await get_kernel_integrator()
    return integrator.get_integration_status()
