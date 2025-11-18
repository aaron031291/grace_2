"""
Job Queue - Background job processing with priority queue
"""

import uuid
import time
from enum import Enum
from typing import Optional, Callable, Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from queue import PriorityQueue
from threading import Thread, Lock
import traceback


class JobStatus(str, Enum):
    """Job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    """Job priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass(order=True)
class Job:
    """Background job"""
    priority: int = field(compare=True)
    job_id: str = field(compare=False)
    name: str = field(compare=False)
    func: Callable = field(compare=False, repr=False)
    args: tuple = field(default_factory=tuple, compare=False, repr=False)
    kwargs: dict = field(default_factory=dict, compare=False, repr=False)
    tenant_id: Optional[str] = field(default=None, compare=False)
    status: JobStatus = field(default=JobStatus.PENDING, compare=False)
    result: Any = field(default=None, compare=False, repr=False)
    error: Optional[str] = field(default=None, compare=False)
    created_at: float = field(default_factory=time.time, compare=False)
    started_at: Optional[float] = field(default=None, compare=False)
    completed_at: Optional[float] = field(default=None, compare=False)
    progress: float = field(default=0.0, compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)
    
    def duration_ms(self) -> Optional[float]:
        """Get job duration in milliseconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return None


class JobQueue:
    """Priority-based job queue with worker pool"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.queue: PriorityQueue = PriorityQueue()
        self.jobs: Dict[str, Job] = {}
        self.workers: List[Thread] = []
        self.running = False
        self.lock = Lock()
        
        self.total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
    
    def start(self):
        """Start worker threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = Thread(target=self._worker, name=f"JobWorker-{i}", daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self, wait: bool = True):
        """Stop worker threads"""
        self.running = False
        
        if wait:
            for worker in self.workers:
                worker.join(timeout=5)
        
        self.workers.clear()
    
    def submit(
        self,
        func: Callable,
        *args,
        name: Optional[str] = None,
        priority: JobPriority = JobPriority.NORMAL,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Job:
        """Submit a job to the queue"""
        job_id = str(uuid.uuid4())
        
        job = Job(
            priority=priority.value,
            job_id=job_id,
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            tenant_id=tenant_id,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self.total_jobs += 1
        
        self.queue.put(job)
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        tenant_id: Optional[str] = None
    ) -> List[Job]:
        """List jobs with optional filters"""
        with self.lock:
            jobs = list(self.jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]
        
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            return True
        return False
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        with self.lock:
            pending = sum(1 for j in self.jobs.values() if j.status == JobStatus.PENDING)
            running = sum(1 for j in self.jobs.values() if j.status == JobStatus.RUNNING)
        
        return {
            "total_jobs": self.total_jobs,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "pending_jobs": pending,
            "running_jobs": running,
            "queue_size": self.queue.qsize(),
            "workers": len(self.workers),
            "max_workers": self.max_workers
        }
    
    def _worker(self):
        """Worker thread that processes jobs"""
        while self.running:
            try:
                try:
                    job = self.queue.get(timeout=1)
                except:
                    continue
                
                if job.status == JobStatus.CANCELLED:
                    self.queue.task_done()
                    continue
                
                job.status = JobStatus.RUNNING
                job.started_at = time.time()
                
                try:
                    result = job.func(*job.args, **job.kwargs)
                    job.result = result
                    job.status = JobStatus.COMPLETED
                    
                    with self.lock:
                        self.completed_jobs += 1
                
                except Exception as e:
                    job.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                    job.status = JobStatus.FAILED
                    
                    with self.lock:
                        self.failed_jobs += 1
                
                finally:
                    job.completed_at = time.time()
                    job.progress = 100.0
                    self.queue.task_done()
            
            except Exception as e:
                print(f"Worker error: {e}")
                continue
