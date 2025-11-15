"""
Progression Tracker & Mission Timeline

Tracks Grace's journey through agentic actions:
- Where she started (safe points)
- Where she is now (current state)
- How far to go (mission progress)
- Confidence in current state

Provides visibility into autonomy progression and rollback capability.
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from sqlalchemy import Column, String, JSON, DateTime, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base

from .models import Base, async_session
from .immutable_log import immutable_log


class MissionTimeline(Base):
    """Tracks progression through a mission or operational phase"""
    __tablename__ = "mission_timelines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mission_id = Column(String, unique=True, nullable=False)
    
    # Mission definition
    mission_name = Column(String, nullable=False)
    mission_goal = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Safe points
    initial_snapshot_id = Column(String, nullable=True)  # Starting point
    current_safe_point_id = Column(String, nullable=True)  # Last validated safe point
    
    # Current state
    current_state_hash = Column(String, nullable=True)
    current_health_score = Column(Integer, nullable=True)
    
    # Progress tracking
    total_planned_actions = Column(Integer, default=0)
    completed_actions = Column(Integer, default=0)
    failed_actions = Column(Integer, default=0)
    rolled_back_actions = Column(Integer, default=0)
    
    progress_ratio = Column(Float, default=0.0)  # 0.0 - 1.0
    confidence_score = Column(Float, default=1.0)  # 0.0 - 1.0
    
    # Status
    status = Column(String, default="in_progress")  # in_progress, completed, failed, paused
    
    # Rollback capability
    can_rollback = Column(Boolean, default=True)
    rollback_available_count = Column(Integer, default=0)
    
    # Metadata
    mission_metadata = Column(JSON, nullable=True)


@dataclass
class ProgressionSnapshot:
    """Point-in-time view of progression status"""
    mission_id: str
    mission_name: str
    started_at: str
    
    # Safe points
    last_safe_point: Optional[str]
    last_safe_point_time: Optional[str]
    
    # Progress
    progress_percent: float
    completed_actions: int
    total_actions: int
    failed_actions: int
    
    # Confidence
    confidence_score: float
    current_health_score: int
    
    # Rollback
    can_rollback: bool
    rollback_points_available: int
    
    # Time estimates
    elapsed_time_seconds: float
    estimated_time_remaining_seconds: Optional[float]


class ProgressionTracker:
    """
    Tracks Grace's progression through missions and operational phases.
    Provides visibility into where she came from and how far to go.
    """
    
    async def start_mission(
        self,
        mission_name: str,
        mission_goal: Optional[str] = None,
        planned_actions: int = 0,
        initial_snapshot_id: Optional[str] = None
    ) -> MissionTimeline:
        """Start tracking a new mission"""
        
        mission_id = f"mission-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        timeline = MissionTimeline(
            mission_id=mission_id,
            mission_name=mission_name,
            mission_goal=mission_goal,
            started_at=datetime.now(timezone.utc),
            initial_snapshot_id=initial_snapshot_id,
            current_safe_point_id=initial_snapshot_id,
            total_planned_actions=planned_actions,
            status="in_progress",
            can_rollback=(initial_snapshot_id is not None),
            rollback_available_count=1 if initial_snapshot_id else 0
        )
        
        async with async_session() as session:
            session.add(timeline)
            await session.commit()
        
        await immutable_log.append(
            actor="progression_tracker",
            action="mission_started",
            resource=mission_id,
            subsystem="progression",
            payload={
                "mission_id": mission_id,
                "mission_name": mission_name,
                "planned_actions": planned_actions
            },
            result="started"
        )
        
        print(f"  [MISSION] Mission started: {mission_name} ({planned_actions} actions planned)")
        
        return timeline
    
    async def record_action_completed(
        self,
        mission_id: str,
        action_contract_id: str,
        success: bool,
        new_safe_point_id: Optional[str] = None
    ):
        """Record completion of an action (success or failure)"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
            )
            timeline = result.scalar_one_or_none()
            
            if not timeline:
                return
            
            if success:
                timeline.completed_actions += 1
                
                # Update safe point if provided
                if new_safe_point_id:
                    timeline.current_safe_point_id = new_safe_point_id
                    timeline.can_rollback = True
                    timeline.rollback_available_count += 1
            else:
                timeline.failed_actions += 1
            
            # Update progress ratio
            if timeline.total_planned_actions > 0:
                timeline.progress_ratio = timeline.completed_actions / timeline.total_planned_actions
            
            # Update confidence based on success rate
            total_attempts = timeline.completed_actions + timeline.failed_actions
            if total_attempts > 0:
                success_rate = timeline.completed_actions / total_attempts
                timeline.confidence_score = success_rate
            
            await session.commit()
        
        await immutable_log.append(
            actor="progression_tracker",
            action="action_completed",
            resource=mission_id,
            subsystem="progression",
            payload={
                "mission_id": mission_id,
                "action_contract_id": action_contract_id,
                "success": success,
                "progress": timeline.progress_ratio
            },
            result="success" if success else "failed"
        )
    
    async def record_rollback(
        self,
        mission_id: str,
        rolled_back_to: str
    ):
        """Record a rollback event"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
            )
            timeline = result.scalar_one_or_none()
            
            if not timeline:
                return
            
            timeline.rolled_back_actions += 1
            timeline.current_safe_point_id = rolled_back_to
            
            # Decrease confidence after rollback
            timeline.confidence_score *= 0.8
            
            await session.commit()
        
        await immutable_log.append(
            actor="progression_tracker",
            action="rollback_executed",
            resource=mission_id,
            subsystem="progression",
            payload={
                "mission_id": mission_id,
                "rolled_back_to": rolled_back_to
            },
            result="rolled_back"
        )
        
        print(f"  🔙 Rolled back to: {rolled_back_to}")
    
    async def update_health_score(
        self,
        mission_id: str,
        health_score: int
    ):
        """Update current system health score"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
            )
            timeline = result.scalar_one_or_none()
            
            if not timeline:
                return
            
            timeline.current_health_score = health_score
            
            # Adjust confidence based on health
            if health_score < 70:
                timeline.confidence_score *= 0.9
            
            await session.commit()
    
    async def get_current_status(
        self,
        mission_id: Optional[str] = None
    ) -> Optional[ProgressionSnapshot]:
        """
        Get current progression status.
        If no mission_id provided, returns status of active mission.
        """
        
        async with async_session() as session:
            from sqlalchemy import select
            
            if mission_id:
                result = await session.execute(
                    select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
                )
            else:
                # Get most recent in-progress mission
                result = await session.execute(
                    select(MissionTimeline)
                    .where(MissionTimeline.status == "in_progress")
                    .order_by(MissionTimeline.started_at.desc())
                    .limit(1)
                )
            
            timeline = result.scalar_one_or_none()
            
            if not timeline:
                return None
            
            # Calculate elapsed time
            elapsed = (datetime.now(timezone.utc) - timeline.started_at).total_seconds()
            
            # Estimate time remaining (simple linear projection)
            estimated_remaining = None
            if timeline.progress_ratio > 0:
                total_estimated = elapsed / timeline.progress_ratio
                estimated_remaining = total_estimated - elapsed
            
            # Get last safe point timestamp
            last_safe_time = None
            if timeline.current_safe_point_id:
                from .self_heal.safe_hold import SafeHoldSnapshot
                safe_result = await session.execute(
                    select(SafeHoldSnapshot)
                    .where(SafeHoldSnapshot.id == timeline.current_safe_point_id)
                )
                safe_snapshot = safe_result.scalar_one_or_none()
                if safe_snapshot:
                    last_safe_time = safe_snapshot.created_at.isoformat()
            
            return ProgressionSnapshot(
                mission_id=timeline.mission_id,
                mission_name=timeline.mission_name,
                started_at=timeline.started_at.isoformat(),
                last_safe_point=timeline.current_safe_point_id,
                last_safe_point_time=last_safe_time,
                progress_percent=timeline.progress_ratio * 100,
                completed_actions=timeline.completed_actions,
                total_actions=timeline.total_planned_actions,
                failed_actions=timeline.failed_actions,
                confidence_score=timeline.confidence_score,
                current_health_score=timeline.current_health_score or 100,
                can_rollback=timeline.can_rollback,
                rollback_points_available=timeline.rollback_available_count,
                elapsed_time_seconds=elapsed,
                estimated_time_remaining_seconds=estimated_remaining
            )
    
    async def complete_mission(
        self,
        mission_id: str,
        success: bool = True
    ):
        """Mark a mission as completed"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MissionTimeline).where(MissionTimeline.mission_id == mission_id)
            )
            timeline = result.scalar_one_or_none()
            
            if not timeline:
                return
            
            timeline.status = "completed" if success else "failed"
            timeline.completed_at = datetime.now(timezone.utc)
            timeline.progress_ratio = 1.0 if success else timeline.progress_ratio
            
            await session.commit()
        
        await immutable_log.append(
            actor="progression_tracker",
            action="mission_completed",
            resource=mission_id,
            subsystem="progression",
            payload={
                "mission_id": mission_id,
                "status": timeline.status,
                "completed_actions": timeline.completed_actions,
                "failed_actions": timeline.failed_actions
            },
            result=timeline.status
        )
        
        print(f"  [OK] Mission {timeline.status}: {timeline.mission_name}")
    
    async def get_mission_history(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent mission history"""
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(MissionTimeline)
                .order_by(MissionTimeline.started_at.desc())
                .limit(limit)
            )
            timelines = result.scalars().all()
            
            history = []
            for t in timelines:
                history.append({
                    "mission_id": t.mission_id,
                    "mission_name": t.mission_name,
                    "status": t.status,
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "progress": t.progress_ratio,
                    "confidence": t.confidence_score,
                    "completed_actions": t.completed_actions,
                    "failed_actions": t.failed_actions,
                    "can_rollback": t.can_rollback
                })
            
            return history


# Singleton instance
progression_tracker = ProgressionTracker()
