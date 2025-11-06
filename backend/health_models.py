from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .models import Base

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    type = Column(String(64), nullable=True)
    owner = Column(String(64), nullable=True)
    criticality = Column(String(16), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ServiceDependency(Base):
    __tablename__ = "service_dependencies"
    id = Column(Integer, primary_key=True)
    from_service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    to_service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    type = Column(String(16), nullable=True)

class HealthSignal(Base):
    __tablename__ = "health_signals"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    signal_type = Column(String(64), nullable=False)
    metric_key = Column(String(128), nullable=True)
    value = Column(Float, nullable=True)
    status = Column(String(16), nullable=False)
    severity = Column(String(16), nullable=True)
    fingerprint = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HealthState(Base):
    __tablename__ = "health_state"
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), unique=True)
    status = Column(String(16), nullable=False)
    confidence = Column(Float, nullable=False)
    top_symptoms = Column(Text, nullable=True)  # JSON string
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
