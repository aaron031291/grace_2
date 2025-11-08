import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .models import Base, async_session

class ExecutionTask(Base):
    __tablename__ = "execution_tasks"
    id = Column(Integer, primary_key=True)
    task_id = Column(String(64), unique=True, nullable=False)
    user = Column(String(64), nullable=False)
    task_type = Column(String(64), nullable=False)
    description = Column(Text)
    status = Column(String(32), default="queued")
    progress = Column(Float, default=0.0)
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

class TaskExecutor:
    def __init__(self):
        self.running_tasks: Dict[str, dict] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.max_parallel = 3
        self.workers: List[asyncio.Task] = []
    
    async def start_workers(self):
        """Start background worker pool"""
        for i in range(self.max_parallel):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
        print(f"[OK] Task executor started ({self.max_parallel} parallel workers)")
    
    async def stop_workers(self):
        """Stop all workers"""
        for worker in self.workers:
            worker.cancel()
        self.workers.clear()
        print("[OK] Task executor stopped")
    
    async def _worker(self, worker_id: int):
        """Background worker that processes tasks"""
        while True:
            try:
                task_id, user, task_type, task_func = await self.task_queue.get()
                
                self.running_tasks[task_id] = {
                    "status": "running",
                    "progress": 0.0,
                    "worker_id": worker_id
                }
                
                async with async_session() as session:
                    from sqlalchemy import update
                    await session.execute(
                        update(ExecutionTask)
                        .where(ExecutionTask.task_id == task_id)
                        .values(status='running', started_at=datetime.utcnow())
                    )
                    await session.commit()
                
                try:
                    result = await task_func(task_id, self._update_progress)
                    
                    async with async_session() as session:
                        from sqlalchemy import update
                        await session.execute(
                            update(ExecutionTask)
                            .where(ExecutionTask.task_id == task_id)
                            .values(status='completed', progress=100.0, result=str(result), completed_at=datetime.utcnow())
                        )
                        await session.commit()
                    
                    self.running_tasks[task_id]["status"] = "completed"
                    self.running_tasks[task_id]["progress"] = 100.0
                    
                    print(f"[OK] Worker {worker_id}: Task {task_id} completed")
                    
                except Exception as e:
                    async with async_session() as session:
                        from sqlalchemy import update
                        await session.execute(
                            update(ExecutionTask)
                            .where(ExecutionTask.task_id == task_id)
                            .values(status='failed', error=str(e), completed_at=datetime.utcnow())
                        )
                        await session.commit()
                    
                    self.running_tasks[task_id]["status"] = "failed"
                    self.running_tasks[task_id]["error"] = str(e)
                    
                    print(f"[FAIL] Worker {worker_id}: Task {task_id} failed: {e}")
                
                finally:
                    self.task_queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
    
    async def _update_progress(self, task_id: str, progress: float):
        """Update task progress (called by task functions)"""
        if task_id in self.running_tasks:
            self.running_tasks[task_id]["progress"] = min(100.0, max(0.0, progress))
            
            async with async_session() as session:
                from sqlalchemy import update
                await session.execute(
                    update(ExecutionTask)
                    .where(ExecutionTask.task_id == task_id)
                    .values(progress=progress)
                )
                await session.commit()
    
    async def submit_task(
        self,
        user: str,
        task_type: str,
        description: str,
        task_func: Callable
    ) -> str:
        """Submit a task for background execution"""
        task_id = str(uuid.uuid4())[:8]
        
        async with async_session() as session:
            exec_task = ExecutionTask(
                task_id=task_id,
                user=user,
                task_type=task_type,
                description=description,
                status="queued"
            )
            session.add(exec_task)
            await session.commit()
        
        await self.task_queue.put((task_id, user, task_type, task_func))
        
        self.running_tasks[task_id] = {
            "status": "queued",
            "progress": 0.0,
            "type": task_type
        }
        
        print(f"[OK] Task queued: {task_id} ({task_type})")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get current task status and progress"""
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ExecutionTask).where(ExecutionTask.task_id == task_id)
            )
            task = result.scalar_one_or_none()
            if task:
                return {
                    "status": task.status,
                    "progress": task.progress,
                    "result": task.result,
                    "error": task.error
                }
        return None
    
    async def list_tasks(self, user: str, limit: int = 20) -> List[dict]:
        """List all execution tasks for a user"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(ExecutionTask)
                .where(ExecutionTask.user == user)
                .order_by(ExecutionTask.created_at.desc())
                .limit(limit)
            )
            tasks = result.scalars().all()
            return [
                {
                    "task_id": t.task_id,
                    "type": t.task_type,
                    "description": t.description,
                    "status": t.status,
                    "progress": t.progress,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at
                }
                for t in tasks
            ]

task_executor = TaskExecutor()
