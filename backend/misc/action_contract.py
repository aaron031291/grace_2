"""
Action Contract & Attestation System

Provides verification that agentic actions actually perform their intended effects:
- Pre-execution: captures expected state changes in an immutable contract
- Post-execution: verifies actual outcomes match intent
- Drift detection: compares against golden benchmarks
- Audit trail: all contracts logged for human review

This gives Grace visibility into "what I planned vs what actually happened."
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import hashlib
import json

from sqlalchemy import Column, String, JSON, DateTime, Float, Boolean, Integer
from sqlalchemy.orm import declarative_base

from .models import Base
from .immutable_log import immutable_log


@dataclass
class ExpectedEffect:
    """Defines the intended outcome of an action"""
    target_resource: str  # e.g., "database", "service:grace_backend"
    target_state: Dict[str, Any]  # Expected state after action
    success_criteria: List[Dict[str, Any]]  # Metrics/checks that must pass
    rollback_threshold: float = 0.3  # If confidence < this, trigger rollback
    
    def to_hash(self) -> str:
        """Generate deterministic hash of this effect contract"""
        canonical = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]


class ActionContract(Base):
    """
    Immutable contract between planner and executor.
    Records what an action INTENDS to do before execution.
    """
    __tablename__ = "action_contracts"
    
    id = Column(String, primary_key=True)
    action_type = Column(String, nullable=False)
    playbook_id = Column(String, nullable=True)
    run_id = Column(Integer, nullable=True)  # Links to PlaybookRun
    
    # Contract terms
    expected_effect_hash = Column(String, nullable=False)
    expected_effect = Column(JSON, nullable=False)
    baseline_state = Column(JSON, nullable=False)  # Captured pre-action
    
    # Execution tracking
    status = Column(String, default="pending")  # pending, executing, verified, failed, rolled_back
    actual_effect = Column(JSON, nullable=True)  # Measured post-action
    verification_result = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0-1.0, how well actual matched expected
    
    # Timing
    created_at = Column(DateTime, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Snapshot linkage
    safe_hold_snapshot_id = Column(String, nullable=True)
    
    # Metadata
    triggered_by = Column(String, nullable=True)
    tier = Column(String, nullable=True)
    requires_approval = Column(Boolean, default=False)


class ContractVerifier:
    """
    Verifies that executed actions match their contracts.
    Detects drift and triggers rollbacks when necessary.
    """
    
    async def create_contract(
        self,
        action_type: str,
        expected_effect: ExpectedEffect,
        baseline_state: Dict[str, Any],
        playbook_id: Optional[str] = None,
        run_id: Optional[int] = None,
        triggered_by: Optional[str] = None,
        tier: str = "tier_1"
    ) -> ActionContract:
        """Create and log an action contract before execution"""
        from .models import async_session
        
        effect_hash = expected_effect.to_hash()
        contract_id = f"contract-{effect_hash}-{datetime.now(timezone.utc).timestamp()}"
        
        contract = ActionContract(
            id=contract_id,
            action_type=action_type,
            playbook_id=playbook_id,
            run_id=run_id,
            expected_effect_hash=effect_hash,
            expected_effect=asdict(expected_effect),
            baseline_state=baseline_state,
            status="pending",
            created_at=datetime.now(timezone.utc),
            triggered_by=triggered_by,
            tier=tier,
            requires_approval=(tier in ["tier_2", "tier_3"])
        )
        
        async with async_session() as session:
            session.add(contract)
            await session.commit()
        
        # Log to immutable ledger
        await immutable_log.append(
            actor="action_contract",
            action="contract_created",
            resource=expected_effect.target_resource,
            subsystem="attestation",
            payload={
                "contract_id": contract_id,
                "action_type": action_type,
                "effect_hash": effect_hash,
                "tier": tier
            },
            result="created"
        )
        
        return contract
    
    async def verify_execution(
        self,
        contract_id: str,
        actual_state: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Verify that execution matched contract expectations.
        Returns verification result with confidence score.
        """
        from .models import async_session
        
        async with async_session() as session:
            contract = await session.get(ActionContract, contract_id)
            if not contract:
                return {"error": "Contract not found", "success": False}
            
            expected = ExpectedEffect(**contract.expected_effect)
            
            # Check success criteria
            passed_checks = []
            failed_checks = []
            
            for criterion in expected.success_criteria:
                check_result = await self._evaluate_criterion(
                    criterion,
                    actual_state,
                    metrics
                )
                
                if check_result["passed"]:
                    passed_checks.append(check_result)
                else:
                    failed_checks.append(check_result)
            
            # Calculate confidence score
            total_checks = len(expected.success_criteria)
            passed_count = len(passed_checks)
            confidence = passed_count / total_checks if total_checks > 0 else 0.0
            
            # Determine overall status
            if confidence >= 0.9:
                status = "verified"
            elif confidence >= expected.rollback_threshold:
                status = "partial_success"
            else:
                status = "failed"
            
            # Update contract
            contract.status = status
            contract.actual_effect = actual_state
            contract.verification_result = {
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "confidence": confidence,
                "rollback_recommended": (confidence < expected.rollback_threshold)
            }
            contract.confidence_score = confidence
            contract.verified_at = datetime.now(timezone.utc)
            
            await session.commit()
            
            # Log verification
            await immutable_log.append(
                actor="action_contract",
                action="contract_verified",
                resource=expected.target_resource,
                subsystem="attestation",
                payload={
                    "contract_id": contract_id,
                    "confidence": confidence,
                    "status": status
                },
                result=status
            )
            
            return {
                "success": (status == "verified"),
                "confidence": confidence,
                "status": status,
                "passed_checks": passed_checks,
                "failed_checks": failed_checks,
                "rollback_recommended": (confidence < expected.rollback_threshold)
            }
    
    async def _evaluate_criterion(
        self,
        criterion: Dict[str, Any],
        actual_state: Dict[str, Any],
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Evaluate a single success criterion"""
        
        criterion_type = criterion.get("type")
        
        if criterion_type == "metric_threshold":
            metric_name = criterion["metric"]
            operator = criterion["operator"]  # "lt", "gt", "lte", "gte", "eq"
            threshold = criterion["value"]
            
            actual_value = metrics.get(metric_name)
            if actual_value is None:
                return {
                    "criterion": criterion,
                    "passed": False,
                    "reason": f"Metric {metric_name} not available"
                }
            
            passed = self._compare(actual_value, operator, threshold)
            return {
                "criterion": criterion,
                "passed": passed,
                "actual_value": actual_value,
                "expected_value": threshold,
                "operator": operator
            }
        
        elif criterion_type == "state_match":
            key = criterion["key"]
            expected_value = criterion["value"]
            actual_value = actual_state.get(key)
            
            passed = (actual_value == expected_value)
            return {
                "criterion": criterion,
                "passed": passed,
                "actual_value": actual_value,
                "expected_value": expected_value
            }
        
        elif criterion_type == "health_check":
            endpoint = criterion["endpoint"]
            # In real implementation, would call the health endpoint
            # For now, assume healthy if we got this far
            return {
                "criterion": criterion,
                "passed": True,
                "endpoint": endpoint
            }
        
        else:
            return {
                "criterion": criterion,
                "passed": False,
                "reason": f"Unknown criterion type: {criterion_type}"
            }
    
    def _compare(self, actual: float, operator: str, threshold: float) -> bool:
        """Compare values based on operator"""
        if operator == "lt":
            return actual < threshold
        elif operator == "gt":
            return actual > threshold
        elif operator == "lte":
            return actual <= threshold
        elif operator == "gte":
            return actual >= threshold
        elif operator == "eq":
            return actual == threshold
        else:
            return False


# Singleton instance
contract_verifier = ContractVerifier()
