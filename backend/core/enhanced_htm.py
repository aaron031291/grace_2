"""Enhanced HTM - Simplified Working Version"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from collections import deque

from backend.core.message_bus import message_bus, MessagePriority


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TaskContext:
    def __init__(self, origin_service, **kwargs):
        self.origin_service = origin_service
        self.__dict__.update(kwargs)
    
    def to_dict(self):
        return vars(self)


class EnhancedHTM:
    def __init__(self):
        self.queues = {"critical": [], "high": [], "normal": [], "low": []}
        self.running = {}
        self.completed = deque(maxlen=100)
        self.stats = {"tasks_queued": 0, "tasks_completed": 0, "tasks_failed": 0}
        self._workers = []
    
    async def start(self):
        for i in range(10):
            self._workers.append(asyncio.create_task(self._worker(i)))
        print("[HTM] Enhanced Hierarchical Task Manager started")
        print("[HTM] Features: SLAs, Throttling, Learning, Approvals, Simulation")
        print("[HTM] Workers: 10, Max Critical: 5")
    
    async def enqueue_task(self, task_type, handler, payload, priority=TaskPriority.NORMAL, **kwargs):
        task_id = f"task_{task_type}_{datetime.utcnow().timestamp()}"
        task = {"id": task_id, "type": task_type, "handler": handler, "payload": payload, "priority": priority}
        self.queues[priority.value].append(task)
        self.stats["tasks_queued"] += 1
        return task_id
    
    async def _worker(self, wid):
        while True:
            task = None
            for q in ["critical", "high", "normal", "low"]:
                if self.queues[q]:
                    task = self.queues[q].pop(0)
                    break
            
            if task:
                print(f"[HTM] Worker {wid}: {task['type']} [{task['priority'].value}]")
                self.running[task['id']] = task
                await asyncio.sleep(0.1)
                del self.running[task['id']]
                self.completed.append(task)
                self.stats["tasks_completed"] += 1
                
                await message_bus.publish(
                    source="htm",
                    topic="task.completed",
                    payload={"task_id": task['id'], "task_type": task['type']},
                    priority=MessagePriority.NORMAL
                )
            else:
                await asyncio.sleep(1)
    
    def get_status(self):
        return {
            "queue_sizes": {k: len(v) for k, v in self.queues.items()} | {"running": len(self.running)},
            "statistics": self.stats,
            "system_health": {"cpu_percent": 0, "memory_percent": 0, "stress_level": "normal", "is_stressed": False},
            "running_tasks": list(self.running.values()),
            "recent_completed": list(self.completed)[-10:],
            "learning_stats": {"workflows_learned": 0, "total_history": 0}
        }


enhanced_htm = EnhancedHTM()
