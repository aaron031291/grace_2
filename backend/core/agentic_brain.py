"""
Agentic Brain - Grace's Intent & Evaluation Core
Top-tier reasoning system that sets goals and learns from outcomes

Responsibilities:
- Set ingestion goals based on priorities
- Read telemetry from all systems
- Create/update HTM tasks with outcomes and deadlines
- Review HTM outcomes to learn best pipelines
- Adjust future intent based on results
- Conduct retrospectives

Integration:
- Reads: Telemetry from ingestion, Hunter, watchdog, kernels
- Writes: Tasks to HTM with intent and SLAs
- Learns: Which pipelines/processors deliver best signal
- Decides: What work matters and why

Three-Tier Architecture:
1. Agentic Brain (this) - Intent + Evaluation
2. HTM - Priority + Orchestration
3. Ingestion/Kernels - Execution + Feedback
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from enum import Enum

from backend.core.message_bus import message_bus, MessagePriority


class Intent(str, Enum):
    """Agentic intents"""
    INDEX_NEW_DOCUMENTS = "index_new_documents"
    REPROCESS_LOW_QUALITY = "reprocess_low_quality"
    AUDIT_EXTERNAL_FEEDS = "audit_external_feeds"
    IMPROVE_TRUST_SCORES = "improve_trust_scores"
    OPTIMIZE_RETRIEVAL = "optimize_retrieval"
    INVESTIGATE_ANOMALIES = "investigate_anomalies"


class TelemetrySnapshot:
    """Snapshot of system telemetry"""
    
    def __init__(self):
        self.timestamp = datetime.utcnow()
        
        # Ingestion metrics
        self.ingestion_queue_depth = 0
        self.ingestion_success_rate = 0.0
        self.average_chunk_quality = 0.0
        
        # Hunter alerts
        self.active_alerts = 0
        self.critical_alerts = 0
        
        # Watchdog status
        self.kernel_health = {}
        self.restart_events = 0
        
        # HTM status
        self.htm_queue_sizes = {}
        self.sla_breaches = 0
        
        # Resource metrics
        self.cpu_percent = 0.0
        self.memory_percent = 0.0


class PipelinePerformance:
    """Track pipeline performance for learning"""
    
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.executions = []
        self.success_count = 0
        self.failure_count = 0
        self.average_quality = 0.0
        self.average_duration = 0.0
    
    def record_execution(self, outcome: Dict[str, Any]):
        """Record pipeline execution"""
        self.executions.append(outcome)
        
        if outcome.get("success"):
            self.success_count += 1
        else:
            self.failure_count += 1
        
        # Update averages
        qualities = [e.get("quality_score", 0.0) for e in self.executions if e.get("quality_score")]
        self.average_quality = sum(qualities) / len(qualities) if qualities else 0.0
        
        durations = [e.get("duration_seconds", 0.0) for e in self.executions]
        self.average_duration = sum(durations) / len(durations) if durations else 0.0
    
    def get_score(self) -> float:
        """Get overall performance score"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5
        
        success_rate = self.success_count / total
        quality_factor = self.average_quality
        speed_factor = 1.0 / (1.0 + self.average_duration / 60)  # Favor faster pipelines
        
        return (success_rate * 0.5 + quality_factor * 0.3 + speed_factor * 0.2)


class AgenticBrain:
    """
    Grace's reasoning core - Intent setting and outcome evaluation
    
    The brain owns:
    - Global intent (why work matters)
    - Goal prioritization
    - Learning from outcomes
    - Retrospectives and adjustments
    - Proactive task generation
    """
    
    def __init__(self):
        # Current intents and goals
        self.active_intents: List[Intent] = []
        self.goals: Dict[str, Dict[str, Any]] = {}
        
        # Telemetry
        self.telemetry_history = deque(maxlen=1000)
        self.current_telemetry = TelemetrySnapshot()
        
        # Learning
        self.pipeline_performance: Dict[str, PipelinePerformance] = {}
        self.outcome_history = deque(maxlen=1000)
        self.retrospectives = []
        
        # Tasks created by brain
        self.tasks_created = 0
        self.tasks_completed = 0
        
        # Monitoring
        self._telemetry_task: Optional[asyncio.Task] = None
        self._evaluation_task: Optional[asyncio.Task] = None
        self._intent_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start agentic brain"""
        
        print("="*70)
        print("AGENTIC BRAIN - Starting Intent & Evaluation Core")
        print("="*70)
        
        # Set initial intents
        self._set_initial_intents()
        
        # Start monitoring loops
        self._telemetry_task = asyncio.create_task(self._collect_telemetry())
        self._evaluation_task = asyncio.create_task(self._evaluate_outcomes())
        self._intent_task = asyncio.create_task(self._execute_intents())
        
        # Subscribe to task completions for learning
        asyncio.create_task(self._learn_from_outcomes())
        
        print("[BRAIN] Agentic brain started")
        print(f"[BRAIN] Active intents: {len(self.active_intents)}")
        print("="*70)
    
    def _set_initial_intents(self):
        """Set initial system intents"""
        
        self.active_intents = [
            Intent.INDEX_NEW_DOCUMENTS,
            Intent.IMPROVE_TRUST_SCORES,
            Intent.INVESTIGATE_ANOMALIES
        ]
        
        # Create goals from intents
        for intent in self.active_intents:
            self.goals[intent.value] = {
                "intent": intent.value,
                "priority": self._intent_priority(intent),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
    
    def _intent_priority(self, intent: Intent) -> str:
        """Map intent to priority"""
        
        priority_map = {
            Intent.INDEX_NEW_DOCUMENTS: "normal",
            Intent.REPROCESS_LOW_QUALITY: "low",
            Intent.AUDIT_EXTERNAL_FEEDS: "normal",
            Intent.IMPROVE_TRUST_SCORES: "high",
            Intent.OPTIMIZE_RETRIEVAL: "low",
            Intent.INVESTIGATE_ANOMALIES: "high"
        }
        
        return priority_map.get(intent, "normal")
    
    async def _collect_telemetry(self):
        """Collect telemetry from all systems"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                
                snapshot = TelemetrySnapshot()
                
                # Get ingestion metrics (would query actual service)
                try:
                    from backend.core.enhanced_ingestion_pipeline import enhanced_ingestion_pipeline
                    stats = enhanced_ingestion_pipeline.get_stats()
                    snapshot.ingestion_queue_depth = stats.get("active_jobs", 0)
                except:
                    pass
                
                # Get HTM status
                try:
                    from backend.core.enhanced_htm import enhanced_htm
                    htm_status = enhanced_htm.get_status()
                    snapshot.htm_queue_sizes = htm_status.get("queue_sizes", {})
                    snapshot.sla_breaches = htm_status.get("statistics", {}).get("sla_breaches", 0)
                except:
                    pass
                
                # Get resource metrics
                try:
                    import psutil
                    snapshot.cpu_percent = psutil.cpu_percent(interval=0.5)
                    snapshot.memory_percent = psutil.virtual_memory().percent
                except:
                    pass
                
                # Store snapshot
                self.current_telemetry = snapshot
                self.telemetry_history.append(snapshot)
                
                # Analyze and adjust intents
                await self._analyze_telemetry(snapshot)
            
            except Exception as e:
                print(f"[BRAIN] Telemetry collection error: {e}")
    
    async def _analyze_telemetry(self, snapshot: TelemetrySnapshot):
        """Analyze telemetry and adjust intents"""
        
        # If queue depth is high, add intent to prioritize critical items
        if snapshot.ingestion_queue_depth > 10:
            if Intent.OPTIMIZE_RETRIEVAL not in self.active_intents:
                self.active_intents.append(Intent.OPTIMIZE_RETRIEVAL)
                print(f"[BRAIN] Added intent: {Intent.OPTIMIZE_RETRIEVAL.value} (queue depth: {snapshot.ingestion_queue_depth})")
        
        # If SLA breaches detected, investigate
        if snapshot.sla_breaches > 0:
            if Intent.INVESTIGATE_ANOMALIES not in self.active_intents:
                self.active_intents.append(Intent.INVESTIGATE_ANOMALIES)
                print(f"[BRAIN] Added intent: {Intent.INVESTIGATE_ANOMALIES.value} (SLA breaches: {snapshot.sla_breaches})")
        
        # If resource stress, defer low-priority work
        if snapshot.cpu_percent > 80:
            print(f"[BRAIN] Resource stress detected (CPU: {snapshot.cpu_percent:.1f}%) - adjusting priorities")
    
    async def _execute_intents(self):
        """Execute active intents by creating HTM tasks"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Execute every minute
                
                for intent in self.active_intents:
                    await self._execute_intent(intent)
            
            except Exception as e:
                print(f"[BRAIN] Intent execution error: {e}")
    
    async def _execute_intent(self, intent: Intent):
        """Execute specific intent"""
        
        if intent == Intent.INDEX_NEW_DOCUMENTS:
            # Check if new documents need indexing
            await self._create_indexing_tasks()
        
        elif intent == Intent.REPROCESS_LOW_QUALITY:
            # Find and reprocess low-quality chunks
            await self._create_reprocess_tasks()
        
        elif intent == Intent.AUDIT_EXTERNAL_FEEDS:
            # Audit external sources
            await self._create_audit_tasks()
        
        elif intent == Intent.IMPROVE_TRUST_SCORES:
            # Review and improve trust scores
            await self._create_trust_improvement_tasks()
    
    async def _create_indexing_tasks(self):
        """Create HTM tasks for indexing new documents"""
        
        # Would query for unindexed files
        # For now, publish intent to HTM
        
        await message_bus.publish(
            source="agentic_brain",
            topic="task.enqueue",
            payload={
                "task_type": "index_new_documents",
                "handler": "librarian",
                "priority": "normal",
                "context": {
                    "intent": Intent.INDEX_NEW_DOCUMENTS.value,
                    "created_by": "agentic_brain",
                    "outcome_desired": "all_new_docs_indexed"
                }
            },
            priority=MessagePriority.NORMAL
        )
        
        self.tasks_created += 1
    
    async def _create_reprocess_tasks(self):
        """Create tasks to reprocess low-quality chunks"""
        
        # Would query for low-quality chunks
        # For now, demonstrate intent publishing
        
        await message_bus.publish(
            source="agentic_brain",
            topic="task.enqueue",
            payload={
                "task_type": "reprocess_low_quality",
                "handler": "librarian",
                "priority": "low",
                "context": {
                    "intent": Intent.REPROCESS_LOW_QUALITY.value,
                    "quality_threshold": 0.6,
                    "playbook": "improve_chunking"
                }
            },
            priority=MessagePriority.LOW
        )
    
    async def _create_audit_tasks(self):
        """Create audit tasks for external feeds"""
        
        await message_bus.publish(
            source="agentic_brain",
            topic="task.enqueue",
            payload={
                "task_type": "audit_external_feeds",
                "handler": "hunter",
                "priority": "high",
                "context": {
                    "intent": Intent.AUDIT_EXTERNAL_FEEDS.value,
                    "sources": ["github", "reddit", "youtube"],
                    "verification_required": True
                }
            },
            priority=MessagePriority.HIGH
        )
    
    async def _create_trust_improvement_tasks(self):
        """Create tasks to improve trust scores"""
        
        # Analyze current trust scores and create improvement tasks
        pass  # Would implement based on telemetry
    
    async def _evaluate_outcomes(self):
        """Evaluate outcomes and adjust strategies"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Review every 5 minutes
                
                # Conduct mini-retrospective
                await self._conduct_retrospective()
            
            except Exception as e:
                print(f"[BRAIN] Evaluation error: {e}")
    
    async def _learn_from_outcomes(self):
        """Learn from HTM task outcomes"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="agentic_brain",
                topic="task.completed"
            )
            
            while True:
                msg = await queue.get()
                await self._process_outcome(msg.payload)
        
        except Exception as e:
            print(f"[BRAIN] Learning error: {e}")
    
    async def _process_outcome(self, task_data: Dict[str, Any]):
        """Process task outcome and learn"""
        
        self.tasks_completed += 1
        
        task_type = task_data.get("task_type")
        handler = task_data.get("handler")
        workflow = task_data.get("workflow", [])
        result = task_data.get("result", {})
        
        # Record outcome
        outcome = {
            "task_type": task_type,
            "handler": handler,
            "workflow": workflow,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.outcome_history.append(outcome)
        
        # Update pipeline performance
        pipeline_key = f"{handler}_{task_type}"
        
        if pipeline_key not in self.pipeline_performance:
            self.pipeline_performance[pipeline_key] = PipelinePerformance(pipeline_key)
        
        self.pipeline_performance[pipeline_key].record_execution({
            "success": result.get("status") == "success",
            "quality_score": result.get("quality_score", 0.0),
            "duration_seconds": result.get("duration_seconds", 0.0)
        })
        
        # Get performance score
        perf = self.pipeline_performance[pipeline_key]
        score = perf.get_score()
        
        if score > 0.8:
            print(f"[BRAIN] Learned: {pipeline_key} performs well (score: {score:.2f})")
        elif score < 0.5:
            print(f"[BRAIN] Warning: {pipeline_key} underperforming (score: {score:.2f})")
    
    async def _conduct_retrospective(self):
        """Conduct retrospective and adjust strategy"""
        
        retro = {
            "timestamp": datetime.utcnow().isoformat(),
            "period": "last_5_minutes",
            "tasks_created": self.tasks_created,
            "tasks_completed": self.tasks_completed,
            "completion_rate": self.tasks_completed / max(self.tasks_created, 1),
            "pipeline_scores": {},
            "adjustments": []
        }
        
        # Review pipeline performance
        for pipeline_name, perf in self.pipeline_performance.items():
            score = perf.get_score()
            retro["pipeline_scores"][pipeline_name] = score
            
            # Make adjustments
            if score > 0.9:
                # Excellent pipeline - use more
                retro["adjustments"].append({
                    "pipeline": pipeline_name,
                    "action": "increase_usage",
                    "reason": f"high_performance_{score:.2f}"
                })
            elif score < 0.4:
                # Poor pipeline - use less or investigate
                retro["adjustments"].append({
                    "pipeline": pipeline_name,
                    "action": "decrease_usage",
                    "reason": f"low_performance_{score:.2f}"
                })
        
        self.retrospectives.append(retro)
        
        if retro["adjustments"]:
            print(f"[BRAIN] Retrospective: {len(retro['adjustments'])} adjustments")
            for adj in retro["adjustments"]:
                print(f"[BRAIN]   - {adj['action']} for {adj['pipeline']}: {adj['reason']}")
    
    def recommend_pipeline(self, task_type: str, handler: str) -> Optional[str]:
        """Recommend best pipeline based on learned performance"""
        
        pipeline_key = f"{handler}_{task_type}"
        
        if pipeline_key in self.pipeline_performance:
            perf = self.pipeline_performance[pipeline_key]
            score = perf.get_score()
            
            if score > 0.7:
                return pipeline_key
        
        # No recommendation or low score
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get brain status"""
        return {
            "active_intents": [i.value for i in self.active_intents],
            "goals": len(self.goals),
            "tasks_created": self.tasks_created,
            "tasks_completed": self.tasks_completed,
            "pipelines_learned": len(self.pipeline_performance),
            "retrospectives_conducted": len(self.retrospectives),
            "telemetry": {
                "ingestion_queue": self.current_telemetry.ingestion_queue_depth,
                "sla_breaches": self.current_telemetry.sla_breaches,
                "cpu_percent": self.current_telemetry.cpu_percent
            }
        }


# Global instance
agentic_brain = AgenticBrain()
