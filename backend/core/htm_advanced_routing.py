"""
HTM Advanced Routing - Task Origin Tagging & Workload Balancing

Features:
- Tag tasks by origin (filesystem, api, hunter, scheduler, user)
- Balance workload to prevent origin starvation
- Fair scheduling across all task sources
- Priority-aware round-robin
- Burst protection per origin

Prevents:
- API requests starving scheduled tasks
- Hunter alerts blocking user requests
- Filesystem events overwhelming system
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

from backend.models.htm_models import HTMTask
from backend.models.base_models import async_session
from backend.logging_utils import log_event
from sqlalchemy import select


class TaskOrigin(str, Enum):
    """Task origin classifications"""
    USER_REQUEST = "user_request"          # Direct user action
    FILESYSTEM_TRIGGER = "filesystem"      # File watcher, inotify
    EXTERNAL_API = "external_api"          # Webhook, API call
    HUNTER_ALERT = "hunter_alert"          # Security alert
    SCHEDULER = "scheduler"                # Cron, scheduled job
    INTENT = "intent"                      # Agentic brain intent
    REMEDIATION = "remediation"            # Auto-healing task
    INTERNAL = "internal"                  # System-initiated


@dataclass
class OriginQuota:
    """Per-origin workload quota"""
    origin: TaskOrigin
    max_concurrent: int           # Max tasks from this origin
    current_count: int = 0        # Currently running
    total_queued: int = 0         # In queue
    quota_percent: float = 0.0    # % of total capacity
    tasks_completed: int = 0
    tasks_starved: int = 0        # Times quota was full
    
    def available_slots(self) -> int:
        """How many more tasks this origin can run"""
        return max(0, self.max_concurrent - self.current_count)
    
    def is_starved(self) -> bool:
        """Check if origin is being starved"""
        return self.total_queued > 0 and self.current_count == 0


class HTMAdvancedRouter:
    """
    Advanced HTM routing with origin-aware workload balancing
    
    Ensures fair scheduling across all task sources:
    - User requests get priority but don't starve others
    - Hunter alerts processed promptly
    - Scheduled tasks run on time
    - Filesystem events don't flood system
    """
    
    def __init__(self, total_capacity: int = 50):
        self.total_capacity = total_capacity
        
        # Origin quotas (percentage of total capacity)
        self.origin_quotas = {
            TaskOrigin.USER_REQUEST: OriginQuota(
                origin=TaskOrigin.USER_REQUEST,
                max_concurrent=int(total_capacity * 0.30),  # 30%
                quota_percent=0.30
            ),
            TaskOrigin.INTENT: OriginQuota(
                origin=TaskOrigin.INTENT,
                max_concurrent=int(total_capacity * 0.25),  # 25%
                quota_percent=0.25
            ),
            TaskOrigin.HUNTER_ALERT: OriginQuota(
                origin=TaskOrigin.HUNTER_ALERT,
                max_concurrent=int(total_capacity * 0.15),  # 15%
                quota_percent=0.15
            ),
            TaskOrigin.EXTERNAL_API: OriginQuota(
                origin=TaskOrigin.EXTERNAL_API,
                max_concurrent=int(total_capacity * 0.10),  # 10%
                quota_percent=0.10
            ),
            TaskOrigin.SCHEDULER: OriginQuota(
                origin=TaskOrigin.SCHEDULER,
                max_concurrent=int(total_capacity * 0.10),  # 10%
                quota_percent=0.10
            ),
            TaskOrigin.FILESYSTEM_TRIGGER: OriginQuota(
                origin=TaskOrigin.FILESYSTEM_TRIGGER,
                max_concurrent=int(total_capacity * 0.05),  # 5%
                quota_percent=0.05
            ),
            TaskOrigin.REMEDIATION: OriginQuota(
                origin=TaskOrigin.REMEDIATION,
                max_concurrent=int(total_capacity * 0.03),  # 3%
                quota_percent=0.03
            ),
            TaskOrigin.INTERNAL: OriginQuota(
                origin=TaskOrigin.INTERNAL,
                max_concurrent=int(total_capacity * 0.02),  # 2%
                quota_percent=0.02
            ),
        }
        
        # Burst protection (max tasks per minute per origin)
        self.burst_limits = {
            TaskOrigin.FILESYSTEM_TRIGGER: 100,  # Limit filesystem floods
            TaskOrigin.EXTERNAL_API: 50,
            TaskOrigin.HUNTER_ALERT: 20,
            TaskOrigin.USER_REQUEST: 30,
            TaskOrigin.SCHEDULER: 10
        }
        
        # Burst tracking
        self.recent_tasks: Dict[TaskOrigin, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Stats
        self.stats = {
            "total_routed": 0,
            "starvation_prevented": 0,
            "burst_limited": 0,
            "quota_adjustments": 0
        }
        
        print(f"[HTM ROUTER] Initialized with {total_capacity} task capacity")
    
    def tag_task_origin(
        self,
        task_type: str,
        payload: Dict[str, Any],
        created_by: str
    ) -> TaskOrigin:
        """
        Determine task origin from context
        
        Args:
            task_type: Type of task
            payload: Task payload
            created_by: Who created the task
            
        Returns:
            TaskOrigin classification
        """
        # Check payload hints
        if payload.get("from_filesystem_trigger"):
            return TaskOrigin.FILESYSTEM_TRIGGER
        
        if payload.get("from_hunter_alert"):
            return TaskOrigin.HUNTER_ALERT
        
        if payload.get("from_external_api") or payload.get("webhook_trigger"):
            return TaskOrigin.EXTERNAL_API
        
        if payload.get("scheduled") or created_by == "scheduler":
            return TaskOrigin.SCHEDULER
        
        if payload.get("intent_id") or created_by == "agentic_brain":
            return TaskOrigin.INTENT
        
        if task_type == "remediation" or payload.get("auto_remediation"):
            return TaskOrigin.REMEDIATION
        
        if created_by in ["user", "api_user", "web_user"]:
            return TaskOrigin.USER_REQUEST
        
        # Default
        return TaskOrigin.INTERNAL
    
    async def route_task(
        self,
        task_id: str,
        task_type: str,
        priority: str,
        payload: Dict[str, Any],
        created_by: str,
        data_size_bytes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Route task with origin-aware balancing
        
        Args:
            task_id: Task identifier
            task_type: Type of task
            priority: Task priority
            payload: Task payload
            created_by: Creator
            data_size_bytes: Data size (optional)
            
        Returns:
            Routing decision with queue assignment
        """
        # Determine origin
        origin = self.tag_task_origin(task_type, payload, created_by)
        
        # Check burst limits
        if await self._is_burst_limited(origin):
            self.stats["burst_limited"] += 1
            
            return {
                "task_id": task_id,
                "origin": origin.value,
                "route": "delayed",
                "delay_seconds": 60,
                "reasoning": f"Burst limit reached for {origin.value} (max {self.burst_limits.get(origin, 0)}/min)",
                "action": "retry_later"
            }
        
        # Check origin quota
        quota = self.origin_quotas.get(origin)
        if not quota:
            origin = TaskOrigin.INTERNAL  # Fallback
            quota = self.origin_quotas[origin]
        
        # Update quota tracking
        quota.total_queued += 1
        
        # Check for starvation of other origins
        starved_origins = self._check_starvation()
        
        if starved_origins and origin not in starved_origins:
            # This origin has capacity, but others are starved
            # Temporarily reduce this origin's quota to help others
            if quota.current_count >= quota.max_concurrent * 0.8:
                self.stats["starvation_prevented"] += 1
                
                return {
                    "task_id": task_id,
                    "origin": origin.value,
                    "route": "deferred",
                    "delay_seconds": 30,
                    "reasoning": f"Deferring {origin.value} to prevent starvation of {[o.value for o in starved_origins]}",
                    "action": "fair_scheduling"
                }
        
        # Check if origin has available quota
        if quota.current_count >= quota.max_concurrent:
            # Origin at capacity
            if priority == "critical":
                # Critical tasks override quota
                return {
                    "task_id": task_id,
                    "origin": origin.value,
                    "route": "express",
                    "reasoning": "Critical priority overrides quota",
                    "action": "queue_high_priority"
                }
            else:
                # Queue for this origin
                quota.tasks_starved += 1
                
                return {
                    "task_id": task_id,
                    "origin": origin.value,
                    "route": "queued",
                    "queue_name": f"{origin.value}_queue",
                    "reasoning": f"Origin quota full ({quota.current_count}/{quota.max_concurrent})",
                    "action": "queue_by_origin"
                }
        
        # Route to appropriate queue
        self.stats["total_routed"] += 1
        
        return {
            "task_id": task_id,
            "origin": origin.value,
            "route": "accepted",
            "queue_name": f"{priority}_queue",
            "quota_used": f"{quota.current_count + 1}/{quota.max_concurrent}",
            "reasoning": f"Routed to {priority} queue",
            "action": "schedule_now"
        }
    
    async def _is_burst_limited(self, origin: TaskOrigin) -> bool:
        """Check if origin is burst-limited"""
        if origin not in self.burst_limits:
            return False
        
        # Count recent tasks from this origin
        now = datetime.now(timezone.utc)
        one_minute_ago = now - timedelta(minutes=1)
        
        recent = self.recent_tasks[origin]
        
        # Remove old entries
        while recent and recent[0] < one_minute_ago:
            recent.popleft()
        
        # Check limit
        limit = self.burst_limits[origin]
        if len(recent) >= limit:
            return True
        
        # Add this task
        recent.append(now)
        return False
    
    def _check_starvation(self) -> List[TaskOrigin]:
        """Check for starved origins"""
        starved = []
        
        for origin, quota in self.origin_quotas.items():
            if quota.is_starved():
                starved.append(origin)
        
        return starved
    
    async def update_origin_count(
        self,
        origin: TaskOrigin,
        started: bool
    ):
        """
        Update running count for origin
        
        Args:
            origin: Task origin
            started: True if task starting, False if finishing
        """
        quota = self.origin_quotas.get(origin)
        if not quota:
            return
        
        if started:
            quota.current_count += 1
        else:
            quota.current_count = max(0, quota.current_count - 1)
            quota.tasks_completed += 1
            quota.total_queued = max(0, quota.total_queued - 1)
    
    async def adjust_quotas(self):
        """
        Dynamically adjust quotas based on demand
        
        Reallocates capacity from underutilized origins to busy ones
        """
        # Find underutilized origins
        underutilized = []
        overutilized = []
        
        for origin, quota in self.origin_quotas.items():
            utilization = quota.current_count / quota.max_concurrent if quota.max_concurrent > 0 else 0
            
            if utilization < 0.3 and quota.total_queued == 0:
                # Underutilized
                underutilized.append(origin)
            elif utilization > 0.9 and quota.total_queued > 5:
                # Overutilized
                overutilized.append(origin)
        
        # Reallocate if needed
        if underutilized and overutilized:
            # Temporarily give 1 slot from underutilized to overutilized
            for under_origin in underutilized[:1]:
                for over_origin in overutilized[:1]:
                    under_quota = self.origin_quotas[under_origin]
                    over_quota = self.origin_quotas[over_origin]
                    
                    if under_quota.max_concurrent > 1:
                        under_quota.max_concurrent -= 1
                        over_quota.max_concurrent += 1
                        
                        self.stats["quota_adjustments"] += 1
                        
                        print(f"[HTM ROUTER] Adjusted quota: {under_origin.value} -1, {over_origin.value} +1")
                        
                        # Log adjustment
                        log_event(
                            action="htm.quota.adjusted",
                            actor="htm_router",
                            resource="workload_balance",
                            outcome="rebalanced",
                            payload={
                                "from_origin": under_origin.value,
                                "to_origin": over_origin.value,
                                "reason": "demand_based_reallocation"
                            }
                        )
    
    async def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        origin_stats = {}
        
        for origin, quota in self.origin_quotas.items():
            utilization = quota.current_count / quota.max_concurrent if quota.max_concurrent > 0 else 0
            
            origin_stats[origin.value] = {
                "max_concurrent": quota.max_concurrent,
                "current_count": quota.current_count,
                "total_queued": quota.total_queued,
                "utilization": utilization,
                "quota_percent": quota.quota_percent,
                "tasks_completed": quota.tasks_completed,
                "tasks_starved": quota.tasks_starved,
                "burst_limit": self.burst_limits.get(origin)
            }
        
        return {
            "total_capacity": self.total_capacity,
            "origins": origin_stats,
            "stats": self.stats
        }
    
    async def get_next_task(self) -> Optional[str]:
        """
        Get next task to execute using fair scheduling
        
        Returns:
            task_id or None
        """
        # Load queued tasks grouped by origin
        async with async_session() as session:
            result = await session.execute(
                select(HTMTask)
                .where(HTMTask.status == 'queued')
                .order_by(HTMTask.created_at.asc())
            )
            queued_tasks = result.scalars().all()
        
        if not queued_tasks:
            return None
        
        # Group by origin and priority
        by_origin_priority: Dict[Tuple[str, str], List[HTMTask]] = defaultdict(list)
        
        for task in queued_tasks:
            origin = task.payload.get("origin", TaskOrigin.INTERNAL.value)
            by_origin_priority[(origin, task.priority)].append(task)
        
        # Round-robin across origins, respecting quotas
        # Priority order: critical > high > normal > low
        for priority in ["critical", "high", "normal", "low"]:
            for origin_enum in self.origin_quotas.keys():
                origin = origin_enum.value
                quota = self.origin_quotas[origin_enum]
                
                # Check if origin has capacity
                if quota.current_count >= quota.max_concurrent:
                    continue
                
                # Get tasks for this origin+priority
                tasks = by_origin_priority.get((origin, priority), [])
                
                if tasks:
                    # Return first task
                    selected_task = tasks[0]
                    
                    print(f"[HTM ROUTER] Selected task {selected_task.task_id} from {origin} ({priority})")
                    
                    return selected_task.task_id
        
        # No task found within quotas
        # Check for starved origins and allow one task through
        starved = self._check_starvation()
        if starved:
            for origin in starved:
                tasks = [
                    t for tasks in by_origin_priority.values() for t in tasks
                    if t.payload.get("origin") == origin.value
                ]
                
                if tasks:
                    # Allow one starved task through
                    print(f"[HTM ROUTER] Anti-starvation: allowing {origin.value} task")
                    return tasks[0].task_id
        
        return None


# Global instance
htm_router = HTMAdvancedRouter(total_capacity=50)
