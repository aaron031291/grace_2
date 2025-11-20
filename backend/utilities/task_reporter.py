"""
Task Reporter Utility
Helper for subsystems to easily report tasks to the unified registry

Usage example:
    from backend.utilities.task_reporter import TaskReporter
    
    reporter = TaskReporter(subsystem='healing', task_type='playbook')
    
    # Start a task
    task_id = await reporter.start_task(
        title="Fix port collision",
        created_by="guardian"
    )
    
    # Complete the task
    await reporter.complete_task(
        task_id=task_id,
        success=True,
        verification_passed=True,
        resource_usage={'cpu_seconds': 2.5, 'memory_peak_mb': 150}
    )
"""

import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)


class TaskReporter:
    """
    Helper class for subsystems to report tasks
    Makes it easy to integrate with task registry
    """
    
    def __init__(self, subsystem: str, task_type: str):
        """
        Initialize task reporter for a subsystem
        
        Args:
            subsystem: Name of subsystem (healing, coding_agent, learning, ml_pipeline, etc.)
            task_type: Default task type (playbook, work_order, mission, training_job, etc.)
        """
        self.subsystem = subsystem
        self.task_type = task_type
        self.registry = None
        
        # Resource tracking for current task
        self.current_task_id = None
        self.task_start_resources = None
    
    async def _get_registry(self):
        """Lazy load task registry"""
        if not self.registry:
            try:
                from backend.services.task_registry import task_registry
                self.registry = task_registry
            except ImportError:
                logger.debug(f"[{self.subsystem}] Task registry not available")
                return None
        return self.registry
    
    async def start_task(
        self,
        title: str,
        created_by: str,
        task_id: Optional[str] = None,
        description: Optional[str] = None,
        priority: int = 5,
        sla_hours: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register and start a task
        
        Returns:
            task_id for tracking
        """
        
        registry = await self._get_registry()
        if not registry:
            # Generate ID even if registry not available
            return task_id or f"{self.subsystem}_{uuid.uuid4().hex[:8]}"
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"{self.subsystem}_{self.task_type}_{uuid.uuid4().hex[:8]}"
        
        # Register task
        await registry.register_task(
            task_id=task_id,
            task_type=self.task_type,
            subsystem=self.subsystem,
            title=title,
            created_by=created_by,
            description=description,
            priority=priority,
            sla_hours=sla_hours,
            metadata=metadata
        )
        
        # Start it
        await registry.start_task(task_id)
        
        # Track resources
        self.current_task_id = task_id
        self.task_start_resources = self._capture_resources()
        
        logger.info(f"[{self.subsystem}] Task started: {task_id}")
        
        return task_id
    
    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
        verification_passed: bool = True,
        resource_usage: Optional[Dict[str, float]] = None,
        ml_metrics: Optional[Dict[str, Any]] = None,
        result_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Complete a task with metrics
        
        If resource_usage not provided, automatically calculates from start
        """
        
        registry = await self._get_registry()
        if not registry:
            return
        
        # Calculate resource usage if not provided
        if resource_usage is None and self.task_start_resources:
            resource_usage = self._calculate_resource_delta()
        
        await registry.complete_task(
            task_id=task_id,
            success=success,
            verification_passed=verification_passed,
            resource_usage=resource_usage,
            ml_metrics=ml_metrics,
            result_metadata=result_metadata
        )
        
        # Clear tracking
        if task_id == self.current_task_id:
            self.current_task_id = None
            self.task_start_resources = None
        
        logger.info(f"[{self.subsystem}] Task completed: {task_id} (success={success})")
    
    def _capture_resources(self) -> Dict[str, float]:
        """Capture current resource state"""
        try:
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_mb': psutil.virtual_memory().used / (1024 * 1024),
                'disk_read_mb': disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                'disk_write_mb': disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                'network_sent_mb': net_io.bytes_sent / (1024 * 1024) if net_io else 0,
                'network_recv_mb': net_io.bytes_recv / (1024 * 1024) if net_io else 0
            }
        except Exception as e:
            logger.debug(f"[{self.subsystem}] Resource capture failed: {e}")
            return {}
    
    def _calculate_resource_delta(self) -> Dict[str, float]:
        """Calculate resource usage since task started"""
        
        if not self.task_start_resources:
            return {}
        
        try:
            current = self._capture_resources()
            
            return {
                'cpu_seconds': None,  # TODO: track actual CPU time
                'memory_peak_mb': current.get('memory_mb'),
                'disk_read_mb': current.get('disk_read_mb', 0) - self.task_start_resources.get('disk_read_mb', 0),
                'disk_write_mb': current.get('disk_write_mb', 0) - self.task_start_resources.get('disk_write_mb', 0),
                'network_tx_mb': current.get('network_sent_mb', 0) - self.task_start_resources.get('network_sent_mb', 0),
                'network_rx_mb': current.get('network_recv_mb', 0) - self.task_start_resources.get('network_recv_mb', 0)
            }
        except Exception as e:
            logger.debug(f"[{self.subsystem}] Resource delta calculation failed: {e}")
            return {}
    
    async def fail_task(
        self,
        task_id: str,
        error_message: str,
        resource_usage: Optional[Dict[str, float]] = None
    ):
        """Mark task as failed"""
        
        await self.complete_task(
            task_id=task_id,
            success=False,
            verification_passed=False,
            resource_usage=resource_usage,
            result_metadata={'error': error_message}
        )
