from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, text
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from .settings import settings

# Prefer env-provided DATABASE_URL; fallback to local sqlite for dev
DATABASE_URL = settings.DATABASE_URL or "sqlite+aiosqlite:///./grace.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

from .sandbox_models import SandboxRun, SandboxFile
from .governance_models import GovernancePolicy, AuditLog, ApprovalRequest, SecurityEvent, SecurityRule, HealthCheck, HealingAction
from .task_executor import ExecutionTask
from .issue_models import IssueReport
from .memory_models import MemoryArtifact, MemoryOperation, MemoryEvent
from .immutable_log import ImmutableLogEntry
from .mldl import MLEvent
from .avn_avm import VerificationEvent
from .meta_loop import MetaLoopConfig, MetaAnalysis, MetaMetaEvaluation
from .knowledge_models import KnowledgeArtifact
from .trusted_sources import TrustedSource
from .verification import VerificationEnvelope
from .ml_models_table import MLModel, TrainingRun
from .temporal_models import EventPattern, Simulation, DurationEstimate, TemporalAnomaly, PredictionRecord
from .cognition.models import MemoryArtifact as CognitionMemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog
from .transcendence.business.models import StripeTransaction, StripeWebhook, PaymentMethod, MarketplaceJob, MarketplaceProposal, MarketplaceMessage, MarketplaceDeliverable

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    password_hash_is_legacy = Column(Boolean, nullable=False, default=True, server_default=text("1"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    status = Column(String(32), default="pending")
    priority = Column(String(16), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    auto_generated = Column(Boolean, default=False)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    goal_text = Column(Text, nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class CausalEvent(Base):
    __tablename__ = "causal_events"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), nullable=False)
    trigger_message_id = Column(Integer, ForeignKey("chat_messages.id"))
    response_message_id = Column(Integer, ForeignKey("chat_messages.id"))
    event_type = Column(String(64))
    outcome = Column(String(64))
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
