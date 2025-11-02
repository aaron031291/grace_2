from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON
from sqlalchemy.sql import func
from .models import Base

class EventPattern(Base):
    """Stores discovered temporal patterns in event sequences"""
    __tablename__ = "event_patterns"
    id = Column(Integer, primary_key=True)
    pattern_type = Column(String(64), nullable=False)
    sequence = Column(JSON, nullable=False)
    frequency = Column(Integer, default=1)
    confidence = Column(Float, default=0.5)
    avg_duration = Column(Float)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Simulation(Base):
    """Records simulations and their outcomes"""
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True)
    scenario = Column(Text, nullable=False)
    parameters = Column(JSON)
    predicted_outcome = Column(JSON, nullable=False)
    actual_outcome = Column(JSON)
    confidence = Column(Float, default=0.5)
    accuracy_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))

class DurationEstimate(Base):
    """Statistical duration estimates for different task types"""
    __tablename__ = "duration_estimates"
    id = Column(Integer, primary_key=True)
    task_type = Column(String(64), nullable=False, unique=True)
    avg_duration = Column(Float, nullable=False)
    std_deviation = Column(Float, default=0.0)
    min_duration = Column(Float)
    max_duration = Column(Float)
    sample_count = Column(Integer, default=0)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

class TemporalAnomaly(Base):
    """Records anomalous timing events"""
    __tablename__ = "temporal_anomalies"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(64), nullable=False)
    event_id = Column(String(128))
    expected_duration = Column(Float)
    actual_duration = Column(Float)
    deviation_sigma = Column(Float)
    severity = Column(String(16))
    details = Column(JSON)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

class PredictionRecord(Base):
    """Track prediction accuracy over time"""
    __tablename__ = "prediction_records"
    id = Column(Integer, primary_key=True)
    prediction_type = Column(String(64), nullable=False)
    predicted_event = Column(String(128))
    predicted_probability = Column(Float)
    actual_event = Column(String(128))
    correct = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
