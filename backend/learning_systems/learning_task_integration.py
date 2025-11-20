"""
Learning System Integration with Unified Task Registry

Registers all learning activities (training, knowledge acquisition, etc.)
with the unified task manager for centralized tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Import task registry
try:
    from backend.services.task_registry import task_registry
    TASK_REGISTRY_AVAILABLE = True
except ImportError:
    TASK_REGISTRY_AVAILABLE = False
    logger.warning("[LEARNING-TASK-INT] Task registry not available")


class LearningTaskIntegration:
    """Integrates learning system with unified task registry"""
    
    async def register_learning_event(
        self,
        event_type: str,
        title: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> Optional[str]:
        """
        Register a learning event with task registry
        
        Args:
            event_type: Type of learning (training, knowledge_update, config_update, etc.)
            title: Human-readable title
            description: Detailed description
            metadata: Additional data
            priority: Task priority (1-10)
        
        Returns:
            task_id if successful, None otherwise
        """
        if not TASK_REGISTRY_AVAILABLE:
            logger.debug("[LEARNING-TASK-INT] Task registry not available")
            return None
        
        try:
            task_id = f"learn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            
            task_data = {
                "task_id": task_id,
                "task_type": event_type,
                "subsystem": "learning",
                "title": title,
                "description": description,
                "created_by": "continuous_learning_loop",
                "priority": priority,
                "task_metadata": metadata or {}
            }
            
            await task_registry.register_task(**task_data)
            logger.info(f"[LEARNING-TASK-INT] Registered learning task: {task_id}")
            
            return task_id
            
        except Exception as e:
            logger.error(f"[LEARNING-TASK-INT] Failed to register learning task: {e}")
            return None
    
    async def update_learning_progress(
        self,
        task_id: str,
        progress_percent: float,
        status_message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update learning task progress
        
        Args:
            task_id: Task identifier
            progress_percent: 0.0 to 100.0
            status_message: Current status description
            metadata: Additional progress data
        """
        if not TASK_REGISTRY_AVAILABLE:
            return
        
        try:
            # Update via task registry
            from backend.services.task_registry import task_registry
            
            update_data = {
                "status": "active",
                "task_metadata": {
                    "progress_percent": progress_percent,
                    "status_message": status_message,
                    "last_update": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            }
            
            await task_registry.update_task(task_id, **update_data)
            logger.info(f"[LEARNING-TASK-INT] Updated task {task_id}: {progress_percent}%")
        except Exception as e:
            logger.error(f"[LEARNING-TASK-INT] Failed to update progress: {e}")
    
    async def complete_learning_task(
        self,
        task_id: str,
        success: bool = True,
        result: Optional[Dict[str, Any]] = None
    ):
        """Mark learning task as completed"""
        if not TASK_REGISTRY_AVAILABLE:
            return
        
        try:
            await task_registry.complete_task(
                task_id=task_id,
                success=success,
                result=result or {}
            )
            logger.info(f"[LEARNING-TASK-INT] Completed learning task: {task_id}")
        except Exception as e:
            logger.error(f"[LEARNING-TASK-INT] Failed to complete task: {e}")
    
    async def get_active_learning_tasks(self) -> List[Dict[str, Any]]:
        """Get all currently active learning tasks with progress"""
        if not TASK_REGISTRY_AVAILABLE:
            return []
        
        try:
            from backend.services.task_registry import task_registry
            tasks = await task_registry.get_tasks_by_subsystem("learning", status="active")
            
            learning_activities = []
            for task in tasks:
                activity = {
                    "task_id": task.task_id,
                    "type": task.task_type,
                    "title": task.title,
                    "description": task.description,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "progress_percent": 0.0,
                    "status_message": "In progress",
                }
                
                # Extract progress from metadata
                if task.task_metadata:
                    activity["progress_percent"] = task.task_metadata.get("progress_percent", 0.0)
                    activity["status_message"] = task.task_metadata.get("status_message", "In progress")
                
                learning_activities.append(activity)
            
            return learning_activities
        except Exception as e:
            logger.error(f"[LEARNING-TASK-INT] Failed to get active tasks: {e}")
            return []
    
    async def register_training_job(
        self,
        model_name: str,
        dataset_size: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Register ML training job"""
        return await self.register_learning_event(
            event_type="ml_training",
            title=f"Training: {model_name}",
            description=f"ML model training for {model_name}",
            metadata={
                "model_name": model_name,
                "dataset_size": dataset_size,
                **(metadata or {})
            },
            priority=7
        )
    
    async def register_config_update(
        self,
        component: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Register configuration update"""
        return await self.register_learning_event(
            event_type="config_update",
            title=f"Config Update: {component}",
            description=f"Automated configuration improvement for {component}",
            metadata={
                "component": component,
                "version": version,
                **(metadata or {})
            },
            priority=5
        )
    
    async def register_knowledge_acquisition(
        self,
        source: str,
        knowledge_type: str,
        items_learned: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Register knowledge acquisition event"""
        return await self.register_learning_event(
            event_type="knowledge_acquisition",
            title=f"Learned from {source}",
            description=f"Acquired {items_learned} {knowledge_type} items",
            metadata={
                "source": source,
                "knowledge_type": knowledge_type,
                "items_count": items_learned,
                **(metadata or {})
            },
            priority=4
        )


# Global instance
learning_task_integration = LearningTaskIntegration()
