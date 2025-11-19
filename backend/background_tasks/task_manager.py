"""
Background Task Manager - Monitor and control Grace's background work

Features:
- Track running jobs/missions
- Show progress and status
- Allow pause/resume/cancel
- Proactive notifications when complete or needing input
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4
from enum import Enum

from backend.event_bus import event_bus, Event, EventType


class TaskStatus(str, Enum):
    """Background task status"""
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_INPUT = "needs_input"
    CANCELLED = "cancelled"


class BackgroundTask:
    """A background task/job/mission"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        description: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.user_id = user_id
        self.status = TaskStatus.QUEUED
        self.progress = 0.0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Any] = None
        self.metadata = metadata or {}
        self.logs: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status.value,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
            "logs": self.logs[-10:],  # Last 10 log entries
        }


class BackgroundTaskManager:
    """
    Manages all background tasks
    
    Provides:
    - Task creation and tracking
    - Progress monitoring
    - Proactive notifications
    - Pause/resume/cancel controls
    """
    
    def __init__(self):
        self.tasks: Dict[str, BackgroundTask] = {}
    
    async def create_task(
        self,
        task_type: str,
        description: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new background task
        
        Args:
            task_type: Type (data_import, deployment, training, etc.)
            description: Human-readable description
            user_id: User who initiated
            metadata: Additional metadata
        
        Returns:
            task_id
        """
        task_id = f"task_{uuid4().hex[:12]}"
        
        task = BackgroundTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            user_id=user_id,
            metadata=metadata
        )
        
        self.tasks[task_id] = task
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.TASK_STARTED,
            source="background_task_manager",
            data={
                "task_id": task_id,
                "task_type": task_type,
                "description": description,
                "user_id": user_id,
            }
        ))
        
        # Notify user
        from backend.routes.notifications_api import notify_user
        await notify_user(
            user_id=user_id,
            notification_type="task_started",
            message=f"🚀 Started: {description}",
            data={"task_id": task_id},
            badge="🚀"
        )
        
        print(f"[BackgroundTaskManager] Created task: {task_id}")
        return task_id
    
    async def update_progress(
        self,
        task_id: str,
        progress: float,
        log_message: Optional[str] = None
    ):
        """Update task progress"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.progress = progress
        
        if log_message:
            task.logs.append(f"{datetime.utcnow().isoformat()}: {log_message}")
        
        # Notify on significant progress milestones
        if progress in [0.25, 0.5, 0.75, 1.0]:
            from backend.routes.notifications_api import notify_user
            await notify_user(
                user_id=task.user_id,
                notification_type="task_progress",
                message=f"📊 {task.description}: {int(progress * 100)}% complete",
                data={"task_id": task_id, "progress": progress},
                badge="📊"
            )
    
    async def complete_task(
        self,
        task_id: str,
        result: Optional[Any] = None
    ):
        """Mark task as completed"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.result = result
        task.progress = 1.0
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.TASK_COMPLETED,
            source="background_task_manager",
            data={
                "task_id": task_id,
                "result": result,
                "duration_seconds": (task.completed_at - task.started_at).total_seconds() if task.started_at else 0
            }
        ))
        
        # Proactive notification
        from backend.routes.notifications_api import notify_user
        await notify_user(
            user_id=task.user_id,
            notification_type="task_completed",
            message=f"✅ Completed: {task.description}",
            data={"task_id": task_id, "result": result},
            badge="✅"
        )
        
        print(f"[BackgroundTaskManager] Task completed: {task_id}")
    
    async def fail_task(
        self,
        task_id: str,
        error: str
    ):
        """Mark task as failed"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        task.error = error
        
        # Publish event
        await event_bus.publish(Event(
            event_type=EventType.TASK_COMPLETED,
            source="background_task_manager",
            data={
                "task_id": task_id,
                "status": "failed",
                "error": error
            }
        ))
        
        # Proactive notification
        from backend.routes.notifications_api import notify_user
        await notify_user(
            user_id=task.user_id,
            notification_type="task_failed",
            message=f"❌ Failed: {task.description} - {error}",
            data={"task_id": task_id, "error": error},
            badge="❌"
        )
        
        print(f"[BackgroundTaskManager] Task failed: {task_id}")
    
    async def request_input(
        self,
        task_id: str,
        prompt: str,
        options: Optional[List[str]] = None
    ):
        """Request user input for task"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.NEEDS_INPUT
        task.metadata["input_prompt"] = prompt
        task.metadata["input_options"] = options
        
        # Proactive notification
        from backend.routes.notifications_api import notify_user
        await notify_user(
            user_id=task.user_id,
            notification_type="task_needs_input",
            message=f"❓ {task.description}: {prompt}",
            data={
                "task_id": task_id,
                "prompt": prompt,
                "options": options
            },
            badge="❓"
        )
        
        print(f"[BackgroundTaskManager] Task needs input: {task_id}")
    
    async def provide_input(
        self,
        task_id: str,
        input_value: Any
    ):
        """Provide user input to continue task"""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.metadata["user_input"] = input_value
        
        # Clear input prompt
        task.metadata.pop("input_prompt", None)
        task.metadata.pop("input_options", None)
        
        print(f"[BackgroundTaskManager] Input provided for task: {task_id}")
    
    def get_active_tasks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        active = []
        
        for task in self.tasks.values():
            if task.status in [TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.NEEDS_INPUT]:
                if user_id is None or task.user_id == user_id:
                    active.append(task.to_dict())
        
        return sorted(active, key=lambda t: t["started_at"] or "", reverse=True)
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get specific task"""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return None


# Global instance
background_task_manager = BackgroundTaskManager()
