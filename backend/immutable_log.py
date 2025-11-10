import hashlib
import json
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .base_models import ImmutableLogEntry, async_session

class ImmutableLog:
    """Append-only log with cryptographic chain"""
    
    async def append(
        self,
        actor: str,
        action: str,
        resource: str,
        subsystem: str,
        payload: dict,
        result: str,
        signature: Optional[str] = None,
        max_retries: int = 5
    ) -> int:
        """
        Append entry to immutable log with optional signature.
        Retries on sequence conflicts (handles concurrent writes).
        
        Args:
            actor: Who performed the action
            action: What action was performed
            resource: What resource was affected
            subsystem: Which subsystem logged this
            payload: Additional data (dict)
            result: Outcome of the action
            signature: Optional cryptographic signature for audit trail
            max_retries: Maximum retry attempts on conflict
        
        Returns:
            Entry ID
        """
        
        for attempt in range(max_retries):
            try:
                async with async_session() as session:
                    last_result = await session.execute(
                        select(ImmutableLogEntry)
                        .order_by(ImmutableLogEntry.sequence.desc())
                        .limit(1)
                    )
                    last_entry = last_result.scalar_one_or_none()
                    
                    sequence = (last_entry.sequence + 1) if last_entry else 1
                    previous_hash = last_entry.entry_hash if last_entry else "0" * 64
                    
                    # Add signature to payload if provided
                    if signature:
                        payload["_signature"] = signature
                    
                    # Convert datetime objects to ISO format strings
                    def convert_datetime(obj):
                        if isinstance(obj, datetime):
                            return obj.isoformat()
                        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
                    
                    payload_str = json.dumps(payload, sort_keys=True, default=convert_datetime)
                    
                    entry_hash = ImmutableLogEntry.compute_hash(
                        sequence, actor, action, resource, payload_str, result, previous_hash
                    )
                    
                    entry = ImmutableLogEntry(
                        sequence=sequence,
                        actor=actor,
                        action=action,
                        resource=resource,
                        subsystem=subsystem,
                        payload=payload_str,
                        result=result,
                        entry_hash=entry_hash,
                        previous_hash=previous_hash
                    )
                    
                    session.add(entry)
                    await session.commit()
                    await session.refresh(entry)
                    
                    return entry.id
            except (IntegrityError, Exception) as e:
                error_msg = str(e)
                if ("UNIQUE constraint failed: immutable_log.sequence" in error_msg or 
                    "database is locked" in error_msg) and attempt < max_retries - 1:
                    # Retry with exponential backoff
                    await asyncio.sleep(0.1 * (2 ** attempt))
                    continue
                # If all retries failed, log but don't crash
                import logging
                logging.error(f"ImmutableLog append failed after {max_retries} retries: {e}")
                return -1  # Return error code instead of raising
    
    async def verify_integrity(self, start_seq: int = 1, end_seq: int = None) -> dict:
        """Verify hash chain integrity"""
        async with async_session() as session:
            query = select(ImmutableLogEntry).order_by(ImmutableLogEntry.sequence)
            if end_seq:
                query = query.where(
                    ImmutableLogEntry.sequence >= start_seq,
                    ImmutableLogEntry.sequence <= end_seq
                )
            else:
                query = query.where(ImmutableLogEntry.sequence >= start_seq)
            
            result = await session.execute(query)
            entries = result.scalars().all()
            
            for i, entry in enumerate(entries):
                expected_hash = ImmutableLogEntry.compute_hash(
                    entry.sequence,
                    entry.actor,
                    entry.action,
                    entry.resource,
                    entry.payload,
                    entry.result,
                    entry.previous_hash
                )
                
                if expected_hash != entry.entry_hash:
                    return {
                        "valid": False,
                        "corrupted_at": entry.sequence,
                        "entry_id": entry.id,
                        "message": "Hash mismatch detected"
                    }
                
                if i > 0 and entry.previous_hash != entries[i-1].entry_hash:
                    return {
                        "valid": False,
                        "broken_chain_at": entry.sequence,
                        "message": "Chain broken - previous hash mismatch"
                    }
            
            return {
                "valid": True,
                "entries_verified": len(entries),
                "sequence_range": f"{entries[0].sequence}-{entries[-1].sequence}" if entries else "empty"
            }
    
    async def replay_cycle(self, cycle_id: str) -> List[dict]:
        """
        Replay all events from a specific healing cycle.
        
        Used for:
        - Audit and compliance
        - Learning from outcomes
        - Debugging failed cycles
        - Training ML models
        
        Returns chronological list of all signed entries for the cycle.
        """
        async with async_session() as session:
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(ImmutableLogEntry.payload.contains(f'"cycle_id": "{cycle_id}"'))
                .order_by(ImmutableLogEntry.sequence.asc())
            )
            entries = result.scalars().all()
            
            replay = []
            for entry in entries:
                payload = json.loads(entry.payload) if entry.payload else {}
                signature = payload.pop("_signature", None)
                
                replay.append({
                    "sequence": entry.sequence,
                    "timestamp": entry.timestamp.isoformat(),
                    "actor": entry.actor,
                    "action": entry.action,
                    "resource": entry.resource,
                    "subsystem": entry.subsystem,
                    "payload": payload,
                    "result": entry.result,
                    "signature": signature,
                    "entry_hash": entry.entry_hash
                })
            
            return replay
    
    async def get_signed_outcomes(
        self,
        subsystem: str = "meta_coordinated_healing",
        hours_back: int = 24,
        limit: int = 100
    ) -> List[dict]:
        """Get signed execution outcomes for learning"""
        async with async_session() as session:
            cutoff = datetime.utcnow() - timedelta(hours=hours_back)
            
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(
                    ImmutableLogEntry.subsystem == subsystem,
                    ImmutableLogEntry.action == "execution_outcome",
                    ImmutableLogEntry.timestamp >= cutoff
                )
                .order_by(ImmutableLogEntry.timestamp.desc())
                .limit(limit)
            )
            entries = result.scalars().all()
            
            outcomes = []
            for entry in entries:
                payload = json.loads(entry.payload) if entry.payload else {}
                signature = payload.pop("_signature", None)
                
                outcomes.append({
                    "timestamp": entry.timestamp.isoformat(),
                    "outcome_id": payload.get("outcome_id"),
                    "cycle_id": payload.get("cycle_id"),
                    "playbook": payload.get("playbook"),
                    "result": entry.result,
                    "verification_passed": payload.get("verification_passed"),
                    "duration_seconds": payload.get("duration_seconds"),
                    "signature": signature,
                    "learned_insights": payload.get("learned_insights", [])
                })
            
            return outcomes
    
    async def get_entries(
        self,
        actor: str = None,
        subsystem: str = None,
        resource: str = None,
        limit: int = 100
    ) -> List[dict]:
        """Query log entries"""
        async with async_session() as session:
            query = select(ImmutableLogEntry).order_by(ImmutableLogEntry.sequence.desc())
            
            if actor:
                query = query.where(ImmutableLogEntry.actor == actor)
            if subsystem:
                query = query.where(ImmutableLogEntry.subsystem == subsystem)
            if resource:
                query = query.where(ImmutableLogEntry.resource == resource)
            
            query = query.limit(limit)
            result = await session.execute(query)
            
            return [
                {
                    "id": e.id,
                    "sequence": e.sequence,
                    "actor": e.actor,
                    "action": e.action,
                    "resource": e.resource,
                    "subsystem": e.subsystem,
                    "result": e.result,
                    "payload": e.payload,
                    "timestamp": e.timestamp,
                    "entry_hash": e.entry_hash
                }
                for e in result.scalars().all()
            ]

immutable_log = ImmutableLog()


# Backwards compatibility alias for legacy imports
# Some modules expect `ImmutableLogger`; alias it to the existing `ImmutableLog` implementation.
ImmutableLogger = ImmutableLog


# Compatibility shim for legacy imports expecting `append_to_log`
# Some components import: from backend.immutable_log import append_to_log
# This async function forwards to the global immutable_log instance.
async def append_to_log(
    actor: str,
    action: str,
    resource: str,
    subsystem: str,
    payload: dict,
    result: str,
) -> int:
    return await immutable_log.append(
        actor=actor,
        action=action,
        resource=resource,
        subsystem=subsystem,
        payload=payload,
        result=result,
    )
