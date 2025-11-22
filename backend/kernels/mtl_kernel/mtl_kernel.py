"""
MTL Kernel - Unified Memory, Trust, Logs, and Logic
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MTLKernel:
    """
    MTL Kernel - Single source of truth for Grace's intelligence

    Unifies Memory, Trust, Logs, and Unified Logic into a coherent
    decision-making and learning system.
    """

    def __init__(self):
        self.component_id = "mtl_kernel"
        self.running = False

        # Component references (lazy loaded)
        self.memory_adapter = None
        self.trust_ledger = None
        self.audit_logger = None
        self.unified_logic = None

        # Event bus
        self.event_bus = None

        # Kernel state
        self.kernel_state = {
            "memory_integrity": True,
            "trust_consensus": 0.8,
            "log_chain_valid": True,
            "logic_coherence": 0.9,
            "last_synthesis": None
        }

    async def initialize(self) -> None:
        """Initialize the MTL kernel and all sub-components"""
        logger.info("[MTL] Initializing MTL Kernel (Memory + Trust + Logs + Logic)")

        # Initialize memory adapter
        try:
            from .memory_adapter import MemoryAdapter
            self.memory_adapter = MemoryAdapter()
            await self.memory_adapter.initialize()
            logger.info("[MTL] Memory adapter initialized")
        except Exception as e:
            logger.warning(f"[MTL] Memory adapter initialization failed: {e}")

        # Initialize trust ledger
        try:
            from .trust_ledger import TrustLedger
            self.trust_ledger = TrustLedger()
            await self.trust_ledger.initialize()
            logger.info("[MTL] Trust ledger initialized")
        except Exception as e:
            logger.warning(f"[MTL] Trust ledger initialization failed: {e}")

        # Initialize audit logger
        try:
            from ..layer_04_audit_logs.audit_logger_component import audit_logger_component
            self.audit_logger = audit_logger_component
            await self.audit_logger.initialize()
            logger.info("[MTL] Audit logger initialized")
        except Exception as e:
            logger.warning(f"[MTL] Audit logger initialization failed: {e}")

        # Initialize unified logic
        try:
            from .unified_logic import UnifiedLogic
            self.unified_logic = UnifiedLogic(self)
            await self.unified_logic.initialize()
            logger.info("[MTL] Unified logic initialized")
        except Exception as e:
            logger.warning(f"[MTL] Unified logic initialization failed: {e}")

        # Connect to event bus
        try:
            from backend.core.unified_event_publisher import get_unified_publisher
            self.event_bus = get_unified_publisher()
            logger.info("[MTL] Connected to unified event publisher")
        except Exception as e:
            logger.warning(f"[MTL] Event bus connection failed: {e}")

        logger.info("[MTL] MTL Kernel initialization complete")

    async def start(self) -> None:
        """Start the MTL kernel"""
        if self.running:
            return

        await self.initialize()

        # Start sub-components
        if self.memory_adapter:
            await self.memory_adapter.start()
        if self.trust_ledger:
            await self.trust_ledger.start()
        if self.audit_logger:
            await self.audit_logger.start()
        if self.unified_logic:
            await self.unified_logic.start()

        # Subscribe to events
        await self._subscribe_to_events()

        self.running = True
        logger.info("[MTL] MTL Kernel started")

        # Emit startup event
        await self._emit_mtl_event("mtl.kernel_started", {
            "components": self._get_component_status()
        })

    async def stop(self) -> None:
        """Stop the MTL kernel"""
        if not self.running:
            return

        # Emit shutdown event
        await self._emit_mtl_event("mtl.kernel_stopped", {
            "uptime": "unknown"  # Could track this
        })

        # Stop sub-components
        if self.unified_logic:
            await self.unified_logic.stop()
        if self.audit_logger:
            await self.audit_logger.stop()
        if self.trust_ledger:
            await self.trust_ledger.stop()
        if self.memory_adapter:
            await self.memory_adapter.stop()

        self.running = False
        logger.info("[MTL] MTL Kernel stopped")

    async def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events"""
        if not self.event_bus:
            return

        # Key events that affect MTL state
        subscriptions = [
            "governance.decision_made",
            "learning.experience_recorded",
            "trust.score_updated",
            "memory.consolidated",
            "security.anomaly_detected",
            "health.status_changed"
        ]

        for event_pattern in subscriptions:
            try:
                await self.event_bus.subscribe(event_pattern, self._handle_mtl_event)
                logger.debug(f"[MTL] Subscribed to: {event_pattern}")
            except Exception as e:
                logger.warning(f"[MTL] Failed to subscribe to {event_pattern}: {e}")

    async def _handle_mtl_event(self, event) -> None:
        """Handle events that affect MTL state"""
        try:
            event_type = getattr(event, 'event_type', getattr(event, 'type', 'unknown'))

            # Update kernel state based on event
            if event_type.startswith("governance."):
                await self._update_governance_state(event)
            elif event_type.startswith("learning."):
                await self._update_learning_state(event)
            elif event_type.startswith("trust."):
                await self._update_trust_state(event)
            elif event_type.startswith("memory."):
                await self._update_memory_state(event)
            elif event_type.startswith("security.") or event_type.startswith("health."):
                await self._update_security_state(event)

            # Emit MTL state update
            await self._emit_mtl_event("mtl.state_updated", {
                "trigger_event": event_type,
                "kernel_state": self.kernel_state.copy()
            })

        except Exception as e:
            logger.error(f"[MTL] Failed to handle MTL event: {e}")

    async def _update_governance_state(self, event) -> None:
        """Update kernel state based on governance events"""
        # Governance decisions affect trust consensus
        payload = getattr(event, 'payload', getattr(event, 'data', {}))
        if 'trust_score' in payload:
            self.kernel_state["trust_consensus"] = payload['trust_score']

    async def _update_learning_state(self, event) -> None:
        """Update kernel state based on learning events"""
        # Learning events affect logic coherence
        payload = getattr(event, 'payload', getattr(event, 'data', {}))
        if 'confidence' in payload:
            self.kernel_state["logic_coherence"] = payload['confidence']

    async def _update_trust_state(self, event) -> None:
        """Update kernel state based on trust events"""
        # Trust updates directly affect trust consensus
        payload = getattr(event, 'payload', getattr(event, 'data', {}))
        if 'new_trust' in payload:
            self.kernel_state["trust_consensus"] = payload['new_trust']

    async def _update_memory_state(self, event) -> None:
        """Update kernel state based on memory events"""
        # Memory consolidation affects integrity
        self.kernel_state["memory_integrity"] = True

    async def _update_security_state(self, event) -> None:
        """Update kernel state based on security/health events"""
        # Security events might affect overall trust
        payload = getattr(event, 'payload', getattr(event, 'data', {}))
        severity = payload.get('severity', 'low')
        if severity in ['high', 'critical']:
            # Reduce trust consensus for security issues
            self.kernel_state["trust_consensus"] *= 0.95

    async def _emit_mtl_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Emit an MTL kernel event"""
        try:
            if self.event_bus:
                await self.event_bus.publish_event(
                    event_type=event_type,
                    payload={
                        **payload,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "kernel_id": self.component_id
                    },
                    source=self.component_id
                )
        except Exception as e:
            logger.debug(f"[MTL] Failed to emit MTL event: {e}")

    def _get_component_status(self) -> Dict[str, bool]:
        """Get status of all MTL components"""
        return {
            "memory_adapter": self.memory_adapter is not None,
            "trust_ledger": self.trust_ledger is not None,
            "audit_logger": self.audit_logger is not None,
            "unified_logic": self.unified_logic is not None,
            "event_bus": self.event_bus is not None
        }

    # Public API methods

    async def store_experience(self, experience: Dict[str, Any]) -> bool:
        """Store a learning experience"""
        if not self.memory_adapter:
            return False

        try:
            return await self.memory_adapter.store_experience(experience)
        except Exception as e:
            logger.error(f"[MTL] Failed to store experience: {e}")
            return False

    async def update_trust_score(self, component_id: str, new_score: float, reason: str) -> bool:
        """Update trust score for a component"""
        if not self.trust_ledger:
            return False

        try:
            old_score = await self.trust_ledger.get_trust_score(component_id)
            success = await self.trust_ledger.update_trust_score(component_id, new_score, reason)

            if success and self.audit_logger:
                # Log the trust update
                await self.audit_logger._log_kernel_event(
                    "trust_score_updated",
                    f"Component {component_id}: {old_score} -> {new_score} ({reason})"
                )

            return success
        except Exception as e:
            logger.error(f"[MTL] Failed to update trust score: {e}")
            return False

    async def append_log(self, event_type: str, actor: str, resource: str, payload: Dict[str, Any]) -> bool:
        """Append an entry to the audit log"""
        if not self.audit_logger:
            return False

        try:
            # Use the audit logger to create and persist the entry
            if event_type.startswith("governance."):
                await self.audit_logger._handle_auditable_event(type('Event', (), {
                    'event_type': event_type,
                    'actor': actor,
                    'resource': resource,
                    'payload': payload,
                    'data': payload
                })())
            return True
        except Exception as e:
            logger.error(f"[MTL] Failed to append log: {e}")
            return False

    async def synthesize_decision(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Synthesize a decision using unified logic"""
        if not self.unified_logic:
            return None

        try:
            decision = await self.unified_logic.synthesize_decision(context)
            self.kernel_state["last_synthesis"] = datetime.now(timezone.utc).isoformat()
            return decision
        except Exception as e:
            logger.error(f"[MTL] Failed to synthesize decision: {e}")
            return None

    async def get_mtl_state(self) -> Dict[str, Any]:
        """Get the current MTL kernel state"""
        return {
            "kernel_id": self.component_id,
            "running": self.running,
            "kernel_state": self.kernel_state.copy(),
            "component_status": self._get_component_status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def query_memory(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Query the memory system"""
        if not self.memory_adapter:
            return []

        try:
            return await self.memory_adapter.query_memory(query, context or {})
        except Exception as e:
            logger.error(f"[MTL] Failed to query memory: {e}")
            return []

    async def get_trust_score(self, component_id: str) -> Optional[float]:
        """Get trust score for a component"""
        if not self.trust_ledger:
            return None

        try:
            return await self.trust_ledger.get_trust_score(component_id)
        except Exception as e:
            logger.error(f"[MTL] Failed to get trust score: {e}")
            return None


# Global instance
mtl_kernel = MTLKernel()
