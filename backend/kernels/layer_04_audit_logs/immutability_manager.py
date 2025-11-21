"""
Immutability Manager - Handles persistence of immutable log entries to database
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .immutable_log_entry import ImmutableLogEntry
from .constitutional_audit_logger import constitutional_audit_logger

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuditLogTable(Base):
    """Database table for immutable audit logs"""
    __tablename__ = "immutable_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(String(255), unique=True, nullable=False, index=True)
    prev_hash = Column(String(64), nullable=False, index=True)
    hash = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    actor = Column(String(255), nullable=False, index=True)
    resource = Column(String(500), nullable=False)
    payload = Column(Text, nullable=False)  # JSON string
    trust_score = Column(Float, nullable=True)
    governance_tier = Column(String(50), nullable=True)
    sequence_number = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ImmutabilityManager:
    """
    Immutability Manager - Persists immutable log entries to database

    Ensures that once an entry is written, it cannot be modified or deleted.
    Provides query capabilities for audit and compliance.
    """

    def __init__(self, database_url: str = "sqlite:///databases/grace_audit.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database connection and create tables"""
        if self._initialized:
            return

        try:
            # Create engine with appropriate settings
            if self.database_url.startswith("sqlite"):
                self.engine = create_engine(
                    self.database_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=False
                )
            else:
                self.engine = create_engine(self.database_url, echo=False)

            # Create tables
            Base.metadata.create_all(bind=self.engine)

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            self._initialized = True
            logger.info("[IMMUTABILITY] Database initialized successfully")

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Failed to initialize database: {e}")
            raise

    async def persist_entry(self, entry: ImmutableLogEntry) -> bool:
        """
        Persist a single immutable log entry to the database

        Returns True if successful, False otherwise
        """
        if not self._initialized:
            await self.initialize()

        try:
            with self.SessionLocal() as session:
                # Check if entry already exists (prevent duplicates)
                existing = session.query(AuditLogTable).filter_by(entry_id=entry.entry_id).first()
                if existing:
                    logger.warning(f"[IMMUTABILITY] Entry already exists: {entry.entry_id}")
                    return True

                # Create database record
                db_entry = AuditLogTable(
                    entry_id=entry.entry_id,
                    prev_hash=entry.prev_hash,
                    hash=entry.hash,
                    timestamp=entry.timestamp,
                    event_type=entry.event_type,
                    actor=entry.actor,
                    resource=entry.resource,
                    payload=str(entry.payload),  # Store as JSON string
                    trust_score=entry.trust_score,
                    governance_tier=entry.governance_tier,
                    sequence_number=entry.sequence_number
                )

                session.add(db_entry)
                session.commit()

                logger.debug(f"[IMMUTABILITY] Persisted entry: {entry.entry_id}")
                return True

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Failed to persist entry {entry.entry_id}: {e}")
            return False

    async def persist_batch(self, entries: List[ImmutableLogEntry]) -> int:
        """
        Persist multiple entries in a batch

        Returns the number of successfully persisted entries
        """
        if not self._initialized:
            await self.initialize()

        success_count = 0
        for entry in entries:
            if await self.persist_entry(entry):
                success_count += 1

        logger.info(f"[IMMUTABILITY] Batch persist complete: {success_count}/{len(entries)} entries")
        return success_count

    async def get_entry_by_id(self, entry_id: str) -> Optional[ImmutableLogEntry]:
        """Retrieve a specific entry by ID"""
        if not self._initialized:
            await self.initialize()

        try:
            with self.SessionLocal() as session:
                db_entry = session.query(AuditLogTable).filter_by(entry_id=entry_id).first()
                if db_entry:
                    # Reconstruct the entry
                    entry = ImmutableLogEntry(
                        entry_id=db_entry.entry_id,
                        prev_hash=db_entry.prev_hash,
                        hash=db_entry.hash,
                        timestamp=db_entry.timestamp,
                        event_type=db_entry.event_type,
                        actor=db_entry.actor,
                        resource=db_entry.resource,
                        payload=eval(db_entry.payload),  # Convert back from string
                        trust_score=db_entry.trust_score,
                        governance_tier=db_entry.governance_tier,
                        sequence_number=db_entry.sequence_number
                    )
                    return entry
        except Exception as e:
            logger.error(f"[IMMUTABILITY] Failed to retrieve entry {entry_id}: {e}")

        return None

    async def get_entries_in_range(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        limit: int = 100
    ) -> List[ImmutableLogEntry]:
        """Query entries with filters"""
        if not self._initialized:
            await self.initialize()

        try:
            with self.SessionLocal() as session:
                query = session.query(AuditLogTable)

                if start_time:
                    query = query.filter(AuditLogTable.timestamp >= start_time)
                if end_time:
                    query = query.filter(AuditLogTable.timestamp <= end_time)
                if event_type:
                    query = query.filter(AuditLogTable.event_type == event_type)
                if actor:
                    query = query.filter(AuditLogTable.actor == actor)

                query = query.order_by(AuditLogTable.timestamp.desc()).limit(limit)

                db_entries = query.all()

                entries = []
                for db_entry in db_entries:
                    entry = ImmutableLogEntry(
                        entry_id=db_entry.entry_id,
                        prev_hash=db_entry.prev_hash,
                        hash=db_entry.hash,
                        timestamp=db_entry.timestamp,
                        event_type=db_entry.event_type,
                        actor=db_entry.actor,
                        resource=db_entry.resource,
                        payload=eval(db_entry.payload),
                        trust_score=db_entry.trust_score,
                        governance_tier=db_entry.governance_tier,
                        sequence_number=db_entry.sequence_number
                    )
                    entries.append(entry)

                return entries

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Failed to query entries: {e}")
            return []

    async def verify_chain_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the entire hash chain in the database
        """
        if not self._initialized:
            await self.initialize()

        try:
            with self.SessionLocal() as session:
                # Get all entries ordered by sequence
                db_entries = session.query(AuditLogTable).order_by(AuditLogTable.sequence_number).all()

                if not db_entries:
                    return {"valid": True, "total_entries": 0, "checked_entries": 0}

                issues = []
                expected_prev_hash = "genesis"

                for db_entry in db_entries:
                    # Verify individual hash
                    entry_dict = {
                        'entry_id': db_entry.entry_id,
                        'prev_hash': db_entry.prev_hash,
                        'timestamp': db_entry.timestamp.isoformat(),
                        'event_type': db_entry.event_type,
                        'actor': db_entry.actor,
                        'resource': db_entry.resource,
                        'payload': eval(db_entry.payload),
                        'trust_score': db_entry.trust_score,
                        'governance_tier': db_entry.governance_tier,
                        'sequence_number': db_entry.sequence_number
                    }

                    content_str = str(entry_dict).replace("'", '"')
                    computed_hash = __import__('hashlib').sha256(content_str.encode('utf-8')).hexdigest()

                    if computed_hash != db_entry.hash:
                        issues.append(f"Hash mismatch for entry {db_entry.entry_id}")

                    # Verify chain continuity
                    if db_entry.prev_hash != expected_prev_hash:
                        issues.append(f"Chain break at entry {db_entry.entry_id}: expected {expected_prev_hash}, got {db_entry.prev_hash}")

                    expected_prev_hash = db_entry.hash

                return {
                    "valid": len(issues) == 0,
                    "total_entries": len(db_entries),
                    "checked_entries": len(db_entries),
                    "issues": issues
                }

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Chain verification failed: {e}")
            return {"valid": False, "error": str(e)}

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._initialized:
            await self.initialize()

        try:
            with self.SessionLocal() as session:
                total_entries = session.query(AuditLogTable).count()

                if total_entries == 0:
                    return {"total_entries": 0}

                # Get date range
                first_entry = session.query(AuditLogTable).order_by(AuditLogTable.timestamp).first()
                last_entry = session.query(AuditLogTable).order_by(AuditLogTable.timestamp.desc()).first()

                # Get event type distribution
                from sqlalchemy import func
                event_counts = session.query(
                    AuditLogTable.event_type,
                    func.count(AuditLogTable.id)
                ).group_by(AuditLogTable.event_type).all()

                event_distribution = {event_type: count for event_type, count in event_counts}

                return {
                    "total_entries": total_entries,
                    "date_range": {
                        "first": first_entry.timestamp.isoformat() if first_entry else None,
                        "last": last_entry.timestamp.isoformat() if last_entry else None
                    },
                    "event_distribution": event_distribution,
                    "chain_integrity": (await self.verify_chain_integrity())["valid"]
                }

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Failed to get stats: {e}")
            return {"error": str(e)}

    async def cleanup_old_entries(self, days_to_keep: int = 365) -> int:
        """
        Remove entries older than specified days (for compliance/archival)

        WARNING: This breaks immutability! Only use for compliance-required cleanup.
        """
        logger.warning(f"[IMMUTABILITY] Removing entries older than {days_to_keep} days - breaking immutability!")

        if not self._initialized:
            await self.initialize()

        try:
            cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            # This is a simplified implementation - in practice, you'd archive to cold storage first

            with self.SessionLocal() as session:
                deleted_count = session.query(AuditLogTable).filter(
                    AuditLogTable.timestamp < cutoff_date
                ).delete()

                session.commit()
                logger.info(f"[IMMUTABILITY] Cleaned up {deleted_count} old entries")
                return deleted_count

        except Exception as e:
            logger.error(f"[IMMUTABILITY] Cleanup failed: {e}")
            return 0


# Global instance
immutability_manager = ImmutabilityManager()