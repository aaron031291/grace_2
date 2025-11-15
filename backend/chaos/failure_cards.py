"""
Failure Card Catalog
Defines all synthetic failure scenarios for chaos testing

Each card:
- Trigger condition
- Expected playbooks/actions
- Verification steps
- Rollback criteria
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class FailureCategory(Enum):
    """Failure categories"""
    CODE_ERROR = "code_error"
    DEPENDENCY = "dependency"
    KERNEL_HEALTH = "kernel_health"
    SCHEMA_DRIFT = "schema_drift"
    MODEL_CORRUPTION = "model_corruption"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAULT = "network_fault"
    SECURITY_BREACH = "security_breach"
    CONFIG_DRIFT = "config_drift"


@dataclass
class FailureCard:
    """Single failure scenario"""
    card_id: str
    category: FailureCategory
    name: str
    description: str
    
    # Injection
    injection_method: str  # code_patch, config_change, resource_stress, etc.
    injection_params: Dict[str, Any]
    
    # Detection
    expected_trigger: str  # Which trigger should detect this
    
    # Response
    expected_playbooks: List[str]  # Playbooks that should execute
    
    # Verification
    verification_steps: List[str]
    rollback_criteria: List[str]
    
    # Optional fields with defaults
    detection_timeout: int = 60  # Max seconds to detect
    expected_coding_agent_tasks: int = 0  # Number of coding agent tasks
    
    # SLO
    max_healing_time: int = 300  # Max seconds to heal
    
    # Risk weighting
    risk_weight: float = 1.0  # Higher = inject more often
    
    # Tracking
    drill_count: int = 0
    last_drilled: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0


# ========== FAILURE CARD CATALOG ==========

FAILURE_CATALOG: List[FailureCard] = [
    
    # CODE ERRORS
    FailureCard(
        card_id="CE001",
        category=FailureCategory.CODE_ERROR,
        name="Syntax Error in Main",
        description="Inject syntax error in backend/main.py",
        injection_method="code_patch",
        injection_params={
            'file': 'backend/main.py',
            'patch': 'async def broken(\n    pass  # Missing closing paren'
        },
        expected_trigger="live_error_feed",
        expected_playbooks=["repeated_error_pattern"],
        expected_coding_agent_tasks=1,
        verification_steps=[
            "python -m py_compile backend/main.py",
            "curl http://localhost:8000/health"
        ],
        rollback_criteria=["syntax_error_count == 0", "api_responding == true"],
        max_healing_time=120,
        risk_weight=2.0
    ),
    
    FailureCard(
        card_id="CE002",
        category=FailureCategory.CODE_ERROR,
        name="Import Error",
        description="Add import to non-existent module",
        injection_method="code_patch",
        injection_params={
            'file': 'backend/test_target.py',
            'patch': 'from nonexistent_module import something'
        },
        expected_trigger="live_error_feed",
        expected_playbooks=["repeated_error_pattern"],
        expected_coding_agent_tasks=1,
        verification_steps=["python -c 'import backend.test_target'"],
        rollback_criteria=["import_succeeds == true"],
        max_healing_time=90,
        risk_weight=1.5
    ),
    
    # DEPENDENCY ISSUES
    FailureCard(
        card_id="DEP001",
        category=FailureCategory.DEPENDENCY,
        name="Missing Binary",
        description="Temporarily hide git binary",
        injection_method="binary_hide",
        injection_params={'binary': 'git'},
        expected_trigger="dependency_regression",
        expected_playbooks=["dependency_regression_detected"],
        expected_coding_agent_tasks=1,
        verification_steps=["which git", "git --version"],
        rollback_criteria=["binary_found == true"],
        max_healing_time=60,
        risk_weight=1.0
    ),
    
    # KERNEL HEALTH
    FailureCard(
        card_id="KH001",
        category=FailureCategory.KERNEL_HEALTH,
        name="Kernel Heartbeat Stops",
        description="Stop sending heartbeats from coding_agent",
        injection_method="heartbeat_block",
        injection_params={'kernel': 'coding_agent', 'duration': 40},
        expected_trigger="health_signal_gap",
        expected_playbooks=["kernel_heartbeat_gap"],
        verification_steps=["check_kernel_running coding_agent"],
        rollback_criteria=["heartbeat_received == true"],
        max_healing_time=90,
        risk_weight=2.5
    ),
    
    FailureCard(
        card_id="KH002",
        category=FailureCategory.KERNEL_HEALTH,
        name="Kernel Crash",
        description="Kill kernel process",
        injection_method="kill_process",
        injection_params={'kernel': 'librarian'},
        expected_trigger="health_signal_gap",
        expected_playbooks=["kernel_heartbeat_gap"],
        verification_steps=["check_kernel_state librarian running"],
        rollback_criteria=["kernel_state == running"],
        max_healing_time=60,
        risk_weight=2.0
    ),
    
    # SCHEMA DRIFT
    FailureCard(
        card_id="SD001",
        category=FailureCategory.SCHEMA_DRIFT,
        name="API Response Missing Field",
        description="Remove field from /api/health response",
        injection_method="response_patch",
        injection_params={
            'endpoint': '/api/health',
            'remove_field': 'total_kernels'
        },
        expected_trigger="telemetry_drift",
        expected_playbooks=["schema_drift_detected"],
        expected_coding_agent_tasks=1,
        verification_steps=["curl http://localhost:8000/api/health | jq .total_kernels"],
        rollback_criteria=["field_present == true"],
        max_healing_time=120,
        risk_weight=1.5
    ),
    
    # MODEL CORRUPTION
    FailureCard(
        card_id="MC001",
        category=FailureCategory.MODEL_CORRUPTION,
        name="Corrupted Model Weights",
        description="Write random bytes to model file",
        injection_method="file_corrupt",
        injection_params={
            'file': 'ml_artifacts/grace_model.pt',
            'bytes': 1024
        },
        expected_trigger="model_integrity",
        expected_playbooks=["model_corruption_detected"],
        verification_steps=["validate_model_checksum ml_artifacts/grace_model.pt"],
        rollback_criteria=["checksum_valid == true"],
        max_healing_time=180,
        risk_weight=1.0
    ),
    
    # RESOURCE EXHAUSTION
    FailureCard(
        card_id="RE001",
        category=FailureCategory.RESOURCE_EXHAUSTION,
        name="CPU Saturation",
        description="Spawn CPU-intensive workload",
        injection_method="cpu_stress",
        injection_params={'cores': 4, 'duration': 60},
        expected_trigger="resource_pressure",
        expected_playbooks=["cpu_saturation"],
        verification_steps=["check_cpu_percent < 80"],
        rollback_criteria=["cpu_normal == true"],
        max_healing_time=90,
        risk_weight=2.0
    ),
    
    FailureCard(
        card_id="RE002",
        category=FailureCategory.RESOURCE_EXHAUSTION,
        name="Memory Leak",
        description="Allocate large memory buffers",
        injection_method="memory_stress",
        injection_params={'size_mb': 1024, 'duration': 60},
        expected_trigger="resource_pressure",
        expected_playbooks=["memory_pressure"],
        verification_steps=["check_memory_percent < 85"],
        rollback_criteria=["memory_normal == true"],
        max_healing_time=90,
        risk_weight=1.5
    ),
    
    FailureCard(
        card_id="RE003",
        category=FailureCategory.RESOURCE_EXHAUSTION,
        name="Queue Backlog",
        description="Flood message bus with requests",
        injection_method="queue_flood",
        injection_params={'queue': 'message_bus', 'count': 5000},
        expected_trigger="latency_queue_spike",
        expected_playbooks=["high_queue_backlog"],
        verification_steps=["check_queue_size message_bus < 100"],
        rollback_criteria=["queue_cleared == true"],
        max_healing_time=120,
        risk_weight=1.8
    ),
    
    # CONFIG DRIFT
    FailureCard(
        card_id="CF001",
        category=FailureCategory.CONFIG_DRIFT,
        name="Config File Modified",
        description="Change model_manifest.yaml",
        injection_method="config_modify",
        injection_params={
            'file': 'config/model_manifest.yaml',
            'change': 'governance.approval_required: false'
        },
        expected_trigger="config_drift",
        expected_playbooks=["config_drift_detected"],
        verification_steps=["verify_config_checksum config/model_manifest.yaml"],
        rollback_criteria=["checksum_match == true"],
        max_healing_time=60,
        risk_weight=1.2
    ),
    
    # NETWORK FAULTS
    FailureCard(
        card_id="NF001",
        category=FailureCategory.NETWORK_FAULT,
        name="API Latency Spike",
        description="Add artificial delay to endpoints",
        injection_method="latency_injection",
        injection_params={'delay_ms': 1000, 'endpoints': ['/api/chat']},
        expected_trigger="latency_queue_spike",
        expected_playbooks=["api_latency_spike"],
        verification_steps=["measure_latency /api/chat < 500"],
        rollback_criteria=["latency_normal == true"],
        max_healing_time=90,
        risk_weight=1.5
    ),
    
    # SECURITY
    FailureCard(
        card_id="SEC001",
        category=FailureCategory.SECURITY_BREACH,
        name="Secret Leak Attempt",
        description="Log secret to file",
        injection_method="secret_leak",
        injection_params={'target': 'logs/test.log'},
        expected_trigger="security_signal",
        expected_playbooks=["security_incident"],
        verification_steps=["scan_logs_for_secrets"],
        rollback_criteria=["secrets_safe == true"],
        max_healing_time=30,
        risk_weight=3.0
    ),
]


def get_card_by_id(card_id: str) -> Optional[FailureCard]:
    """Get failure card by ID"""
    return next((c for c in FAILURE_CATALOG if c.card_id == card_id), None)


def get_cards_by_category(category: FailureCategory) -> List[FailureCard]:
    """Get all cards in category"""
    return [c for c in FAILURE_CATALOG if c.category == category]


def get_high_risk_cards() -> List[FailureCard]:
    """Get cards with risk_weight >= 2.0"""
    return sorted(
        [c for c in FAILURE_CATALOG if c.risk_weight >= 2.0],
        key=lambda c: c.risk_weight,
        reverse=True
    )
