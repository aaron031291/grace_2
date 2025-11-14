"""
HTM Task Models - Comprehensive Task Tracking with Timing
Stores all task state changes, attempts, and duration metrics
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, JSON
from sqlalchemy.sql import func
from .base_models import Base


class HTMTask(Base):
    """
    HTM Task with complete lifecycle tracking
    
    Tracks:
    - All state transitions with timestamps
    - Multiple attempts with individual timings
    - SLA compliance
    - Worker assignments
    - Completion metrics
    """
    __tablename__ = "htm_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Task identification
    task_id = Column(String(128), unique=True, nullable=False, index=True)
    task_type = Column(String(64), nullable=False, index=True)
    domain = Column(String(64), nullable=False)
    
    # Intent linkage (from Layer 3)
    intent_id = Column(String(128), nullable=True, index=True)
    
    # Task details
    priority = Column(String(32), nullable=False, default="normal")
    payload = Column(JSON, nullable=False)
    
    # State tracking
    status = Column(String(32), nullable=False, default="queued", index=True)
    # States: queued -> assigned -> running -> completed/failed/timeout
    
    # Timestamps for each state change
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    queued_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    # Execution details
    assigned_worker = Column(String(128), nullable=True)  # Which kernel/agent
    execution_context = Column(JSON, nullable=True)
    
    # Timing metrics
    queue_time_ms = Column(Float, nullable=True)  # queued_at -> assigned_at
    execution_time_ms = Column(Float, nullable=True)  # started_at -> finished_at
    total_time_ms = Column(Float, nullable=True)  # created_at -> finished_at
    
    # SLA tracking
    sla_ms = Column(Integer, nullable=True)  # Expected completion time
    sla_deadline = Column(DateTime(timezone=True), nullable=True)
    sla_met = Column(Boolean, nullable=True)
    sla_buffer_ms = Column(Float, nullable=True)  # How much time left/over
    
    # Retry tracking
    attempt_number = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)
    attempts = Column(JSON, nullable=True)  # Array of attempt records
    
    # Outcome
    success = Column(Boolean, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String(128), default="htm")
    tags = Column(JSON, nullable=True)  # For filtering/grouping
    
    # Learning
    learned_from = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)


class HTMTaskAttempt(Base):
    """
    Individual attempt record for retried tasks
    Enables detailed retry analysis
    """
    __tablename__ = "htm_task_attempts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    task_id = Column(String(128), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    
    # Attempt lifecycle
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    
    # Attempt details
    assigned_worker = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False)  # completed, failed, timeout
    success = Column(Boolean, nullable=False)
    
    # Outcome
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_type = Column(String(64), nullable=True)
    
    # Why retry happened
    retry_reason = Column(String(128), nullable=True)


class HTMMetrics(Base):
    """
    Aggregated HTM performance metrics
    Updated periodically for dashboard/planning
    """
    __tablename__ = "htm_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Time bucket
    bucket = Column(String(32), nullable=False)  # hourly, daily
    bucket_start = Column(DateTime(timezone=True), nullable=False, index=True)
    bucket_end = Column(DateTime(timezone=True), nullable=False)
    
    # Task type (or "all" for overall)
    task_type = Column(String(64), nullable=False, index=True)
    domain = Column(String(64), nullable=True)
    
    # Volume metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    timeout_tasks = Column(Integer, default=0)
    
    # Duration metrics (milliseconds)
    avg_queue_time_ms = Column(Float, default=0.0)
    avg_execution_time_ms = Column(Float, default=0.0)
    avg_total_time_ms = Column(Float, default=0.0)
    
    # Percentiles
    p50_execution_ms = Column(Float, default=0.0)
    p95_execution_ms = Column(Float, default=0.0)
    p99_execution_ms = Column(Float, default=0.0)
    
    # SLA metrics
    sla_met_count = Column(Integer, default=0)
    sla_missed_count = Column(Integer, default=0)
    sla_compliance_rate = Column(Float, default=0.0)
    
    # Retry metrics
    total_attempts = Column(Integer, default=0)
    tasks_retried = Column(Integer, default=0)
    avg_attempts = Column(Float, default=1.0)
    
    # Quality metrics
    success_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    
    # Metadata
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
