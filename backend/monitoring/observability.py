"""
Observability Hooks

Structured logging with correlation IDs and Prometheus metrics for key events.
Emits counters/gauges for actions executed, rollbacks, approvals, and confidence.

Benefits:
- Dashboards can immediately visualize system health
- Ops can alert on rollbacks or confidence dips
- Full correlation across logs, events, and metrics
"""

import structlog
from typing import Optional
import time

# Prometheus metrics (optional dependency)
try:
    from prometheus_client import Counter, Gauge, Histogram, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback no-op metrics
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def inc(self, amount=1): pass
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def set(self, value): pass
        def inc(self, amount=1): pass
        def dec(self, amount=1): pass
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def observe(self, value): pass
    
    class Summary:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def observe(self, value): pass


# ============================================================================
# Structured Logger Configuration
# ============================================================================

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# ============================================================================
# Prometheus Metrics
# ============================================================================

# Action Execution Metrics
actions_executed_total = Counter(
    'grace_actions_executed_total',
    'Total number of actions executed',
    ['action_type', 'tier', 'status']
)

action_duration_seconds = Histogram(
    'grace_action_duration_seconds',
    'Action execution duration in seconds',
    ['action_type', 'tier'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)

# Contract Verification Metrics
contracts_created_total = Counter(
    'grace_contracts_created_total',
    'Total number of action contracts created',
    ['tier']
)

contracts_verified_total = Counter(
    'grace_contracts_verified_total',
    'Total number of contracts verified',
    ['tier', 'status']
)

contract_violations_total = Counter(
    'grace_contract_violations_total',
    'Total number of contract violations',
    ['action_type', 'tier']
)

# Rollback Metrics
rollbacks_total = Counter(
    'grace_rollbacks_total',
    'Total number of action rollbacks',
    ['action_type', 'tier', 'reason']
)

rollback_duration_seconds = Histogram(
    'grace_rollback_duration_seconds',
    'Rollback execution duration in seconds',
    ['action_type'],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

# Approval Metrics
approvals_requested_total = Counter(
    'grace_approvals_requested_total',
    'Total number of approvals requested',
    ['tier']
)

approvals_decided_total = Counter(
    'grace_approvals_decided_total',
    'Total number of approval decisions',
    ['tier', 'decision']
)

approval_latency_seconds = Histogram(
    'grace_approval_latency_seconds',
    'Time from approval request to decision',
    ['tier'],
    buckets=[60, 300, 900, 1800, 3600, 7200, 14400]  # 1min to 4hrs
)

# Benchmark Metrics
benchmarks_run_total = Counter(
    'grace_benchmarks_run_total',
    'Total number of benchmarks run',
    ['benchmark_type', 'passed']
)

benchmark_score = Gauge(
    'grace_benchmark_score',
    'Latest benchmark score',
    ['benchmark_type']
)

benchmark_duration_seconds = Histogram(
    'grace_benchmark_duration_seconds',
    'Benchmark execution duration in seconds',
    ['benchmark_type'],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0]
)

# Confidence Metrics
action_confidence = Gauge(
    'grace_action_confidence',
    'Confidence score for planned actions',
    ['action_type']
)

playbook_success_rate = Gauge(
    'grace_playbook_success_rate',
    'Success rate for playbooks',
    ['playbook_id']
)

# Mission Metrics
missions_active = Gauge(
    'grace_missions_active',
    'Number of active missions'
)

missions_completed_total = Counter(
    'grace_missions_completed_total',
    'Total number of missions completed',
    ['status']
)

mission_progress = Gauge(
    'grace_mission_progress',
    'Mission progress percentage',
    ['mission_id']
)

# Job Queue Metrics
jobs_enqueued_total = Counter(
    'grace_jobs_enqueued_total',
    'Total number of jobs enqueued',
    ['job_type']
)

jobs_completed_total = Counter(
    'grace_jobs_completed_total',
    'Total number of jobs completed',
    ['job_type', 'status']
)

jobs_pending = Gauge(
    'grace_jobs_pending',
    'Number of pending jobs',
    ['job_type']
)

job_duration_seconds = Histogram(
    'grace_job_duration_seconds',
    'Job execution duration in seconds',
    ['job_type'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)


# ============================================================================
# Structured Logging Helpers
# ============================================================================

class ObservabilityContext:
    """
    Context manager for structured logging with correlation IDs.
    
    Usage:
        with ObservabilityContext(
            correlation_id="req-123",
            contract_id=456,
            mission_id="mission-789"
        ) as ctx:
            ctx.log("action_started", action_type="restart_service")
    """
    
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        contract_id: Optional[int] = None,
        mission_id: Optional[str] = None,
        action_id: Optional[str] = None,
        **extra_context
    ):
        self.correlation_id = correlation_id
        self.contract_id = contract_id
        self.mission_id = mission_id
        self.action_id = action_id
        self.extra_context = extra_context
        self.logger = logger.bind(
            correlation_id=correlation_id,
            contract_id=contract_id,
            mission_id=mission_id,
            action_id=action_id,
            **extra_context
        )
        self.start_time = time.time()
    
    def log(
        self,
        event: str,
        level: str = "info",
        **kwargs
    ):
        """Log a structured event"""
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(event, **kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            self.log("context_failed", level="error", duration=duration, error=str(exc_val))
        else:
            self.log("context_completed", duration=duration)


# ============================================================================
# Event Tracking Functions
# ============================================================================

def track_action_execution(
    action_type: str,
    tier: str,
    status: str,
    duration_seconds: float,
    correlation_id: Optional[str] = None,
    contract_id: Optional[int] = None,
    mission_id: Optional[str] = None
):
    """Track action execution with metrics and logs"""
    
    # Increment counter
    actions_executed_total.labels(
        action_type=action_type,
        tier=tier,
        status=status
    ).inc()
    
    # Record duration
    action_duration_seconds.labels(
        action_type=action_type,
        tier=tier
    ).observe(duration_seconds)
    
    # Structured log
    logger.info(
        "action_executed",
        action_type=action_type,
        tier=tier,
        status=status,
        duration_seconds=duration_seconds,
        correlation_id=correlation_id,
        contract_id=contract_id,
        mission_id=mission_id
    )


def track_contract_verification(
    contract_id: int,
    tier: str,
    status: str,
    action_type: str,
    verified: bool,
    violations: Optional[list] = None
):
    """Track contract verification with metrics and logs"""
    
    contracts_verified_total.labels(
        tier=tier,
        status=status
    ).inc()
    
    if violations:
        contract_violations_total.labels(
            action_type=action_type,
            tier=tier
        ).inc(len(violations))
    
    logger.info(
        "contract_verified",
        contract_id=contract_id,
        tier=tier,
        status=status,
        action_type=action_type,
        verified=verified,
        violation_count=len(violations) if violations else 0
    )


def track_rollback(
    action_type: str,
    tier: str,
    reason: str,
    duration_seconds: float,
    contract_id: Optional[int] = None
):
    """Track action rollback with metrics and logs"""
    
    rollbacks_total.labels(
        action_type=action_type,
        tier=tier,
        reason=reason
    ).inc()
    
    rollback_duration_seconds.labels(
        action_type=action_type
    ).observe(duration_seconds)
    
    logger.warning(
        "action_rolled_back",
        action_type=action_type,
        tier=tier,
        reason=reason,
        duration_seconds=duration_seconds,
        contract_id=contract_id
    )


def track_approval(
    tier: str,
    decision: Optional[str] = None,
    latency_seconds: Optional[float] = None,
    approval_id: Optional[int] = None
):
    """Track approval request/decision with metrics and logs"""
    
    if decision is None:
        # Approval requested
        approvals_requested_total.labels(tier=tier).inc()
        logger.info("approval_requested", tier=tier, approval_id=approval_id)
    else:
        # Approval decided
        approvals_decided_total.labels(
            tier=tier,
            decision=decision
        ).inc()
        
        if latency_seconds:
            approval_latency_seconds.labels(tier=tier).observe(latency_seconds)
        
        logger.info(
            "approval_decided",
            tier=tier,
            decision=decision,
            latency_seconds=latency_seconds,
            approval_id=approval_id
        )


def track_benchmark(
    benchmark_type: str,
    passed: bool,
    score: float,
    duration_seconds: float,
    contract_id: Optional[int] = None
):
    """Track benchmark execution with metrics and logs"""
    
    benchmarks_run_total.labels(
        benchmark_type=benchmark_type,
        passed=str(passed).lower()
    ).inc()
    
    benchmark_score.labels(benchmark_type=benchmark_type).set(score)
    
    benchmark_duration_seconds.labels(
        benchmark_type=benchmark_type
    ).observe(duration_seconds)
    
    logger.info(
        "benchmark_executed",
        benchmark_type=benchmark_type,
        passed=passed,
        score=score,
        duration_seconds=duration_seconds,
        contract_id=contract_id
    )


def track_confidence(action_type: str, confidence: float):
    """Track action confidence score"""
    action_confidence.labels(action_type=action_type).set(confidence)


def track_playbook_success_rate(playbook_id: str, success_rate: float):
    """Track playbook success rate"""
    playbook_success_rate.labels(playbook_id=playbook_id).set(success_rate)


def track_mission(
    mission_id: str,
    status: Optional[str] = None,
    progress: Optional[float] = None
):
    """Track mission status and progress"""
    
    if status == "active":
        missions_active.inc()
    elif status in ["completed", "failed", "cancelled"]:
        missions_active.dec()
        missions_completed_total.labels(status=status).inc()
    
    if progress is not None:
        mission_progress.labels(mission_id=mission_id).set(progress)


def track_job(
    job_type: str,
    status: str,
    duration_seconds: Optional[float] = None,
    job_id: Optional[str] = None
):
    """Track background job execution"""
    
    if status == "enqueued":
        jobs_enqueued_total.labels(job_type=job_type).inc()
        jobs_pending.labels(job_type=job_type).inc()
    
    elif status in ["completed", "failed", "cancelled"]:
        jobs_completed_total.labels(
            job_type=job_type,
            status=status
        ).inc()
        jobs_pending.labels(job_type=job_type).dec()
        
        if duration_seconds:
            job_duration_seconds.labels(job_type=job_type).observe(duration_seconds)
    
    logger.info(
        "job_tracked",
        job_type=job_type,
        status=status,
        duration_seconds=duration_seconds,
        job_id=job_id
    )
