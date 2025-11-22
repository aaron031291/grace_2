"""
Constitutional Audit Logger - Manages the audit trail for constitutional compliance
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .immutable_log_entry import ImmutableLogEntry

logger = logging.getLogger(__name__)


class ConstitutionalAuditLogger:
    """
    Constitutional Audit Logger - Ensures all governance decisions are logged

    This logger maintains the hash chain and ensures that every decision
    affecting Grace's behavior is recorded immutably.
    """

    def __init__(self):
        self.entries: List[ImmutableLogEntry] = []
        self.last_hash = "genesis"  # Starting hash for the chain
        self.sequence_counter = 0

    async def log_governance_decision(
        self,
        decision_type: str,
        actor: str,
        resource: str,
        decision: Dict[str, Any],
        trust_score: Optional[float] = None,
        governance_tier: str = "standard"
    ) -> ImmutableLogEntry:
        """
        Log a governance decision with full audit trail
        """
        self.sequence_counter += 1

        entry = ImmutableLogEntry.create(
            prev_hash=self.last_hash,
            event_type=f"governance.{decision_type}",
            actor=actor,
            resource=resource,
            payload={
                "decision": decision,
                "constitutional_check": True,
                "audit_required": True
            },
            trust_score=trust_score,
            governance_tier=governance_tier,
            sequence_number=self.sequence_counter
        )

        # Update chain
        self.last_hash = entry.hash
        self.entries.append(entry)

        logger.info(f"[AUDIT] Logged governance decision: {entry.entry_id} (seq: {self.sequence_counter})")

        return entry

    async def log_external_action(
        self,
        action_type: str,
        actor: str,
        resource: str,
        action_details: Dict[str, Any],
        trust_score: Optional[float] = None
    ) -> ImmutableLogEntry:
        """
        Log an external action (API calls, file operations, etc.)
        """
        self.sequence_counter += 1

        entry = ImmutableLogEntry.create(
            prev_hash=self.last_hash,
            event_type=f"external.{action_type}",
            actor=actor,
            resource=resource,
            payload={
                "action_details": action_details,
                "external_interaction": True,
                "audit_required": True
            },
            trust_score=trust_score,
            governance_tier="external",
            sequence_number=self.sequence_counter
        )

        # Update chain
        self.last_hash = entry.hash
        self.entries.append(entry)

        logger.info(f"[AUDIT] Logged external action: {entry.entry_id} (seq: {self.sequence_counter})")

        return entry

    async def log_system_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        event_data: Dict[str, Any],
        severity: str = "info"
    ) -> ImmutableLogEntry:
        """
        Log a system event (boot, health checks, etc.)
        """
        self.sequence_counter += 1

        entry = ImmutableLogEntry.create(
            prev_hash=self.last_hash,
            event_type=f"system.{event_type}",
            actor=actor,
            resource=resource,
            payload={
                "event_data": event_data,
                "severity": severity,
                "system_event": True
            },
            governance_tier="system",
            sequence_number=self.sequence_counter
        )

        # Update chain
        self.last_hash = entry.hash
        self.entries.append(entry)

        logger.debug(f"[AUDIT] Logged system event: {entry.entry_id} (seq: {self.sequence_counter})")

        return entry

    async def log_trust_update(
        self,
        component_id: str,
        old_trust: float,
        new_trust: float,
        reason: str,
        actor: str = "trust_system"
    ) -> ImmutableLogEntry:
        """
        Log trust score updates
        """
        self.sequence_counter += 1

        entry = ImmutableLogEntry.create(
            prev_hash=self.last_hash,
            event_type="trust.update",
            actor=actor,
            resource=component_id,
            payload={
                "old_trust": old_trust,
                "new_trust": new_trust,
                "change": new_trust - old_trust,
                "reason": reason,
                "trust_update": True
            },
            trust_score=new_trust,
            governance_tier="trust",
            sequence_number=self.sequence_counter
        )

        # Update chain
        self.last_hash = entry.hash
        self.entries.append(entry)

        logger.info(f"[AUDIT] Logged trust update for {component_id}: {old_trust} -> {new_trust}")

        return entry

    def get_chain_integrity(self) -> bool:
        """
        Verify the integrity of the entire hash chain
        """
        if not self.entries:
            return True

        # Check each entry's hash
        for entry in self.entries:
            if not entry.verify_hash():
                logger.error(f"[AUDIT] Hash verification failed for entry: {entry.entry_id}")
                return False

        # Check chain continuity
        expected_prev_hash = "genesis"
        for entry in self.entries:
            if entry.prev_hash != expected_prev_hash:
                logger.error(f"[AUDIT] Chain continuity broken at entry: {entry.entry_id}")
                return False
            expected_prev_hash = entry.hash

        return True

    def get_entries_since(self, timestamp: datetime) -> List[ImmutableLogEntry]:
        """
        Get all entries since a given timestamp
        """
        return [entry for entry in self.entries if entry.timestamp >= timestamp]

    def get_entries_by_actor(self, actor: str) -> List[ImmutableLogEntry]:
        """
        Get all entries by a specific actor
        """
        return [entry for entry in self.entries if entry.actor == actor]

    def get_entries_by_type(self, event_type: str) -> List[ImmutableLogEntry]:
        """
        Get all entries of a specific event type
        """
        return [entry for entry in self.entries if entry.event_type == event_type]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get audit statistics
        """
        if not self.entries:
            return {"total_entries": 0, "chain_integrity": True}

        event_types = {}
        actors = {}
        governance_tiers = {}

        for entry in self.entries:
            event_types[entry.event_type] = event_types.get(entry.event_type, 0) + 1
            actors[entry.actor] = actors.get(entry.actor, 0) + 1
            if entry.governance_tier:
                governance_tiers[entry.governance_tier] = governance_tiers.get(entry.governance_tier, 0) + 1

        return {
            "total_entries": len(self.entries),
            "sequence_number": self.sequence_counter,
            "last_hash": self.last_hash,
            "chain_integrity": self.get_chain_integrity(),
            "event_types": event_types,
            "actors": actors,
            "governance_tiers": governance_tiers,
            "time_range": {
                "first": self.entries[0].timestamp.isoformat() if self.entries else None,
                "last": self.entries[-1].timestamp.isoformat() if self.entries else None
            }
        }


# Global instance
constitutional_audit_logger = ConstitutionalAuditLogger()
