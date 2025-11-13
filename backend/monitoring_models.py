"""
Monitoring Models
Real incident tracking with database schema
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.sql import func
from .models import Base


class MonitoringEvent(Base):
    """
    Real-time monitoring events from all subsystems
    Feeds the Health Dashboard
    """
    __tablename__ = "memory_monitoring_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)  # db.connection_lost, api.rate_limit, etc.
    severity = Column(String, nullable=False)  # high, medium, low
    source = Column(String, nullable=False)  # PostgreSQL Connector, OpenAI API, etc.
    component = Column(String, nullable=False)  # Which component detected it
    title = Column(String, nullable=False)  # Friendly title
    description = Column(Text)  # Details
    error_details = Column(Text)  # Stack trace, error message
    status = Column(String, default="active")  # active, acknowledged, resolving, resolved
    playbook_applied = Column(String)  # Which playbook is handling it
    detected_at = Column(DateTime, default=func.now(), nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    resolution_time_seconds = Column(Float)
    auto_fixed = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "severity": self.severity,
            "source": self.source,
            "component": self.component,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "playbook_applied": self.playbook_applied,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_time_seconds": self.resolution_time_seconds,
            "auto_fixed": self.auto_fixed,
        }


class SelfHealingExecution(Base):
    """
    Tracks self-healing playbook executions
    """
    __tablename__ = "memory_execution_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, unique=True, nullable=False)
    playbook_id = Column(String, nullable=False)
    playbook_name = Column(String)
    incident_id = Column(Integer)  # Links to MonitoringEvent
    status = Column(String, default="running")  # running, awaiting_patch, completed, failed
    steps_total = Column(Integer)
    steps_completed = Column(Integer, default=0)
    coding_work_order_id = Column(String)  # If escalated to coding agent
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    error_message = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "playbook_id": self.playbook_id,
            "playbook_name": self.playbook_name,
            "incident_id": self.incident_id,
            "status": self.status,
            "steps_completed": f"{self.steps_completed}/{self.steps_total}",
            "coding_work_order_id": self.coding_work_order_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


class ActiveAgent(Base):
    """
    Tracks active sub-agents working on incidents
    """
    __tablename__ = "memory_sub_agents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, unique=True, nullable=False)
    agent_name = Column(String, nullable=False)
    agent_type = Column(String)  # self_heal_db, api_backoff, schema_fix
    task = Column(String)  # What it's currently doing
    incident_id = Column(Integer)
    execution_id = Column(Integer)
    trust_score = Column(Float, default=0.85)
    status = Column(String, default="active")  # active, idle, stopped
    started_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    
    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "task": self.task,
            "trust_score": self.trust_score,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }
