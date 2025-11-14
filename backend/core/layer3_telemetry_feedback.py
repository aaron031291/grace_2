"""
Layer 3: Telemetry & Learning Feedback
Continuous metrics/logs/traces feeding HTM and Agentic Brain

Powers:
- "After each run" learning
- Anomaly detection
- Hunter diagnostics
- Self-healing decisions
- Performance optimization

Collects:
- Metrics (latency, throughput, error rates)
- Logs (structured events)
- Traces (execution paths)
- Resource usage (CPU, RAM, disk, network)
- Quality scores (trust, chunks, outcomes)

Feeds to:
- Agentic Brain: For intent adjustment
- HTM: For priority decisions
- Hunter: For diagnostics
- Self-Healing: For playbook selection
- Governance: For policy enforcement
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque, defaultdict
from pathlib import Path
import json
import psutil

from backend.core.message_bus import message_bus, MessagePriority


class MetricSnapshot:
    """Point-in-time metrics snapshot"""
    
    def __init__(self):
        self.timestamp = datetime.utcnow()
        
        # System metrics
        self.cpu_percent = 0.0
        self.memory_percent = 0.0
        self.disk_percent = 0.0
        self.network_io_mbps = 0.0
        
        # Application metrics
        self.ingestion_queue_depth = 0
        self.ingestion_throughput = 0.0
        self.ingestion_success_rate = 0.0
        self.average_chunk_quality = 0.0
        
        # HTM metrics
        self.htm_queue_depths = {}
        self.htm_latency_ms = 0.0
        self.sla_compliance_rate = 0.0
        
        # Quality metrics
        self.trust_scores = []
        self.error_rate = 0.0
        self.anomaly_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "system": {
                "cpu_percent": self.cpu_percent,
                "memory_percent": self.memory_percent,
                "disk_percent": self.disk_percent,
                "network_io_mbps": self.network_io_mbps
            },
            "application": {
                "ingestion_queue": self.ingestion_queue_depth,
                "throughput": self.ingestion_throughput,
                "success_rate": self.ingestion_success_rate,
                "avg_quality": self.average_chunk_quality
            },
            "htm": {
                "queues": self.htm_queue_depths,
                "latency_ms": self.htm_latency_ms,
                "sla_compliance": self.sla_compliance_rate
            },
            "quality": {
                "avg_trust": sum(self.trust_scores) / len(self.trust_scores) if self.trust_scores else 0.0,
                "error_rate": self.error_rate,
                "anomalies": self.anomaly_count
            }
        }


class LearningFeedback:
    """Learning feedback aggregator"""
    
    def __init__(self):
        self.outcomes = deque(maxlen=1000)
        self.patterns = defaultdict(list)  # pattern_type -> instances
        self.insights = []
    
    def record_outcome(
        self,
        task_type: str,
        success: bool,
        metrics: Dict[str, Any]
    ):
        """Record task outcome"""
        
        outcome = {
            "task_type": task_type,
            "success": success,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.outcomes.append(outcome)
        
        # Detect patterns
        self._detect_patterns(outcome)
    
    def _detect_patterns(self, outcome: Dict[str, Any]):
        """Detect patterns in outcomes"""
        
        # Success patterns
        if outcome["success"]:
            pattern_key = f"success_{outcome['task_type']}"
            self.patterns[pattern_key].append(outcome)
        
        # Failure patterns
        else:
            pattern_key = f"failure_{outcome['task_type']}"
            self.patterns[pattern_key].append(outcome)
        
        # Quality patterns
        if outcome["metrics"].get("quality_score", 0) > 0.8:
            self.patterns["high_quality"].append(outcome)
        elif outcome["metrics"].get("quality_score", 0) < 0.5:
            self.patterns["low_quality"].append(outcome)
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate learning insights"""
        
        insights = []
        
        # Identify high-success patterns
        for pattern_key, instances in self.patterns.items():
            if pattern_key.startswith("success_") and len(instances) >= 5:
                insights.append({
                    "type": "success_pattern",
                    "pattern": pattern_key,
                    "confidence": len(instances) / len(self.outcomes),
                    "recommendation": f"Continue using this workflow for {pattern_key.split('_', 1)[1]}"
                })
        
        # Identify failure patterns
        for pattern_key, instances in self.patterns.items():
            if pattern_key.startswith("failure_") and len(instances) >= 3:
                insights.append({
                    "type": "failure_pattern",
                    "pattern": pattern_key,
                    "risk": "high",
                    "recommendation": f"Investigate failures in {pattern_key.split('_', 1)[1]}"
                })
        
        return insights


class TelemetryCollector:
    """
    Telemetry & Learning Feedback Service
    
    Collects from:
    - Ingestion pipeline (job metrics)
    - HTM (queue metrics, SLA compliance)
    - Kernels (health, heartbeats)
    - System (CPU, RAM, disk, network)
    - Hunter (alerts, diagnostics)
    - Self-healing (playbook outcomes)
    
    Feeds to:
    - Agentic Brain (for intent adjustment)
    - HTM (for priority decisions)
    - Hunter (for diagnostics)
    - Self-Healing (for playbook selection)
    """
    
    def __init__(self):
        self.snapshots = deque(maxlen=1000)
        self.current_snapshot = MetricSnapshot()
        self.learning_feedback = LearningFeedback()
        
        # Collectors
        self._system_collector: Optional[asyncio.Task] = None
        self._application_collector: Optional[asyncio.Task] = None
        self._learning_collector: Optional[asyncio.Task] = None
        
        # Feed publishers
        self._brain_feeder: Optional[asyncio.Task] = None
        self._htm_feeder: Optional[asyncio.Task] = None
        self._hunter_feeder: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start telemetry collection"""
        
        print("="*70)
        print("TELEMETRY & LEARNING FEEDBACK - Starting")
        print("="*70)
        
        # Start collectors
        self._system_collector = asyncio.create_task(self._collect_system_metrics())
        self._application_collector = asyncio.create_task(self._collect_application_metrics())
        self._learning_collector = asyncio.create_task(self._collect_learning_feedback())
        
        # Start feeders
        self._brain_feeder = asyncio.create_task(self._feed_to_brain())
        self._htm_feeder = asyncio.create_task(self._feed_to_htm())
        self._hunter_feeder = asyncio.create_task(self._feed_to_hunter())
        
        print("[TELEMETRY] Collectors: system, application, learning")
        print("[TELEMETRY] Feeders: brain, HTM, Hunter")
        print("="*70)
    
    async def _collect_system_metrics(self):
        """Collect system resource metrics"""
        
        while True:
            try:
                await asyncio.sleep(5)  # Collect every 5 seconds
                
                self.current_snapshot.cpu_percent = psutil.cpu_percent(interval=1)
                self.current_snapshot.memory_percent = psutil.virtual_memory().percent
                self.current_snapshot.disk_percent = psutil.disk_usage('/').percent
                
                # Network I/O
                net_io = psutil.net_io_counters()
                # Calculate approximate Mbps (simplified)
                self.current_snapshot.network_io_mbps = (net_io.bytes_sent + net_io.bytes_recv) / 1_000_000
                
                self.current_snapshot.timestamp = datetime.utcnow()
            
            except Exception as e:
                print(f"[TELEMETRY] System metrics error: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-level metrics"""
        
        while True:
            try:
                await asyncio.sleep(10)  # Collect every 10 seconds
                
                # Get ingestion metrics
                try:
                    from backend.core.enhanced_ingestion_pipeline import enhanced_ingestion_pipeline
                    stats = enhanced_ingestion_pipeline.get_stats()
                    
                    self.current_snapshot.ingestion_queue_depth = stats.get("active_jobs", 0)
                    
                    # Calculate throughput (jobs per minute)
                    if len(self.snapshots) > 0:
                        prev = self.snapshots[-1]
                        time_delta = (datetime.utcnow() - prev.timestamp).total_seconds() / 60
                        jobs_delta = stats.get("jobs_processed", 0)
                        self.current_snapshot.ingestion_throughput = jobs_delta / time_delta if time_delta > 0 else 0
                except:
                    pass
                
                # Get HTM metrics
                try:
                    from backend.core.enhanced_htm import enhanced_htm
                    htm_status = enhanced_htm.get_status()
                    
                    self.current_snapshot.htm_queue_depths = htm_status.get("queue_sizes", {})
                    
                    # Calculate SLA compliance
                    stats = htm_status.get("statistics", {})
                    total_tasks = stats.get("tasks_completed", 0) + stats.get("tasks_failed", 0)
                    breaches = stats.get("sla_breaches", 0)
                    self.current_snapshot.sla_compliance_rate = (total_tasks - breaches) / max(total_tasks, 1)
                except:
                    pass
                
                # Store snapshot
                self.snapshots.append(self.current_snapshot)
            
            except Exception as e:
                print(f"[TELEMETRY] Application metrics error: {e}")
    
    async def _collect_learning_feedback(self):
        """Collect learning feedback from task outcomes"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="telemetry_learning",
                topic="task.completed"
            )
            
            while True:
                msg = await queue.get()
                
                task_data = msg.payload
                
                self.learning_feedback.record_outcome(
                    task_type=task_data.get("task_type", "unknown"),
                    success=task_data.get("result", {}).get("status") == "success",
                    metrics={
                        "duration": task_data.get("duration_seconds", 0),
                        "quality_score": task_data.get("quality_score", 0.0),
                        "trust_score": task_data.get("trust_score", 0.0)
                    }
                )
        
        except Exception as e:
            print(f"[TELEMETRY] Learning collection error: {e}")
    
    async def _feed_to_brain(self):
        """Feed telemetry to Agentic Brain"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Feed every 30 seconds
                
                # Generate insights
                insights = self.learning_feedback.generate_insights()
                
                # Publish to brain
                await message_bus.publish(
                    source="telemetry",
                    topic="brain.telemetry.feed",
                    payload={
                        "snapshot": self.current_snapshot.to_dict(),
                        "insights": insights,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=MessagePriority.NORMAL
                )
            
            except Exception as e:
                print(f"[TELEMETRY] Brain feed error: {e}")
    
    async def _feed_to_htm(self):
        """Feed resource metrics to HTM for throttling decisions"""
        
        while True:
            try:
                await asyncio.sleep(5)  # Feed every 5 seconds
                
                await message_bus.publish(
                    source="telemetry",
                    topic="htm.resource.metrics",
                    payload={
                        "cpu_percent": self.current_snapshot.cpu_percent,
                        "memory_percent": self.current_snapshot.memory_percent,
                        "queue_depths": self.current_snapshot.htm_queue_depths,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    priority=MessagePriority.NORMAL
                )
            
            except Exception as e:
                print(f"[TELEMETRY] HTM feed error: {e}")
    
    async def _feed_to_hunter(self):
        """Feed anomaly data to Hunter"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Feed every minute
                
                # Detect anomalies
                anomalies = self._detect_anomalies()
                
                if anomalies:
                    await message_bus.publish(
                        source="telemetry",
                        topic="hunter.anomaly.detected",
                        payload={
                            "anomalies": anomalies,
                            "snapshot": self.current_snapshot.to_dict(),
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        priority=MessagePriority.HIGH
                    )
            
            except Exception as e:
                print(f"[TELEMETRY] Hunter feed error: {e}")
    
    def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in telemetry"""
        
        anomalies = []
        
        # High CPU
        if self.current_snapshot.cpu_percent > 90:
            anomalies.append({
                "type": "high_cpu",
                "value": self.current_snapshot.cpu_percent,
                "threshold": 90,
                "severity": "high"
            })
        
        # High memory
        if self.current_snapshot.memory_percent > 85:
            anomalies.append({
                "type": "high_memory",
                "value": self.current_snapshot.memory_percent,
                "threshold": 85,
                "severity": "high"
            })
        
        # Low SLA compliance
        if self.current_snapshot.sla_compliance_rate < 0.9:
            anomalies.append({
                "type": "sla_compliance_low",
                "value": self.current_snapshot.sla_compliance_rate,
                "threshold": 0.9,
                "severity": "medium"
            })
        
        return anomalies
    
    def get_status(self) -> Dict[str, Any]:
        """Get telemetry status"""
        return {
            "snapshots_collected": len(self.snapshots),
            "current_snapshot": self.current_snapshot.to_dict(),
            "learning_outcomes": len(self.learning_feedback.outcomes),
            "patterns_detected": len(self.learning_feedback.patterns),
            "insights_generated": len(self.learning_feedback.generate_insights())
        }


class Layer3Service:
    """
    Layer 3 Complete Service
    Context Memory + Telemetry + Learning Feedback
    
    The foundation layer that all other layers depend on.
    """
    
    def __init__(self):
        self.context_memory = None
        self.telemetry = TelemetryCollector()
    
    async def start(self):
        """Start Layer 3 services"""
        
        print()
        print("="*70)
        print("LAYER 3 - STARTING FOUNDATION SERVICES")
        print("="*70)
        print()
        
        # Import and start context memory
        from backend.core.layer3_context_memory import context_memory_service
        self.context_memory = context_memory_service
        
        print("[LAYER 3] Starting Context Memory & Provenance...")
        await self.context_memory.start()
        
        print("[LAYER 3] Starting Telemetry & Learning Feedback...")
        await self.telemetry.start()
        
        print()
        print("="*70)
        print("[LAYER 3] Foundation services operational")
        print("[LAYER 3] Context Memory: Tracking all W's")
        print("[LAYER 3] Telemetry: Feeding brain, HTM, Hunter")
        print("="*70)
        print()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Layer 3 status"""
        return {
            "context_memory": self.context_memory.get_status() if self.context_memory else {},
            "telemetry": self.telemetry.get_status()
        }


# Global instance
layer3_service = Layer3Service()
