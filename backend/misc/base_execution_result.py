"""
Standardized ExecutionResult Model

Normalizes outcome payloads across all executors:
- Real executors (self_heal/real_executors.py)
- Action executor
- Playbook runners
- Mission executors

Consistent fields for serialization to immutable log, contracts, and analytics.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum


class ExecutionStatus(Enum):
    """Standard execution outcome statuses"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    ROLLED_BACK = "rolled_back"
    PENDING = "pending"
    TIMEOUT = "timeout"


@dataclass
class ExecutionResult:
    """
    Standardized execution result across all action executors.
    
    Use this for all execution outcomes to maintain consistency.
    """
    
    # Core outcome
    status: ExecutionStatus
    ok: bool  # Simple boolean for quick checks
    
    # Result data
    result: Optional[Any] = None
    error: Optional[str] = None
    error_resolved: bool = False
    
    # Metrics
    metrics: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    
    # Verification
    contract_id: Optional[int] = None
    verified: bool = False
    verification_score: Optional[float] = None
    
    # Context
    action_type: Optional[str] = None
    action_id: Optional[str] = None
    mission_id: Optional[str] = None
    triggered_by: Optional[str] = None
    tier: Optional[str] = None
    
    # Audit trail
    executed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enum to string
        data["status"] = self.status.value
        # Convert datetime to ISO format
        if self.executed_at:
            data["executed_at"] = self.executed_at.isoformat()
        return data
    
    def to_immutable_log_payload(self) -> Dict[str, Any]:
        """Format for immutable log persistence"""
        return {
            "status": self.status.value,
            "ok": self.ok,
            "error_resolved": self.error_resolved,
            "result": self.result,
            "error": self.error,
            "metrics": self.metrics or {},
            "duration_ms": self.duration_ms,
            "contract_id": self.contract_id,
            "verified": self.verified,
            "verification_score": self.verification_score,
            "action_type": self.action_type,
            "mission_id": self.mission_id,
            "tier": self.tier
        }
    
    def to_contract_outcome(self) -> Dict[str, Any]:
        """Format for action contract actual_outcome field"""
        return {
            "status": self.status.value,
            "success": self.ok,
            "error_resolved": self.error_resolved,
            "metrics": self.metrics or {},
            "duration_ms": self.duration_ms,
            "result_summary": self._get_summary(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None
        }
    
    def _get_summary(self) -> str:
        """Generate human-readable summary"""
        if self.ok:
            return f"{self.action_type or 'Action'} completed successfully"
        elif self.error_resolved:
            return f"{self.action_type or 'Action'} resolved issue despite errors"
        else:
            return f"{self.action_type or 'Action'} failed: {self.error or 'Unknown error'}"
    
    @classmethod
    def success(
        cls,
        result: Any = None,
        action_type: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "ExecutionResult":
        """Create a successful execution result"""
        return cls(
            status=ExecutionStatus.SUCCESS,
            ok=True,
            result=result,
            action_type=action_type,
            metrics=metrics,
            executed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    def failure(
        cls,
        error: str,
        action_type: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "ExecutionResult":
        """Create a failed execution result"""
        return cls(
            status=ExecutionStatus.FAILED,
            ok=False,
            error=error,
            action_type=action_type,
            metrics=metrics,
            executed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    def partial(
        cls,
        result: Any = None,
        error: Optional[str] = None,
        action_type: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "ExecutionResult":
        """Create a partial success execution result"""
        return cls(
            status=ExecutionStatus.PARTIAL,
            ok=False,
            result=result,
            error=error,
            action_type=action_type,
            metrics=metrics,
            executed_at=datetime.now(timezone.utc),
            **kwargs
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        """Create from dictionary"""
        # Handle status enum
        if isinstance(data.get("status"), str):
            data["status"] = ExecutionStatus(data["status"])
        
        # Handle datetime
        if isinstance(data.get("executed_at"), str):
            data["executed_at"] = datetime.fromisoformat(data["executed_at"])
        
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def normalize_executor_result(raw_result: Any, action_type: str) -> ExecutionResult:
    """
    Normalize various executor result formats into ExecutionResult.
    
    Handles:
    - Dict with {"ok": bool, "status": str, ...}
    - Dict with {"success": bool, ...}
    - Simple boolean
    - Exception objects
    """
    
    if isinstance(raw_result, ExecutionResult):
        return raw_result
    
    if isinstance(raw_result, dict):
        ok = raw_result.get("ok", raw_result.get("success", False))
        status_str = raw_result.get("status", "success" if ok else "failed")
        
        try:
            status = ExecutionStatus(status_str)
        except ValueError:
            status = ExecutionStatus.SUCCESS if ok else ExecutionStatus.FAILED
        
        return ExecutionResult(
            status=status,
            ok=ok,
            result=raw_result.get("result"),
            error=raw_result.get("error"),
            error_resolved=raw_result.get("error_resolved", False),
            metrics=raw_result.get("metrics"),
            duration_ms=raw_result.get("duration_ms"),
            action_type=action_type,
            executed_at=datetime.now(timezone.utc)
        )
    
    if isinstance(raw_result, bool):
        return ExecutionResult.success() if raw_result else ExecutionResult.failure("Execution returned False")
    
    if isinstance(raw_result, Exception):
        return ExecutionResult.failure(str(raw_result), action_type=action_type)
    
    # Default: treat as success with result
    return ExecutionResult.success(result=raw_result, action_type=action_type)
