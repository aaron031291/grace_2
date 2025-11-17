"""
Event-to-DB Persistence Layer

Whenever InputSentinel publishes agentic.action_* events, persist a corresponding 
record to keep Trigger Mesh, immutable log, and relational tables in sync.

Every emitted event gets a retrievable audit row.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.asyncio import AsyncSession

from .base_models import Base
from .models import async_session
from .trigger_mesh import TriggerEvent
from .immutable_log import immutable_log


class ActionEvent(Base):
    """
    Persistent record of all agentic.action_* events.
    
    Maps to:
    - agentic.action_planned
    - agentic.action_executing
    - agentic.action_completed
    - agentic.problem_resolved
    - agentic.action_failed
    """
    __tablename__ = "action_events"
    
    id = Column(Integer, primary_key=True)
    
    # Event metadata
    event_type = Column(String, nullable=False, index=True)  # action_planned, action_executing, etc.
    event_id = Column(String, unique=True, nullable=False, index=True)
    triggered_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Action context
    action_id = Column(String, nullable=True, index=True)
    error_id = Column(String, nullable=True, index=True)
    contract_id = Column(Integer, nullable=True, index=True)  # FK to action_contracts
    mission_id = Column(String, nullable=True, index=True)
    approval_id = Column(String, nullable=True, index=True)
    
    # Approval/governance
    approval_status = Column(String, nullable=True)  # pending, approved, rejected, auto_approved
    approval_tier = Column(String, nullable=True)  # tier_1, tier_2, tier_3
    can_auto_execute = Column(Boolean, nullable=True)
    
    # Result tracking
    success = Column(Boolean, nullable=True)
    result_summary = Column(String, nullable=True)
    
    # Full event payload
    payload = Column(JSON, nullable=False)
    
    # Correlation
    triggered_by = Column(String, nullable=True)
    parent_event_id = Column(String, nullable=True, index=True)
    
    # Immutable log reference
    immutable_log_id = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index("ix_action_events_action_mission", "action_id", "mission_id"),
        Index("ix_action_events_error_action", "error_id", "action_id"),
        Index("ix_action_events_triggered_at", "triggered_at"),
    )


class EventPersistence:
    """
    Persists agentic.action_* events to database for audit and retrieval.
    """
    
    async def persist_action_event(
        self,
        event: TriggerEvent,
        contract_id: Optional[int] = None,
        mission_id: Optional[str] = None,
        parent_event_id: Optional[str] = None
    ) -> ActionEvent:
        """
        Persist an agentic.action_* event to the database.
        
        Args:
            event: The TriggerEvent from TriggerMesh
            contract_id: Associated action contract ID (if exists)
            mission_id: Associated mission ID (if exists)
            parent_event_id: Parent event ID for correlation
            
        Returns:
            Persisted ActionEvent record
        """
        
        # Extract fields from event payload
        payload = event.payload
        action_id = payload.get("action_id")
        error_id = payload.get("error_id")
        approval_id = payload.get("approval_id")
        approval_status = payload.get("approval_status")
        approval_tier = payload.get("tier")
        can_auto_execute = payload.get("can_auto_execute")
        success = payload.get("success")
        triggered_by = payload.get("triggered_by")
        
        # Create result summary
        result_summary = None
        if success is not None:
            if success:
                result_summary = "Action completed successfully"
            else:
                error_msg = payload.get("error", "Unknown error")
                result_summary = f"Action failed: {error_msg}"
        
        # Create database record
        async with async_session() as session:
            async with session.begin():
                action_event = ActionEvent(
                    event_type=event.event_type,
                    event_id=event.event_id,
                    triggered_at=event.timestamp,  # Use timestamp instead of triggered_at
                    action_id=action_id,
                    error_id=error_id,
                    contract_id=contract_id,
                    mission_id=mission_id,
                    approval_id=approval_id,
                    approval_status=approval_status,
                    approval_tier=approval_tier,
                    can_auto_execute=can_auto_execute,
                    success=success,
                    result_summary=result_summary,
                    payload=payload,
                    triggered_by=triggered_by,
                    parent_event_id=parent_event_id
                )
                
                session.add(action_event)
                await session.flush()
        
        # Log to immutable log AFTER committing the action_event (avoids nested session deadlock)
        log_entry_id = await immutable_log.append(
            actor=triggered_by or "input_sentinel",
            action=event.event_type,
            resource=f"action:{action_id}" if action_id else "action",
            subsystem="agentic_events",
            payload=payload,
            result="persisted"
        )
        
        # Update with immutable log ID
        async with async_session() as session:
            async with session.begin():
                action_event.immutable_log_id = log_entry_id
                session.add(action_event)
        
        return action_event
    
    async def get_action_timeline(
        self,
        action_id: str,
        session: AsyncSession
    ) -> list[ActionEvent]:
        """
        Get full timeline of events for a specific action.
        
        Args:
            action_id: The action ID to retrieve
            session: Database session
            
        Returns:
            List of ActionEvent records in chronological order
        """
        from sqlalchemy import select
        
        query = select(ActionEvent).where(
            ActionEvent.action_id == action_id
        ).order_by(ActionEvent.triggered_at)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_mission_events(
        self,
        mission_id: str,
        session: AsyncSession
    ) -> list[ActionEvent]:
        """
        Get all events for a specific mission.
        
        Args:
            mission_id: The mission ID
            session: Database session
            
        Returns:
            List of ActionEvent records for the mission
        """
        from sqlalchemy import select
        
        query = select(ActionEvent).where(
            ActionEvent.mission_id == mission_id
        ).order_by(ActionEvent.triggered_at)
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_events_by_contract(
        self,
        contract_id: int,
        session: AsyncSession
    ) -> list[ActionEvent]:
        """
        Get all events associated with a contract.
        
        Args:
            contract_id: The contract ID
            session: Database session
            
        Returns:
            List of ActionEvent records
        """
        from sqlalchemy import select
        
        query = select(ActionEvent).where(
            ActionEvent.contract_id == contract_id
        ).order_by(ActionEvent.triggered_at)
        
        result = await session.execute(query)
        return list(result.scalars().all())


# Global singleton
event_persistence = EventPersistence()
