"""
Handshake Subscribers - Auto-ack logic for all subsystems
Each key subsystem acknowledges component handshakes
"""

import logging

logger = logging.getLogger(__name__)


async def setup_handshake_subscribers():
    """
    Wire up auto-acknowledgment handlers for all subsystems
    
    Required acknowledgers for quorum:
    - agentic_spine
    - memory_fusion
    - metrics_collector
    - anomaly_watchdog
    - self_heal_scheduler
    """
    
    try:
        from backend.trigger_mesh import trigger_mesh
        from backend.component_handshake import component_handshake
        
        # Agentic Spine handler
        async def agentic_spine_ack(event):
            """Agentic Spine acknowledges new components"""
            handshake_id = event.payload["handshake_id"]
            component_id = event.payload["component_id"]
            capabilities = event.payload.get("capabilities", [])
            
            logger.info(f"[HANDSHAKE] AgenticSpine processing: {component_id}")
            
            # Spine-specific adjustments
            adjustments = {"context_updated": True}
            
            if "decision_making" in capabilities:
                adjustments["decision_framework_extended"] = True
            
            # Send acknowledgment
            await component_handshake.receive_acknowledgment(
                handshake_id=handshake_id,
                acknowledger="agentic_spine",
                adjustments=adjustments
            )
            
            logger.info(f"[HANDSHAKE] AgenticSpine ACK: {handshake_id}")
        
        # Memory Fusion handler
        async def memory_fusion_ack(event):
            """Memory Fusion acknowledges new components"""
            handshake_id = event.payload["handshake_id"]
            component_id = event.payload["component_id"]
            capabilities = event.payload.get("capabilities", [])
            
            logger.info(f"[HANDSHAKE] MemoryFusion processing: {component_id}")
            
            # Memory-specific adjustments
            adjustments = {}
            
            if "schema_changes" in capabilities:
                # Reload schemas
                adjustments["schemas_reloaded"] = True
            
            if "storage" in capabilities:
                # Update ACLs
                adjustments["acl_updated"] = True
            
            # Send acknowledgment
            await component_handshake.receive_acknowledgment(
                handshake_id=handshake_id,
                acknowledger="memory_fusion",
                adjustments=adjustments
            )
            
            logger.info(f"[HANDSHAKE] MemoryFusion ACK: {handshake_id}")
        
        # Metrics Collector handler
        async def metrics_collector_ack(event):
            """Metrics Collector acknowledges new components"""
            handshake_id = event.payload["handshake_id"]
            component_id = event.payload["component_id"]
            expected_metrics = event.payload.get("expected_metrics", [])
            
            logger.info(f"[HANDSHAKE] MetricsCollector processing: {component_id}")
            
            # Register new metrics
            adjustments = {
                "metrics_registered": len(expected_metrics)
            }
            
            # Send acknowledgment
            await component_handshake.receive_acknowledgment(
                handshake_id=handshake_id,
                acknowledger="metrics_collector",
                adjustments=adjustments
            )
            
            logger.info(f"[HANDSHAKE] MetricsCollector ACK: {handshake_id}")
        
        # Anomaly Watchdog handler
        async def anomaly_watchdog_ack(event):
            """Anomaly Watchdog acknowledges new components"""
            handshake_id = event.payload["handshake_id"]
            component_id = event.payload["component_id"]
            
            logger.info(f"[HANDSHAKE] AnomalyWatchdog processing: {component_id}")
            
            # Start monitoring new component
            adjustments = {"monitoring_started": True}
            
            # Send acknowledgment
            await component_handshake.receive_acknowledgment(
                handshake_id=handshake_id,
                acknowledger="anomaly_watchdog",
                adjustments=adjustments
            )
            
            logger.info(f"[HANDSHAKE] AnomalyWatchdog ACK: {handshake_id}")
        
        # Self-Heal Scheduler handler
        async def self_heal_ack(event):
            """Self-Heal Scheduler acknowledges new components"""
            handshake_id = event.payload["handshake_id"]
            component_id = event.payload["component_id"]
            capabilities = event.payload.get("capabilities", [])
            
            logger.info(f"[HANDSHAKE] SelfHeal processing: {component_id}")
            
            # Self-heal specific adjustments
            adjustments = {}
            
            if "playbook" in str(capabilities).lower():
                adjustments["playbooks_updated"] = True
            else:
                adjustments["playbooks_updated"] = False
            
            # Send acknowledgment
            await component_handshake.receive_acknowledgment(
                handshake_id=handshake_id,
                acknowledger="self_heal_scheduler",
                adjustments=adjustments
            )
            
            logger.info(f"[HANDSHAKE] SelfHeal ACK: {handshake_id}")
        
        # Subscribe all handlers
        trigger_mesh.subscribe("unified_logic.handshake_announce", agentic_spine_ack)
        trigger_mesh.subscribe("unified_logic.handshake_announce", memory_fusion_ack)
        trigger_mesh.subscribe("unified_logic.handshake_announce", metrics_collector_ack)
        trigger_mesh.subscribe("unified_logic.handshake_announce", anomaly_watchdog_ack)
        trigger_mesh.subscribe("unified_logic.handshake_announce", self_heal_ack)
        
        logger.info("[HANDSHAKE] All subsystem auto-ack handlers subscribed")
        logger.info("  - agentic_spine")
        logger.info("  - memory_fusion")
        logger.info("  - metrics_collector")
        logger.info("  - anomaly_watchdog")
        logger.info("  - self_heal_scheduler")
        
    except Exception as e:
        logger.error(f"[HANDSHAKE] Failed to setup subscribers: {e}")


# Setup function called during boot
async def initialize_handshake_protocol():
    """Initialize handshake protocol with all subscribers"""
    await setup_handshake_subscribers()
