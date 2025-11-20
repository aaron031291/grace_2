# -*- coding: utf-8 -*-
"""
Clarity Ingestion Orchestrator
Manages all ingestion pipelines using Clarity Framework
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_component import BaseComponent, ComponentStatus
from .event_bus import get_event_bus, Event
from .component_manifest import get_manifest, TrustLevel
from .loop_output import GraceLoopOutput
from backend.core.unified_event_publisher import publish_event_obj


class IngestionTask:
    """Represents an ingestion task"""
    
    def __init__(self, task_id: str, task_type: str, source: str):
        self.task_id = task_id
        self.task_type = task_type
        self.source = source
        self.status = "pending"
        self.progress = 0.0
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.results: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "source": self.source,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "results": self.results
        }


class ClarityIngestionOrchestrator(BaseComponent):
    """
    Ingestion orchestrator using Clarity Framework.
    Manages GitHub, Reddit, YouTube, and other knowledge ingestion pipelines.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.component_type = "ingestion_orchestrator"
        if config:
            self.config.update(config)
        
        # Component state
        self.event_bus = get_event_bus()
        self.tasks: Dict[str, IngestionTask] = {}
        self.active_tasks: List[str] = []
        self.max_concurrent = self.config.get("max_concurrent", 3)
        
        # Ingestion modules
        self.ingest_modules = {}
    
    async def activate(self) -> bool:
        """Activate the ingestion orchestrator"""
        try:
            self.set_status(ComponentStatus.ACTIVATING)
            
            # Register with manifest
            manifest = get_manifest()
            manifest.register(
                self,
                trust_level=TrustLevel.HIGH,
                role_tags=["ingestion", "knowledge", "learning"]
            )
            
            # Subscribe to ingestion events
            self.event_bus.subscribe("task.created", self._handle_task_created)
            self.event_bus.subscribe("ingest.start", self._handle_ingest_start)
            self.event_bus.subscribe("ingest.stop", self._handle_ingest_stop)
            
            # Load ingestion modules
            await self._load_ingest_modules()
            
            self.set_status(ComponentStatus.ACTIVE)
            self.activated_at = datetime.utcnow()
            
            # Publish activation event
            await publish_event_obj(
                event_type="component.activated",
                source=self.component_id,
                payload={
                    "component_type": self.component_type,
                    "max_concurrent": self.max_concurrent
                }
            )
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate the ingestion orchestrator"""
        try:
            self.set_status(ComponentStatus.DEACTIVATING)
            
            # Stop all active tasks
            for task_id in list(self.active_tasks):
                await self.stop_task(task_id)
            
            # Unsubscribe from events
            self.event_bus.unsubscribe("task.created", self._handle_task_created)
            self.event_bus.unsubscribe("ingest.start", self._handle_ingest_start)
            self.event_bus.unsubscribe("ingest.stop", self._handle_ingest_stop)
            
            # Unregister from manifest
            manifest = get_manifest()
            manifest.unregister(self.component_id)
            
            self.set_status(ComponentStatus.STOPPED)
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "status": self.status.value,
            "total_tasks": len(self.tasks),
            "active_tasks": len(self.active_tasks),
            "max_concurrent": self.max_concurrent,
            "modules_loaded": list(self.ingest_modules.keys()),
            "config": self.config,
            "metadata": self.metadata
        }
    
    async def _load_ingest_modules(self):
        """Load available ingestion modules"""
        # Check for ingest modules
        modules_to_check = {
            'github': 'backend.github_knowledge_miner',
            'reddit': 'backend.reddit_learning',
            'youtube': 'backend.youtube_learning',
            'web': 'backend.safe_web_scraper'
        }
        
        for name, module_path in modules_to_check.items():
            try:
                # Try to import the module
                module = __import__(module_path, fromlist=['*'])
                self.ingest_modules[name] = module
                self.add_metadata(f"{name}_available", True)
            except ImportError:
                self.add_metadata(f"{name}_available", False)
    
    async def create_task(
        self,
        task_type: str,
        source: str,
        config: Dict[str, Any] = None
    ) -> IngestionTask:
        """Create a new ingestion task"""
        task = IngestionTask(
            task_id=f"ingest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{task_type}",
            task_type=task_type,
            source=source
        )
        
        if config:
            task.results["config"] = config
        
        self.tasks[task.task_id] = task
        
        # Publish task creation event
        await publish_event_obj(
            event_type="task.created",
            source=self.component_id,
            payload={
                "task_id": task.task_id,
                "task_type": task_type,
                "source": source
            }
        )
        
        return task
    
    async def start_task(self, task_id: str) -> bool:
        """Start an ingestion task"""
        if task_id not in self.tasks:
            return False
        
        if len(self.active_tasks) >= self.max_concurrent:
            return False  # Too many concurrent tasks
        
        task = self.tasks[task_id]
        task.status = "running"
        task.started_at = datetime.utcnow()
        self.active_tasks.append(task_id)
        
        # Create loop output for traceability
        loop_output = GraceLoopOutput(
            loop_type="ingestion",
            component_id=self.component_id
        )
        loop_output.metadata["task_id"] = task_id
        loop_output.metadata["task_type"] = task.task_type
        
        # Publish start event
        await publish_event_obj(
            event_type="ingest.start",
            source=self.component_id,
            payload={
                "task_id": task_id,
                "task_type": task.task_type,
                "loop_id": loop_output.loop_id
            }
        )
        
        # Run the ingestion (simulate for now)
        asyncio.create_task(self._run_ingestion(task, loop_output))
        
        return True
    
    async def stop_task(self, task_id: str) -> bool:
        """Stop an active ingestion task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = "stopped"
        task.completed_at = datetime.utcnow()
        
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
        
        # Publish stop event
        await publish_event_obj(
            event_type="ingest.stop",
            source=self.component_id,
            payload={"task_id": task_id}
        )
        
        return True
    
    async def _run_ingestion(self, task: IngestionTask, loop_output: GraceLoopOutput):
        """Run the actual ingestion task"""
        try:
            # Simulate ingestion progress
            for i in range(10):
                if task.status == "stopped":
                    break
                
                await asyncio.sleep(1)
                task.progress = (i + 1) * 10
                
                # Publish progress event
                await publish_event_obj(
                    event_type="ingest.progress",
                    source=self.component_id,
                    payload={
                        "task_id": task.task_id,
                        "progress": task.progress
                    }
                )
            
            if task.status != "stopped":
                # Mark as completed
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.results["items_processed"] = 100  # Example
                
                loop_output.mark_completed(task.results, confidence=0.95)
                
                # Publish completion event
                await publish_event_obj(
                    event_type="task.completed",
                    source=self.component_id,
                    payload={
                        "task_id": task.task_id,
                        "loop_output": loop_output.to_dict(),
                        "results": task.results
                    }
                )
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            
            loop_output.mark_failed(str(e))
            
            # Publish failure event
            await publish_event_obj(
                event_type="task.failed",
                source=self.component_id,
                payload={
                    "task_id": task.task_id,
                    "error": str(e),
                    "loop_output": loop_output.to_dict()
                }
            )
        
        finally:
            if task.task_id in self.active_tasks:
                self.active_tasks.remove(task.task_id)
    
    async def _handle_task_created(self, event: Event):
        """Handle task creation event"""
        # Auto-start if capacity available
        task_id = event.payload.get("task_id")
        if task_id and len(self.active_tasks) < self.max_concurrent:
            await self.start_task(task_id)
    
    async def _handle_ingest_start(self, event: Event):
        """Handle manual ingestion start request"""
        task_id = event.payload.get("task_id")
        if task_id:
            await self.start_task(task_id)
    
    async def _handle_ingest_stop(self, event: Event):
        """Handle ingestion stop request"""
        task_id = event.payload.get("task_id")
        if task_id:
            await self.stop_task(task_id)
    
    def get_tasks(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())
        
        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]
        
        return [t.to_dict() for t in tasks]
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return None


# Global ingestion orchestrator instance
_ingestion_orchestrator: Optional[ClarityIngestionOrchestrator] = None


async def get_ingestion_orchestrator() -> ClarityIngestionOrchestrator:
    """Get or create the global ingestion orchestrator"""
    global _ingestion_orchestrator
    if _ingestion_orchestrator is None:
        _ingestion_orchestrator = ClarityIngestionOrchestrator()
        await _ingestion_orchestrator.activate()
    return _ingestion_orchestrator
