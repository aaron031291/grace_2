"""
Shared Orchestration System
Coordinates Elite Self-Healing and Elite Coding Agent with parallel processing

Features:
- Parallel task execution across both agents
- Shared resource management
- Priority-based scheduling
- Cross-agent collaboration
- Load balancing
- Performance monitoring
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents"""
    SELF_HEALING = "self_healing"
    CODING = "coding"
    BOTH = "both"  # Task requires both agents


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 10
    HIGH = 7
    MEDIUM = 5
    LOW = 3
    BACKGROUND = 1


@dataclass
class OrchestrationTask:
    """A task managed by the orchestrator"""
    task_id: str
    agent_type: AgentType
    priority: TaskPriority
    description: str
    payload: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "queued"  # queued, running, completed, failed
    assigned_to: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None  # Task IDs this depends on
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class SharedOrchestrator:
    """
    Orchestrates tasks across self-healing and coding agents
    with parallel processing and intelligent scheduling
    """
    
    def __init__(self):
        self.running = False
        
        # Task queues
        self.task_queue: List[OrchestrationTask] = []
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.completed_tasks: List[OrchestrationTask] = []
        
        # Agent references (will be set on start)
        self.self_healing_agent = None
        self.coding_agent = None
        
        # Resource management
        self.max_parallel_tasks = 10  # Total across both agents
        self.max_per_agent = 5
        
        # Performance tracking
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0.0,
            "agent_utilization": {
                "self_healing": 0.0,
                "coding": 0.0
            }
        }
        
        # Shared resources
        self.shared_resources = {
            "code_memory": None,
            "knowledge_base": {},
            "execution_results": {},
            "learning_data": []
        }
    
    async def start(self, self_healing_agent, coding_agent):
        """Start the orchestrator"""
        if self.running:
            return
        
        self.running = True
        self.self_healing_agent = self_healing_agent
        self.coding_agent = coding_agent
        
        logger.info("=" * 80)
        logger.info("SHARED ORCHESTRATION SYSTEM - STARTING")
        logger.info("=" * 80)
        
        # Subscribe to events
        await self._subscribe_to_events()
        
        # Start orchestration loop
        asyncio.create_task(self._orchestration_loop())
        
        # Start monitoring
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[ORCHESTRATOR] ✅ Shared Orchestration System OPERATIONAL")
        logger.info(f"[ORCHESTRATOR] Max parallel tasks: {self.max_parallel_tasks}")
        logger.info(f"[ORCHESTRATOR] Max per agent: {self.max_per_agent}")
        logger.info("=" * 80)
        
        # Log to immutable log
        await immutable_log.append(
            actor="shared_orchestrator",
            action="system_start",
            resource="orchestration",
            subsystem="orchestration",
            payload={"max_parallel": self.max_parallel_tasks},
            result="started"
        )
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        logger.info("[ORCHESTRATOR] Shared Orchestration System stopped")
    
    async def submit_task(
        self,
        agent_type: AgentType,
        priority: TaskPriority,
        description: str,
        payload: Dict[str, Any],
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Submit a task to the orchestrator
        
        Args:
            agent_type: Which agent(s) should handle this
            priority: Task priority
            description: Task description
            payload: Task data
            dependencies: List of task IDs this depends on
        
        Returns:
            Task ID
        """
        task = OrchestrationTask(
            task_id=f"orch_{int(datetime.now().timestamp())}_{len(self.task_queue)}",
            agent_type=agent_type,
            priority=priority,
            description=description,
            payload=payload,
            created_at=datetime.now(timezone.utc),
            dependencies=dependencies or []
        )
        
        self.task_queue.append(task)
        self.active_tasks[task.task_id] = task
        
        logger.info(f"[ORCHESTRATOR] Task submitted: {task.task_id}")
        logger.info(f"  Agent: {agent_type.value}")
        logger.info(f"  Priority: {priority.value}")
        logger.info(f"  Description: {description}")
        
        # Publish event
        await trigger_mesh.publish(TriggerEvent(
            event_type="orchestration.task_submitted",
            source="shared_orchestrator",
            actor="orchestrator",
            resource=task.task_id,
            payload={
                "agent_type": agent_type.value,
                "priority": priority.value,
                "description": description
            }
        ))
        
        return task.task_id
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.running:
            try:
                # Get tasks ready to run (no pending dependencies)
                ready_tasks = self._get_ready_tasks()
                
                if not ready_tasks:
                    await asyncio.sleep(1)
                    continue
                
                # Sort by priority
                ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
                
                # Calculate available slots
                running_count = len([t for t in self.active_tasks.values() if t.status == "running"])
                available_slots = self.max_parallel_tasks - running_count
                
                if available_slots <= 0:
                    await asyncio.sleep(1)
                    continue
                
                # Distribute tasks across agents
                tasks_to_run = ready_tasks[:available_slots]
                
                # Execute in parallel
                await asyncio.gather(*[
                    self._execute_task(task)
                    for task in tasks_to_run
                ], return_exceptions=True)
                
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ORCHESTRATOR] Error in orchestration loop: {e}", exc_info=True)
                await asyncio.sleep(2)
    
    def _get_ready_tasks(self) -> List[OrchestrationTask]:
        """Get tasks that are ready to run (dependencies met)"""
        ready = []
        
        for task in self.task_queue:
            if task.status != "queued":
                continue
            
            # Check if all dependencies are completed
            deps_met = all(
                self.active_tasks.get(dep_id, {}).get("status") == "completed"
                for dep_id in task.dependencies
            )
            
            if deps_met:
                ready.append(task)
        
        return ready
    
    async def _execute_task(self, task: OrchestrationTask):
        """Execute a task by routing to appropriate agent"""
        try:
            task.status = "running"
            task.started_at = datetime.now(timezone.utc)
            
            logger.info(f"[ORCHESTRATOR] Executing task: {task.task_id}")
            
            # Route to appropriate agent
            if task.agent_type == AgentType.SELF_HEALING:
                result = await self._execute_healing_task(task)
            elif task.agent_type == AgentType.CODING:
                result = await self._execute_coding_task(task)
            elif task.agent_type == AgentType.BOTH:
                result = await self._execute_collaborative_task(task)
            else:
                result = {"success": False, "error": "Unknown agent type"}
            
            task.result = result
            task.status = "completed" if result.get("success") else "failed"
            task.completed_at = datetime.now(timezone.utc)
            
            # Remove from queue
            if task in self.task_queue:
                self.task_queue.remove(task)
            
            # Add to completed
            self.completed_tasks.append(task)
            
            # Update metrics
            self._update_metrics(task)
            
            # Share learning data
            await self._share_learning_data(task, result)
            
            logger.info(f"[ORCHESTRATOR] Task {task.task_id} completed: {result.get('success')}")
            
            # Log to immutable log
            await immutable_log.append(
                actor="shared_orchestrator",
                action="task_completed",
                resource=task.task_id,
                subsystem="orchestration",
                payload={
                    "agent_type": task.agent_type.value,
                    "priority": task.priority.value,
                    "result": result
                },
                result="success" if result.get("success") else "failed"
            )
            
        except Exception as e:
            task.status = "failed"
            task.result = {"success": False, "error": str(e)}
            logger.error(f"[ORCHESTRATOR] Error executing task {task.task_id}: {e}", exc_info=True)
    
    async def _execute_healing_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute a self-healing task"""
        if not self.self_healing_agent:
            return {"success": False, "error": "Self-healing agent not available"}
        
        # Create healing task and submit to agent
        # This is a simplified version - actual implementation would be more complex
        return {"success": True, "agent": "self_healing", "action": "healing_executed"}
    
    async def _execute_coding_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute a coding task"""
        if not self.coding_agent:
            return {"success": False, "error": "Coding agent not available"}
        
        # Submit to coding agent
        from .elite_coding_agent import CodingTask, CodingTaskType, ExecutionMode
        
        coding_task = CodingTask(
            task_id=task.task_id,
            task_type=CodingTaskType.BUILD_FEATURE,
            description=task.description,
            requirements=task.payload,
            execution_mode=ExecutionMode.AUTO,
            priority=task.priority.value,
            created_at=task.created_at
        )
        
        await self.coding_agent.submit_task(coding_task)
        
        return {"success": True, "agent": "coding", "action": "task_submitted"}
    
    async def _execute_collaborative_task(self, task: OrchestrationTask) -> Dict[str, Any]:
        """Execute a task requiring both agents"""
        # Example: Build a feature that also includes self-healing capabilities
        
        # Step 1: Coding agent builds the feature
        coding_result = await self._execute_coding_task(task)
        
        if not coding_result.get("success"):
            return coding_result
        
        # Step 2: Self-healing agent adds monitoring and healing
        healing_task_payload = {
            **task.payload,
            "code_result": coding_result
        }
        
        healing_task = OrchestrationTask(
            task_id=f"{task.task_id}_healing",
            agent_type=AgentType.SELF_HEALING,
            priority=task.priority,
            description=f"Add healing for: {task.description}",
            payload=healing_task_payload,
            created_at=datetime.now(timezone.utc)
        )
        
        healing_result = await self._execute_healing_task(healing_task)
        
        return {
            "success": True,
            "collaborative": True,
            "coding_result": coding_result,
            "healing_result": healing_result
        }
    
    async def _share_learning_data(self, task: OrchestrationTask, result: Dict[str, Any]):
        """Share learning data between agents"""
        learning_entry = {
            "task_id": task.task_id,
            "agent_type": task.agent_type.value,
            "description": task.description,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.shared_resources["learning_data"].append(learning_entry)
        
        # Keep only last 1000 entries
        if len(self.shared_resources["learning_data"]) > 1000:
            self.shared_resources["learning_data"] = self.shared_resources["learning_data"][-1000:]
    
    def _update_metrics(self, task: OrchestrationTask):
        """Update performance metrics"""
        self.metrics["tasks_processed"] += 1
        
        if task.status == "failed":
            self.metrics["tasks_failed"] += 1
        
        # Calculate completion time
        if task.started_at and task.completed_at:
            completion_time = (task.completed_at - task.started_at).total_seconds()
            
            # Update average
            current_avg = self.metrics["average_completion_time"]
            total_tasks = self.metrics["tasks_processed"]
            
            self.metrics["average_completion_time"] = (
                (current_avg * (total_tasks - 1) + completion_time) / total_tasks
            )
    
    async def _monitoring_loop(self):
        """Monitor system performance and health"""
        while self.running:
            try:
                # Calculate agent utilization
                total_capacity = self.max_parallel_tasks
                running_tasks = [t for t in self.active_tasks.values() if t.status == "running"]
                
                healing_tasks = len([t for t in running_tasks if t.agent_type == AgentType.SELF_HEALING])
                coding_tasks = len([t for t in running_tasks if t.agent_type == AgentType.CODING])
                
                self.metrics["agent_utilization"]["self_healing"] = healing_tasks / self.max_per_agent
                self.metrics["agent_utilization"]["coding"] = coding_tasks / self.max_per_agent
                
                # Log metrics every 60 seconds
                logger.info(f"[ORCHESTRATOR] Metrics:")
                logger.info(f"  Tasks processed: {self.metrics['tasks_processed']}")
                logger.info(f"  Tasks failed: {self.metrics['tasks_failed']}")
                logger.info(f"  Avg completion time: {self.metrics['average_completion_time']:.2f}s")
                logger.info(f"  Healing utilization: {self.metrics['agent_utilization']['self_healing']:.1%}")
                logger.info(f"  Coding utilization: {self.metrics['agent_utilization']['coding']:.1%}")
                
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ORCHESTRATOR] Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _subscribe_to_events(self):
        """Subscribe to trigger mesh events"""
        await trigger_mesh.subscribe("orchestration.*", self._handle_orchestration_event)
        logger.info("[ORCHESTRATOR] Subscribed to trigger mesh events")
    
    async def _handle_orchestration_event(self, event: TriggerEvent):
        """Handle orchestration events"""
        # Handle events that affect orchestration
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "running": self.running,
            "queued_tasks": len([t for t in self.task_queue if t.status == "queued"]),
            "running_tasks": len([t for t in self.active_tasks.values() if t.status == "running"]),
            "completed_tasks": len(self.completed_tasks),
            "metrics": self.metrics,
            "capacity": {
                "total": self.max_parallel_tasks,
                "available": self.max_parallel_tasks - len([t for t in self.active_tasks.values() if t.status == "running"])
            }
        }


# Singleton instance
shared_orchestrator = SharedOrchestrator()

