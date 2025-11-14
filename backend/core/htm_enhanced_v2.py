"""
HTM Enhanced V2 - Complete Task Tracking Implementation

Features:
- Full timestamp tracking at each state change
- Worker reporting protocol (htm.task.update)
- Retry logic with exponential backoff
- SLA compliance monitoring
- Metrics aggregation (avg, p50, p95, p99)
- Feedback to agentic brain

Based on Oracle recommendations.
"""

import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from collections import deque, defaultdict
from dataclasses import dataclass, field

from backend.core.message_bus import message_bus, MessagePriority
from backend.models.htm_models import HTMTask, HTMTaskAttempt, HTMMetrics
from backend.models.base_models import async_session
from sqlalchemy import select, update, and_


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class TaskAttempt:
    """Single execution attempt"""
    attempt_number: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    assigned_worker: Optional[str] = None
    status: str = "running"
    success: bool = False
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_reason: Optional[str] = None


@dataclass
class TrackedTask:
    """Task with complete timing tracking"""
    task_id: str
    task_type: str
    domain: str
    priority: TaskPriority
    payload: Dict[str, Any]
    handler: str
    
    # State
    status: TaskStatus = TaskStatus.QUEUED
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    queued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    
    # Timing metrics
    queue_time_ms: Optional[float] = None
    execution_time_ms: Optional[float] = None
    total_time_ms: Optional[float] = None
    
    # SLA
    sla_ms: int = 60000  # Default 60s
    sla_deadline: Optional[datetime] = None
    sla_met: Optional[bool] = None
    sla_buffer_ms: Optional[float] = None
    
    # Execution
    assigned_worker: Optional[str] = None
    attempt_number: int = 1
    max_attempts: int = 3
    attempts: List[TaskAttempt] = field(default_factory=list)
    
    # Outcome
    success: Optional[bool] = None
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    
    # Intent linkage
    intent_id: Optional[str] = None
    
    def calculate_timings(self):
        """Calculate all timing metrics"""
        now = datetime.now(timezone.utc)
        
        if self.assigned_at and self.queued_at:
            self.queue_time_ms = (self.assigned_at - self.queued_at).total_seconds() * 1000
        
        if self.finished_at and self.started_at:
            self.execution_time_ms = (self.finished_at - self.started_at).total_seconds() * 1000
        
        if self.finished_at and self.created_at:
            self.total_time_ms = (self.finished_at - self.created_at).total_seconds() * 1000
        
        if self.sla_deadline:
            finish_time = self.finished_at or now
            self.sla_buffer_ms = (self.sla_deadline - finish_time).total_seconds() * 1000
            self.sla_met = self.sla_buffer_ms >= 0


class HTMEnhancedV2:
    """
    HTM with comprehensive task tracking and timing
    
    Worker Reporting Protocol:
        Topic: htm.task.update
        Fields:
            - task_id (required)
            - status: assigned|started|heartbeat|progress|completed|failed|timeout
            - worker_id (required)
            - attempt_number (required)
            - at: ISO timestamp
            - result: JSON (on completed)
            - error_message: string (on failed/timeout)
            - error_type: validation|transient|timeout|system|nonretryable
            - retryable: bool (hint to HTM)
            - progress: 0.0-1.0
            - metrics: {duration_ms}
    """
    
    def __init__(self):
        # Task queues (store task_ids)
        self.queues = {
            "critical": deque(),
            "high": deque(),
            "normal": deque(),
            "low": deque()
        }
        
        # Task tracking
        self.tasks: Dict[str, TrackedTask] = {}
        self.running: Dict[str, TrackedTask] = {}
        self.completed = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            "tasks_queued": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_timeout": 0,
            "tasks_retried": 0,
            "sla_met": 0,
            "sla_missed": 0
        }
        
        # Workers
        self._workers = []
        self.num_workers = 10
        self.running_flag = False
        
        # SLA defaults per priority (milliseconds)
        self.default_sla = {
            TaskPriority.CRITICAL: 300000,  # 5 minutes
            TaskPriority.HIGH: 900000,      # 15 minutes
            TaskPriority.NORMAL: 3600000,   # 60 minutes
            TaskPriority.LOW: 10800000      # 180 minutes
        }
        
        # Metrics
        self.metrics_cache: Dict[str, Any] = {}
        self.last_metrics_update = datetime.now(timezone.utc)
    
    async def start(self):
        """Start HTM with full tracking"""
        if self.running_flag:
            return
        
        self.running_flag = True
        
        # Start worker pool (dispatchers)
        for i in range(self.num_workers):
            self._workers.append(asyncio.create_task(self._worker(i)))
        
        # Start metrics aggregation
        asyncio.create_task(self._metrics_aggregation_loop())
        
        # Subscribe to worker updates
        asyncio.create_task(self._subscribe_to_worker_updates())
        
        print("[HTM-V2] Enhanced Hierarchical Task Manager started")
        print(f"[HTM-V2] Workers: {self.num_workers}")
        print("[HTM-V2] Features: Full timing, retries, SLA, metrics, worker protocol")
    
    async def _subscribe_to_worker_updates(self):
        """Subscribe to worker status reports"""
        try:
            queue = await message_bus.subscribe(
                subscriber="htm_v2",
                topic="htm.task.update"
            )
            asyncio.create_task(self._process_worker_updates(queue))
            print("[HTM-V2] Subscribed to worker updates")
        except Exception as e:
            print(f"[HTM-V2] Failed to subscribe: {e}")
    
    async def enqueue_task(
        self,
        task_type: str,
        handler: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        domain: str = "general",
        sla_ms: Optional[int] = None,
        max_attempts: int = 3,
        intent_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Enqueue task with complete tracking
        
        Returns:
            task_id for tracking
        """
        # Generate task ID
        task_id = f"htm_{task_type}_{datetime.now(timezone.utc).timestamp()}"
        
        # Calculate SLA
        sla_milliseconds = sla_ms or self.default_sla.get(priority, 3600000)
        sla_deadline = datetime.now(timezone.utc) + timedelta(milliseconds=sla_milliseconds)
        
        # Create tracked task
        tracked = TrackedTask(
            task_id=task_id,
            task_type=task_type,
            domain=domain,
            priority=priority,
            payload=payload,
            handler=handler,
            sla_ms=sla_milliseconds,
            sla_deadline=sla_deadline,
            max_attempts=max_attempts,
            intent_id=intent_id
        )
        
        # Store in memory
        self.tasks[task_id] = tracked
        
        # Persist to database
        await self._persist_task_initial(tracked)
        
        # Enqueue
        self.queues[priority.value].append(task_id)
        self.stats["tasks_queued"] += 1
        
        print(f"[HTM-V2] Enqueued task {task_id}: {task_type} (SLA: {sla_milliseconds/1000:.0f}s)")
        
        return task_id
    
    async def _worker(self, worker_id: int):
        """Worker that dispatches tasks to kernels/agents"""
        while self.running_flag:
            task_id = None
            
            # Dequeue by priority
            for q in ["critical", "high", "normal", "low"]:
                if self.queues[q]:
                    task_id = self.queues[q].popleft()  # Fixed: use popleft()
                    break
            
            if task_id:
                tracked = self.tasks.get(task_id)
                if not tracked:
                    continue
                
                # Mark as assigned
                now = datetime.now(timezone.utc)
                tracked.assigned_at = now
                tracked.status = TaskStatus.ASSIGNED
                tracked.assigned_worker = f"worker_{worker_id}"
                
                # Persist assignment
                await self._persist_task_update(tracked, ["status", "assigned_at", "assigned_worker"])
                
                # Dispatch to worker/kernel
                await message_bus.publish(
                    source="htm_v2",
                    topic=f"htm.task.dispatch.{tracked.task_type}",
                    payload={
                        "task_id": task_id,
                        "task_type": tracked.task_type,
                        "payload": tracked.payload,
                        "attempt_number": tracked.attempt_number,
                        "priority": tracked.priority.value,
                        "sla_deadline": tracked.sla_deadline.isoformat() if tracked.sla_deadline else None,
                        "handler": tracked.handler
                    },
                    priority=MessagePriority.HIGH if tracked.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH] else MessagePriority.NORMAL
                )
                
                # Move to running
                self.running[task_id] = tracked
                
                # Start watchdog
                asyncio.create_task(self._watchdog(task_id, tracked.attempt_number))
                
                print(f"[HTM-V2] Worker-{worker_id} dispatched: {task_id}")
            else:
                await asyncio.sleep(1)
    
    async def _watchdog(self, task_id: str, attempt_number: int):
        """Monitor task execution and handle timeouts"""
        tracked = self.tasks.get(task_id)
        if not tracked or tracked.attempt_number != attempt_number:
            return
        
        # Grace period for worker to accept (15s)
        await asyncio.sleep(15)
        
        if task_id in self.running and tracked.started_at is None:
            # Worker didn't report start
            print(f"[HTM-V2] Task {task_id} not accepted, timing out")
            await self._handle_timeout(task_id, "not_accepted")
            return
        
        # Execution timeout based on SLA
        timeout_seconds = (tracked.sla_ms / 1000) + 30 if tracked.sla_ms else 300
        await asyncio.sleep(timeout_seconds)
        
        if task_id in self.running and tracked.finished_at is None:
            # Task exceeded timeout
            print(f"[HTM-V2] Task {task_id} exceeded timeout, terminating")
            await self._handle_timeout(task_id, "execution_timeout")
    
    async def _handle_timeout(self, task_id: str, reason: str):
        """Handle task timeout"""
        tracked = self.tasks.get(task_id)
        if not tracked or tracked.finished_at:
            return
        
        now = datetime.now(timezone.utc)
        
        # Create timeout attempt
        attempt = TaskAttempt(
            attempt_number=tracked.attempt_number,
            started_at=tracked.started_at or tracked.assigned_at or now,
            finished_at=now,
            assigned_worker=tracked.assigned_worker,
            status="timeout",
            success=False,
            retry_reason=reason
        )
        attempt.duration_ms = (attempt.finished_at - attempt.started_at).total_seconds() * 1000
        tracked.attempts.append(attempt)
        
        # Persist attempt
        await self._persist_attempt(tracked, attempt)
        
        # Decide retry
        should_retry = tracked.attempt_number < tracked.max_attempts
        
        if should_retry:
            # Schedule retry
            tracked.status = TaskStatus.RETRYING
            tracked.attempt_number += 1
            self.stats["tasks_retried"] += 1
            
            delay = self._calculate_backoff(tracked.attempt_number)
            await self._persist_task_update(tracked, ["status", "attempt_number"])
            
            asyncio.create_task(self._schedule_retry(task_id, delay))
            
            if task_id in self.running:
                del self.running[task_id]
        else:
            # Final timeout
            await self._finalize_task(tracked, TaskStatus.TIMEOUT, False)
    
    async def _process_worker_updates(self, queue):
        """Process worker status updates"""
        while self.running_flag:
            try:
                msg = await queue.get()
                payload = msg.payload
                
                task_id = payload.get("task_id")
                status = payload.get("status")
                attempt_number = payload.get("attempt_number", 1)
                worker_id = payload.get("worker_id")
                
                tracked = self.tasks.get(task_id)
                if not tracked:
                    continue
                
                # Ignore stale updates
                if attempt_number < tracked.attempt_number:
                    continue
                
                now = datetime.now(timezone.utc)
                
                # Handle different status updates
                if status == "started":
                    tracked.started_at = now
                    tracked.status = TaskStatus.RUNNING
                    tracked.assigned_worker = worker_id
                    tracked.last_heartbeat_at = now
                    
                    # Create attempt record
                    attempt = TaskAttempt(
                        attempt_number=attempt_number,
                        started_at=now,
                        assigned_worker=worker_id
                    )
                    tracked.attempts.append(attempt)
                    
                    await self._persist_task_update(tracked, ["status", "started_at", "assigned_worker"])
                    
                    print(f"[HTM-V2] Task {task_id} started by {worker_id}")
                
                elif status in ["heartbeat", "progress"]:
                    tracked.last_heartbeat_at = now
                    # In-memory only, don't persist heartbeats
                
                elif status in ["completed", "failed", "timeout"]:
                    # Get current attempt
                    current_attempt = tracked.attempts[-1] if tracked.attempts else TaskAttempt(
                        attempt_number=attempt_number,
                        started_at=tracked.started_at or now
                    )
                    
                    current_attempt.finished_at = now
                    current_attempt.status = status
                    current_attempt.success = (status == "completed")
                    current_attempt.result = payload.get("result")
                    current_attempt.error_message = payload.get("error_message")
                    current_attempt.error_type = payload.get("error_type")
                    current_attempt.assigned_worker = worker_id
                    
                    if current_attempt.started_at:
                        current_attempt.duration_ms = (current_attempt.finished_at - current_attempt.started_at).total_seconds() * 1000
                    else:
                        current_attempt.duration_ms = payload.get("metrics", {}).get("duration_ms")
                    
                    # Persist attempt
                    await self._persist_attempt(tracked, current_attempt)
                    
                    # Decide retry
                    should_retry = (
                        (payload.get("retryable", False) or status == "timeout") and
                        tracked.attempt_number < tracked.max_attempts and
                        payload.get("error_type") not in ["validation", "user", "nonretryable"]
                    )
                    
                    if should_retry:
                        # Retry
                        tracked.status = TaskStatus.RETRYING
                        tracked.attempt_number += 1
                        self.stats["tasks_retried"] += 1
                        
                        current_attempt.retry_reason = payload.get("error_type", "retry_requested")
                        
                        delay = self._calculate_backoff(tracked.attempt_number)
                        await self._persist_task_update(tracked, ["status", "attempt_number"])
                        
                        asyncio.create_task(self._schedule_retry(task_id, delay))
                        
                        if task_id in self.running:
                            del self.running[task_id]
                        
                        print(f"[HTM-V2] Task {task_id} retry scheduled (attempt {tracked.attempt_number}/{tracked.max_attempts})")
                    else:
                        # Finalize
                        final_status = TaskStatus.COMPLETED if current_attempt.success else (
                            TaskStatus.TIMEOUT if status == "timeout" else TaskStatus.FAILED
                        )
                        await self._finalize_task(tracked, final_status, current_attempt.success, current_attempt.result, current_attempt.error_message)
            
            except Exception as e:
                print(f"[HTM-V2] Error processing worker update: {e}")
                await asyncio.sleep(1)
    
    async def _schedule_retry(self, task_id: str, delay_seconds: float):
        """Schedule task retry after delay"""
        await asyncio.sleep(delay_seconds)
        
        tracked = self.tasks.get(task_id)
        if not tracked:
            return
        
        # Reset for retry
        tracked.status = TaskStatus.QUEUED
        tracked.assigned_at = None
        tracked.started_at = None
        tracked.assigned_worker = None
        
        # Re-enqueue
        self.queues[tracked.priority.value].append(task_id)
        
        await self._persist_task_update(tracked, ["status"])
        
        print(f"[HTM-V2] Task {task_id} requeued (attempt {tracked.attempt_number})")
    
    async def _finalize_task(
        self,
        tracked: TrackedTask,
        final_status: TaskStatus,
        success: bool,
        result: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Finalize task and update all metrics"""
        now = datetime.now(timezone.utc)
        
        tracked.finished_at = now
        tracked.status = final_status
        tracked.success = success
        tracked.result = result
        tracked.error_message = error_message
        
        # Calculate timings
        tracked.calculate_timings()
        
        # Update stats
        if success:
            self.stats["tasks_completed"] += 1
            if tracked.sla_met:
                self.stats["sla_met"] += 1
            else:
                self.stats["sla_missed"] += 1
        elif final_status == TaskStatus.TIMEOUT:
            self.stats["tasks_timeout"] += 1
            self.stats["sla_missed"] += 1
        else:
            self.stats["tasks_failed"] += 1
            if not tracked.sla_met:
                self.stats["sla_missed"] += 1
        
        # Persist final state
        await self._persist_task_final(tracked)
        
        # Move to completed
        if task_id in self.running:
            del self.running[task_id]
        self.completed.append(tracked)
        
        # Publish completion event
        await message_bus.publish(
            source="htm_v2",
            topic=f"task.{final_status.value}",
            payload={
                "task_id": tracked.task_id,
                "task_type": tracked.task_type,
                "success": success,
                "execution_time_ms": tracked.execution_time_ms,
                "total_time_ms": tracked.total_time_ms,
                "sla_met": tracked.sla_met,
                "attempts": tracked.attempt_number
            },
            priority=MessagePriority.NORMAL
        )
        
        print(f"[HTM-V2] Task {tracked.task_id} finalized: {final_status.value} (SLA met: {tracked.sla_met})")
    
    def _calculate_backoff(self, attempt_number: int) -> float:
        """Calculate exponential backoff with jitter"""
        base = 1.0
        max_delay = 60.0
        
        delay = min(max_delay, base * (2 ** (attempt_number - 1)))
        jitter = delay * 0.2 * (random.random() - 0.5)  # ±20% jitter
        
        return max(0, delay + jitter)
    
    async def _persist_task_initial(self, tracked: TrackedTask):
        """Persist initial task creation"""
        try:
            async with async_session() as session:
                htm_task = HTMTask(
                    task_id=tracked.task_id,
                    task_type=tracked.task_type,
                    domain=tracked.domain,
                    intent_id=tracked.intent_id,
                    priority=tracked.priority.value,
                    payload=tracked.payload,
                    status="queued",
                    created_at=tracked.created_at,
                    queued_at=tracked.queued_at,
                    sla_ms=tracked.sla_ms,
                    sla_deadline=tracked.sla_deadline,
                    attempt_number=1,
                    max_attempts=tracked.max_attempts,
                    attempts=[]
                )
                session.add(htm_task)
                await session.commit()
        except Exception as e:
            print(f"[HTM-V2] Failed to persist task: {e}")
    
    async def _persist_task_update(self, tracked: TrackedTask, fields: List[str]):
        """Update specific fields in database"""
        try:
            async with async_session() as session:
                update_values = {
                    "status": tracked.status.value if isinstance(tracked.status, TaskStatus) else tracked.status
                }
                
                if "assigned_at" in fields and tracked.assigned_at:
                    update_values["assigned_at"] = tracked.assigned_at
                if "started_at" in fields and tracked.started_at:
                    update_values["started_at"] = tracked.started_at
                if "assigned_worker" in fields and tracked.assigned_worker:
                    update_values["assigned_worker"] = tracked.assigned_worker
                if "attempt_number" in fields:
                    update_values["attempt_number"] = tracked.attempt_number
                
                await session.execute(
                    update(HTMTask)
                    .where(HTMTask.task_id == tracked.task_id)
                    .values(**update_values)
                )
                await session.commit()
        except Exception as e:
            print(f"[HTM-V2] Failed to update task: {e}")
    
    async def _persist_task_final(self, tracked: TrackedTask):
        """Persist final task state with all metrics"""
        try:
            async with async_session() as session:
                # Serialize attempts
                attempts_json = [
                    {
                        "attempt": a.attempt_number,
                        "duration_ms": a.duration_ms,
                        "status": a.status,
                        "success": a.success,
                        "retry_reason": a.retry_reason
                    }
                    for a in tracked.attempts
                ]
                
                await session.execute(
                    update(HTMTask)
                    .where(HTMTask.task_id == tracked.task_id)
                    .values(
                        status=tracked.status.value,
                        finished_at=tracked.finished_at,
                        queue_time_ms=tracked.queue_time_ms,
                        execution_time_ms=tracked.execution_time_ms,
                        total_time_ms=tracked.total_time_ms,
                        sla_met=tracked.sla_met,
                        sla_buffer_ms=tracked.sla_buffer_ms,
                        success=tracked.success,
                        result=tracked.result,
                        error_message=tracked.error_message,
                        attempts=attempts_json
                    )
                )
                await session.commit()
        except Exception as e:
            print(f"[HTM-V2] Failed to persist final state: {e}")
    
    async def _persist_attempt(self, tracked: TrackedTask, attempt: TaskAttempt):
        """Persist individual attempt"""
        try:
            async with async_session() as session:
                attempt_record = HTMTaskAttempt(
                    task_id=tracked.task_id,
                    attempt_number=attempt.attempt_number,
                    started_at=attempt.started_at,
                    finished_at=attempt.finished_at,
                    duration_ms=attempt.duration_ms,
                    assigned_worker=attempt.assigned_worker,
                    status=attempt.status,
                    success=attempt.success,
                    result=attempt.result,
                    error_message=attempt.error_message,
                    error_type=attempt.error_type,
                    retry_reason=attempt.retry_reason
                )
                session.add(attempt_record)
                await session.commit()
        except Exception as e:
            print(f"[HTM-V2] Failed to persist attempt: {e}")
    
    async def _metrics_aggregation_loop(self):
        """Aggregate task metrics hourly"""
        while self.running_flag:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                await self._aggregate_hourly_metrics()
                
            except Exception as e:
                print(f"[HTM-V2] Metrics aggregation error: {e}")
    
    async def _aggregate_hourly_metrics(self):
        """Calculate and store hourly metrics"""
        try:
            now = datetime.now(timezone.utc)
            bucket_end = now.replace(minute=0, second=0, microsecond=0)
            bucket_start = bucket_end - timedelta(hours=1)
            
            async with async_session() as session:
                # Get completed tasks in this hour
                result = await session.execute(
                    select(HTMTask)
                    .where(
                        and_(
                            HTMTask.finished_at >= bucket_start,
                            HTMTask.finished_at < bucket_end,
                            HTMTask.status.in_(["completed", "failed", "timeout"])
                        )
                    )
                )
                tasks = result.scalars().all()
                
                # Group by task_type
                by_type = defaultdict(list)
                all_tasks = []
                
                for task in tasks:
                    by_type[task.task_type].append(task)
                    all_tasks.append(task)
                
                # Aggregate for each type + overall
                for task_type, type_tasks in list(by_type.items()) + [("all", all_tasks)]:
                    metrics = self._calculate_metrics(type_tasks)
                    
                    # Upsert metrics
                    htm_metrics = HTMMetrics(
                        bucket="hourly",
                        bucket_start=bucket_start,
                        bucket_end=bucket_end,
                        task_type=task_type,
                        **metrics
                    )
                    session.add(htm_metrics)
                
                await session.commit()
                
                self.last_metrics_update = now
                print(f"[HTM-V2] Metrics aggregated for hour {bucket_start.strftime('%Y-%m-%d %H:00')}")
        
        except Exception as e:
            print(f"[HTM-V2] Metrics aggregation failed: {e}")
    
    def _calculate_metrics(self, tasks: List) -> Dict[str, Any]:
        """Calculate metrics from task list"""
        if not tasks:
            return {}
        
        total = len(tasks)
        completed = sum(1 for t in tasks if t.success)
        failed = sum(1 for t in tasks if t.status == "failed")
        timeout = sum(1 for t in tasks if t.status == "timeout")
        
        # Timing metrics
        queue_times = [t.queue_time_ms for t in tasks if t.queue_time_ms]
        exec_times = [t.execution_time_ms for t in tasks if t.execution_time_ms]
        total_times = [t.total_time_ms for t in tasks if t.total_time_ms]
        
        # Percentiles
        def percentile(values, p):
            if not values:
                return 0.0
            sorted_vals = sorted(values)
            idx = int(p * len(sorted_vals))
            return sorted_vals[min(idx, len(sorted_vals) - 1)]
        
        # SLA metrics
        sla_met = sum(1 for t in tasks if t.sla_met)
        sla_missed = total - sla_met
        
        # Retry metrics
        total_attempts = sum(t.attempt_number for t in tasks)
        retried_tasks = sum(1 for t in tasks if t.attempt_number > 1)
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "timeout_tasks": timeout,
            "avg_queue_time_ms": sum(queue_times) / len(queue_times) if queue_times else 0,
            "avg_execution_time_ms": sum(exec_times) / len(exec_times) if exec_times else 0,
            "avg_total_time_ms": sum(total_times) / len(total_times) if total_times else 0,
            "p50_execution_ms": percentile(exec_times, 0.50),
            "p95_execution_ms": percentile(exec_times, 0.95),
            "p99_execution_ms": percentile(exec_times, 0.99),
            "sla_met_count": sla_met,
            "sla_missed_count": sla_missed,
            "sla_compliance_rate": sla_met / total if total > 0 else 0,
            "total_attempts": total_attempts,
            "tasks_retried": retried_tasks,
            "avg_attempts": total_attempts / total if total > 0 else 1.0,
            "success_rate": completed / total if total > 0 else 0
        }
