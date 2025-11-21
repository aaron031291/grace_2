"""
Immutable Log Entry - Cryptographically signed audit trail entry
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ImmutableLogEntry:
    """
    Single immutable audit log entry with cryptographic hash chain

    Each entry contains:
    - prev_hash: Hash of the previous entry (creates chain)
    - hash: Hash of this entry's content
    - timestamp: When the event occurred
    - event_type: Type of event (governance, action, etc.)
    - actor: Component or user that performed the action
    - resource: What was affected
    - payload: Event-specific data
    - trust_score: Trust level at time of event
    - governance_tier: Governance level required
    """

    entry_id: str
    prev_hash: str
    hash: str
    timestamp: datetime
    event_type: str
    actor: str
    resource: str
    payload: Dict[str, Any]
    trust_score: Optional[float] = None
    governance_tier: Optional[str] = None
    sequence_number: Optional[int] = None

    @classmethod
    def create(
        cls,
        prev_hash: str,
        event_type: str,
        actor: str,
        resource: str,
        payload: Dict[str, Any],
        trust_score: Optional[float] = None,
        governance_tier: Optional[str] = None,
        sequence_number: Optional[int] = None
    ) -> 'ImmutableLogEntry':
        """
        Create a new immutable log entry with computed hash
        """
        timestamp = datetime.now(timezone.utc)
        entry_id = f"audit_{int(timestamp.timestamp() * 1000000)}_{hash(event_type + actor) % 10000}"

        # Create hash content (everything except the hash field itself)
        hash_content = {
            'entry_id': entry_id,
            'prev_hash': prev_hash,
            'timestamp': timestamp.isoformat(),
            'event_type': event_type,
            'actor': actor,
            'resource': resource,
            'payload': payload,
            'trust_score': trust_score,
            'governance_tier': governance_tier,
            'sequence_number': sequence_number
        }

        # Compute hash
        content_str = json.dumps(hash_content, sort_keys=True, default=str)
        hash_value = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        return cls(
            entry_id=entry_id,
            prev_hash=prev_hash,
            hash=hash_value,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            resource=resource,
            payload=payload,
            trust_score=trust_score,
            governance_tier=governance_tier,
            sequence_number=sequence_number
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime to ISO string
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImmutableLogEntry':
        """Create from dictionary"""
        # Convert ISO string back to datetime
        data_copy = data.copy()
        data_copy['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data_copy)

    def verify_hash(self) -> bool:
        """
        Verify that the hash matches the content
        """
        # Create hash content without the hash field
        hash_content = {
            'entry_id': self.entry_id,
            'prev_hash': self.prev_hash,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'actor': self.actor,
            'resource': self.resource,
            'payload': self.payload,
            'trust_score': self.trust_score,
            'governance_tier': self.governance_tier,
            'sequence_number': self.sequence_number
        }

        content_str = json.dumps(hash_content, sort_keys=True, default=str)
        computed_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        return computed_hash == self.hash

    def __str__(self) -> str:
        return f"ImmutableLogEntry(id={self.entry_id}, type={self.event_type}, actor={self.actor}, hash={self.hash[:8]}...)"