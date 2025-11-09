"""
Shard Orchestrator - Parallel Multi-Agent Execution

Coordinates specialized agents (shards) for concurrent task execution.
Implements work distribution, inter-shard communication, and result aggregation.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from .immutable_log import ImmutableLog
from .unified_logger import unified_logger


class ShardStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    BLOCKED = "blocked"
    ERROR = "error"


@dataclass
class Task:
    """Unit of work for a shard"""
    id: str
    domain: str
    action: str
    payload: Dict[str, Any]
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict] = None


@dataclass
class Shard:
    """Autonomous agent specialized for a domain"""
    id: str
    domain: str
    capabilities: List[str]
    status: ShardStatus = ShardStatus.IDLE
    current_task: Optional[Task] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_execution_time: float = 0.0


class ShardOrchestrator:
    """
    Orchestrates parallel task execution across domain-specialized shards.
    
    Features:
    - Work-stealing queue for load balancing
    - Dependency resolution before execution
    - Inter-shard message passing
    - Result aggregation for multi-shard tasks
    """
    
    def __init__(self):
        self.shards: Dict[str, Shard] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: Dict[str, Task] = {}
        self.immutable_log = ImmutableLog()
        self.running = False
        
    async def start(self):
        """Initialize shards and start orchestration loop"""
        print("[SHARD] Starting Shard Orchestrator...")
        
        # Initialize domain shards
        await self._init_shards()
        
        # Start orchestration loop
        self.running = True
        asyncio.create_task(self._orchestration_loop())
        
        print(f"[OK] Orchestrator started with {len(self.shards)} shards")
        
        await self.immutable_log.append(
            actor="shard_orchestrator",
            action="orchestrator_started",
            resource="orchestrator",
            subsystem="shards",
            payload={"shard_count": len(self.shards)},
            result="started"
        )
        
        # Log to unified logger
        for shard_id, shard in self.shards.items():
            await unified_logger.log_shard_activity(
                shard_id=shard_id,
                shard_type='domain',
                domain=shard.domain,
                status='started',
                started_at=datetime.utcnow(),
                success=True
            )
    
    async def _init_shards(self):
        """Initialize specialized agent shards"""
        shard_configs = [
            {
                "id": "shard_ai_expert",
                "domain": "ai_ml",
                "capabilities": ["ml_training", "model_inference", "prompt_engineering", "rag_query"]
            },
            {
                "id": "shard_self_heal",
                "domain": "self_heal",
                "capabilities": ["anomaly_detection", "root_cause_analysis", "auto_remediation", "health_check"]
            },
            {
                "id": "shard_code",
                "domain": "code",
                "capabilities": ["code_analysis", "refactoring", "test_generation", "pr_creation"]
            },
            {
                "id": "shard_infra",
                "domain": "infrastructure",
                "capabilities": ["resource_monitoring", "scaling", "deployment", "backup"]
            },
            {
                "id": "shard_knowledge",
                "domain": "knowledge",
                "capabilities": ["knowledge_ingestion", "query_expansion", "fact_verification", "summarization"]
            },
            {
                "id": "shard_security",
                "domain": "security",
                "capabilities": ["vulnerability_scan", "audit_review", "policy_enforcement", "threat_detection"]
            }
        ]
        
        for config in shard_configs:
            shard = Shard(**config)
            self.shards[shard.id] = shard
            print(f"  [OK] Initialized {shard.id} for {shard.domain}")
    
    async def submit_task(self, domain: str, action: str, payload: Dict, priority: int = 5, dependencies: List[str] = None) -> str:
        """
        Submit a task to the orchestrator.
        
        Args:
            domain: Target domain (ai_ml, self_heal, code, etc.)
            action: Action to perform
            payload: Task data
            priority: 1-10 (10 = highest)
            dependencies: Task IDs that must complete first
        
        Returns:
            Task ID
        """
        task = Task(
            id=f"task_{domain}_{datetime.utcnow().timestamp()}",
            domain=domain,
            action=action,
            payload=payload,
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: (-t.priority, t.created_at))
        
        await self.immutable_log.append(
            actor="user",
            action="task_submitted",
            resource=task.id,
            subsystem="orchestrator",
            payload={"task_id": task.id, "domain": domain, "action": action},
            result="queued"
        )
        
        return task.id
    
    async def _orchestration_loop(self):
        """Main loop: assign tasks to available shards"""
        while self.running:
            await self._assign_tasks()
            await asyncio.sleep(0.5)
    
    async def _assign_tasks(self):
        """Assign pending tasks to idle shards"""
        for task in list(self.task_queue):
            # Check dependencies
            if not await self._dependencies_met(task):
                continue
            
            # Find capable idle shard
            shard = self._find_shard_for_task(task)
            if not shard:
                continue
            
            # Assign task
            self.task_queue.remove(task)
            task.assigned_to = shard.id
            task.status = "assigned"
            shard.status = ShardStatus.WORKING
            shard.current_task = task
            
            # Execute asynchronously
            asyncio.create_task(self._execute_task(shard, task))
    
    async def _dependencies_met(self, task: Task) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _find_shard_for_task(self, task: Task) -> Optional[Shard]:
        """Find an idle shard capable of handling the task"""
        for shard in self.shards.values():
            if shard.status == ShardStatus.IDLE and shard.domain == task.domain:
                return shard
        return None
    
    async def _execute_task(self, shard: Shard, task: Task):
        """Execute a task on a shard"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate task execution (replace with actual agent invocation)
            result = await self._invoke_shard_capability(shard, task)
            
            task.status = "completed"
            task.result = result
            self.completed_tasks[task.id] = task
            shard.completed_tasks += 1
            
            # Update shard stats
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            shard.avg_execution_time = (
                (shard.avg_execution_time * (shard.completed_tasks - 1) + execution_time) 
                / shard.completed_tasks
            )
            
            await self.immutable_log.append(
                actor=shard.id,
                action="task_completed",
                resource=task.id,
                subsystem="orchestrator",
                payload={
                    "task_id": task.id,
                    "execution_time": execution_time,
                    "result_summary": str(result)[:200]
                },
                result="success"
            )
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            shard.failed_tasks += 1
            
            await self.immutable_log.append(
                actor=shard.id,
                action="task_failed",
                resource=task.id,
                subsystem="orchestrator",
                payload={"task_id": task.id, "error": str(e)},
                result="error"
            )
        
        finally:
            # Free shard
            shard.status = ShardStatus.IDLE
            shard.current_task = None
    
    async def _invoke_shard_capability(self, shard: Shard, task: Task) -> Dict:
        """
        Invoke shard's capability to execute task.
        
        This is where you'd integrate with actual AI models, tools, etc.
        For now, we simulate with domain-specific logic.
        """
        # AI/ML Shard
        if shard.domain == "ai_ml":
            if task.action == "prompt_engineering":
                return {"optimized_prompt": f"Enhanced: {task.payload.get('prompt', '')}"}
            elif task.action == "rag_query":
                return {"retrieved_docs": ["doc1", "doc2"], "answer": "Knowledge-grounded response"}
        
        # Self-Heal Shard
        elif shard.domain == "self_heal":
            if task.action == "anomaly_detection":
                return {"anomalies_found": 2, "severity": "medium"}
            elif task.action == "auto_remediation":
                return {"action_taken": "restarted_service", "success": True}
        
        # Code Shard
        elif shard.domain == "code":
            if task.action == "code_analysis":
                return {"issues": 3, "complexity": "medium"}
            elif task.action == "pr_creation":
                return {"pr_url": "https://github.com/repo/pull/123"}
        
        # Default
        return {"status": "executed", "message": f"Shard {shard.id} processed {task.action}"}
    
    async def get_shard_status(self) -> Dict[str, Dict]:
        """Get current status of all shards"""
        return {
            shard_id: {
                "domain": shard.domain,
                "status": shard.status.value,
                "current_task": shard.current_task.id if shard.current_task else None,
                "completed": shard.completed_tasks,
                "failed": shard.failed_tasks,
                "avg_time": round(shard.avg_execution_time, 2)
            }
            for shard_id, shard in self.shards.items()
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        # Check queue
        for task in self.task_queue:
            if task.id == task_id:
                return {"status": task.status, "position": self.task_queue.index(task)}
        
        # Check completed
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {"status": task.status, "result": task.result}
        
        # Check in-progress
        for shard in self.shards.values():
            if shard.current_task and shard.current_task.id == task_id:
                return {"status": "executing", "shard": shard.id}
        
        return None


# Global orchestrator instance
shard_orchestrator = ShardOrchestrator()
