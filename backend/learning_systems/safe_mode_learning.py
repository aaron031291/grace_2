"""
Safe Mode Learning - Retry/Backoff & CI Safety
Implements retry/backoff policies, safe mode for CI, rollback on failure, and learning simulation
"""

import asyncio
import logging
import os
import random
from typing import Dict, Any, List, Optional, Tuple, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Learning mode states"""
    NORMAL = "normal"          # Full learning with external access
    SAFE = "safe"             # Limited learning, no external access
    SIMULATION = "simulation" # Mock learning for testing
    DISABLED = "disabled"     # Learning completely disabled


class FailureType(Enum):
    """Types of learning failures"""
    NETWORK_ERROR = "network_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT = "rate_limit"
    CONTENT_ERROR = "content_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_factor: float = 2.0
    jitter: bool = True

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        if attempt <= 1:
            return 0.0

        delay = min(self.base_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)

        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0.0, delay)


@dataclass
class LearningOperation:
    """Learning operation with retry tracking"""
    operation_id: str
    operation_type: str  # 'web_search', 'content_fetch', 'knowledge_update', etc.
    target: str  # URL, query, etc.
    status: str = "pending"  # pending, running, completed, failed, retrying
    attempts: int = 0
    max_attempts: int = 3
    last_attempt_at: Optional[str] = None
    next_attempt_at: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

    def record_attempt(self, error: Optional[str] = None):
        """Record an attempt"""
        self.attempts += 1
        self.last_attempt_at = datetime.utcnow().isoformat()

        if error:
            self.errors.append(error)
            if self.attempts < self.max_attempts:
                self.status = "retrying"
            else:
                self.status = "failed"
        else:
            self.status = "completed"
            self.completed_at = datetime.utcnow().isoformat()

    def should_retry(self) -> bool:
        """Check if operation should be retried"""
        return self.attempts < self.max_attempts and self.status != "completed"

    def get_next_retry_delay(self, retry_policy: RetryPolicy) -> float:
        """Get delay until next retry"""
        return retry_policy.get_delay(self.attempts + 1)


class SafeModeLearningManager:
    """
    Manages safe mode learning with retry policies, CI safety, and rollback capabilities
    """

    def __init__(self):
        self.learning_mode = self._determine_learning_mode()
        self.retry_policy = RetryPolicy()
        self.operations: Dict[str, LearningOperation] = {}
        self.rollback_snapshots: Dict[str, Dict[str, Any]] = {}

        # Failure tracking
        self.failure_counts: Dict[str, int] = {}
        self.consecutive_failures = 0
        self.last_success_at: Optional[str] = None

        # Circuit breaker
        self.circuit_breaker_enabled = False
        self.circuit_failure_threshold = 5
        self.circuit_recovery_timeout = 300  # 5 minutes

        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "retried_operations": 0,
            "rollbacks_performed": 0,
            "circuit_breaker_trips": 0
        }

    def _determine_learning_mode(self) -> LearningMode:
        """Determine current learning mode based on environment"""
        # Check environment variables
        offline_mode = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        ci_mode = os.getenv("CI", "false").lower() == "true"
        safe_mode = os.getenv("SAFE_MODE", "false").lower() == "true"
        simulation_mode = os.getenv("SIMULATION_MODE", "false").lower() == "true"

        if simulation_mode:
            return LearningMode.SIMULATION
        elif ci_mode or offline_mode or safe_mode:
            return LearningMode.SAFE
        elif os.getenv("DISABLE_LEARNING", "false").lower() == "true":
            return LearningMode.DISABLED
        else:
            return LearningMode.NORMAL

    def is_safe_mode(self) -> bool:
        """Check if system is in safe mode"""
        return self.learning_mode in [LearningMode.SAFE, LearningMode.SIMULATION, LearningMode.DISABLED]

    def can_perform_operation(self, operation_type: str) -> Tuple[bool, str]:
        """
        Check if operation can be performed in current mode

        Returns:
            (allowed, reason)
        """
        if self.learning_mode == LearningMode.DISABLED:
            return False, "Learning is disabled"

        if self.learning_mode == LearningMode.SAFE:
            # In safe mode, only allow certain operations
            safe_operations = ["knowledge_query", "local_processing", "simulation"]
            if operation_type not in safe_operations:
                return False, f"Operation '{operation_type}' not allowed in safe mode"

        if self.learning_mode == LearningMode.SIMULATION:
            # In simulation mode, only allow mock operations
            if not operation_type.startswith("sim_"):
                return False, f"Only simulation operations allowed, got '{operation_type}'"

        # Check circuit breaker
        if self.circuit_breaker_enabled:
            return False, "Circuit breaker is open due to excessive failures"

        return True, ""

    async def execute_with_retry(self, operation_func: Callable[[], Awaitable[Any]],
                               operation_type: str, target: str,
                               operation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute operation with retry logic

        Args:
            operation_func: Async function to execute
            operation_type: Type of operation
            target: Operation target (URL, query, etc.)
            operation_id: Optional operation ID

        Returns:
            Execution result
        """
        if operation_id is None:
            operation_id = f"op_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(operation_type + target) % 10000}"

        # Create operation record
        operation = LearningOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            target=target,
            max_attempts=self.retry_policy.max_attempts
        )
        self.operations[operation_id] = operation
        self.stats["total_operations"] += 1

        result = {
            "operation_id": operation_id,
            "success": False,
            "attempts": 0,
            "error": None,
            "data": None,
            "mode": self.learning_mode.value
        }

        # Check if operation is allowed
        allowed, reason = self.can_perform_operation(operation_type)
        if not allowed:
            operation.record_attempt(f"Operation not allowed: {reason}")
            result["error"] = reason
            self.stats["failed_operations"] += 1
            return result

        # Execute with retries
        while operation.should_retry():
            try:
                operation.status = "running"

                # Create rollback snapshot before operation
                await self._create_rollback_snapshot(operation_id)

                # Execute operation
                if self.learning_mode == LearningMode.SIMULATION:
                    data = await self._simulate_operation(operation_type, target)
                else:
                    data = await operation_func()

                # Success
                operation.record_attempt()
                result["success"] = True
                result["data"] = data
                result["attempts"] = operation.attempts

                self.stats["successful_operations"] += 1
                self.consecutive_failures = 0
                self.last_success_at = datetime.utcnow().isoformat()

                # Clean up rollback snapshot
                await self._cleanup_rollback_snapshot(operation_id)

                break

            except Exception as e:
                error_msg = str(e)
                operation.record_attempt(error_msg)

                result["attempts"] = operation.attempts
                result["error"] = error_msg

                # Check if we should retry
                if operation.should_retry():
                    delay = operation.get_next_retry_delay(self.retry_policy)
                    operation.next_attempt_at = (datetime.utcnow() + timedelta(seconds=delay)).isoformat()

                    logger.info(f"[SAFE-MODE] Retrying operation {operation_id} in {delay:.1f}s (attempt {operation.attempts}/{operation.max_attempts})")
                    await asyncio.sleep(delay)
                else:
                    # Failed after all retries
                    await self._handle_operation_failure(operation, error_msg)
                    break

        # Log final result
        await immutable_log.append(
            actor="safe_mode_learning",
            action="operation_executed",
            resource=operation_id,
            outcome="success" if result["success"] else "failed",
            payload={
                "operation_type": operation_type,
                "attempts": result["attempts"],
                "mode": self.learning_mode.value,
                "error": result["error"]
            }
        )

        return result

    async def _simulate_operation(self, operation_type: str, target: str) -> Dict[str, Any]:
        """Simulate operation for testing/safe mode"""
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Return mock data based on operation type
        if operation_type == "sim_web_search":
            return {
                "query": target,
                "results": [
                    {
                        "title": f"Mock result {i+1} for '{target}'",
                        "url": f"https://example.com/result{i+1}",
                        "snippet": f"This is simulated content about {target}..."
                    } for i in range(3)
                ],
                "simulated": True
            }

        elif operation_type == "sim_content_fetch":
            return {
                "url": target,
                "content": f"Simulated content from {target}",
                "title": f"Mock page from {target}",
                "simulated": True
            }

        else:
            return {"message": f"Simulated {operation_type} for {target}", "simulated": True}

    async def _create_rollback_snapshot(self, operation_id: str):
        """Create rollback snapshot before operation"""
        # This would snapshot relevant system state
        # For now, just store operation metadata
        self.rollback_snapshots[operation_id] = {
            "operation_id": operation_id,
            "created_at": datetime.utcnow().isoformat(),
            "system_state": {
                "learning_mode": self.learning_mode.value,
                "consecutive_failures": self.consecutive_failures,
                "circuit_breaker_enabled": self.circuit_breaker_enabled
            }
        }

    async def _cleanup_rollback_snapshot(self, operation_id: str):
        """Clean up rollback snapshot after successful operation"""
        if operation_id in self.rollback_snapshots:
            del self.rollback_snapshots[operation_id]

    async def _handle_operation_failure(self, operation: LearningOperation, error: str):
        """Handle operation failure"""
        self.stats["failed_operations"] += 1
        self.consecutive_failures += 1

        # Update failure counts
        failure_type = self._classify_failure(error)
        self.failure_counts[failure_type] = self.failure_counts.get(failure_type, 0) + 1

        # Check circuit breaker
        if self.consecutive_failures >= self.circuit_failure_threshold:
            self.circuit_breaker_enabled = True
            self.stats["circuit_breaker_trips"] += 1

            logger.warning(f"[SAFE-MODE] Circuit breaker activated after {self.consecutive_failures} consecutive failures")

            # Schedule circuit breaker recovery
            asyncio.create_task(self._recover_circuit_breaker())

        # Attempt rollback if snapshot exists
        if operation.operation_id in self.rollback_snapshots:
            await self._perform_rollback(operation.operation_id)
            self.stats["rollbacks_performed"] += 1

    async def _recover_circuit_breaker(self):
        """Recover circuit breaker after timeout"""
        await asyncio.sleep(self.circuit_recovery_timeout)

        # Check if we've had recent success
        if self.last_success_at:
            last_success = datetime.fromisoformat(self.last_success_at)
            time_since_success = (datetime.utcnow() - last_success).total_seconds()

            if time_since_success < self.circuit_recovery_timeout:
                self.circuit_breaker_enabled = False
                self.consecutive_failures = 0
                logger.info("[SAFE-MODE] Circuit breaker recovered")
            else:
                # Schedule another check
                asyncio.create_task(self._recover_circuit_breaker())
        else:
            # No recent success, keep circuit breaker active
            asyncio.create_task(self._recover_circuit_breaker())

    async def _perform_rollback(self, operation_id: str):
        """Perform rollback to pre-operation state"""
        if operation_id not in self.rollback_snapshots:
            return

        snapshot = self.rollback_snapshots[operation_id]

        # Restore system state
        system_state = snapshot["system_state"]
        self.learning_mode = LearningMode(system_state["learning_mode"])
        self.consecutive_failures = system_state["consecutive_failures"]
        self.circuit_breaker_enabled = system_state["circuit_breaker_enabled"]

        logger.info(f"[SAFE-MODE] Rolled back operation {operation_id}")

        # Clean up snapshot
        del self.rollback_snapshots[operation_id]

    def _classify_failure(self, error: str) -> str:
        """Classify failure type from error message"""
        error_lower = error.lower()

        if "network" in error_lower or "connection" in error_lower:
            return FailureType.NETWORK_ERROR.value
        elif "timeout" in error_lower:
            return FailureType.TIMEOUT.value
        elif "rate limit" in error_lower or "429" in error_lower:
            return FailureType.RATE_LIMIT.value
        elif "parse" in error_lower or "html" in error_lower:
            return FailureType.PARSING_ERROR.value
        elif "validation" in error_lower:
            return FailureType.VALIDATION_ERROR.value
        elif "content" in error_lower:
            return FailureType.CONTENT_ERROR.value
        else:
            return FailureType.UNKNOWN.value

    def set_learning_mode(self, mode: LearningMode):
        """Set learning mode"""
        old_mode = self.learning_mode
        self.learning_mode = mode

        logger.info(f"[SAFE-MODE] Learning mode changed: {old_mode.value} -> {mode.value}")

        # Log mode change
        asyncio.create_task(immutable_log.append(
            actor="safe_mode_learning",
            action="mode_changed",
            resource="learning_system",
            outcome="changed",
            payload={"old_mode": old_mode.value, "new_mode": mode.value}
        ))

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "learning_mode": self.learning_mode.value,
            "safe_mode_active": self.is_safe_mode(),
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
            "consecutive_failures": self.consecutive_failures,
            "last_success_at": self.last_success_at,
            "failure_counts": self.failure_counts,
            "active_operations": len([op for op in self.operations.values() if op.status in ["running", "retrying"]]),
            "pending_rollbacks": len(self.rollback_snapshots),
            "stats": self.stats
        }

    def get_operation_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation status"""
        operation = self.operations.get(operation_id)
        return operation.__dict__ if operation else None

    def force_recovery(self):
        """Force system recovery (admin function)"""
        self.circuit_breaker_enabled = False
        self.consecutive_failures = 0
        self.failure_counts.clear()
        self.rollback_snapshots.clear()

        logger.warning("[SAFE-MODE] Forced system recovery initiated")

        # Log recovery
        asyncio.create_task(immutable_log.append(
            actor="safe_mode_learning",
            action="forced_recovery",
            resource="learning_system",
            outcome="recovered",
            payload={"reason": "admin_forced"}
        ))


class LearningSimulationFramework:
    """
    Framework for simulating learning operations in safe/test environments
    """

    def __init__(self):
        self.simulations: Dict[str, Dict[str, Any]] = {}
        self.simulation_stats = {
            "total_simulations": 0,
            "successful_simulations": 0,
            "failed_simulations": 0,
            "simulation_types": {}
        }

    async def run_simulation(self, simulation_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a learning simulation

        Args:
            simulation_type: Type of simulation to run
            parameters: Simulation parameters

        Returns:
            Simulation results
        """
        simulation_id = f"sim_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(parameters)) % 10000}"

        self.simulations[simulation_id] = {
            "simulation_id": simulation_id,
            "type": simulation_type,
            "parameters": parameters,
            "started_at": datetime.utcnow().isoformat(),
            "status": "running"
        }

        self.simulation_stats["total_simulations"] += 1
        self.simulation_stats["simulation_types"][simulation_type] = \
            self.simulation_stats["simulation_types"].get(simulation_type, 0) + 1

        try:
            # Run simulation based on type
            if simulation_type == "web_learning":
                result = await self._simulate_web_learning(parameters)
            elif simulation_type == "knowledge_update":
                result = await self._simulate_knowledge_update(parameters)
            elif simulation_type == "gap_detection":
                result = await self._simulate_gap_detection(parameters)
            else:
                result = {"error": f"Unknown simulation type: {simulation_type}"}

            # Mark as successful
            self.simulations[simulation_id]["status"] = "completed"
            self.simulations[simulation_id]["completed_at"] = datetime.utcnow().isoformat()
            self.simulations[simulation_id]["result"] = result
            self.simulation_stats["successful_simulations"] += 1

            return {
                "simulation_id": simulation_id,
                "success": True,
                "result": result
            }

        except Exception as e:
            # Mark as failed
            self.simulations[simulation_id]["status"] = "failed"
            self.simulations[simulation_id]["error"] = str(e)
            self.simulations[simulation_id]["completed_at"] = datetime.utcnow().isoformat()
            self.simulation_stats["failed_simulations"] += 1

            return {
                "simulation_id": simulation_id,
                "success": False,
                "error": str(e)
            }

    async def _simulate_web_learning(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate web learning operation"""
        query = parameters.get("query", "test query")
        num_results = parameters.get("num_results", 3)

        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 2.0))

        return {
            "query": query,
            "results": [
                {
                    "title": f"Simulated result {i+1}",
                    "url": f"https://example.com/sim{i+1}",
                    "content": f"Simulated content about {query} result {i+1}",
                    "relevance_score": random.uniform(0.5, 0.9)
                } for i in range(num_results)
            ],
            "processing_time": random.uniform(0.5, 2.0),
            "simulated": True
        }

    async def _simulate_knowledge_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate knowledge update operation"""
        concept = parameters.get("concept", "test_concept")
        content = parameters.get("content", "test content")

        # Simulate processing time
        await asyncio.sleep(random.uniform(0.2, 1.0))

        return {
            "concept": concept,
            "updated": True,
            "trust_score": random.uniform(0.7, 0.95),
            "confidence": random.uniform(0.8, 0.98),
            "simulated": True
        }

    async def _simulate_gap_detection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate gap detection operation"""
        query = parameters.get("query", "test query")

        # Simulate processing time
        await asyncio.sleep(random.uniform(0.1, 0.5))

        gaps = []
        if random.random() > 0.5:  # 50% chance of finding gaps
            gaps = [
                {
                    "gap_type": "missing_concept",
                    "concept": f"simulated_gap_{random.randint(1, 10)}",
                    "description": f"Gap detected in response to: {query}",
                    "priority_score": random.uniform(0.3, 0.9)
                }
            ]

        return {
            "query": query,
            "gaps_found": len(gaps),
            "gaps": gaps,
            "simulated": True
        }

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        return self.simulation_stats

    def get_simulation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent simulation history"""
        simulations = list(self.simulations.values())
        simulations.sort(key=lambda x: x.get("started_at", ""), reverse=True)
        return simulations[:limit]


# Global instances
safe_mode_learning_manager = SafeModeLearningManager()
learning_simulation_framework = LearningSimulationFramework()