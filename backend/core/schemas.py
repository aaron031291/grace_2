"""
Message Bus Schemas
Common contract for all kernels to communicate

All kernels speak the same language via these schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """All possible message types"""
    # Kernel lifecycle
    KERNEL_START = "kernel.start"
    KERNEL_STOP = "kernel.stop"
    KERNEL_STATUS = "kernel.status"
    KERNEL_HEARTBEAT = "kernel.heartbeat"
    
    # Task management
    TASK_ENQUEUE = "task.enqueue"
    TASK_DEQUEUE = "task.dequeue"
    TASK_RESULT = "task.result"
    TASK_CANCEL = "task.cancel"
    
    # Events
    EVENT_INCIDENT = "event.incident"
    EVENT_METRIC = "event.metric"
    EVENT_GOVERNANCE_DECISION = "event.governance_decision"
    EVENT_PROPOSAL = "event.proposal"
    
    # Configuration
    CONFIG_UPDATE = "config.update"
    SECRET_ROTATE = "secret.rotate"
    
    # System control
    SYSTEM_BOOT = "system.boot"
    SYSTEM_PAUSE = "system.pause"
    SYSTEM_RESUME = "system.resume"
    SYSTEM_SHUTDOWN = "system.shutdown"


class TrustLevel(str, Enum):
    """Trust levels for messages"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


class MessageMetadata(BaseModel):
    """Metadata attached to every message"""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    trust_level: TrustLevel = TrustLevel.MEDIUM
    auth_token: Optional[str] = None
    source_kernel: str
    target_kernel: Optional[str] = None
    priority: int = 2  # 1=low, 2=normal, 3=high, 4=critical


class BusMessage(BaseModel):
    """
    Standard message format for the bus
    All kernels use this format
    """
    type: MessageType
    source: str
    target: Optional[str] = None  # None = broadcast
    payload: Dict[str, Any]
    metadata: MessageMetadata
    
    class Config:
        use_enum_values = True


# Specific message payloads

class KernelStartPayload(BaseModel):
    """Payload for kernel.start"""
    kernel_name: str
    config: Dict[str, Any] = {}


class KernelStatusPayload(BaseModel):
    """Payload for kernel.status"""
    kernel_name: str
    state: str  # running, stopped, failed
    health: str  # healthy, degraded, unhealthy
    metrics: Dict[str, Any] = {}


class TaskEnqueuePayload(BaseModel):
    """Payload for task.enqueue"""
    task_id: str
    task_type: str  # ingest, sandbox, heal, code
    priority: int = 2
    data: Dict[str, Any]
    requires_approval: bool = False


class TaskResultPayload(BaseModel):
    """Payload for task.result"""
    task_id: str
    status: str  # success, failed, cancelled
    result: Dict[str, Any] = {}
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class IncidentPayload(BaseModel):
    """Payload for event.incident"""
    incident_id: str
    severity: str  # low, medium, high, critical
    component: str
    description: str
    metrics: Dict[str, Any] = {}
    auto_heal: bool = True


class GovernanceDecisionPayload(BaseModel):
    """Payload for event.governance_decision"""
    decision_id: str
    proposal_id: str
    decision: str  # approved, rejected, needs_review
    rationale: str
    approver: str
    trust_score: float
    risk_score: float


class ProposalPayload(BaseModel):
    """Payload for event.proposal"""
    proposal_id: str
    proposal_type: str  # improvement, integration, deployment
    description: str
    evidence: Dict[str, Any]
    confidence: float
    risk_level: str
    requires_human_approval: bool = True


class SecretRotatePayload(BaseModel):
    """Payload for secret.rotate"""
    secret_name: str
    rotation_reason: str  # scheduled, compromised, expired


class ConfigUpdatePayload(BaseModel):
    """Payload for config.update"""
    config_key: str
    config_value: Any
    scope: str  # system, kernel, user


# Helper functions

def create_kernel_message(
    msg_type: MessageType,
    source: str,
    payload: Dict[str, Any],
    target: Optional[str] = None,
    correlation_id: Optional[str] = None,
    trust_level: TrustLevel = TrustLevel.MEDIUM
) -> BusMessage:
    """
    Create a properly formatted bus message
    
    Args:
        msg_type: Message type
        source: Source kernel
        payload: Message payload
        target: Target kernel (None = broadcast)
        correlation_id: For request/response correlation
        trust_level: Trust level of message
    
    Returns:
        Formatted bus message
    """
    
    metadata = MessageMetadata(
        correlation_id=correlation_id,
        trust_level=trust_level,
        source_kernel=source,
        target_kernel=target
    )
    
    return BusMessage(
        type=msg_type,
        source=source,
        target=target,
        payload=payload,
        metadata=metadata
    )


def parse_bus_message(data: Dict[str, Any]) -> BusMessage:
    """
    Parse raw message data into BusMessage
    
    Args:
        data: Raw message dictionary
    
    Returns:
        Parsed BusMessage
    """
    
    return BusMessage(**data)
