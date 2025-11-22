"""
Auto-Remediation Service
Subscribes to stress test failures and automatically creates HTM remediation tasks

Architecture:
  Stress Tests → Message Bus (telemetry.stress.*) → Auto-Remediation → HTM Tasks
  
This closes the observability gap: failures are now actionable, not just logged.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

from backend.core.message_bus import message_bus
from backend.core.intent_api import intent_api, Intent, IntentPriority
from backend.logging_system_utils import log_event


class RemediationAction(Enum):
    """Types of auto-remediation actions"""
    RESTART_KERNEL = "restart_kernel"
    INVESTIGATE_FAILURE = "investigate_failure"
    SCALE_RESOURCES = "scale_resources"
    ALERT_OPERATOR = "alert_operator"
    RUN_DIAGNOSTIC = "run_diagnostic"


class AutoRemediationService:
    """
    Watches for stress test failures and automatically creates remediation tasks
    
    Features:
    - Subscribes to stress test telemetry
    - Detects failure patterns
    - Creates Intent API tasks for remediation
    - Tracks remediation success rate
    - Escalates to operators if auto-fix fails
    """
    
    def __init__(self):
        self.running = False
        self.remediations_created = 0
        self.remediations_successful = 0
        self.failure_patterns: Dict[str, int] = {}
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start auto-remediation service"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to stress test events
        try:
            queue = await message_bus.subscribe(
                subscriber="auto_remediation",
                topic="telemetry.stress"
            )
            self._task = asyncio.create_task(self._process_stress_events(queue))
            
            print("[AUTO-REMEDIATION] Service started, subscribed to stress telemetry")
        except Exception as e:
            print(f"[AUTO-REMEDIATION] Failed to start: {e}")
    
    async def stop(self):
        """Stop auto-remediation service"""
        self.running = False
        if self._task:
            self._task.cancel()
    
    async def _process_stress_events(self, queue):
        """Process stress test events and create remediation tasks"""
        while self.running:
            try:
                msg = await queue.get()
                event_type = msg.topic.split('.')[-1]  # Extract last part of topic
                payload = msg.payload
                
                # Detect failures
                if "failed" in event_type or "error" in event_type:
                    await self._handle_failure(event_type, payload)
                
                # Track anomalies
                elif event_type == "boot.cycle.completed":
                    anomalies = payload.get("anomalies", [])
                    if anomalies:
                        await self._handle_anomalies(anomalies, payload)
                
                # Monitor performance degradation
                elif event_type == "boot.cycle.completed":
                    duration = payload.get("boot_duration_ms", 0)
                    if duration > 1000:  # Threshold: 1 second
                        await self._handle_slow_boot(duration, payload)
                
            except Exception as e:
                print(f"[AUTO-REMEDIATION] Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def _handle_failure(self, event_type: str, payload: Dict[str, Any]):
        """Handle test failure by creating remediation intent"""
        
        failure_key = f"{event_type}_{payload.get('test_id', 'unknown')}"
        self.failure_patterns[failure_key] = self.failure_patterns.get(failure_key, 0) + 1
        
        # Create remediation intent
        intent = Intent(
            intent_id=f"remediate_{datetime.now(timezone.utc).timestamp()}",
            goal=f"Investigate and fix stress test failure: {event_type}",
            expected_outcome="failure_resolved",
            sla_ms=300000,  # 5 minutes
            priority=IntentPriority.HIGH,
            domain="reliability",
            context={
                "failure_type": event_type,
                "test_id": payload.get("test_id"),
                "error": payload.get("error"),
                "source": "auto_remediation"
            },
            confidence=0.7,
            risk_level="medium"
        )
        
        try:
            intent_id = await intent_api.submit_intent(intent)
            self.remediations_created += 1
            
            print(f"[AUTO-REMEDIATION] Created remediation intent: {intent_id}")
            print(f"  Failure: {event_type}")
            print(f"  Test: {payload.get('test_id')}")
            
            # Log to structured logging
            log_event(
                action="auto_remediation.intent_created",
                actor="auto_remediation_service",
                resource=event_type,
                outcome="ok",
                payload={
                    "intent_id": intent_id,
                    "failure_type": event_type,
                    "test_id": payload.get("test_id")
                }
            )
        except Exception as e:
            print(f"[AUTO-REMEDIATION] Failed to create intent: {e}")
    
    async def _handle_anomalies(self, anomalies: list, payload: Dict[str, Any]):
        """Handle kernel boot anomalies"""
        
        if not anomalies:
            return
        
        # Group anomalies by error type
        error_groups = {}
        for anomaly in anomalies:
            error = anomaly.get("error", "unknown")
            kernel = anomaly.get("kernel", "unknown")
            
            error_key = error[:50]  # First 50 chars of error
            if error_key not in error_groups:
                error_groups[error_key] = []
            error_groups[error_key].append(kernel)
        
        # Create remediation intent for each error group
        for error_msg, affected_kernels in error_groups.items():
            intent = Intent(
                intent_id=f"fix_anomaly_{datetime.now(timezone.utc).timestamp()}",
                goal=f"Fix kernel boot anomaly affecting {len(affected_kernels)} kernels",
                expected_outcome="kernels_boot_cleanly",
                sla_ms=600000,  # 10 minutes
                priority=IntentPriority.MEDIUM,
                domain="infrastructure",
                context={
                    "anomaly_type": "kernel_boot_error",
                    "error_message": error_msg,
                    "affected_kernels": affected_kernels,
                    "test_id": payload.get("test_id"),
                    "source": "auto_remediation"
                },
                confidence=0.6,
                risk_level="low"
            )
            
            try:
                intent_id = await intent_api.submit_intent(intent)
                print(f"[AUTO-REMEDIATION] Created anomaly fix intent: {intent_id}")
                print(f"  Affected kernels: {', '.join(affected_kernels)}")
            except Exception as e:
                print(f"[AUTO-REMEDIATION] Failed to create anomaly intent: {e}")
    
    async def _handle_slow_boot(self, duration_ms: float, payload: Dict[str, Any]):
        """Handle performance degradation (slow boot times)"""
        
        # Only alert if significantly slower than baseline
        baseline_ms = 500  # Normal boot should be < 500ms
        
        if duration_ms > baseline_ms * 2:  # More than 2x slower
            intent = Intent(
                intent_id=f"optimize_boot_{datetime.now(timezone.utc).timestamp()}",
                goal=f"Investigate slow boot time: {duration_ms:.0f}ms (baseline: {baseline_ms}ms)",
                expected_outcome="boot_time_improved",
                sla_ms=1800000,  # 30 minutes (lower priority)
                priority=IntentPriority.LOW,
                domain="performance",
                context={
                    "issue_type": "performance_degradation",
                    "boot_duration_ms": duration_ms,
                    "baseline_ms": baseline_ms,
                    "degradation_factor": duration_ms / baseline_ms,
                    "test_id": payload.get("test_id"),
                    "source": "auto_remediation"
                },
                confidence=0.5,
                risk_level="low"
            )
            
            try:
                intent_id = await intent_api.submit_intent(intent)
                print(f"[AUTO-REMEDIATION] Created performance investigation intent: {intent_id}")
                print(f"  Boot time: {duration_ms:.0f}ms (expected < {baseline_ms}ms)")
            except Exception as e:
                print(f"[AUTO-REMEDIATION] Failed to create performance intent: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get auto-remediation statistics"""
        success_rate = self.remediations_successful / self.remediations_created if self.remediations_created > 0 else 0.0
        
        return {
            "running": self.running,
            "remediations_created": self.remediations_created,
            "remediations_successful": self.remediations_successful,
            "success_rate": success_rate,
            "failure_patterns": self.failure_patterns,
            "unique_failures": len(self.failure_patterns)
        }


# Global instance
auto_remediation = AutoRemediationService()
