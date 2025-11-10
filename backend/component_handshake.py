"""
Component Handshake Protocol
Secure onboarding for new services/versions joining Grace
"""

import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timezone
import asyncio
import uuid

logger = logging.getLogger(__name__)


class ComponentHandshake:
    """
    Handshake protocol for component onboarding:
    1. New service submits handshake request
    2. Hub validates governance + crypto
    3. Hub announces to all subsystems
    4. Subsystems acknowledge
    5. Hub tracks quorum
    6. Marks as integrated when quorum met
    7. Starts validation window
    """
    
    def __init__(self):
        # Active handshakes (handshake_id -> handshake_data)
        self.active_handshakes: Dict[str, Dict[str, Any]] = {}
        
        # Component registry (component_id -> component_info)
        self.component_registry: Dict[str, Dict[str, Any]] = {}
        
        # Required acknowledgers for quorum
        self.required_acks = {
            "agentic_spine",
            "memory_fusion",
            "metrics_collector",
            "anomaly_watchdog",
            "self_heal_scheduler"
        }
        
        # Lazy-loaded dependencies
        self._governance = None
        self._crypto_engine = None
        self._immutable_log = None
        self._trigger_mesh = None
        self._unified_logic_hub = None
    
    async def submit_handshake_request(
        self,
        component_id: str,
        component_type: str,
        capabilities: List[str],
        expected_metrics: List[str],
        version: str,
        crypto_signature: Optional[str] = None
    ) -> str:
        """
        Submit handshake request for new/updated component
        
        Args:
            component_id: Unique component identifier
            component_type: Type (service, agent, model, etc.)
            capabilities: List of capabilities provided
            expected_metrics: Metrics this component will emit
            version: Component version
            crypto_signature: Optional signature
            
        Returns:
            handshake_id for tracking
        """
        
        handshake_id = f"handshake_{uuid.uuid4().hex[:12]}"
        
        # Create handshake package
        handshake = {
            "handshake_id": handshake_id,
            "component_id": component_id,
            "component_type": component_type,
            "capabilities": capabilities,
            "expected_metrics": expected_metrics,
            "version": version,
            "crypto_signature": crypto_signature,
            "submitted_at": datetime.now(timezone.utc),
            "status": "pending",
            "acknowledgments": set(),
            "quorum_met": False
        }
        
        self.active_handshakes[handshake_id] = handshake
        
        # Start async processing
        asyncio.create_task(self._process_handshake(handshake))
        
        logger.info(f"[HANDSHAKE] Request submitted: {component_id} ({handshake_id})")
        
        return handshake_id
    
    async def _process_handshake(self, handshake: Dict[str, Any]):
        """
        Process handshake through full protocol:
        1. Validate governance + crypto
        2. Log request
        3. Announce to subsystems
        4. Wait for acknowledgments
        5. Check quorum
        6. Mark as integrated
        7. Start validation window
        """
        
        handshake_id = handshake["handshake_id"]
        component_id = handshake["component_id"]
        
        try:
            # Step 1: Governance validation
            await self._validate_governance(handshake)
            
            # Step 2: Crypto validation
            await self._validate_crypto(handshake)
            
            # Step 3: Log request
            await self._log_handshake_request(handshake)
            
            # Step 4: Announce to subsystems
            await self._announce_handshake(handshake)
            
            # Step 5: Wait for acknowledgments (timeout: 60s)
            await self._wait_for_quorum(handshake, timeout=60)
            
            # Step 6: Check quorum and integrate
            if handshake["quorum_met"]:
                await self._integrate_component(handshake)
            else:
                await self._handle_quorum_failure(handshake)
            
        except Exception as e:
            logger.error(f"[HANDSHAKE] Processing failed for {handshake_id}: {e}")
            handshake["status"] = "failed"
            handshake["error"] = str(e)
    
    async def _validate_governance(self, handshake: Dict[str, Any]):
        """Validate handshake against governance policies"""
        
        try:
            from backend.governance import governance_engine
            self._governance = governance_engine
            
            decision = await self._governance.check_action(
                actor=handshake["component_id"],
                action="component_handshake",
                resource="grace_system",
                context={
                    "handshake_id": handshake["handshake_id"],
                    "component_type": handshake["component_type"],
                    "capabilities": handshake["capabilities"],
                    "version": handshake["version"]
                }
            )
            
            if not decision.get("approved", True):
                raise Exception(f"Governance blocked handshake: {decision.get('reason')}")
            
            handshake["governance_approval_id"] = decision.get("approval_id")
            logger.info(f"[HANDSHAKE] Governance approved: {handshake['handshake_id']}")
            
        except ImportError:
            logger.warning(f"[HANDSHAKE] Governance not available - skipping validation")
    
    async def _validate_crypto(self, handshake: Dict[str, Any]):
        """Validate crypto signature and assign identity"""
        
        try:
            from backend.crypto_assignment_engine import crypto_engine
            self._crypto_engine = crypto_engine
            
            # Assign crypto identity if not provided
            if not handshake.get("crypto_signature"):
                identity = await self._crypto_engine.assign_universal_crypto_identity(
                    entity_id=handshake["handshake_id"],
                    entity_type="grace_components",
                    crypto_context={
                        "component_id": handshake["component_id"],
                        "component_type": handshake["component_type"],
                        "capabilities": handshake["capabilities"]
                    }
                )
                
                handshake["crypto_id"] = identity.crypto_id
                handshake["crypto_signature"] = identity.signature
            else:
                # Verify provided signature
                validation = await self._crypto_engine.validate_signature_lightning_fast({
                    "crypto_id": handshake["component_id"],
                    "signature": handshake["crypto_signature"]
                })
                
                if not validation.get("valid"):
                    raise Exception("Invalid crypto signature")
            
            logger.info(f"[HANDSHAKE] Crypto validated: {handshake['handshake_id']}")
            
        except ImportError:
            logger.warning(f"[HANDSHAKE] Crypto engine not available - skipping validation")
    
    async def _log_handshake_request(self, handshake: Dict[str, Any]):
        """Log handshake request to immutable log"""
        
        try:
            from backend.immutable_log import immutable_log
            self._immutable_log = immutable_log
            
            await self._immutable_log.append(
                actor=handshake["component_id"],
                action="component_handshake_requested",
                resource="grace_system",
                subsystem="component_handshake",
                payload={
                    "handshake_id": handshake["handshake_id"],
                    "component_id": handshake["component_id"],
                    "component_type": handshake["component_type"],
                    "capabilities": handshake["capabilities"],
                    "expected_metrics": handshake["expected_metrics"],
                    "version": handshake["version"],
                    "governance_approval_id": handshake.get("governance_approval_id")
                },
                result="requested",
                signature=handshake.get("crypto_signature")
            )
            
            logger.info(f"[HANDSHAKE] Logged to immutable log: {handshake['handshake_id']}")
            
        except Exception as e:
            logger.debug(f"Could not log handshake: {e}")
    
    async def _announce_handshake(self, handshake: Dict[str, Any]):
        """Announce handshake to all subsystems via trigger mesh"""
        
        try:
            from backend.trigger_mesh import trigger_mesh, TriggerEvent
            self._trigger_mesh = trigger_mesh
            
            event = TriggerEvent(
                event_type="unified_logic.handshake_announce",
                source="component_handshake",
                actor=handshake["component_id"],
                resource="grace_system",
                payload={
                    "handshake_id": handshake["handshake_id"],
                    "component_id": handshake["component_id"],
                    "component_type": handshake["component_type"],
                    "capabilities": handshake["capabilities"],
                    "expected_metrics": handshake["expected_metrics"],
                    "version": handshake["version"],
                    "crypto_signature": handshake.get("crypto_signature"),
                    "requires_ack": True
                },
                timestamp=datetime.now(timezone.utc)
            )
            
            await self._trigger_mesh.publish(event)
            
            logger.info(f"[HANDSHAKE] Announced to subsystems: {handshake['handshake_id']}")
            
        except Exception as e:
            logger.error(f"Could not announce handshake: {e}")
    
    async def _wait_for_quorum(self, handshake: Dict[str, Any], timeout: int):
        """Wait for subsystem acknowledgments"""
        
        handshake_id = handshake["handshake_id"]
        start_time = datetime.now(timezone.utc)
        
        while True:
            # Check if quorum met
            acks = handshake["acknowledgments"]
            required = self.required_acks
            
            if acks >= required:
                handshake["quorum_met"] = True
                logger.info(f"[HANDSHAKE] Quorum met: {handshake_id} ({len(acks)}/{len(required)})")
                break
            
            # Check timeout
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            if elapsed > timeout:
                logger.warning(f"[HANDSHAKE] Quorum timeout: {handshake_id} ({len(acks)}/{len(required)})")
                logger.warning(f"  Received: {acks}")
                logger.warning(f"  Missing: {required - acks}")
                break
            
            # Wait a bit
            await asyncio.sleep(1)
    
    async def receive_acknowledgment(
        self,
        handshake_id: str,
        acknowledger: str,
        adjustments: Optional[Dict[str, Any]] = None
    ):
        """
        Receive acknowledgment from subsystem
        
        Args:
            handshake_id: Handshake being acknowledged
            acknowledger: Subsystem name sending ack
            adjustments: Optional adjustments (schema reload, ACL update, etc.)
        """
        
        handshake = self.active_handshakes.get(handshake_id)
        
        if not handshake:
            logger.warning(f"[HANDSHAKE] Unknown handshake: {handshake_id}")
            return
        
        # Record acknowledgment
        handshake["acknowledgments"].add(acknowledger)
        
        # Store adjustments
        if not handshake.get("subsystem_adjustments"):
            handshake["subsystem_adjustments"] = {}
        
        handshake["subsystem_adjustments"][acknowledger] = adjustments or {}
        
        logger.info(f"[HANDSHAKE] Ack received from {acknowledger}: {handshake_id}")
        logger.info(f"  Progress: {len(handshake['acknowledgments'])}/{len(self.required_acks)}")
    
    async def _integrate_component(self, handshake: Dict[str, Any]):
        """Mark component as integrated and start validation"""
        
        handshake_id = handshake["handshake_id"]
        component_id = handshake["component_id"]
        
        # Update status
        handshake["status"] = "integrated"
        handshake["integrated_at"] = datetime.now(timezone.utc)
        
        # Register component
        self.component_registry[component_id] = {
            "component_id": component_id,
            "component_type": handshake["component_type"],
            "capabilities": handshake["capabilities"],
            "expected_metrics": handshake["expected_metrics"],
            "version": handshake["version"],
            "crypto_id": handshake.get("crypto_id"),
            "handshake_id": handshake_id,
            "integrated_at": handshake["integrated_at"],
            "status": "active"
        }
        
        # Log integration
        if self._immutable_log:
            try:
                await self._immutable_log.append(
                    actor="component_handshake",
                    action="component_integrated",
                    resource=component_id,
                    subsystem="component_handshake",
                    payload={
                        "handshake_id": handshake_id,
                        "component_id": component_id,
                        "quorum_size": len(handshake["acknowledgments"]),
                        "subsystem_adjustments": handshake.get("subsystem_adjustments", {})
                    },
                    result="integrated",
                    signature=handshake.get("crypto_signature")
                )
            except Exception as e:
                logger.debug(f"Could not log integration: {e}")
        
        # Start validation window
        await self._start_validation_window(handshake)
        
        logger.info(f"[HANDSHAKE] Component integrated: {component_id}")
    
    async def _handle_quorum_failure(self, handshake: Dict[str, Any]):
        """Handle failure to reach quorum"""
        
        handshake["status"] = "quorum_failed"
        handshake["failed_at"] = datetime.now(timezone.utc)
        
        missing_acks = self.required_acks - handshake["acknowledgments"]
        
        logger.error(f"[HANDSHAKE] Quorum failed: {handshake['handshake_id']}")
        logger.error(f"  Missing acks: {missing_acks}")
        
        # Log failure
        if self._immutable_log:
            try:
                await self._immutable_log.append(
                    actor="component_handshake",
                    action="handshake_quorum_failed",
                    resource=handshake["component_id"],
                    subsystem="component_handshake",
                    payload={
                        "handshake_id": handshake["handshake_id"],
                        "received_acks": list(handshake["acknowledgments"]),
                        "missing_acks": list(missing_acks)
                    },
                    result="failed"
                )
            except Exception as e:
                logger.debug(f"Could not log failure: {e}")
    
    async def _start_validation_window(self, handshake: Dict[str, Any]):
        """Start validation window for newly integrated component"""
        
        try:
            from backend.logic_update_awareness import logic_update_awareness
            
            # Create observation window
            summary = {
                "update_id": handshake["handshake_id"],
                "update_type": "component_onboarding",
                "components_touched": [handshake["component_id"]],
                "risk_level": "medium",
                "observation_window_duration": 3600,  # 1 hour
                "stability_criteria": {
                    "max_error_rate": 0.01,
                    "min_uptime": 0.95
                }
            }
            
            await logic_update_awareness.start_observation_window(
                update_id=handshake["handshake_id"],
                summary=summary
            )
            
            logger.info(f"[HANDSHAKE] Validation window started: {handshake['handshake_id']}")
            
        except Exception as e:
            logger.warning(f"Could not start validation window: {e}")
    
    def get_handshake_status(self, handshake_id: str) -> Optional[Dict[str, Any]]:
        """Get status of handshake"""
        handshake = self.active_handshakes.get(handshake_id)
        
        if not handshake:
            return None
        
        return {
            "handshake_id": handshake_id,
            "component_id": handshake["component_id"],
            "status": handshake["status"],
            "acks_received": len(handshake["acknowledgments"]),
            "acks_required": len(self.required_acks),
            "quorum_met": handshake["quorum_met"],
            "subsystem_adjustments": handshake.get("subsystem_adjustments", {})
        }
    
    def get_component_info(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get registered component info"""
        return self.component_registry.get(component_id)


# Global instance
component_handshake = ComponentHandshake()
