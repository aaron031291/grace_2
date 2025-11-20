"""
Task Registry Models
Unified task tracking across all subsystems with resource usage metrics
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON, Index
from sqlalchemy.sql import func
from .base_models import Base


class TaskRegistryEntry(Base):
    """
    Unified task registry - single source of truth for all subsystem tasks
    
    Captures:
    - Time metrics (started, completed, duration)
    - Resource usage (CPU, memory, disk, network, storage)
    - Verification status
    - Subsystem-specific metadata
    """
    __tablename__ = "task_registry"
    
    # Identity
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(128), unique=True, nullable=False, index=True)
    
    # Task details
    task_type = Column(String(64), nullable=False, index=True)  # mission, playbook, work_order, training_job, etc.
    subsystem = Column(String(64), nullable=False, index=True)  # healing, coding_agent, learning, ml_pipeline, rag, etc.
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    
    # Ownership
    created_by = Column(String(128), nullable=False)  # guardian, user, autonomous_agent, etc.
    assigned_to = Column(String(128), nullable=True)  # Which subsystem/agent owns execution
    
    # Status
    status = Column(String(32), nullable=False, index=True)  # pending, active, completed, failed, cancelled
    priority = Column(Integer, default=5)  # 1-10, higher = more urgent
    
    # Time tracking
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)  # Derived: completed_at - started_at
    
    # Resource usage
    cpu_seconds = Column(Float, nullable=True)  # Total CPU time consumed
    memory_peak_mb = Column(Float, nullable=True)  # Peak memory usage
    memory_avg_mb = Column(Float, nullable=True)  # Average memory usage
    disk_read_mb = Column(Float, nullable=True)  # Disk reads
    disk_write_mb = Column(Float, nullable=True)  # Disk writes
    network_tx_mb = Column(Float, nullable=True)  # Network sent
    network_rx_mb = Column(Float, nullable=True)  # Network received
    storage_delta_mb = Column(Float, nullable=True)  # Storage expansion (new files created)
    
    # ML/DL specific metrics
    dataset_size_mb = Column(Float, nullable=True)  # Training dataset size
    vectors_processed = Column(Integer, nullable=True)  # Embeddings/vectors created
    tokens_processed = Column(Integer, nullable=True)  # LLM tokens used
    model_size_mb = Column(Float, nullable=True)  # Model weights size
    epochs_completed = Column(Integer, nullable=True)  # Training epochs
    
    # Sub-task metrics
    subtasks_total = Column(Integer, default=0)  # Total sub-tasks
    subtasks_completed = Column(Integer, default=0)  # Completed sub-tasks
    subtasks_failed = Column(Integer, default=0)  # Failed sub-tasks
    retries_count = Column(Integer, default=0)  # Number of retries
    verification_passes = Column(Integer, default=0)  # Verification attempts passed
    verification_failures = Column(Integer, default=0)  # Verification attempts failed
    
    # Verification
    verification_required = Column(Boolean, default=True)
    verification_status = Column(String(32), nullable=True)  # pending, passed, failed, skipped
    verification_details = Column(JSON, nullable=True)  # What was verified and results
    
    # Dependencies
    depends_on_tasks = Column(JSON, nullable=True)  # Array of task_ids this depends on
    blocks_tasks = Column(JSON, nullable=True)  # Array of task_ids blocked by this
    
    # Context & task metadata
    context = Column(JSON, nullable=True)  # Task-specific context
    task_metadata = Column(JSON, nullable=True)  # Additional metadata
    tags = Column(JSON, nullable=True)  # Tags for categorization
    
    # Error tracking
    error_message = Column(Text, nullable=True)  # If failed, why
    error_count = Column(Integer, default=0)  # Number of errors encountered
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    # SLA tracking
    sla_deadline = Column(DateTime(timezone=True), nullable=True)  # When task must complete
    sla_met = Column(Boolean, nullable=True)  # Whether SLA was met
    
    # Audit
    immutable_log_id = Column(Integer, nullable=True)  # Link to immutable log entry
    verification_envelope_id = Column(Integer, nullable=True)  # Link to verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_subsystem_status', 'subsystem', 'status'),
        Index('idx_created_by_status', 'created_by', 'status'),
        Index('idx_task_type_status', 'task_type', 'status'),
        Index('idx_started_at', 'started_at'),
        Index('idx_completed_at', 'completed_at'),
    )


class TaskResourceSnapshot(Base):
    """
    Periodic resource snapshots during long-running tasks
    Allows tracking resource usage over time
    """
    __tablename__ = "task_resource_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(128), nullable=False, index=True)
    
    # Snapshot timing
    snapshot_at = Column(DateTime(timezone=True), server_default=func.now())
    elapsed_seconds = Column(Float, nullable=False)  # Time since task started
    
    # Resource state at snapshot
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    disk_io_mb = Column(Float, nullable=True)
    network_io_mb = Column(Float, nullable=True)
    
    # ML/DL progress
    progress_percent = Column(Float, nullable=True)
    current_epoch = Column(Integer, nullable=True)
    current_loss = Column(Float, nullable=True)
    
    # Metadata
    snapshot_metadata = Column(JSON, nullable=True)


class TaskDependency(Base):
    """
    Task dependency graph - tracks what blocks what
    """
    __tablename__ = "task_dependencies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relationship
    task_id = Column(String(128), nullable=False, index=True)  # Task that depends
    depends_on_task_id = Column(String(128), nullable=False, index=True)  # Task it depends on
    
    # Dependency type
    dependency_type = Column(String(32), default="blocks")  # blocks, requires, optional
    
    # Status
    resolved = Column(Boolean, default=False)  # True when dependency is satisfied
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_task_depends', 'task_id', 'depends_on_task_id'),
    )


class SubsystemTaskMetrics(Base):
    """
    Aggregate metrics per subsystem for forecasting and anomaly detection
    """
    __tablename__ = "subsystem_task_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Subsystem identification
    subsystem = Column(String(64), nullable=False, index=True)
    task_type = Column(String(64), nullable=False, index=True)
    
    # Aggregate statistics (updated periodically)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    
    # Time statistics
    avg_duration_seconds = Column(Float, nullable=True)
    min_duration_seconds = Column(Float, nullable=True)
    max_duration_seconds = Column(Float, nullable=True)
    p95_duration_seconds = Column(Float, nullable=True)  # 95th percentile
    
    # Resource statistics
    avg_cpu_seconds = Column(Float, nullable=True)
    avg_memory_mb = Column(Float, nullable=True)
    avg_storage_mb = Column(Float, nullable=True)
    
    # Success metrics
    success_rate = Column(Float, nullable=True)  # completed / total
    verification_pass_rate = Column(Float, nullable=True)  # verified / completed
    
    # SLA metrics
    sla_met_rate = Column(Float, nullable=True)  # Tasks meeting SLA
    avg_sla_margin_seconds = Column(Float, nullable=True)  # How early/late tasks finish
    
    # Anomaly detection baselines
    anomaly_threshold_duration = Column(Float, nullable=True)  # Alert if task takes > this
    anomaly_threshold_memory = Column(Float, nullable=True)  # Alert if memory > this
    
    # Last update
    last_calculated_at = Column(DateTime(timezone=True), nullable=True)
    sample_size = Column(Integer, default=0)  # How many tasks in calculation
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        Index('idx_subsystem_tasktype', 'subsystem', 'task_type'),
    )
