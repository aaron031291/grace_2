from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from backend.models.base_models import Base

class MLModel(Base):
    """Trained models with complete lineage"""
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True)
    model_name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    model_type = Column(String(64))
    model_hash = Column(String(64), nullable=False)
    dataset_hash = Column(String(64))
    trust_score_min = Column(Float)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_data_count = Column(Integer)
    verification_status = Column(String(32), default="unverified")
    deployment_status = Column(String(32), default="training")
    approved_by = Column(String(64))
    signature = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_at = Column(DateTime(timezone=True))
    deprecated_at = Column(DateTime(timezone=True))

class TrainingRun(Base):
    """Training execution logs"""
    __tablename__ = "training_runs"
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer)
    dataset_trust_threshold = Column(Float)
    samples_used = Column(Integer)
    duration_seconds = Column(Integer)
    final_loss = Column(Float)
    validation_score = Column(Float)
    approved = Column(Boolean, default=False)
    signature = Column(String(256))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
