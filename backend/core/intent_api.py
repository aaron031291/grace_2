"""
Intent API - Bridge Between Layer 3 (Agentic Brain) and Layer 2 (HTM)

This is the critical connection that allows the autonomous brain to
communicate goals and receive execution feedback.

Architecture:
    Layer 3: Agentic Brain -> Intent API -> Layer 2: HTM
    Layer 2: HTM -> Intent API -> Layer 3: Learning Loop
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime, timezone
from enum import Enum

from backend.core.message_bus import message_bus, MessagePriority
from backend.logging.immutable_log import immutable_log
from sqlalchemy import Column, String, JSON, DateTime, Float, Integer, Boolean
from backend.models.base_models import Base, async_session


class IntentStatus(Enum):
    """Lifecycle states of an intent"""
    CREATED = "created"
    ENRICHED = "enriched"
    DISPATCHED = "dispatched"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class IntentPriority(int, Enum):
    """Intent priority"""
    MINIMUM = 1
    CRITICAL = 10
    HIGH = 8
    NORMAL = 5
    LOW = 3
    IDLE = 0


class IntentDomain(str, Enum):
    """Intent domains for categorization"""
    INGESTION = "ingestion"
    QUERY = "query"
    LEARNING = "learning"
    ANALYSIS = "analysis"
    ORCHESTRATION = "orchestration"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Structured intent from agentic brain to orchestration layer"""
    intent_id: str
    goal: str
    expected_outcome: str
    sla_ms: int
    priority: IntentPriority
    domain: str
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "agentic_brain"
    confidence: float = 0.8
    risk_level: str = "low"


@dataclass
class IntentOutcome:
    """Result of executing an intent"""
    intent_id: str
    status: IntentStatus
    result: Dict[str, Any]
    execution_time_ms: float
    success: bool
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IntentRecord(Base):
    """Database record of intents for tracking and learning"""
    __tablename__ = "intent_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    intent_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Intent details
    goal = Column(String(512), nullable=False)
    expected_outcome = Column(String(512))
    domain = Column(String(64), nullable=False)
    priority = Column(String(32), nullable=False)
    
    # Execution tracking
    status = Column(String(32), nullable=False, default="created")
    htm_task_id = Column(String(128), nullable=True)
    
    # Performance
    sla_ms = Column(Integer, nullable=False)
    actual_execution_ms = Column(Float, nullable=True)
    sla_met = Column(Boolean, nullable=True)
    
    # Outcome
    success = Column(Boolean, nullable=True)
    confidence = Column(Float, default=0.8)
    risk_level = Column(String(32))
    
    # Learning
    learned_from = Column(Boolean, default=False)
    
    # Metadata
    context = Column(JSON)
    result = Column(JSON)
    
    # Timing
    created_at = Column(DateTime(timezone=True), nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_by = Column(String(128), default="agentic_brain")


class IntentAPI:
    """
    API for agentic brain to submit intents and receive execution feedback
    
    Usage:
        # Layer 3: Submit intent
        intent = Intent(
            intent_id="int_123",
            goal="Index new documents in uploads folder",
            expected_outcome="documents_indexed",
            sla_ms=30000,
            priority=IntentPriority.HIGH,
            domain="ingestion"
        )
        task_id = await intent_api.submit_intent(intent)
        
        # Layer 2: Report completion
        await intent_api.complete_intent(
            intent_id="int_123",
            outcome=IntentOutcome(...)
        )
        
        # Layer 3: Check status
        status = await intent_api.get_intent_status("int_123")
    """
    
    def __init__(self):
        self.intents: Dict[str, Intent] = {}
        self.intent_status: Dict[str, IntentStatus] = {}
        self.intent_outcomes: Dict[str, IntentOutcome] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize intent API and restore active intents"""
        if self._initialized:
            return
        
        # Load active intents from database
        try:
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(IntentRecord)
                    .where(IntentRecord.status.in_(["created", "dispatched", "executing"]))
                )
                records = result.scalars().all()
                
                for record in records:
                    # Restore intent to memory
                    self.intent_status[record.intent_id] = IntentStatus(record.status)
        except Exception as e:
            print(f"[INTENT-API] Failed to restore intents: {e}")
        
        self._initialized = True
        print(f"[INTENT-API] Initialized with {len(self.intents)} active intents")
    
    async def submit_intent(self, intent: Intent) -> str:
        """
        Submit intent from Layer 3 to Layer 2
        
        Returns:
            intent_id for tracking
        """
        # Store in memory
        self.intents[intent.intent_id] = intent
        self.intent_status[intent.intent_id] = IntentStatus.CREATED
        
        # Persist to database
        async with async_session() as session:
            record = IntentRecord(
                intent_id=intent.intent_id,
                goal=intent.goal,
                expected_outcome=intent.expected_outcome,
                domain=intent.domain,
                priority=intent.priority.value,
                sla_ms=intent.sla_ms,
                confidence=intent.confidence,
                risk_level=intent.risk_level,
                context=intent.context,
                created_at=intent.created_at,
                created_by=intent.created_by,
                status="created"
            )
            session.add(record)
            await session.commit()
        
        # Emit intent.created event to message bus
        await message_bus.publish(
            source="intent_api",
            topic="agentic.intent.created",
            payload={
                "intent_id": intent.intent_id,
                "goal": intent.goal,
                "domain": intent.domain,
                "priority": intent.priority.value,
                "sla_ms": intent.sla_ms
            },
            priority=MessagePriority.HIGH if intent.priority == IntentPriority.CRITICAL else MessagePriority.NORMAL
        )
        
        # Log to immutable log
        await immutable_log.append(
            actor="agentic.message_bus",
            action="agentic_intent_created",
            resource=f"intent_{intent.domain}",
            subsystem="intent_api",
            payload={
                "intent_id": intent.intent_id,
                "goal": intent.goal,
                "priority": intent.priority.value,
                "outcome": "submitted"
            },
            result="SUCCESS"
        )
        
        # Update status
        self.intent_status[intent.intent_id] = IntentStatus.DISPATCHED
        
        # Update database
        async with async_session() as session:
            from sqlalchemy import update
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent.intent_id)
                .values(status="dispatched", dispatched_at=datetime.now(timezone.utc))
            )
            await session.commit()
        
        print(f"[INTENT-API] Submitted intent {intent.intent_id}: {intent.goal}")
        
        return intent.intent_id
    
    async def get_intent_status(self, intent_id: str) -> Dict[str, Any]:
        """Get current status of intent"""
        if intent_id not in self.intents:
            # Try loading from database
            async with async_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(IntentRecord)
                    .where(IntentRecord.intent_id == intent_id)
                )
                record = result.scalar_one_or_none()
                
                if record:
                    return {
                        "intent_id": intent_id,
                        "status": record.status,
                        "goal": record.goal,
                        "success": record.success,
                        "sla_met": record.sla_met,
                        "created_at": record.created_at.isoformat() if record.created_at else None,
                        "completed_at": record.completed_at.isoformat() if record.completed_at else None
                    }
            
            return {"error": "Intent not found", "intent_id": intent_id}
        
        outcome = self.intent_outcomes.get(intent_id)
        
        return {
            "intent_id": intent_id,
            "status": self.intent_status[intent_id].value,
            "intent": {
                "goal": self.intents[intent_id].goal,
                "domain": self.intents[intent_id].domain,
                "priority": self.intents[intent_id].priority.value
            },
            "outcome": {
                "success": outcome.success,
                "execution_time_ms": outcome.execution_time_ms,
                "result": outcome.result
            } if outcome else None
        }
    
    async def complete_intent(
        self, 
        intent_id: str, 
        outcome: IntentOutcome
    ):
        """
        Mark intent as completed with outcome
        Called by Layer 2 (HTM) when task finishes
        """
        if intent_id not in self.intents:
            print(f"[INTENT-API] Warning: Completing unknown intent {intent_id}")
            return
        
        # Store outcome
        self.intent_outcomes[intent_id] = outcome
        self.intent_status[intent_id] = outcome.status
        
        # Update database
        async with async_session() as session:
            from sqlalchemy import update
            
            sla_met = outcome.execution_time_ms <= self.intents[intent_id].sla_ms if outcome.execution_time_ms else None
            
            await session.execute(
                update(IntentRecord)
                .where(IntentRecord.intent_id == intent_id)
                .values(
                    status=outcome.status.value,
                    success=outcome.success,
                    actual_execution_ms=outcome.execution_time_ms,
                    sla_met=sla_met,
                    result=outcome.result,
                    completed_at=outcome.completed_at
                )
            )
            await session.commit()
        
        # Emit completion event
        await message_bus.publish(
            source="intent_api",
            topic="agentic.intent.completed",
            payload={
                "intent_id": intent_id,
                "success": outcome.success,
                "execution_time_ms": outcome.execution_time_ms,
                "status": outcome.status.value
            },
            priority=MessagePriority.NORMAL
        )
        
        # Log to immutable log
        await immutable_log.append(
            actor="intent.message_bus",
            action="agentic_intent_completed",
            resource=f"intent_{intent_id}",
            subsystem="intent_api",
            payload={
                "intent_id": intent_id,
                "execution_time_ms": outcome.execution_time_ms,
                "result": outcome.result
            },
            result="success" if outcome.success else "failed"
        )
        
        # Feed to learning loop
        await self._feed_to_learning_loop(intent_id, outcome)
        
        print(f"[INTENT-API] Completed intent {intent_id}: {'SUCCESS' if outcome.success else 'FAILED'}")
    
    async def _feed_to_learning_loop(self, intent_id: str, outcome: IntentOutcome):
        """Feed intent outcome to learning loop for continuous improvement"""
        try:
            from backend.learning_systems.learning_loop import LearningLoop
            
            learning_loop = LearningLoop()
            
            intent = self.intents.get(intent_id)
            if not intent:
                return
            
            # Record outcome for learning
            await learning_loop.record_outcome(
                playbook_id=f"intent_{intent.domain}",
                action_type=intent.goal,
                success=outcome.success,
                confidence_score=intent.confidence,
                execution_time=outcome.execution_time_ms / 1000.0,
                problem_resolved=outcome.success,
                rolled_back=len(outcome.errors) > 0,
                context={
                    "intent_id": intent_id,
                    "domain": intent.domain,
                    "priority": intent.priority.value
                }
            )
            
            print(f"[INTENT-API] Outcome recorded to learning loop for intent {intent_id}")
        except Exception as e:
            print(f"[INTENT-API] Failed to feed learning loop: {e}")
    
    async def get_active_intents(self) -> List[Dict[str, Any]]:
        """Get all active intents"""
        return [
            {
                "intent_id": intent_id,
                "goal": intent.goal,
                "domain": intent.domain,
                "status": self.intent_status[intent_id].value,
                "created_at": intent.created_at.isoformat()
            }
            for intent_id, intent in self.intents.items()
            if self.intent_status[intent_id] not in [IntentStatus.COMPLETED, IntentStatus.FAILED]
        ]
    
    async def get_intent_metrics(self) -> Dict[str, Any]:
        """Get overall intent execution metrics"""
        total = len(self.intents)
        completed = sum(1 for status in self.intent_status.values() if status == IntentStatus.COMPLETED)
        failed = sum(1 for status in self.intent_status.values() if status == IntentStatus.FAILED)
        active = total - completed - failed
        
        # Calculate success rate from outcomes
        successful_outcomes = sum(1 for outcome in self.intent_outcomes.values() if outcome.success)
        success_rate = successful_outcomes / total if total > 0 else 0.0
        
        # Calculate average execution time
        execution_times = [o.execution_time_ms for o in self.intent_outcomes.values() if o.execution_time_ms]
        avg_execution_ms = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        return {
            "total_intents": total,
            "active": active,
            "completed": completed,
            "failed": failed,
            "success_rate": success_rate,
            "avg_execution_ms": avg_execution_ms
        }


# Global instance
intent_api = IntentAPI()
