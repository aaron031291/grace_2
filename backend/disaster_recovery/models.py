"""
Disaster Recovery Models
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BackupType(str, Enum):
    """Backup types"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, Enum):
    """Backup status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Backup(BaseModel):
    """Backup model"""
    backup_id: str
    tenant_id: str
    
    backup_type: BackupType
    status: BackupStatus = BackupStatus.PENDING
    
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    file_count: int = 0
    
    storage_location: Optional[str] = None
    storage_provider: str = "s3"  # "s3", "gcs", "azure", etc.
    
    # Metadata
    components: List[str] = Field(default_factory=list)  # ["database", "files", "config", ...]
    encryption_enabled: bool = True
    compression_enabled: bool = True
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    retention_days: int = 30
    expires_at: Optional[datetime] = None
    
    error_message: Optional[str] = None
    retry_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RestoreStatus(str, Enum):
    """Restore status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class RestoreJob(BaseModel):
    """Restore job model"""
    restore_id: str
    backup_id: str
    tenant_id: str
    
    status: RestoreStatus = RestoreStatus.PENDING
    restore_point: datetime
    
    target_environment: str = "production"  # "production", "staging", "test"
    target_location: Optional[str] = None
    
    components_to_restore: List[str] = Field(default_factory=list)
    verify_after_restore: bool = True
    
    progress_percent: float = 0.0
    files_restored: int = 0
    bytes_restored: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    verification_passed: Optional[bool] = None
    verification_errors: List[str] = Field(default_factory=list)
    
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChaosTestType(str, Enum):
    """Chaos test types"""
    SERVICE_FAILURE = "service_failure"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PARTITION = "network_partition"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    DEPENDENCY_FAILURE = "dependency_failure"


class ChaosTestStatus(str, Enum):
    """Chaos test status"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class ChaosTest(BaseModel):
    """Chaos engineering test"""
    test_id: str
    tenant_id: str
    
    name: str
    description: str
    test_type: ChaosTestType
    status: ChaosTestStatus = ChaosTestStatus.SCHEDULED
    
    target_service: str
    target_environment: str = "staging"
    
    duration_seconds: int = 300  # 5 minutes default
    intensity: float = 0.5  # 0.0 to 1.0
    config: Dict[str, Any] = Field(default_factory=dict)
    
    passed: Optional[bool] = None
    mttr_seconds: Optional[float] = None  # Mean Time To Recovery
    impact_assessment: Dict[str, Any] = Field(default_factory=dict)
    
    observations: List[str] = Field(default_factory=list)
    metrics_before: Dict[str, Any] = Field(default_factory=dict)
    metrics_during: Dict[str, Any] = Field(default_factory=dict)
    metrics_after: Dict[str, Any] = Field(default_factory=dict)
    
    # Timing
    scheduled_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    auto_rollback_enabled: bool = True
    rollback_triggered: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DRRunbook(BaseModel):
    """Disaster recovery runbook"""
    runbook_id: str
    name: str
    description: str
    
    scenario_type: str  # "data_loss", "service_outage", "security_breach", etc.
    severity: str = "high"  # "low", "medium", "high", "critical"
    
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    
    primary_contact: Optional[str] = None
    escalation_contacts: List[str] = Field(default_factory=list)
    
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective
    
    last_tested_at: Optional[datetime] = None
    test_frequency_days: int = 90
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
