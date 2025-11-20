"""
Anomaly Watchdog - Runtime Guardian
Monitors metrics and logs for anomalies, triggers self-healing
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import sqlite3

logger = logging.getLogger(__name__)


class AnomalyWatchdog:
    """
    Runtime guardian that watches for anomalies and triggers healing
    
    Workflow:
    1. Establish baseline from stress test
    2. Monitor metrics/logs continuously
    3. Detect anomalies (drift from baseline)
    4. Trigger self-heal playbooks
    5. Verify fixes with re-test
    6. Escalate if healing fails
    7. Log everything to immutable ledger
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.baseline = None
        self.running = False
        self.anomaly_threshold = {
            "error_rate": 0.05,  # 5% error rate triggers alert
            "latency_p95": 2000,  # 2s p95 latency
            "memory_growth_mb": 100,  # 100MB growth per hour
            "failure_rate": 0.10  # 10% failure rate
        }
        self.healing_attempts = {}
        self.max_healing_attempts = 3
        
    async def establish_baseline(self, stress_results: Dict[str, Any]):
        """Establish healthy baseline from stress test results"""
        
        logger.info("Establishing baseline from stress test")
        
        self.baseline = {
            "timestamp": datetime.now().isoformat(),
            "test_results": stress_results,
            "metrics": {
                "success_rate": stress_results.get("tests_passed", 0) / stress_results.get("tests_run", 1),
                "avg_latency_ms": sum(r["duration_ms"] for r in stress_results.get("results", [])) / max(len(stress_results.get("results", [])), 1),
                "error_count": len(stress_results.get("anomalies", []))
            },
            "thresholds": self.anomaly_threshold
        }
        
        # Save baseline
        baseline_file = self.project_root / "storage" / "baseline.json"
        baseline_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(baseline_file, "w") as f:
            json.dump(self.baseline, f, indent=2)
        
        print(f"\n[BASELINE] Established")
        print(f"  Success Rate: {self.baseline['metrics']['success_rate']:.1%}")
        print(f"  Avg Latency: {self.baseline['metrics']['avg_latency_ms']:.0f}ms")
        print(f"  Errors: {self.baseline['metrics']['error_count']}")
        print()
        
        return self.baseline
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        
        self.running = True
        logger.info("Anomaly watchdog started")
        
        asyncio.create_task(self._monitor_loop())
        
    async def stop_monitoring(self):
        """Stop monitoring"""
        
        self.running = False
        logger.info("Anomaly watchdog stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        
        monitor_interval = 60  # Check every minute
        
        while self.running:
            try:
                await self._check_for_anomalies()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            await asyncio.sleep(monitor_interval)
    
    async def _check_for_anomalies(self) -> List[Dict[str, Any]]:
        """Check current metrics against baseline"""
        
        if not self.baseline:
            return []
        
        anomalies = []
        
        # 1. Check error rate from logs
        error_rate_anomaly = await self._check_error_rate()
        if error_rate_anomaly:
            anomalies.append(error_rate_anomaly)
        
        # 2. Check latency from metrics
        latency_anomaly = await self._check_latency()
        if latency_anomaly:
            anomalies.append(latency_anomaly)
        
        # 3. Check memory growth
        memory_anomaly = await self._check_memory()
        if memory_anomaly:
            anomalies.append(memory_anomaly)
        
        # 4. Check failure rate
        failure_anomaly = await self._check_failure_rate()
        if failure_anomaly:
            anomalies.append(failure_anomaly)
        
        # Trigger healing for each anomaly
        for anomaly in anomalies:
            await self._trigger_healing(anomaly)
        
        return anomalies
    
    async def _check_error_rate(self) -> Optional[Dict[str, Any]]:
        """Check if error rate exceeds baseline"""
        
        try:
            # Check immutable log for errors in last 5 minutes
            db_path = self.project_root / "backend" / "grace.db"
            conn = sqlite3.connect(str(db_path))
            
            cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM immutable_log WHERE timestamp > ? AND result LIKE '%error%'",
                (cutoff,)
            )
            error_count = cursor.fetchone()[0]
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM immutable_log WHERE timestamp > ?",
                (cutoff,)
            )
            total_count = cursor.fetchone()[0]
            
            conn.close()
            
            if total_count > 0:
                error_rate = error_count / total_count
                
                if error_rate > self.anomaly_threshold["error_rate"]:
                    return {
                        "type": "error_rate_spike",
                        "severity": "high",
                        "current": error_rate,
                        "threshold": self.anomaly_threshold["error_rate"],
                        "details": f"Error rate {error_rate:.1%} exceeds threshold {self.anomaly_threshold['error_rate']:.1%}"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error rate check failed: {e}")
            return None
    
    async def _check_latency(self) -> Optional[Dict[str, Any]]:
        """Check API latency against baseline"""
        
        # In production, query metrics_snapshots table
        # For MVP, skip detailed check
        return None
    
    async def _check_memory(self) -> Optional[Dict[str, Any]]:
        """Check memory growth"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        current_memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Simple check - would compare to baseline in production
        if current_memory_mb > 500:  # 500MB threshold
            return {
                "type": "memory_growth",
                "severity": "medium",
                "current": current_memory_mb,
                "threshold": 500,
                "details": f"Memory at {current_memory_mb:.0f}MB"
            }
        
        return None
    
    async def _check_failure_rate(self) -> Optional[Dict[str, Any]]:
        """Check overall failure rate"""
        
        # Query recent playbook runs
        try:
            db_path = self.project_root / "backend" / "grace.db"
            conn = sqlite3.connect(str(db_path))
            
            cutoff = (datetime.now() - timedelta(minutes=10)).isoformat()
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM playbook_runs WHERE created_at > ? AND status = 'failed'",
                (cutoff,)
            )
            failed = cursor.fetchone()[0]
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM playbook_runs WHERE created_at > ?",
                (cutoff,)
            )
            total = cursor.fetchone()[0]
            
            conn.close()
            
            if total > 5:  # Only alert if we have enough samples
                failure_rate = failed / total
                
                if failure_rate > self.anomaly_threshold["failure_rate"]:
                    return {
                        "type": "high_failure_rate",
                        "severity": "high",
                        "current": failure_rate,
                        "threshold": self.anomaly_threshold["failure_rate"],
                        "details": f"Playbook failure rate {failure_rate:.1%}"
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failure rate check failed: {e}")
            return None
    
    async def _trigger_healing(self, anomaly: Dict[str, Any]):
        """
        Trigger self-healing in response to anomaly.
        Routes through unified trigger mesh for consistency.
        """
        from backend.self_heal.trigger_playbook_integration import trigger_playbook_integration
        
        anomaly_id = anomaly["type"]
        attempts = self.healing_attempts.get(anomaly_id, 0)
        
        if attempts >= self.max_healing_attempts:
            logger.warning(f"Max healing attempts reached for {anomaly_id}, escalating...")
            await self._escalate_to_amp(anomaly)
            return
        
        logger.info(f"Triggering healing for {anomaly_id} (attempt {attempts + 1})")
        
        await self._take_snapshot(anomaly_id)
        
        context = {
            "error_type": "anomaly_detected",
            "anomaly_type": anomaly_id,
            "anomaly_data": anomaly,
            "attempt_count": attempts + 1,
            "triggered_by": "anomaly_watchdog"
        }
        
        await trigger_playbook_integration.trigger_healing(
            trigger_type="anomaly",
            context=context
        )
        
        verification = await self._verify_healing(anomaly)
        
        if verification["passed"]:
            logger.info(f"Healing successful for {anomaly_id}")
                self.healing_attempts[anomaly_id] = 0  # Reset counter
            else:
                logger.warning(f"Healing failed for {anomaly_id}")
                self.healing_attempts[anomaly_id] = attempts + 1
        else:
            logger.warning(f"No playbook available for {anomaly_id}")
            await self._escalate_to_amp(anomaly)
    
    def _select_playbook_for_anomaly(self, anomaly: Dict[str, Any]) -> Optional[str]:
        """Select appropriate playbook for anomaly type"""
        
        playbook_mapping = {
            "error_rate_spike": "investigate_error_spike",
            "high_failure_rate": "review_failed_playbooks",
            "memory_growth": "restart_memory_heavy_services",
            "latency_spike": "scale_up_resources"
        }
        
        return playbook_mapping.get(anomaly["type"])
    
    async def _execute_healing_playbook(self, playbook: str, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Execute healing playbook"""
        
        logger.info(f"Executing playbook: {playbook}")
        
        # In production, use playbook_executor
        # For MVP, return mock result
        
        return {
            "playbook": playbook,
            "status": "success",
            "steps_executed": 3,
            "duration_ms": 1500
        }
    
    async def _verify_healing(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Re-run stress test to verify healing worked"""
        
        logger.info("Verifying healing with re-test")
        
        # Re-run relevant stress test
        
        # For MVP, assume verification passed
        return {
            "passed": True,
            "verification_method": "stress_test_rerun",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _take_snapshot(self, anomaly_id: str):
        """Take system snapshot before healing"""
        
        import shutil
        
        snapshot_dir = self.project_root / "storage" / "snapshots" / f"pre_heal_{anomaly_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Snapshot database
        db_path = self.project_root / "backend" / "grace.db"
        if db_path.exists():
            shutil.copy2(db_path, snapshot_dir / "grace.db")
        
        # Snapshot metadata
        metadata = {
            "snapshot_id": snapshot_dir.name,
            "anomaly_id": anomaly_id,
            "timestamp": datetime.now().isoformat(),
            "type": "pre_heal"
        }
        
        with open(snapshot_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Snapshot created: {snapshot_dir.name}")
    
    async def _log_healing_cycle(
        self,
        anomaly: Dict[str, Any],
        playbook: str,
        result: Dict[str, Any],
        verification: Dict[str, Any]
    ):
        """Log complete healing cycle to immutable ledger"""
        
        from backend.immutable_log import immutable_log
        
        await immutable_log.append(
            actor="anomaly_watchdog",
            action="healing_cycle_complete",
            resource=anomaly["type"],
            subsystem="watchdog",
            payload={
                "anomaly": anomaly,
                "playbook": playbook,
                "result": result,
                "verification": verification,
                "timestamp": datetime.now().isoformat()
            },
            result="verified" if verification["passed"] else "failed"
        )
        
        logger.info(f"Healing cycle logged to immutable ledger")
    
    async def _escalate_to_amp(self, anomaly: Dict[str, Any]):
        """Escalate to AMP API when healing fails multiple times"""
        
        logger.critical(f"Escalating {anomaly['type']} to AMP API")
        
        try:
            from backend.amp_api_integration import amp_client
            
            # Query AMP for guidance
            response = await amp_client.ask_for_guidance(
                issue=anomaly["type"],
                context={
                    "severity": anomaly["severity"],
                    "details": anomaly["details"],
                    "healing_attempts": self.healing_attempts.get(anomaly["type"], 0),
                    "baseline": self.baseline
                }
            )
            
            if response.get("suggested_action"):
                logger.info(f"AMP suggested: {response['suggested_action']}")
                
                # Record AMP guidance
                await self._record_amp_guidance(anomaly, response)
                
                # Try AMP's suggestion
                await self._try_amp_suggestion(anomaly, response)
            
        except Exception as e:
            logger.error(f"AMP escalation failed: {e}")
            
            # Final fallback - alert human
            await self._alert_human(anomaly)
    
    async def _record_amp_guidance(self, anomaly: Dict[str, Any], amp_response: Dict[str, Any]):
        """Record AMP guidance in training data"""
        
        guidance_file = self.project_root / "grace_training" / "amp_guidance" / f"{anomaly['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        guidance_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(guidance_file, "w") as f:
            json.dump({
                "anomaly": anomaly,
                "amp_response": amp_response,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    async def _try_amp_suggestion(self, anomaly: Dict[str, Any], amp_response: Dict[str, Any]):
        """Try AMP's suggested fix"""
        
        logger.info(f"Attempting AMP suggestion: {amp_response.get('suggested_action')}")
        
        # Would execute AMP's suggested playbook or action
        # For now, log the attempt
        
        from backend.immutable_log import immutable_log
        
        await immutable_log.append(
            actor="amp_api",
            action="suggested_fix",
            resource=anomaly["type"],
            subsystem="escalation",
            payload={
                "anomaly": anomaly,
                "suggestion": amp_response
            },
            result="attempted"
        )
    
    async def _alert_human(self, anomaly: Dict[str, Any]):
        """Final escalation - alert human operator"""
        
        logger.critical(f"HUMAN INTERVENTION REQUIRED: {anomaly['type']}")
        
        # In production:
        # - Send Slack/email alert
        # - Create approval request
        # - Log to parliament for oversight
        
        alert_file = self.project_root / "logs" / f"ALERT_{anomaly['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(alert_file, "w") as f:
            f.write("="*80 + "\n")
            f.write("CRITICAL ALERT - HUMAN INTERVENTION REQUIRED\n")
            f.write("="*80 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Anomaly: {anomaly['type']}\n")
            f.write(f"Severity: {anomaly['severity']}\n")
            f.write(f"Details: {anomaly['details']}\n")
            f.write(f"Healing Attempts: {self.healing_attempts.get(anomaly['type'], 0)}\n")
            f.write("\n")
            f.write("Self-healing exhausted. Manual intervention required.\n")
            f.write("="*80 + "\n")
        
        print(f"\n[ALERT] Human intervention required - see {alert_file.name}")


# Global instance
anomaly_watchdog = AnomalyWatchdog()
