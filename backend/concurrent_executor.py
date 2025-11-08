"""
Concurrent Task Executor - Multi-threading for Background Tasks

Enables Grace to:
- Run multiple tasks in parallel
- Execute background operations
- Distribute work across domain adapters
- Coordinate concurrent actions

Uses asyncio for true concurrency with proper resource management.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10


class TaskStatus(Enum):
    """Task execution states"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConcurrentTask:
    """Represents a concurrent task"""
    task_id: str
    domain: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 5
    status: str = "queued"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class ConcurrentExecutor:
    """
    Multi-threaded task executor with work queue.
    
    Features:
    - Priority-based task scheduling
    - Concurrent execution with configurable workers
    - Domain-aware task distribution
    - Background task support
    - Result aggregation
    """
    
    def __init__(self, max_workers: int = 6):
        self.max_workers = max_workers
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, ConcurrentTask] = {}
        self.completed_tasks: Dict[str, ConcurrentTask] = {}
        self.workers: List[asyncio.Task] = []
        self.running = False
        self._seq = 0  # Monotonic counter to break priority ties
        self._max_completed = 1000  # Bound memory
    
    async def start(self):
        """Start worker pool"""
        if self.running:
            return
        
        self.running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        print(f"  [OK] Concurrent executor started ({self.max_workers} workers)")
    
    async def stop(self):
        """Stop worker pool gracefully"""
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        print("  [OK] Concurrent executor stopped")
    
    async def submit_task(
        self,
        domain: str,
        action: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        background: bool = False
    ) -> str:
        """
        Submit task for execution.
        
        Args:
            domain: Domain to execute in (core, knowledge, ml, etc.)
            action: Action to perform
            parameters: Action parameters
            priority: Task priority (1-10)
            background: If True, don't wait for completion
        
        Returns:
            task_id for tracking
        """
        
        task_id = f"{domain}-{action}-{datetime.now(timezone.utc).timestamp()}"
        
        task = ConcurrentTask(
            task_id=task_id,
            domain=domain,
            action=action,
            parameters=parameters,
            priority=priority
        )
        
        # Add to queue (negative priority for max-heap, sequence for tie-breaking)
        self._seq += 1
        await self.task_queue.put((-priority, self._seq, task))
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="concurrent.task.queued",
            source="concurrent_executor",
            actor="executor",
            resource=task_id,
            payload={
                "domain": domain,
                "action": action,
                "priority": priority,
                "background": background
            },
            timestamp=datetime.now(timezone.utc)
        ))
        
        # If not background, wait for completion
        if not background:
            return await self.wait_for_task(task_id)
        else:
            return task_id
    
    async def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        wait_for_all: bool = True
    ) -> List[str]:
        """
        Submit multiple tasks for parallel execution.
        
        Args:
            tasks: List of task specs (domain, action, parameters)
            wait_for_all: Wait for all tasks to complete
        
        Returns:
            List of task_ids
        """
        
        task_ids = []
        
        for task_spec in tasks:
            task_id = await self.submit_task(
                domain=task_spec["domain"],
                action=task_spec["action"],
                parameters=task_spec.get("parameters", {}),
                priority=task_spec.get("priority", 5),
                background=(not wait_for_all)
            )
            task_ids.append(task_id)
        
        if wait_for_all:
            # Wait for all tasks
            await asyncio.gather(*[
                self.wait_for_task(tid) for tid in task_ids
            ], return_exceptions=True)
        
        return task_ids
    
    async def wait_for_task(self, task_id: str, timeout: float = 300.0) -> str:
        """Wait for task to complete (with timeout)"""
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if completed
            if task_id in self.completed_tasks:
                return task_id
            
            # Check timeout
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
            
            # Wait a bit
            await asyncio.sleep(0.1)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {**asdict(task), "created_at": task.created_at.isoformat()}
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {**asdict(task), "created_at": task.created_at.isoformat()}
        
        return None
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        
        return {
            "queued_tasks": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "workers": self.max_workers,
            "running": self.running
        }
    
    async def _worker(self, worker_id: str):
        """Worker loop - processes tasks from queue"""
        
        print(f"  [OK] Worker {worker_id} started")
        
        while self.running:
            try:
                # Get next task (with timeout to check running flag)
                try:
                    priority, seq, task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Mark as active
                task.status = TaskStatus.RUNNING.value
                task.started_at = datetime.now(timezone.utc)
                self.active_tasks[task.task_id] = task
                
                # Publish task started event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="concurrent.task.started",
                    source="concurrent_executor",
                    actor=worker_id,
                    resource=task.task_id,
                    payload={"domain": task.domain, "action": task.action},
                    timestamp=datetime.now(timezone.utc)
                ))
                
                # Execute task
                try:
                    result = await self._execute_task(task)
                    
                    task.status = TaskStatus.COMPLETED.value
                    task.result = result
                    task.completed_at = datetime.now(timezone.utc)
                    
                    # Log success
                    await immutable_log.append(
                        actor=worker_id,
                        action=task.action,
                        resource=task.task_id,
                        subsystem="concurrent_executor",
                        payload={"domain": task.domain},
                        result="success"
                    )
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED.value
                    task.error = str(e)
                    task.completed_at = datetime.now(timezone.utc)
                    
                    # Log failure
                    await immutable_log.append(
                        actor=worker_id,
                        action=task.action,
                        resource=task.task_id,
                        subsystem="concurrent_executor",
                        payload={"domain": task.domain},
                        result=f"failed: {str(e)}"
                    )
                
                # Move to completed (bound memory)
                self.completed_tasks[task.task_id] = task
                self.active_tasks.pop(task.task_id, None)
                
                # Evict oldest if over limit
                if len(self.completed_tasks) > self._max_completed:
                    oldest_id = min(
                        self.completed_tasks.keys(),
                        key=lambda k: self.completed_tasks[k].created_at
                    )
                    self.completed_tasks.pop(oldest_id, None)
                
                # Publish completion event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="concurrent.task.completed" if task.status == "completed" else "concurrent.task.failed",
                    source="concurrent_executor",
                    actor=worker_id,
                    resource=task.task_id,
                    payload={
                        "domain": task.domain,
                        "action": task.action,
                        "status": task.status
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
                
            except Exception as e:
                print(f"  [FAIL] Worker {worker_id} error: {e}")
        
        print(f"  [OK] Worker {worker_id} stopped")
    
    async def _execute_task(self, task: ConcurrentTask) -> Dict[str, Any]:
        """Execute a single task through domain adapter"""
        
        from .domains.all_domain_adapters import domain_registry
        
        # Get domain adapter
        adapter = domain_registry.get_adapter(task.domain)
        
        if not adapter:
            raise ValueError(f"No adapter for domain: {task.domain}")
        
        # Execute through adapter
        result = await adapter.execute_action(
            action_type=task.action,
            parameters=task.parameters
        )
        
        return result


# Singleton
concurrent_executor = ConcurrentExecutor(max_workers=6)
