"""
Task Registry Service
Unified task tracking across all Grace subsystems

Every component (healing, coding, learning, ML/DL, RAG, etc.) reports:
- Task creation (task.created)
- Task updates (task.updated)
- Task completion (task.completed)
- Task failure (task.failed)

Provides:
- Single source of truth for task status
- Resource usage tracking and forecasting
- Verification enforcement
- Anomaly detection
- Cross-subsystem visibility
"""

import asyncio
import logging
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update as sql_update, and_, or_, func
from sqlalchemy.exc import IntegrityError

from backend.models.task_registry_models import (
    TaskRegistryEntry,
    TaskResourceSnapshot,
    TaskDependency,
    SubsystemTaskMetrics
)
from backend.models.base_models import async_session
from backend.core.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class TaskRegistry:
    """
    Centralized task registry for all Grace subsystems
    
    Subsystems that report here:
    - Self-healing playbooks
    - Coding agent work orders
    - Learning missions
    - Guardian tasks
    - ML/DL training jobs
    - RAG index builds
    - Remote access operations
    - Chaos campaigns
    """
    
    def __init__(self):
        self.running = False
        self.message_bus = None
        
        # Resource tracking for active tasks
        self.active_task_resources: Dict[str, Dict[str, Any]] = {}
        
        # Metrics cache
        self.subsystem_metrics_cache = {}
        self.last_metrics_update = None
        
    async def start(self):
        """Start the task registry and subscribe to events"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to message bus events
        try:
            from backend.core.message_bus import message_bus
            self.message_bus = message_bus
            
            # Subscribe to task events
            await self.message_bus.subscribe('task.created', self._handle_task_created)
            await self.message_bus.subscribe('task.started', self._handle_task_started)
            await self.message_bus.subscribe('task.updated', self._handle_task_updated)
            await self.message_bus.subscribe('task.completed', self._handle_task_completed)
            await self.message_bus.subscribe('task.failed', self._handle_task_failed)
            
            # Mission-specific events (for backward compatibility)
            await self.message_bus.subscribe('mission.created', self._handle_mission_event)
            await self.message_bus.subscribe('mission.completed', self._handle_mission_event)
            await self.message_bus.subscribe('mission.failed', self._handle_mission_event)
            
            logger.info("[TASK-REGISTRY] ✅ Subscribed to task events on message bus")
        except Exception as e:
            logger.warning(f"[TASK-REGISTRY] Message bus not available: {e}")
        
        # Start background resource tracking
        asyncio.create_task(self._resource_tracking_loop())
        
        # Start periodic metrics calculation
        asyncio.create_task(self._metrics_calculation_loop())
        
        logger.info("[TASK-REGISTRY] ✅ Started - Unified task tracking active")
    
    async def register_task(
        self,
        task_id: str,
        task_type: str,
        subsystem: str,
        title: str,
        created_by: str,
        description: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: int = 5,
        verification_required: bool = True,
        sla_hours: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a new task in the registry
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task (mission, playbook, work_order, training_job, etc.)
            subsystem: Which subsystem owns this (healing, coding_agent, learning, etc.)
            title: Human-readable title
            created_by: Who/what created this task
            description: Detailed description
            assigned_to: Who/what will execute this
            priority: 1-10, higher = more urgent
            verification_required: Whether verification is needed
            sla_hours: SLA in hours (None = no SLA)
            metadata: Additional metadata
            
        Returns:
            True if registered, False if duplicate
        """
        
        try:
            async with async_session() as session:
                # Check if already exists
                result = await session.execute(
                    select(TaskRegistryEntry).where(TaskRegistryEntry.task_id == task_id)
                )
                if result.scalar_one_or_none():
                    logger.debug(f"[TASK-REGISTRY] Task already registered: {task_id}")
                    return False
                
                # Calculate SLA deadline
                sla_deadline = None
                if sla_hours:
                    sla_deadline = datetime.now(timezone.utc) + timedelta(hours=sla_hours)
                
                # Create task entry
                task = TaskRegistryEntry(
                    task_id=task_id,
                    task_type=task_type,
                    subsystem=subsystem,
                    title=title,
                    description=description,
                    created_by=created_by,
                    assigned_to=assigned_to or subsystem,
                    status='pending',
                    priority=priority,
                    verification_required=verification_required,
                    verification_status='pending' if verification_required else 'skipped',
                    sla_deadline=sla_deadline,
                    metadata=metadata
                )
                
                session.add(task)
                await session.flush()
                await session.commit()
                
                logger.info(f"[TASK-REGISTRY] ✅ Registered: {task_id} ({subsystem}/{task_type})")
                
                # Log to immutable log
                await immutable_log.log_event(
                    actor=created_by,
                    action='task_registered',
                    resource=task_id,
                    result='success',
                    metadata={
                        'task_type': task_type,
                        'subsystem': subsystem,
                        'priority': priority
                    }
                )
                
                # Publish event
                if self.message_bus:
                    await self.message_bus.publish('task.registered', {
                        'task_id': task_id,
                        'subsystem': subsystem,
                        'task_type': task_type,
                        'created_by': created_by
                    })
                
                return True
                
        except IntegrityError:
            logger.warning(f"[TASK-REGISTRY] Duplicate task_id: {task_id}")
            return False
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to register task: {e}")
            return False
    
    async def start_task(self, task_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Mark task as started and begin resource tracking"""
        
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(TaskRegistryEntry).where(TaskRegistryEntry.task_id == task_id)
                )
                task = result.scalar_one_or_none()
                
                if not task:
                    logger.warning(f"[TASK-REGISTRY] Task not found: {task_id}")
                    return False
                
                # Update task
                task.status = 'active'
                task.started_at = datetime.now(timezone.utc)
                
                if metadata:
                    current_meta = task.metadata or {}
                    current_meta.update(metadata)
                    task.metadata = current_meta
                
                await session.commit()
                
                logger.info(f"[TASK-REGISTRY] ▶️  Started: {task_id}")
                
                # Initialize resource tracking
                self.active_task_resources[task_id] = {
                    'start_time': datetime.now(timezone.utc),
                    'start_cpu': psutil.cpu_percent(),
                    'start_memory': psutil.virtual_memory().used / (1024 * 1024),  # MB
                    'start_disk_read': psutil.disk_io_counters().read_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                    'start_disk_write': psutil.disk_io_counters().write_bytes / (1024 * 1024) if psutil.disk_io_counters() else 0,
                    'snapshots': []
                }
                
                # Log to immutable log
                await immutable_log.log_event(
                    actor=task.subsystem,
                    action='task_started',
                    resource=task_id,
                    result='success'
                )
                
                return True
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to start task: {e}")
            return False
    
    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
        verification_passed: bool = True,
        resource_usage: Optional[Dict[str, float]] = None,
        ml_metrics: Optional[Dict[str, Any]] = None,
        result_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark task as completed with verification and resource usage
        
        Args:
            task_id: Task identifier
            success: Whether task succeeded
            verification_passed: Whether verification checks passed
            resource_usage: Resource deltas (cpu_seconds, memory_mb, disk_mb, etc.)
            ml_metrics: ML/DL specific metrics (dataset_size_mb, vectors, tokens, etc.)
            result_metadata: Additional result data
            
        Returns:
            True if completed successfully
        """
        
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(TaskRegistryEntry).where(TaskRegistryEntry.task_id == task_id)
                )
                task = result.scalar_one_or_none()
                
                if not task:
                    logger.warning(f"[TASK-REGISTRY] Task not found: {task_id}")
                    return False
                
                # Calculate duration
                completed_at = datetime.now(timezone.utc)
                if task.started_at:
                    duration = (completed_at - task.started_at).total_seconds()
                else:
                    duration = None
                
                # Update task
                task.status = 'completed' if success else 'failed'
                task.completed_at = completed_at
                task.duration_seconds = duration
                
                # Verification
                if task.verification_required:
                    task.verification_status = 'passed' if verification_passed else 'failed'
                    if verification_passed:
                        task.verification_passes += 1
                    else:
                        task.verification_failures += 1
                
                # SLA check
                if task.sla_deadline:
                    task.sla_met = completed_at <= task.sla_deadline
                
                # Resource usage
                if resource_usage:
                    task.cpu_seconds = resource_usage.get('cpu_seconds')
                    task.memory_peak_mb = resource_usage.get('memory_peak_mb')
                    task.memory_avg_mb = resource_usage.get('memory_avg_mb')
                    task.disk_read_mb = resource_usage.get('disk_read_mb')
                    task.disk_write_mb = resource_usage.get('disk_write_mb')
                    task.network_tx_mb = resource_usage.get('network_tx_mb')
                    task.network_rx_mb = resource_usage.get('network_rx_mb')
                    task.storage_delta_mb = resource_usage.get('storage_delta_mb')
                
                # ML/DL metrics
                if ml_metrics:
                    task.dataset_size_mb = ml_metrics.get('dataset_size_mb')
                    task.vectors_processed = ml_metrics.get('vectors_processed')
                    task.tokens_processed = ml_metrics.get('tokens_processed')
                    task.model_size_mb = ml_metrics.get('model_size_mb')
                    task.epochs_completed = ml_metrics.get('epochs_completed')
                
                # Result metadata
                if result_metadata:
                    current_meta = task.metadata or {}
                    current_meta['result'] = result_metadata
                    task.metadata = current_meta
                
                await session.commit()
                
                # Clean up resource tracking
                if task_id in self.active_task_resources:
                    del self.active_task_resources[task_id]
                
                status_icon = "✅" if success and verification_passed else "❌"
                logger.info(f"[TASK-REGISTRY] {status_icon} Completed: {task_id} ({duration:.1f}s)")
                
                # Log to immutable log
                await immutable_log.log_event(
                    actor=task.subsystem,
                    action='task_completed',
                    resource=task_id,
                    result='success' if success else 'failed',
                    metadata={
                        'duration_seconds': duration,
                        'verification_passed': verification_passed,
                        'sla_met': task.sla_met
                    }
                )
                
                # Publish completion event
                if self.message_bus:
                    await self.message_bus.publish('task.completed', {
                        'task_id': task_id,
                        'subsystem': task.subsystem,
                        'success': success,
                        'duration_seconds': duration,
                        'verification_passed': verification_passed
                    })
                
                # Update subsystem metrics
                await self._update_subsystem_metrics(task.subsystem, task.task_type)
                
                return True
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to complete task: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a task"""
        
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(TaskRegistryEntry).where(TaskRegistryEntry.task_id == task_id)
                )
                task = result.scalar_one_or_none()
                
                if not task:
                    return None
                
                return {
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'subsystem': task.subsystem,
                    'title': task.title,
                    'status': task.status,
                    'priority': task.priority,
                    'created_by': task.created_by,
                    'assigned_to': task.assigned_to,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'duration_seconds': task.duration_seconds,
                    'verification_status': task.verification_status,
                    'sla_met': task.sla_met,
                    'resource_usage': {
                        'cpu_seconds': task.cpu_seconds,
                        'memory_peak_mb': task.memory_peak_mb,
                        'disk_total_mb': (task.disk_read_mb or 0) + (task.disk_write_mb or 0),
                        'storage_delta_mb': task.storage_delta_mb
                    },
                    'ml_metrics': {
                        'dataset_size_mb': task.dataset_size_mb,
                        'vectors_processed': task.vectors_processed,
                        'tokens_processed': task.tokens_processed
                    } if any([task.dataset_size_mb, task.vectors_processed, task.tokens_processed]) else None
                }
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to get task status: {e}")
            return None
    
    async def query_tasks(
        self,
        subsystem: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query tasks with filters
        
        Returns list of task summaries
        """
        
        try:
            async with async_session() as session:
                # Build query
                query = select(TaskRegistryEntry)
                
                filters = []
                if subsystem:
                    filters.append(TaskRegistryEntry.subsystem == subsystem)
                if status:
                    filters.append(TaskRegistryEntry.status == status)
                if task_type:
                    filters.append(TaskRegistryEntry.task_type == task_type)
                if created_by:
                    filters.append(TaskRegistryEntry.created_by == created_by)
                
                if filters:
                    query = query.where(and_(*filters))
                
                query = query.order_by(TaskRegistryEntry.created_at.desc()).limit(limit)
                
                result = await session.execute(query)
                tasks = result.scalars().all()
                
                return [
                    {
                        'task_id': t.task_id,
                        'subsystem': t.subsystem,
                        'task_type': t.task_type,
                        'title': t.title,
                        'status': t.status,
                        'priority': t.priority,
                        'created_at': t.created_at.isoformat() if t.created_at else None,
                        'duration_seconds': t.duration_seconds,
                        'verification_status': t.verification_status
                    }
                    for t in tasks
                ]
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to query tasks: {e}")
            return []
    
    async def get_subsystem_status(self, subsystem: str) -> Dict[str, Any]:
        """
        Get current status for a specific subsystem
        Shows all open tasks and metrics
        """
        
        try:
            async with async_session() as session:
                # Count tasks by status
                result = await session.execute(
                    select(
                        TaskRegistryEntry.status,
                        func.count(TaskRegistryEntry.id)
                    )
                    .where(TaskRegistryEntry.subsystem == subsystem)
                    .group_by(TaskRegistryEntry.status)
                )
                
                status_counts = {row[0]: row[1] for row in result}
                
                # Get metrics
                metrics_result = await session.execute(
                    select(SubsystemTaskMetrics)
                    .where(SubsystemTaskMetrics.subsystem == subsystem)
                )
                metrics = metrics_result.scalars().all()
                
                return {
                    'subsystem': subsystem,
                    'task_counts': status_counts,
                    'total_tasks': sum(status_counts.values()),
                    'active_tasks': status_counts.get('active', 0),
                    'pending_tasks': status_counts.get('pending', 0),
                    'metrics': [
                        {
                            'task_type': m.task_type,
                            'avg_duration_seconds': m.avg_duration_seconds,
                            'success_rate': m.success_rate,
                            'total_completed': m.completed_tasks
                        }
                        for m in metrics
                    ]
                }
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Failed to get subsystem status: {e}")
            return {'subsystem': subsystem, 'error': str(e)}
    
    async def forecast_task_duration(
        self,
        subsystem: str,
        task_type: str
    ) -> Optional[Dict[str, float]]:
        """
        Forecast how long a task will take based on historical data
        
        Returns:
            avg, min, max, p95 duration in seconds
        """
        
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(SubsystemTaskMetrics)
                    .where(and_(
                        SubsystemTaskMetrics.subsystem == subsystem,
                        SubsystemTaskMetrics.task_type == task_type
                    ))
                )
                metrics = result.scalar_one_or_none()
                
                if not metrics or not metrics.avg_duration_seconds:
                    return None
                
                return {
                    'avg_seconds': metrics.avg_duration_seconds,
                    'min_seconds': metrics.min_duration_seconds,
                    'max_seconds': metrics.max_duration_seconds,
                    'p95_seconds': metrics.p95_duration_seconds,
                    'sample_size': metrics.sample_size,
                    'confidence': 'high' if metrics.sample_size >= 10 else 'medium' if metrics.sample_size >= 3 else 'low'
                }
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Forecast failed: {e}")
            return None
    
    async def _handle_task_created(self, event: Dict[str, Any]):
        """Handle task.created events from message bus"""
        # Auto-register from event
        await self.register_task(
            task_id=event['task_id'],
            task_type=event.get('task_type', 'unknown'),
            subsystem=event.get('subsystem', 'unknown'),
            title=event.get('title', 'Untitled Task'),
            created_by=event.get('created_by', 'system'),
            metadata=event.get('metadata')
        )
    
    async def _handle_task_started(self, event: Dict[str, Any]):
        """Handle task.started events"""
        await self.start_task(event['task_id'], event.get('metadata'))
    
    async def _handle_task_updated(self, event: Dict[str, Any]):
        """Handle task.updated events"""
        # Update metadata, status, etc.
        pass
    
    async def _handle_task_completed(self, event: Dict[str, Any]):
        """Handle task.completed events"""
        await self.complete_task(
            task_id=event['task_id'],
            success=event.get('success', True),
            verification_passed=event.get('verification_passed', True),
            resource_usage=event.get('resource_usage'),
            ml_metrics=event.get('ml_metrics'),
            result_metadata=event.get('metadata')
        )
    
    async def _handle_task_failed(self, event: Dict[str, Any]):
        """Handle task.failed events"""
        await self.complete_task(
            task_id=event['task_id'],
            success=False,
            verification_passed=False,
            result_metadata=event.get('metadata')
        )
    
    async def _handle_mission_event(self, event: Dict[str, Any]):
        """Handle mission.* events (backward compatibility)"""
        # Convert mission events to task events
        event_type = event.get('event_type', 'unknown')
        
        if 'created' in event_type:
            await self._handle_task_created(event)
        elif 'completed' in event_type:
            await self._handle_task_completed(event)
        elif 'failed' in event_type:
            await self._handle_task_failed(event)
    
    async def _resource_tracking_loop(self):
        """Background loop to snapshot resources for active tasks"""
        
        while self.running:
            try:
                await asyncio.sleep(30)  # Snapshot every 30 seconds
                
                for task_id, tracking in list(self.active_task_resources.items()):
                    try:
                        elapsed = (datetime.now(timezone.utc) - tracking['start_time']).total_seconds()
                        
                        # Capture current resource state
                        snapshot = TaskResourceSnapshot(
                            task_id=task_id,
                            elapsed_seconds=elapsed,
                            cpu_percent=psutil.cpu_percent(),
                            memory_mb=psutil.virtual_memory().used / (1024 * 1024),
                            snapshot_metadata={'interval': '30s'}
                        )
                        
                        async with async_session() as session:
                            session.add(snapshot)
                            await session.commit()
                        
                        tracking['snapshots'].append(elapsed)
                        
                    except Exception as e:
                        logger.debug(f"[TASK-REGISTRY] Snapshot error for {task_id}: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TASK-REGISTRY] Resource tracking error: {e}")
    
    async def _metrics_calculation_loop(self):
        """Periodically recalculate subsystem metrics for forecasting"""
        
        while self.running:
            try:
                await asyncio.sleep(300)  # Recalculate every 5 minutes
                
                await self._recalculate_all_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TASK-REGISTRY] Metrics calculation error: {e}")
    
    async def _update_subsystem_metrics(self, subsystem: str, task_type: str):
        """Update metrics for a specific subsystem/task_type combination"""
        
        try:
            async with async_session() as session:
                # Get all completed tasks of this type
                result = await session.execute(
                    select(TaskRegistryEntry)
                    .where(and_(
                        TaskRegistryEntry.subsystem == subsystem,
                        TaskRegistryEntry.task_type == task_type,
                        TaskRegistryEntry.status.in_(['completed', 'failed']),
                        TaskRegistryEntry.duration_seconds.isnot(None)
                    ))
                    .order_by(TaskRegistryEntry.completed_at.desc())
                    .limit(100)  # Last 100 tasks for stats
                )
                tasks = result.scalars().all()
                
                if not tasks:
                    return
                
                # Calculate statistics
                durations = [t.duration_seconds for t in tasks if t.duration_seconds]
                completed = [t for t in tasks if t.status == 'completed']
                verified = [t for t in completed if t.verification_status == 'passed']
                sla_met = [t for t in completed if t.sla_met]
                
                # Update or create metrics entry
                metrics_result = await session.execute(
                    select(SubsystemTaskMetrics)
                    .where(and_(
                        SubsystemTaskMetrics.subsystem == subsystem,
                        SubsystemTaskMetrics.task_type == task_type
                    ))
                )
                metrics = metrics_result.scalar_one_or_none()
                
                if not metrics:
                    metrics = SubsystemTaskMetrics(
                        subsystem=subsystem,
                        task_type=task_type
                    )
                    session.add(metrics)
                
                # Update metrics
                metrics.total_tasks = len(tasks)
                metrics.completed_tasks = len(completed)
                metrics.failed_tasks = len([t for t in tasks if t.status == 'failed'])
                
                if durations:
                    metrics.avg_duration_seconds = sum(durations) / len(durations)
                    metrics.min_duration_seconds = min(durations)
                    metrics.max_duration_seconds = max(durations)
                    # P95: 95th percentile
                    sorted_durations = sorted(durations)
                    p95_index = int(len(sorted_durations) * 0.95)
                    metrics.p95_duration_seconds = sorted_durations[p95_index] if p95_index < len(sorted_durations) else sorted_durations[-1]
                
                metrics.success_rate = len(completed) / len(tasks) if tasks else 0
                metrics.verification_pass_rate = len(verified) / len(completed) if completed else 0
                metrics.sla_met_rate = len(sla_met) / len(completed) if completed else 0
                
                metrics.sample_size = len(tasks)
                metrics.last_calculated_at = datetime.now(timezone.utc)
                
                # Set anomaly thresholds (3x average)
                if metrics.avg_duration_seconds:
                    metrics.anomaly_threshold_duration = metrics.avg_duration_seconds * 3
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Metrics update failed: {e}")
    
    async def _recalculate_all_metrics(self):
        """Recalculate metrics for all subsystem/task_type combinations"""
        
        try:
            async with async_session() as session:
                # Get all unique subsystem/task_type combinations
                result = await session.execute(
                    select(
                        TaskRegistryEntry.subsystem,
                        TaskRegistryEntry.task_type
                    )
                    .distinct()
                )
                
                combinations = result.all()
                
                for subsystem, task_type in combinations:
                    await self._update_subsystem_metrics(subsystem, task_type)
                
                logger.info(f"[TASK-REGISTRY] Recalculated metrics for {len(combinations)} combinations")
                
        except Exception as e:
            logger.error(f"[TASK-REGISTRY] Full metrics recalculation failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'running': self.running,
            'active_tasks_tracked': len(self.active_task_resources),
            'message_bus_connected': self.message_bus is not None
        }


# Singleton instance
task_registry = TaskRegistry()
