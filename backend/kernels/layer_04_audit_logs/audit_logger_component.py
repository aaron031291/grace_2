"""
Audit Logger Component - Event bus integration for immutable logging
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .constitutional_audit_logger import constitutional_audit_logger
from .immutability_manager import immutability_manager

logger = logging.getLogger(__name__)


class AuditLoggerComponent:
    """
    Audit Logger Component - Grace kernel that subscribes to auditable events

    This component integrates with the event bus to automatically log
    all events flagged as auditable, ensuring complete audit trails.
    """

    def __init__(self):
        self.component_id = "audit_logger_kernel"
        self.running = False
        self.event_bus = None
        self.subscriptions = []

    async def initialize(self) -> None:
        """Initialize the audit logger component"""
        logger.info("[AUDIT-KERNEL] Initializing Immutable Logs Kernel")

        # Initialize the immutability manager (database)
        await immutability_manager.initialize()

        # Get event bus reference
        try:
            from backend.core.unified_event_publisher import get_unified_publisher
            self.event_bus = get_unified_publisher()
            logger.info("[AUDIT-KERNEL] Connected to unified event publisher")
        except ImportError:
            logger.warning("[AUDIT-KERNEL] Unified event publisher not available")
            return

        # Subscribe to auditable events
        await self._subscribe_to_auditable_events()

        logger.info("[AUDIT-KERNEL] Immutable Logs Kernel initialized")

    async def start(self) -> None:
        """Start the audit logger"""
        if self.running:
            return

        await self.initialize()
        self.running = True

        # Log kernel startup
        await self._log_kernel_event("kernel_started", "Immutable Logs Kernel operational")

        logger.info("[AUDIT-KERNEL] Immutable Logs Kernel started")

    async def stop(self) -> None:
        """Stop the audit logger"""
        if not self.running:
            return

        # Log kernel shutdown
        await self._log_kernel_event("kernel_stopped", "Immutable Logs Kernel shutting down")

        # Unsubscribe from events
        if self.event_bus:
            for subscription in self.subscriptions:
                try:
                    await self.event_bus.unsubscribe(subscription)
                except Exception as e:
                    logger.warning(f"[AUDIT-KERNEL] Failed to unsubscribe: {e}")

        self.running = False
        logger.info("[AUDIT-KERNEL] Immutable Logs Kernel stopped")

    async def _subscribe_to_auditable_events(self) -> None:
        """Subscribe to all events that require auditing"""
        if not self.event_bus:
            return

        # Define auditable event patterns
        auditable_patterns = [
            "governance.*",      # All governance decisions
            "external.*",        # External actions (API calls, etc.)
            "trust.*",          # Trust score changes
            "security.*",       # Security events
            "kernel.*",         # Kernel lifecycle events
            "business.*",       # Business operations
            "constitution.*",   # Constitutional checks
            "verification.*",   # Verification results
            "learning.*",       # Learning events
            "consciousness.*",  # Consciousness updates
            "immune.*",         # Immune system actions
            "mtl.*"            # MTL kernel events
        ]

        for pattern in auditable_patterns:
            try:
                subscription = await self.event_bus.subscribe(pattern, self._handle_auditable_event)
                self.subscriptions.append(subscription)
                logger.debug(f"[AUDIT-KERNEL] Subscribed to: {pattern}")
            except Exception as e:
                logger.warning(f"[AUDIT-KERNEL] Failed to subscribe to {pattern}: {e}")

        logger.info(f"[AUDIT-KERNEL] Subscribed to {len(self.subscriptions)} audit patterns")

    async def _handle_auditable_event(self, event) -> None:
        """
        Handle an auditable event by logging it immutably
        """
        try:
            # Extract event data
            event_type = getattr(event, 'event_type', getattr(event, 'type', 'unknown'))
            actor = getattr(event, 'actor', getattr(event, 'source', 'unknown'))
            resource = getattr(event, 'resource', getattr(event, 'target', 'unknown'))
            payload = getattr(event, 'payload', getattr(event, 'data', {}))
            trust_score = getattr(event, 'trust_score', None)

            # Determine governance tier based on event type
            governance_tier = self._determine_governance_tier(event_type)

            # Log the event
            if event_type.startswith("governance."):
                audit_entry = await constitutional_audit_logger.log_governance_decision(
                    decision_type=event_type.split(".", 1)[1],
                    actor=actor,
                    resource=resource,
                    decision=payload,
                    trust_score=trust_score,
                    governance_tier=governance_tier
                )
            elif event_type.startswith("external."):
                audit_entry = await constitutional_audit_logger.log_external_action(
                    action_type=event_type.split(".", 1)[1],
                    actor=actor,
                    resource=resource,
                    action_details=payload,
                    trust_score=trust_score
                )
            elif event_type.startswith("trust."):
                # Special handling for trust updates
                if "old_trust" in payload and "new_trust" in payload:
                    audit_entry = await constitutional_audit_logger.log_trust_update(
                        component_id=resource,
                        old_trust=payload["old_trust"],
                        new_trust=payload["new_trust"],
                        reason=payload.get("reason", "unspecified"),
                        actor=actor
                    )
                else:
                    audit_entry = await constitutional_audit_logger.log_system_event(
                        event_type=event_type,
                        actor=actor,
                        resource=resource,
                        event_data=payload
                    )
            else:
                # Generic system event
                audit_entry = await constitutional_audit_logger.log_system_event(
                    event_type=event_type,
                    actor=actor,
                    resource=resource,
                    event_data=payload
                )

            # Persist to database
            success = await immutability_manager.persist_entry(audit_entry)
            if not success:
                logger.error(f"[AUDIT-KERNEL] Failed to persist audit entry: {audit_entry.entry_id}")

            # Emit audit confirmation event
            await self._emit_audit_logged_event(audit_entry)

        except Exception as e:
            logger.error(f"[AUDIT-KERNEL] Failed to handle auditable event: {e}", exc_info=True)

    def _determine_governance_tier(self, event_type: str) -> str:
        """Determine the governance tier required for an event type"""
        # High-risk events require elevated governance
        high_risk_patterns = [
            "governance.critical",
            "external.api_call",
            "external.file_operation",
            "security.violation",
            "business.launch",
            "constitution.override"
        ]

        for pattern in high_risk_patterns:
            if pattern in event_type:
                return "critical"

        # Medium-risk events
        medium_risk_patterns = [
            "governance.standard",
            "trust.update",
            "learning.new_pattern",
            "verification.failed"
        ]

        for pattern in medium_risk_patterns:
            if pattern in event_type:
                return "standard"

        return "low"

    async def _log_kernel_event(self, event_type: str, message: str) -> None:
        """Log a kernel lifecycle event"""
        try:
            audit_entry = await constitutional_audit_logger.log_system_event(
                event_type=f"kernel.{event_type}",
                actor=self.component_id,
                resource="audit_logs",
                event_data={"message": message, "kernel_version": "1.0"}
            )

            # Persist to database
            await immutability_manager.persist_entry(audit_entry)

        except Exception as e:
            logger.error(f"[AUDIT-KERNEL] Failed to log kernel event: {e}")

    async def _emit_audit_logged_event(self, audit_entry) -> None:
        """Emit an event confirming the audit was logged"""
        try:
            if self.event_bus:
                await self.event_bus.publish_event(
                    event_type="audit.logged",
                    payload={
                        "audit_entry_id": audit_entry.entry_id,
                        "original_event_type": audit_entry.event_type,
                        "sequence_number": audit_entry.sequence_number,
                        "hash": audit_entry.hash
                    },
                    source=self.component_id
                )
        except Exception as e:
            logger.debug(f"[AUDIT-KERNEL] Failed to emit audit logged event: {e}")

    async def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit statistics"""
        try:
            # Get logger stats
            logger_stats = constitutional_audit_logger.get_stats()

            # Get database stats
            db_stats = await immutability_manager.get_stats()

            return {
                "kernel_id": self.component_id,
                "running": self.running,
                "subscriptions": len(self.subscriptions),
                "logger_stats": logger_stats,
                "database_stats": db_stats
            }

        except Exception as e:
            logger.error(f"[AUDIT-KERNEL] Failed to get stats: {e}")
            return {"error": str(e)}

    async def query_audit_log(
        self,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        start_time: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Query the audit log with filters"""
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_time) if start_time else None

            entries = await immutability_manager.get_entries_in_range(
                event_type=event_type,
                actor=actor,
                start_time=start_dt,
                limit=limit
            )

            return {
                "entries": [entry.to_dict() for entry in entries],
                "count": len(entries),
                "filters": {
                    "event_type": event_type,
                    "actor": actor,
                    "start_time": start_time,
                    "limit": limit
                }
            }

        except Exception as e:
            logger.error(f"[AUDIT-KERNEL] Failed to query audit log: {e}")
            return {"error": str(e)}


# Global instance
audit_logger_component = AuditLoggerComponent()
