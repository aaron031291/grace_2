from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import Base, engine, async_session from base_models (foundation layer)
from .base_models import Base, engine, async_session

from .sandbox_models import SandboxRun, SandboxFile
from .governance_models import GovernancePolicy, AuditLog, ApprovalRequest, SecurityEvent, SecurityRule, HealthCheck, HealingAction
from backend.execution.task_executor import ExecutionTask
from .issue_models import IssueReport
from .memory_models import MemoryArtifact, MemoryOperation, MemoryEvent
from backend.logging.immutable_log import ImmutableLogEntry
from backend.ml_training.mldl import MLEvent
from .avn_avm import VerificationEvent
from .meta_loop import MetaLoopConfig, MetaAnalysis, MetaMetaEvaluation
from .knowledge_models import KnowledgeArtifact
from .lightning_fusion_models import CryptoIdentity, FusionMemoryFragment, LightningMemoryCache, ComponentCryptoRegistration, DiagnosticTrace, VerificationAuditLog
from .trusted_sources import TrustedSource
from .ml_models_table import MLModel, TrainingRun
from .temporal_models import EventPattern, Simulation, DurationEstimate, TemporalAnomaly, PredictionRecord
from .cognition.models import MemoryArtifact as CognitionMemoryArtifact, TrustEvent, MemoryIndex, GarbageCollectionLog
from .transcendence.business.models import StripeTransaction, StripeWebhook, PaymentMethod, MarketplaceJob, MarketplaceProposal, MarketplaceMessage, MarketplaceDeliverable
from .goal_models import GoalDependency, GoalEvaluation

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
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
    priority = Column(String(16), default="medium")
    value_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    success_criteria = Column(Text, nullable=True)  # JSON blob describing success metrics
    owner = Column(String(64), nullable=True)
    category = Column(String(64), nullable=True)
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
