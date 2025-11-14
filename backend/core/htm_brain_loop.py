"""
HTM-Agentic Brain Loop - CLOSED
Finalizes: Intent → HTM → Execution → Feedback → Brain

Flow:
1. Brain reads telemetry, detects drift
2. Brain creates intent task (e.g., "run stress drill")
3. HTM receives, prioritizes, dispatches
4. Execution layer runs stress test or remediation
5. Results feed back to brain
6. Brain learns and adjusts

Use Cases:
- Auto-create stress drills when telemetry flags drift
- Auto-create remediation tasks on quality drops
- Auto-schedule audits on anomalies
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from backend.core.message_bus import message_bus, MessagePriority


class HTMBrainLoop:
    """
    Closes the loop between HTM and Agentic Brain
    
    Enables autonomous:
    - Stress drill creation
    - Remediation task generation
    - Quality improvement cycles
    - Audit scheduling
    """
    
    def __init__(self):
        self._telemetry_monitor: Optional[asyncio.Task] = None
        self._intent_publisher: Optional[asyncio.Task] = None
        
        # Drift detection
        self.baseline_metrics = {
            "boot_time_ms": 200,
            "chunk_quality": 0.85,
            "trust_score": 0.80,
            "sla_compliance": 0.95
        }
        
        self.drift_thresholds = {
            "boot_time_spike": 1.5,      # 50% slower
            "quality_drop": 0.15,         # 15% drop
            "trust_drop": 0.10,           # 10% drop
            "sla_compliance_drop": 0.05   # 5% drop
        }
    
    async def start(self):
        """Start HTM-Brain loop"""
        
        print("[HTM-BRAIN-LOOP] Starting closed loop integration")
        
        # Monitor telemetry for drift
        self._telemetry_monitor = asyncio.create_task(self._monitor_telemetry_for_drift())
        
        # Publish intent to HTM
        self._intent_publisher = asyncio.create_task(self._publish_brain_intent())
        
        print("[HTM-BRAIN-LOOP] Monitoring telemetry for drift detection")
        print("[HTM-BRAIN-LOOP] Auto-creating tasks on anomalies")
    
    async def _monitor_telemetry_for_drift(self):
        """Monitor telemetry and auto-create tasks on drift"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="htm_brain_loop",
                topic="stress.*.completed"
            )
            
            while True:
                msg = await queue.get()
                await self._check_for_drift(msg.payload)
        
        except Exception as e:
            print(f"[HTM-BRAIN-LOOP] Telemetry monitor error: {e}")
    
    async def _check_for_drift(self, test_results: Dict[str, Any]):
        """Check test results for drift and create remediation tasks"""
        
        summary = test_results.get("summary", {})
        
        # Check boot time drift
        avg_boot = summary.get("avg_boot_time", 0)
        if avg_boot > self.baseline_metrics["boot_time_ms"] * self.drift_thresholds["boot_time_spike"]:
            print(f"[HTM-BRAIN-LOOP] DRIFT DETECTED: Boot time {avg_boot:.0f}ms (baseline: {self.baseline_metrics['boot_time_ms']}ms)")
            
            await self._create_remediation_task(
                "boot_performance_degradation",
                {
                    "metric": "boot_time",
                    "current": avg_boot,
                    "baseline": self.baseline_metrics["boot_time_ms"],
                    "action": "run_diagnostics"
                }
            )
        
        # Check quality drift
        avg_quality = summary.get("avg_trust_score", 1.0)
        if avg_quality < self.baseline_metrics["chunk_quality"] - self.drift_thresholds["quality_drop"]:
            print(f"[HTM-BRAIN-LOOP] DRIFT DETECTED: Quality {avg_quality:.2f} (baseline: {self.baseline_metrics['chunk_quality']:.2f})")
            
            await self._create_remediation_task(
                "quality_degradation",
                {
                    "metric": "chunk_quality",
                    "current": avg_quality,
                    "baseline": self.baseline_metrics["chunk_quality"],
                    "action": "reprocess_low_quality"
                }
            )
        
        # Check SLA compliance
        sla_compliance = summary.get("sla_compliance_rate", 1.0)
        if sla_compliance < self.baseline_metrics["sla_compliance"] - self.drift_thresholds["sla_compliance_drop"]:
            print(f"[HTM-BRAIN-LOOP] DRIFT DETECTED: SLA compliance {sla_compliance:.2%}")
            
            await self._create_remediation_task(
                "sla_compliance_issue",
                {
                    "metric": "sla_compliance",
                    "current": sla_compliance,
                    "baseline": self.baseline_metrics["sla_compliance"],
                    "action": "optimize_htm_scheduling"
                }
            )
    
    async def _create_remediation_task(self, issue_type: str, details: Dict[str, Any]):
        """Auto-create remediation task in HTM"""
        
        # Brain publishes intent
        await message_bus.publish(
            source="htm_brain_loop",
            topic="layer3.intent.task",
            payload={
                "intent": "remediate_drift",
                "issue_type": issue_type,
                "details": details,
                "priority": "high",
                "sla_seconds": 3600,  # 1 hour to remediate
                "created_by": "agentic_brain_auto"
            },
            priority=MessagePriority.HIGH
        )
        
        print(f"[HTM-BRAIN-LOOP] Auto-created remediation task: {issue_type}")
    
    async def _publish_brain_intent(self):
        """Publish brain intent to HTM"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Brain evaluates and may create proactive tasks
                # Example: Schedule stress drills during low load
                
                # Get HTM status
                try:
                    from backend.core.enhanced_htm import enhanced_htm
                    htm_status = enhanced_htm.get_status()
                    
                    queue_depth = sum(htm_status.get("queue_sizes", {}).values())
                    
                    # If queue is light, schedule stress drill
                    if queue_depth < 5:
                        await self._schedule_stress_drill()
                
                except:
                    pass
            
            except Exception as e:
                print(f"[HTM-BRAIN-LOOP] Intent publisher error: {e}")
    
    async def _schedule_stress_drill(self):
        """Auto-schedule stress drill during low load"""
        
        await message_bus.publish(
            source="htm_brain_loop",
            topic="layer3.intent.task",
            payload={
                "intent": "proactive_stress_test",
                "task_type": "run_stress_drill",
                "handler": "stress_runner",
                "priority": "low",
                "sla_seconds": 86400,  # 24 hours
                "reasoning": "Queue light, opportunistic stress testing",
                "created_by": "agentic_brain_auto"
            },
            priority=MessagePriority.LOW
        )
        
        print("[HTM-BRAIN-LOOP] Scheduled opportunistic stress drill")


# Global instance
htm_brain_loop = HTMBrainLoop()
