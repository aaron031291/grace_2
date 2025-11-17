"""
Hierarchical Task Manager (HTM) - Grace's Scheduler + Priority Brain

Manages prioritized task queues with time awareness:
- Critical: Prod outages, security incidents, high-priority deployments
- High: Sandbox fixes, canary failures, model drift
- Normal: Daily ingestion, knowledge updates, automation

Features:
- Priority preemption (Critical > High > Normal)
- Time-aware scheduling (recurring tasks, delays, deadlines)
- Resource-aware execution (don't overload system)
- Integration with self-healing, coding agent, all kernels
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
from collections import deque
import heapq

from backend.core.message_bus import message_bus, MessagePriority


class TaskPriority(str, Enum):
    """Task priority levels"""
    CRITICAL = "critical"      # Prod outages, security incidents
    HIGH = "high"              # Sandbox fixes, canary failures
    NORMAL = "normal"          # Daily tasks, automation
    LOW = "low"                # Background optimization


class TaskStatus(str, Enum):
    """Task execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class Task:
    """Represents a task in the queue"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        priority: TaskPriority,
        handler: str,  # Which kernel/agent handles this
        payload: Dict[str, Any],
        deadline: Optional[datetime] = None,
        recurring: bool = False,
        interval_hours: Optional[int] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.priority = priority
        self.handler = handler
        self.payload = payload
        self.deadline = deadline
        self.recurring = recurring
        self.interval_hours = interval_hours
        
        self.status = TaskStatus.QUEUED
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.retry_count = 0
    
    def __lt__(self, other):
        """Comparison for heap queue (priority + deadline)"""
        # Priority order: CRITICAL > HIGH > NORMAL > LOW
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3
        }
        
        # First compare priority
        if priority_order[self.priority] != priority_order[other.priority]:
            return priority_order[self.priority] < priority_order[other.priority]
        
        # If same priority, earlier deadline wins
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        elif self.deadline:
            return True  # This has deadline, other doesn't
        
        # Otherwise, older task first (FIFO)
        return self.created_at < other.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "handler": self.handler,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "recurring": self.recurring,
            "interval_hours": self.interval_hours,
            "retry_count": self.retry_count
        }


class HierarchicalTaskManager:
    """
    Grace's scheduler + priority brain
    
    Responsibilities:
    - Maintain prioritized work queues
    - Time-aware scheduling (recurring tasks, deadlines)
    - Resource-aware execution (don't overload)
    - Preemption (Critical interrupts Normal)
    - Integration with all Layer 1 kernels
    """
    
    def __init__(self):
        # Priority queues (using heapq for efficient priority handling)
        self.critical_queue = []
        self.high_queue = []
        self.normal_queue = []
        self.low_queue = []
        
        # Active tasks
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks = deque(maxlen=1000)
        
        # Recurring task tracking
        self.recurring_tasks: Dict[str, Task] = {}
        self.last_run_times: Dict[str, datetime] = {}
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.max_concurrent_critical = 5
        
        # Worker tasks
        self._worker_tasks: List[asyncio.Task] = []
        self._scheduler_task: Optional[asyncio.Task] = None
        self._time_awareness_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "tasks_queued": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_preempted": 0
        }
    
    async def start(self):
        """Start the task manager"""
        
        # Start worker pools
        for i in range(self.max_concurrent_tasks):
            worker = asyncio.create_task(self._worker_loop(i))
            self._worker_tasks.append(worker)
        
        # Start scheduler
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Start time-awareness loop
        self._time_awareness_task = asyncio.create_task(self._time_awareness_loop())
        
        # Subscribe to task queue events
        asyncio.create_task(self._subscribe_to_task_queue())
        
        print(f"[HTM] Hierarchical Task Manager started")
        print(f"[HTM] Workers: {self.max_concurrent_tasks}")
        print(f"[HTM] Priority queues: CRITICAL > HIGH > NORMAL > LOW")
    
    async def enqueue_task(
        self,
        task_type: str,
        handler: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
        recurring: bool = False,
        interval_hours: Optional[int] = None
    ) -> str:
        """Add a task to the appropriate queue"""
        
        task_id = f"task_{task_type}_{datetime.utcnow().timestamp()}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            handler=handler,
            payload=payload,
            deadline=deadline,
            recurring=recurring,
            interval_hours=interval_hours
        )
        
        # Add to appropriate queue
        if priority == TaskPriority.CRITICAL:
            heapq.heappush(self.critical_queue, task)
            print(f"[HTM] ⚡ CRITICAL task queued: {task_type}")
        elif priority == TaskPriority.HIGH:
            heapq.heappush(self.high_queue, task)
            print(f"[HTM] 🔥 HIGH task queued: {task_type}")
        elif priority == TaskPriority.NORMAL:
            heapq.heappush(self.normal_queue, task)
            print(f"[HTM] 📋 NORMAL task queued: {task_type}")
        else:
            heapq.heappush(self.low_queue, task)
            print(f"[HTM] 💤 LOW task queued: {task_type}")
        
        # Track recurring
        if recurring and interval_hours:
            self.recurring_tasks[task_id] = task
        
        self.stats["tasks_queued"] += 1
        
        # Publish task queued event
        await message_bus.publish(
            source="htm",
            topic="task.queued",
            payload=task.to_dict(),
            priority=MessagePriority.HIGH if priority == TaskPriority.CRITICAL else MessagePriority.NORMAL
        )
        
        return task_id
    
    async def _get_next_task(self) -> Optional[Task]:
        """Get the next task to execute (priority order)"""
        
        # Critical first (preempts everything)
        if self.critical_queue:
            return heapq.heappop(self.critical_queue)
        
        # High second
        if self.high_queue:
            return heapq.heappop(self.high_queue)
        
        # Normal third
        if self.normal_queue:
            return heapq.heappop(self.normal_queue)
        
        # Low last
        if self.low_queue:
            return heapq.heappop(self.low_queue)
        
        return None
    
    async def _worker_loop(self, worker_id: int):
        """Worker that executes tasks"""
        
        while True:
            try:
                # Get next task
                task = await self._get_next_task()
                
                if not task:
                    # No tasks, sleep
                    await asyncio.sleep(1)
                    continue
                
                # Check if we should defer critical tasks
                critical_running = sum(
                    1 for t in self.running_tasks.values()
                    if t.priority == TaskPriority.CRITICAL
                )
                
                if task.priority == TaskPriority.CRITICAL and critical_running >= self.max_concurrent_critical:
                    # Too many critical tasks running, re-queue
                    heapq.heappush(self.critical_queue, task)
                    await asyncio.sleep(0.5)
                    continue
                
                # Execute task
                await self._execute_task(task, worker_id)
            
            except Exception as e:
                print(f"[HTM] Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: Task, worker_id: int):
        """Execute a task"""
        
        print(f"[HTM] Worker {worker_id}: Executing {task.task_type} (priority: {task.priority.value})")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self.running_tasks[task.task_id] = task
        
        # Publish task started
        await message_bus.publish(
            source="htm",
            topic="task.started",
            payload=task.to_dict(),
            priority=MessagePriority.NORMAL
        )
        
        try:
            # Route to appropriate handler
            result = await self._route_task(task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            self.stats["tasks_completed"] += 1
            
            # Publish completion
            await message_bus.publish(
                source="htm",
                topic="task.completed",
                payload={**task.to_dict(), "result": result},
                priority=MessagePriority.NORMAL
            )
            
            print(f"[HTM] ✅ Task completed: {task.task_type}")
            
            # Handle recurring tasks
            if task.recurring and task.interval_hours:
                await self._reschedule_recurring(task)
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            self.stats["tasks_failed"] += 1
            
            # Publish failure
            await message_bus.publish(
                source="htm",
                topic="task.failed",
                payload={**task.to_dict(), "error": str(e)},
                priority=MessagePriority.HIGH
            )
            
            print(f"[HTM] ❌ Task failed: {task.task_type} - {e}")
            
            # Retry logic for critical tasks
            if task.priority == TaskPriority.CRITICAL and task.retry_count < 3:
                task.retry_count += 1
                task.status = TaskStatus.QUEUED
                heapq.heappush(self.critical_queue, task)
                print(f"[HTM] 🔄 Retrying critical task (attempt {task.retry_count})")
        
        finally:
            # Remove from running
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            # Archive
            self.completed_tasks.append(task)
    
    async def _route_task(self, task: Task) -> Any:
        """Route task to appropriate handler"""
        
        # Publish to handler's topic
        await message_bus.publish(
            source="htm",
            topic=f"task.execute.{task.handler}",
            payload={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "payload": task.payload
            },
            priority=MessagePriority.HIGH if task.priority == TaskPriority.CRITICAL else MessagePriority.NORMAL
        )
        
        # Wait for response (simplified - in production use request/response pattern)
        await asyncio.sleep(0.1)
        
        return {"status": "executed", "handler": task.handler}
    
    async def _reschedule_recurring(self, task: Task):
        """Reschedule a recurring task"""
        
        next_run = datetime.utcnow() + timedelta(hours=task.interval_hours)
        
        # Create new task for next run
        await self.enqueue_task(
            task_type=task.task_type,
            handler=task.handler,
            payload=task.payload,
            priority=task.priority,
            recurring=True,
            interval_hours=task.interval_hours
        )
        
        print(f"[HTM] 🔁 Rescheduled recurring task: {task.task_type} (next run: {next_run.isoformat()})")
    
    async def _scheduler_loop(self):
        """Smart scheduler that handles preemption and priorities"""
        
        while True:
            try:
                await asyncio.sleep(5)
                
                # Check for critical tasks that need preemption
                if self.critical_queue:
                    # If we have critical tasks and too many normal tasks running,
                    # consider pausing normal tasks
                    normal_running = [
                        t for t in self.running_tasks.values()
                        if t.priority in [TaskPriority.NORMAL, TaskPriority.LOW]
                    ]
                    
                    if len(normal_running) > 5 and len(self.critical_queue) > 0:
                        print(f"[HTM] ⚡ Critical tasks waiting - prioritizing...")
                        self.stats["tasks_preempted"] += len(normal_running)
                
                # Check for deadline violations
                now = datetime.utcnow()
                for queue in [self.critical_queue, self.high_queue, self.normal_queue]:
                    for task in queue:
                        if task.deadline and task.deadline < now:
                            print(f"[HTM] ⚠️ Task {task.task_id} missed deadline!")
                            # Escalate priority
                            if task.priority != TaskPriority.CRITICAL:
                                queue.remove(task)
                                task.priority = TaskPriority.CRITICAL
                                heapq.heappush(self.critical_queue, task)
            
            except Exception as e:
                print(f"[HTM] Scheduler error: {e}")
    
    async def _time_awareness_loop(self):
        """
        Time-aware scheduling
        
        Examples:
        - "It's been 4 hours since health check, re-run it"
        - "Daily ingestion should run at 2am"
        - "Key rotation due in 2 days"
        """
        
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                
                # Check recurring task schedules
                for task_id, task in self.recurring_tasks.items():
                    last_run = self.last_run_times.get(task_id)
                    
                    if not last_run:
                        continue
                    
                    hours_since = (now - last_run).total_seconds() / 3600
                    
                    if hours_since >= task.interval_hours:
                        print(f"[HTM] ⏰ Time for recurring task: {task.task_type}")
                        
                        # Re-enqueue
                        await self.enqueue_task(
                            task_type=task.task_type,
                            handler=task.handler,
                            payload=task.payload,
                            priority=task.priority,
                            recurring=True,
                            interval_hours=task.interval_hours
                        )
                        
                        self.last_run_times[task_id] = now
                
                # Check for time-based events (examples)
                hour = now.hour
                
                # Daily health check at 2am
                if hour == 2 and not self._ran_today("health_check"):
                    await self.enqueue_task(
                        task_type="daily_health_check",
                        handler="verification",
                        payload={"check_type": "comprehensive"},
                        priority=TaskPriority.NORMAL
                    )
                
                # Weekly key rotation on Sundays at 3am
                if now.weekday() == 6 and hour == 3 and not self._ran_today("key_rotation"):
                    await self.enqueue_task(
                        task_type="rotate_secrets",
                        handler="security",
                        payload={"scope": "all"},
                        priority=TaskPriority.HIGH
                    )
            
            except Exception as e:
                print(f"[HTM] Time awareness error: {e}")
    
    def _ran_today(self, task_type: str) -> bool:
        """Check if a task type already ran today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for task in self.completed_tasks:
            if task.task_type == task_type and task.completed_at and task.completed_at > today_start:
                return True
        
        return False
    
    async def _subscribe_to_task_queue(self):
        """Subscribe to external task queue requests"""
        
        try:
            queue = await message_bus.subscribe(
                subscriber="htm",
                topic="task.enqueue"
            )
            
            while True:
                msg = await queue.get()
                
                # Extract task details
                task_type = msg.payload.get("task_type")
                handler = msg.payload.get("handler", "unknown")
                payload = msg.payload.get("context", {})
                priority_str = msg.payload.get("priority", "normal")
                
                # Map priority
                priority = TaskPriority(priority_str) if priority_str in TaskPriority._value2member_map_ else TaskPriority.NORMAL
                
                # Enqueue
                await self.enqueue_task(
                    task_type=task_type,
                    handler=handler,
                    payload=payload,
                    priority=priority
                )
        
        except Exception as e:
            print(f"[HTM] Task queue subscription error: {e}")
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """Get current queue sizes"""
        return {
            "critical": len(self.critical_queue),
            "high": len(self.high_queue),
            "normal": len(self.normal_queue),
            "low": len(self.low_queue),
            "running": len(self.running_tasks)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get HTM status"""
        return {
            "queue_sizes": self.get_queue_sizes(),
            "statistics": self.stats,
            "running_tasks": [t.to_dict() for t in self.running_tasks.values()],
            "recent_completed": [t.to_dict() for t in list(self.completed_tasks)[-10:]]
        }
    
    async def shutdown(self):
        """Stop the task manager"""
        for worker in self._worker_tasks:
            worker.cancel()
        if self._scheduler_task:
            self._scheduler_task.cancel()
        if self._time_awareness_task:
            self._time_awareness_task.cancel()


# Global instance
htm = HierarchicalTaskManager()
