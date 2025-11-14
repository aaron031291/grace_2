"""
Async Job Orchestration

Lightweight task queue for long-running verification, benchmark runs, and data aggregation.
Uses FastAPI BackgroundTasks for simple cases, with hooks for future migration to arq/Dramatiq.

Benefits:
- Keeps HTTP responses snappy
- Enables retries and progress tracking
- Decouples execution from request lifecycle
"""

import asyncio
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
import traceback
from dataclasses import dataclass, field

from .immutable_log import immutable_log
from .trigger_mesh import trigger_mesh, TriggerEvent


class JobStatus(Enum):
    """Job execution statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class JobResult:
    """Result of an async job execution"""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "metadata": self.metadata
        }


class AsyncJobQueue:
    """
    Lightweight async job queue for verification and benchmark tasks.
    
    Features:
    - Automatic retries with exponential backoff
    - Progress tracking
    - Correlation with contracts and missions
    - Event emission for observability
    """
    
    def __init__(self):
        self.jobs: Dict[str, JobResult] = {}
        self._running = False
    
    async def enqueue(
        self,
        job_id: str,
        task_func: Callable,
        *args,
        job_type: str = "generic",
        max_attempts: int = 3,
        contract_id: Optional[int] = None,
        mission_id: Optional[str] = None,
        **kwargs
    ) -> JobResult:
        """
        Enqueue a background job for async execution.
        
        Args:
            job_id: Unique identifier for the job
            task_func: Async function to execute
            job_type: Type of job (benchmark, verification, aggregation)
            max_attempts: Maximum retry attempts
            contract_id: Associated contract ID
            mission_id: Associated mission ID
            *args, **kwargs: Arguments passed to task_func
            
        Returns:
            JobResult with initial pending status
        """
        
        job = JobResult(
            job_id=job_id,
            status=JobStatus.PENDING,
            max_attempts=max_attempts,
            metadata={
                "job_type": job_type,
                "contract_id": contract_id,
                "mission_id": mission_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        self.jobs[job_id] = job
        
        # Log job creation
        await immutable_log.append(
            actor="async_job_queue",
            action="job_enqueued",
            resource=job_id,
            subsystem="background_jobs",
            payload={
                "job_type": job_type,
                "contract_id": contract_id,
                "mission_id": mission_id
            },
            result="enqueued"
        )
        
        # Emit event
        await trigger_mesh.publish(TriggerEvent(
            event_type="job.enqueued",
            source="async_job_queue",
            actor="system",
            resource=job_id,
            payload=job.to_dict(),
            timestamp=datetime.now(timezone.utc)
        ))
        
        # Execute in background
        asyncio.create_task(self._execute_job(job_id, task_func, *args, **kwargs))
        
        return job
    
    async def _execute_job(
        self,
        job_id: str,
        task_func: Callable,
        *args,
        **kwargs
    ):
        """Execute a job with retry logic"""
        
        job = self.jobs.get(job_id)
        if not job:
            return
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.attempts += 1
        
        # Emit running event
        await trigger_mesh.publish(TriggerEvent(
            event_type="job.running",
            source="async_job_queue",
            actor="system",
            resource=job_id,
            payload=job.to_dict(),
            timestamp=datetime.now(timezone.utc)
        ))
        
        try:
            # Execute the task
            result = await task_func(*args, **kwargs)
            
            # Success
            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.now(timezone.utc)
            
            # Log success
            await immutable_log.append(
                actor="async_job_queue",
                action="job_completed",
                resource=job_id,
                subsystem="background_jobs",
                payload={
                    "attempts": job.attempts,
                    "duration_ms": (job.completed_at - job.started_at).total_seconds() * 1000
                },
                result="success"
            )
            
            # Emit completion event
            await trigger_mesh.publish(TriggerEvent(
                event_type="job.completed",
                source="async_job_queue",
                actor="system",
                resource=job_id,
                payload=job.to_dict(),
                timestamp=datetime.now(timezone.utc)
            ))
            
        except Exception as e:
            # Failure
            job.error = str(e)
            error_trace = traceback.format_exc()
            
            # Retry logic
            if job.attempts < job.max_attempts:
                job.status = JobStatus.RETRYING
                
                # Exponential backoff: 2^attempt seconds
                backoff_seconds = 2 ** job.attempts
                
                await immutable_log.append(
                    actor="async_job_queue",
                    action="job_retry",
                    resource=job_id,
                    subsystem="background_jobs",
                    payload={
                        "attempts": job.attempts,
                        "error": str(e),
                        "backoff_seconds": backoff_seconds
                    },
                    result="retrying"
                )
                
                # Emit retry event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="job.retrying",
                    source="async_job_queue",
                    actor="system",
                    resource=job_id,
                    payload={**job.to_dict(), "backoff_seconds": backoff_seconds},
                    timestamp=datetime.now(timezone.utc)
                ))
                
                # Schedule retry
                await asyncio.sleep(backoff_seconds)
                await self._execute_job(job_id, task_func, *args, **kwargs)
                
            else:
                # Max retries exceeded
                job.status = JobStatus.FAILED
                job.completed_at = datetime.now(timezone.utc)
                
                await immutable_log.append(
                    actor="async_job_queue",
                    action="job_failed",
                    resource=job_id,
                    subsystem="background_jobs",
                    payload={
                        "attempts": job.attempts,
                        "error": str(e),
                        "trace": error_trace
                    },
                    result="failed"
                )
                
                # Emit failure event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="job.failed",
                    source="async_job_queue",
                    actor="system",
                    resource=job_id,
                    payload=job.to_dict(),
                    timestamp=datetime.now(timezone.utc)
                ))
    
    def get_job(self, job_id: str) -> Optional[JobResult]:
        """Get job status and result"""
        return self.jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[str] = None,
        limit: int = 100
    ) -> List[JobResult]:
        """List jobs with optional filtering"""
        
        jobs = list(self.jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        if job_type:
            jobs = [j for j in jobs if j.metadata.get("job_type") == job_type]
        
        # Sort by started_at descending
        jobs.sort(key=lambda j: j.started_at or datetime.min, reverse=True)
        
        return jobs[:limit]
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.RETRYING]:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(timezone.utc)
            
            await immutable_log.append(
                actor="async_job_queue",
                action="job_cancelled",
                resource=job_id,
                subsystem="background_jobs",
                payload={},
                result="cancelled"
            )
            
            await trigger_mesh.publish(TriggerEvent(
                event_type="job.cancelled",
                source="async_job_queue",
                actor="system",
                resource=job_id,
                payload=job.to_dict(),
                timestamp=datetime.now(timezone.utc)
            ))
            
            return True
        
        return False


# Global singleton
async_job_queue = AsyncJobQueue()


# Common job templates

async def run_benchmark_job(contract_id: int, benchmark_type: str = "post_action"):
    """Job template for running benchmarks"""
    from .benchmarks import benchmark_suite
    
    result = await benchmark_suite.run_benchmark(
        benchmark_type=benchmark_type,
        action_contract_id=contract_id
    )
    
    return {
        "benchmark_id": result.id if hasattr(result, "id") else None,
        "passed": result.passed if hasattr(result, "passed") else False,
        "score": result.score if hasattr(result, "score") else 0.0
    }


async def run_verification_job(contract_id: int):
    """Job template for contract verification"""
    from .action_contract import contract_verifier
    
    result = await contract_verifier.verify_contract(contract_id)
    
    return {
        "contract_id": contract_id,
        "verified": result.get("verified", False),
        "violations": result.get("violations", [])
    }


async def run_aggregation_job(aggregation_type: str, hours_back: int = 24):
    """Job template for data aggregation"""
    from .routes.learning import aggregate_learning_data
    
    result = await aggregate_learning_data(hours_back=hours_back)
    
    return {
        "aggregation_type": aggregation_type,
        "records_processed": result.get("count", 0),
        "summary": result.get("summary", {})
    }
