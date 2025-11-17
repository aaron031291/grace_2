"""
Healing System Database Models
Complete tracking of all autonomous healing activities
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from datetime import datetime

from .base_models import Base


class HealingAttempt(Base):
    """Track every healing attempt with full details"""
    __tablename__ = "healing_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(String, unique=True, index=True, nullable=False)
    
    # Error information
    error_type = Column(String, index=True, nullable=False)
    error_message = Column(Text, nullable=False)
    error_file = Column(String, nullable=True)
    error_line = Column(Integer, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Fix information
    fix_type = Column(String, index=True, nullable=True)
    fix_description = Column(Text, nullable=True)
    fix_code = Column(Text, nullable=True)
    original_code = Column(Text, nullable=True)
    
    # Healing metadata
    detected_by = Column(String, index=True, nullable=False)  # log_healer, code_healer, etc.
    severity = Column(String, index=True, nullable=False)  # low, medium, high, critical
    confidence = Column(Float, default=0.0)  # ML confidence score
    
    # ML/DL metadata
    ml_recommendation = Column(JSON, nullable=True)  # ML recommended strategy
    success_probability = Column(Float, nullable=True)  # Predicted success rate
    similar_fixes_count = Column(Integer, default=0)  # DL found similar fixes
    
    # Governance
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String, nullable=True)
    approval_timestamp = Column(DateTime, nullable=True)
    
    # Execution
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    applied_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Outcome
    status = Column(String, index=True, nullable=False)  # pending, applied, failed, rolled_back
    success = Column(Boolean, nullable=True)
    failure_reason = Column(Text, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)  # Cryptographic signature
    hash = Column(String, nullable=True)  # SHA-256 hash of attempt
    previous_hash = Column(String, nullable=True)  # Hash of previous attempt (chain)
    
    # Additional metadata
    healing_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgenticSpineLog(Base):
    """Log all agentic spine autonomous decisions and actions"""
    __tablename__ = "agentic_spine_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True, nullable=False)
    
    # Decision information
    decision_type = Column(String, index=True, nullable=False)  # recovery, optimization, prediction
    decision_context = Column(JSON, nullable=False)
    options_considered = Column(JSON, nullable=True)
    chosen_action = Column(String, nullable=False)
    rationale = Column(Text, nullable=False)
    
    # Confidence and risk
    confidence = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    
    # Execution
    actor = Column(String, index=True, nullable=False)  # Which spine component
    resource = Column(String, nullable=True)
    status = Column(String, index=True, nullable=False)  # proposed, executing, completed, failed
    
    # Outcome
    outcome = Column(String, nullable=True)
    impact = Column(JSON, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    previous_hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MetaLoopLog(Base):
    """Track all meta-loop cycles and decisions"""
    __tablename__ = "meta_loop_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(String, unique=True, index=True, nullable=False)
    cycle_number = Column(Integer, index=True, nullable=False)
    
    # Snapshot data
    snapshot_before = Column(JSON, nullable=True)
    snapshot_after = Column(JSON, nullable=True)
    
    # Analysis
    focus_area = Column(String, index=True, nullable=True)  # routine_maintenance, critical_recovery
    guardrails_mode = Column(String, nullable=True)  # maintain, adjust, override
    ml_root_causes = Column(JSON, nullable=True)  # ML-identified root causes
    
    # Directives issued
    directives_issued = Column(JSON, nullable=True)
    directives_executed = Column(Integer, default=0)
    directives_successful = Column(Integer, default=0)
    
    # Performance
    duration_seconds = Column(Float, nullable=True)
    domains_analyzed = Column(Integer, default=0)
    
    # Outcome
    outcome = Column(String, nullable=True)
    improvements_made = Column(JSON, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    previous_hash = Column(String, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MLLearningLog(Base):
    """Track ML/DL learning cycles and pattern evolution"""
    __tablename__ = "ml_learning_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_id = Column(String, unique=True, index=True, nullable=False)
    
    # Learning type
    learning_type = Column(String, index=True, nullable=False)  # pattern_update, model_training, prediction
    subsystem = Column(String, index=True, nullable=False)  # ml_healing, dl_healing
    
    # Pattern data
    pattern_name = Column(String, index=True, nullable=True)
    pattern_count = Column(Integer, default=0)
    pattern_success_rate = Column(Float, nullable=True)
    pattern_confidence = Column(Float, nullable=True)
    
    # Model data
    model_type = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    training_samples = Column(Integer, default=0)
    accuracy = Column(Float, nullable=True)
    
    # Predictions
    predicted_error = Column(String, nullable=True)
    predicted_likelihood = Column(Float, nullable=True)
    prediction_correct = Column(Boolean, nullable=True)
    
    # Recommendations
    recommended_strategy = Column(String, nullable=True)
    recommendation_confidence = Column(Float, nullable=True)
    recommendation_used = Column(Boolean, nullable=True)
    
    # Data sources
    data_sources = Column(JSON, nullable=True)
    training_duration_seconds = Column(Float, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    previous_hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TriggerMeshLog(Base):
    """Log all trigger mesh events for debugging and analysis"""
    __tablename__ = "trigger_mesh_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    
    # Event details
    event_type = Column(String, index=True, nullable=False)
    source = Column(String, index=True, nullable=False)
    actor = Column(String, index=True, nullable=False)
    resource = Column(String, nullable=True)
    
    # Payload
    payload = Column(JSON, nullable=True)
    
    # Routing
    handlers_notified = Column(Integer, default=0)
    handlers_succeeded = Column(Integer, default=0)
    handlers_failed = Column(Integer, default=0)
    
    # Performance
    processing_time_ms = Column(Float, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ShardLog(Base):
    """Log all shard orchestration and parallel execution"""
    __tablename__ = "shard_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    shard_id = Column(String, index=True, nullable=False)
    log_id = Column(String, unique=True, index=True, nullable=False)
    
    # Shard information
    shard_type = Column(String, index=True, nullable=False)  # domain, workload
    domain = Column(String, index=True, nullable=True)  # ai_ml, self_heal, code, etc.
    worker_id = Column(String, index=True, nullable=True)
    
    # Task information
    task_type = Column(String, nullable=True)
    task_description = Column(Text, nullable=True)
    task_priority = Column(Integer, default=0)
    
    # Execution
    status = Column(String, index=True, nullable=False)  # started, executing, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Performance
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    tasks_processed = Column(Integer, default=0)
    
    # Outcome
    success = Column(Boolean, nullable=True)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    previous_hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ParallelProcessLog(Base):
    """Track all parallel process execution"""
    __tablename__ = "parallel_process_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(String, unique=True, index=True, nullable=False)
    
    # Process info
    process_type = Column(String, index=True, nullable=False)  # concurrent_task, shard_work, etc.
    executor = Column(String, index=True, nullable=False)  # concurrent_executor, shard_orchestrator
    worker_name = Column(String, nullable=True)
    
    # Task details
    task_name = Column(String, nullable=True)
    task_payload = Column(JSON, nullable=True)
    parent_process = Column(String, nullable=True)
    
    # Execution
    status = Column(String, index=True, nullable=False)  # queued, running, completed, failed
    queued_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    wait_time_seconds = Column(Float, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    
    # Performance
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    
    # Outcome
    success = Column(Boolean, nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DataCubeEntry(Base):
    """Data cube for multi-dimensional analytics"""
    __tablename__ = "data_cube"
    
    id = Column(Integer, primary_key=True, index=True)
    cube_id = Column(String, unique=True, index=True, nullable=False)
    
    # Dimensions
    dimension_time = Column(DateTime, index=True, nullable=False)  # When
    dimension_subsystem = Column(String, index=True, nullable=False)  # Where
    dimension_actor = Column(String, index=True, nullable=False)  # Who
    dimension_action = Column(String, index=True, nullable=False)  # What
    dimension_resource = Column(String, index=True, nullable=True)  # Which
    
    # Metrics (Facts)
    metric_success = Column(Boolean, nullable=True)
    metric_duration = Column(Float, nullable=True)  # seconds
    metric_confidence = Column(Float, nullable=True)  # 0.0-1.0
    metric_impact = Column(Float, nullable=True)  # 0.0-1.0
    
    # Aggregatable metrics
    metric_count = Column(Integer, default=1)
    metric_error_count = Column(Integer, default=0)
    metric_fix_count = Column(Integer, default=0)
    metric_learning_count = Column(Integer, default=0)
    
    # Categorical dimensions
    category_tier = Column(String, index=True, nullable=True)  # Autonomy tier
    category_severity = Column(String, index=True, nullable=True)  # Error severity
    category_type = Column(String, index=True, nullable=True)  # Action type
    
    # Context
    context_data = Column(JSON, nullable=True)
    
    # Cryptography
    signature = Column(String, nullable=True)
    hash = Column(String, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
