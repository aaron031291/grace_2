import hashlib
import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, select
from sqlalchemy.sql import func
from .models import Base, async_session

class ImmutableLogEntry(Base):
    """Tamper-proof append-only audit log"""
    __tablename__ = "immutable_log"
    id = Column(Integer, primary_key=True)
    sequence = Column(Integer, unique=True, nullable=False)
    actor = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    resource = Column(String(256))
    subsystem = Column(String(64))
    payload = Column(Text)
    result = Column(String(64))
    entry_hash = Column(String(64), nullable=False, unique=True)
    previous_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    @staticmethod
    def compute_hash(sequence: int, actor: str, action: str, resource: str, payload: str, result: str, previous_hash: str) -> str:
        """Cryptographic hash for tamper detection"""
        data = f"{sequence}:{actor}:{action}:{resource}:{payload}:{result}:{previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class ImmutableLog:
    """Append-only log with cryptographic chain"""
    
    async def append(
        self,
        actor: str,
        action: str,
        resource: str,
        subsystem: str,
        payload: dict,
        result: str
    ) -> int:
        """Append entry to immutable log"""
        
        async with async_session() as session:
            last_result = await session.execute(
                select(ImmutableLogEntry)
                .order_by(ImmutableLogEntry.sequence.desc())
                .limit(1)
            )
            last_entry = last_result.scalar_one_or_none()
            
            sequence = (last_entry.sequence + 1) if last_entry else 1
            previous_hash = last_entry.entry_hash if last_entry else "0" * 64
            
            payload_str = json.dumps(payload, sort_keys=True)
            
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
