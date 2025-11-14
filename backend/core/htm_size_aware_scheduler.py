"""
HTM Size-Aware Scheduler

Routes tasks based on data volume:
- Large tasks → heavy workers or off-peak hours
- Small tasks → fill idle gaps  
- Batch tiny tasks together
- Balance bandwidth across workers
"""

import asyncio
from datetime import datetime, timezone, time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.core.message_bus import message_bus, MessagePriority
from backend.core.htm_size_tracker import (
    TaskSizeClass, classify_task_size, format_bytes,
    get_size_recommendations
)
from backend.logging_utils import log_event
from sqlalchemy import select, and_


@dataclass
class WorkerProfile:
    """Worker capacity profile"""
    worker_id: str
    worker_type: str  # light, standard, heavy
    max_concurrent_tasks: int
    max_data_size_bytes: int
    preferred_size_class: List[TaskSizeClass]
    current_load_bytes: int = 0
    current_task_count: int = 0
    
    def can_accept(self, task_size_bytes: int) -> bool:
        """Check if worker can accept task"""
        if self.current_task_count >= self.max_concurrent_tasks:
            return False
        if self.current_load_bytes + task_size_bytes > self.max_data_size_bytes:
            return False
        return True
    
    def get_utilization(self) -> float:
        """Get current utilization (0.0-1.0)"""
        return self.current_load_bytes / self.max_data_size_bytes if self.max_data_size_bytes > 0 else 0.0


class HTMSizeAwareScheduler:
    """
    Schedule tasks based on data volume and worker capacity
    
    Strategies:
    - Route large tasks to heavy workers
    - Batch small tasks to fill idle time
    - Balance bandwidth across workers
    - Schedule large tasks during off-peak hours
    """
    
    def __init__(self):
        # Worker profiles
        self.workers: Dict[str, WorkerProfile] = {}
        
        # Off-peak hours (UTC)
        self.off_peak_start = time(22, 0)  # 10 PM
        self.off_peak_end = time(6, 0)     # 6 AM
        
        # Batching thresholds
        self.batch_size_threshold = 1024 * 1024  # 1 MB - batch if smaller
        self.max_batch_size = 50  # Max tasks per batch
        
        # Load balancing
        self.max_worker_utilization = 0.8  # Target 80% max
        
        print("[HTM SIZE SCHEDULER] Initialized")
    
    def register_worker(
        self,
        worker_id: str,
        worker_type: str = "standard",
        max_concurrent: int = 5,
        max_data_gb: float = 10.0
    ):
        """
        Register worker with capacity profile
        
        Args:
            worker_id: Worker identifier
            worker_type: light, standard, heavy
            max_concurrent: Max simultaneous tasks
            max_data_gb: Max data load in GB
        """
        # Set preferred size classes based on worker type
        if worker_type == "light":
            preferred = [TaskSizeClass.TINY, TaskSizeClass.SMALL]
        elif worker_type == "heavy":
            preferred = [TaskSizeClass.LARGE, TaskSizeClass.HUGE, TaskSizeClass.MASSIVE]
        else:  # standard
            preferred = [TaskSizeClass.SMALL, TaskSizeClass.MEDIUM, TaskSizeClass.LARGE]
        
        self.workers[worker_id] = WorkerProfile(
            worker_id=worker_id,
            worker_type=worker_type,
            max_concurrent_tasks=max_concurrent,
            max_data_size_bytes=int(max_data_gb * 1024 ** 3),
            preferred_size_class=preferred
        )
        
        print(f"[HTM SIZE SCHEDULER] Registered worker {worker_id} ({worker_type})")
    
    def is_off_peak(self) -> bool:
        """Check if current time is off-peak"""
        now = datetime.now(timezone.utc).time()
        
        if self.off_peak_start < self.off_peak_end:
            return self.off_peak_start <= now < self.off_peak_end
        else:  # Crosses midnight
            return now >= self.off_peak_start or now < self.off_peak_end
    
    async def schedule_task(
        self,
        task_id: str,
        task_type: str,
        data_size_bytes: int,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Determine optimal scheduling for task
        
        Returns:
            {
                "worker_id": str or None,
                "schedule_now": bool,
                "recommended_delay_seconds": int,
                "should_batch": bool,
                "batch_window_seconds": int,
                "reasoning": str
            }
        """
        size_class = classify_task_size(data_size_bytes)
        
        # Get size-based recommendations
        recommendations = get_size_recommendations(data_size_bytes, task_type)
        
        # Check if task should wait for off-peak
        if size_class in [TaskSizeClass.HUGE, TaskSizeClass.MASSIVE]:
            if not self.is_off_peak() and priority != "critical":
                seconds_until_offpeak = self._seconds_until_off_peak()
                return {
                    "worker_id": None,
                    "schedule_now": False,
                    "recommended_delay_seconds": seconds_until_offpeak,
                    "should_batch": False,
                    "batch_window_seconds": 0,
                    "reasoning": f"Large task ({format_bytes(data_size_bytes)}) - schedule during off-peak hours",
                    "estimated_start": (datetime.now(timezone.utc).timestamp() + seconds_until_offpeak)
                }
        
        # Find best worker
        worker = self._find_best_worker(data_size_bytes, size_class, priority)
        
        if worker:
            return {
                "worker_id": worker.worker_id,
                "schedule_now": True,
                "recommended_delay_seconds": 0,
                "should_batch": False,
                "batch_window_seconds": 0,
                "reasoning": f"Assigned to {worker.worker_type} worker (utilization: {worker.get_utilization():.1%})",
                "worker_type": worker.worker_type,
                "current_utilization": worker.get_utilization()
            }
        
        # Check if should batch tiny tasks
        if size_class == TaskSizeClass.TINY and priority != "critical":
            return {
                "worker_id": None,
                "schedule_now": False,
                "recommended_delay_seconds": 60,  # Wait 1 min for batching
                "should_batch": True,
                "batch_window_seconds": 300,  # 5 min batch window
                "reasoning": f"Tiny task ({format_bytes(data_size_bytes)}) - batch with similar tasks",
                "max_batch_size": self.max_batch_size
            }
        
        # No available worker - queue with delay
        return {
            "worker_id": None,
            "schedule_now": False,
            "recommended_delay_seconds": 30,
            "should_batch": False,
            "batch_window_seconds": 0,
            "reasoning": "All workers at capacity - delay and retry",
            "suggestion": "Consider scaling workers or adjusting task size"
        }
    
    def _find_best_worker(
        self,
        data_size_bytes: int,
        size_class: TaskSizeClass,
        priority: str
    ) -> Optional[WorkerProfile]:
        """
        Find best worker for task based on size and capacity
        
        Priority order:
        1. Workers that prefer this size class
        2. Workers with lowest utilization
        3. Workers with capacity
        """
        if not self.workers:
            return None
        
        # Filter workers that can accept task
        available_workers = [
            w for w in self.workers.values()
            if w.can_accept(data_size_bytes)
        ]
        
        if not available_workers:
            return None
        
        # Prefer workers that match size class
        preferred_workers = [
            w for w in available_workers
            if size_class in w.preferred_size_class
        ]
        
        # If critical priority, use any available worker
        if priority == "critical":
            candidates = available_workers
        else:
            candidates = preferred_workers if preferred_workers else available_workers
        
        # Sort by utilization (prefer less loaded workers)
        candidates.sort(key=lambda w: w.get_utilization())
        
        # Return least loaded worker
        return candidates[0] if candidates else None
    
    def _seconds_until_off_peak(self) -> int:
        """Calculate seconds until off-peak hours"""
        now = datetime.now(timezone.utc)
        current_time = now.time()
        
        # Convert times to seconds since midnight
        def time_to_seconds(t: time) -> int:
            return t.hour * 3600 + t.minute * 60 + t.second
        
        current_seconds = time_to_seconds(current_time)
        offpeak_seconds = time_to_seconds(self.off_peak_start)
        
        if current_seconds < offpeak_seconds:
            # Off-peak is later today
            return offpeak_seconds - current_seconds
        else:
            # Off-peak is tomorrow
            return (86400 - current_seconds) + offpeak_seconds
    
    async def update_worker_load(
        self,
        worker_id: str,
        task_started: bool,
        data_size_bytes: int
    ):
        """
        Update worker load when task starts/finishes
        
        Args:
            worker_id: Worker identifier
            task_started: True if task starting, False if finishing
            data_size_bytes: Task data size
        """
        if worker_id not in self.workers:
            return
        
        worker = self.workers[worker_id]
        
        if task_started:
            worker.current_load_bytes += data_size_bytes
            worker.current_task_count += 1
        else:
            worker.current_load_bytes = max(0, worker.current_load_bytes - data_size_bytes)
            worker.current_task_count = max(0, worker.current_task_count - 1)
    
    async def get_batched_tasks(
        self,
        max_batch_size: int = 50,
        max_total_bytes: int = 100 * 1024 * 1024  # 100 MB
    ) -> List[str]:
        """
        Get tasks eligible for batching
        
        Args:
            max_batch_size: Max tasks in batch
            max_total_bytes: Max total data size
            
        Returns:
            List of task_ids to batch
        """
        async with async_session() as session:
            # Find queued tiny/small tasks
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status == 'queued')
                .where(HTMTask.data_size_bytes.isnot(None))
                .where(HTMTask.data_size_bytes < self.batch_size_threshold)
                .order_by(HTMTask.created_at.asc())
                .limit(max_batch_size)
            )
            tasks = result.scalars().all()
        
        # Select tasks that fit in batch
        batch = []
        total_bytes = 0
        
        for task in tasks:
            if len(batch) >= max_batch_size:
                break
            if total_bytes + task.data_size_bytes > max_total_bytes:
                break
            
            batch.append(task.task_id)
            total_bytes += task.data_size_bytes
        
        return batch
    
    async def get_scheduling_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        total_capacity = sum(w.max_data_size_bytes for w in self.workers.values())
        total_load = sum(w.current_load_bytes for w in self.workers.values())
        
        overall_utilization = total_load / total_capacity if total_capacity > 0 else 0.0
        
        worker_stats = [
            {
                "worker_id": w.worker_id,
                "worker_type": w.worker_type,
                "utilization": w.get_utilization(),
                "current_tasks": w.current_task_count,
                "current_load": format_bytes(w.current_load_bytes),
                "capacity": format_bytes(w.max_data_size_bytes)
            }
            for w in self.workers.values()
        ]
        
        return {
            "total_workers": len(self.workers),
            "overall_utilization": overall_utilization,
            "total_capacity": format_bytes(total_capacity),
            "total_load": format_bytes(total_load),
            "is_off_peak": self.is_off_peak(),
            "seconds_until_off_peak": self._seconds_until_off_peak() if not self.is_off_peak() else 0,
            "workers": worker_stats
        }


# Global instance
htm_size_scheduler = HTMSizeAwareScheduler()

# Register default workers
htm_size_scheduler.register_worker("light_worker_1", "light", max_concurrent=10, max_data_gb=1.0)
htm_size_scheduler.register_worker("standard_worker_1", "standard", max_concurrent=5, max_data_gb=10.0)
htm_size_scheduler.register_worker("standard_worker_2", "standard", max_concurrent=5, max_data_gb=10.0)
htm_size_scheduler.register_worker("heavy_worker_1", "heavy", max_concurrent=2, max_data_gb=50.0)
