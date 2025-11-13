"""
Base Domain Kernel
Abstract base class for all domain-specific orchestration kernels
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class KernelStatus(Enum):
    """Kernel lifecycle states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class BaseDomainKernel(ABC):
    """
    Abstract base kernel for domain orchestration.
    
    Each kernel manages:
    - Lifecycle (start/stop/pause/resume)
    - Sub-agent spawning and monitoring
    - Event emission and handling
    - Trust metric tracking
    - Work queue coordination
    """
    
    def __init__(
        self,
        kernel_id: str,
        domain: str,
        registry=None,
        event_bus=None
    ):
        self.kernel_id = kernel_id
        self.domain = domain
        self.registry = registry
        self.event_bus = event_bus
        
        self.status = KernelStatus.STOPPED
        self.started_at: Optional[datetime] = None
        self.last_heartbeat: Optional[datetime] = None
        
        self._running = False
        self._coordinator_task: Optional[asyncio.Task] = None
        self._watchers: List[asyncio.Task] = []
        self._sub_agents: Dict[str, Any] = {}
        
        self.metrics = {
            'events_processed': 0,
            'agents_spawned': 0,
            'jobs_completed': 0,
            'errors': 0
        }
    
    async def start(self) -> bool:
        """
        Start the kernel and initialize all systems.
        
        Returns:
            bool: True if started successfully
        """
        if self.status != KernelStatus.STOPPED:
            logger.warning(f"Kernel {self.kernel_id} already running")
            return False
        
        try:
            self.status = KernelStatus.STARTING
            self.started_at = datetime.utcnow()
            
            logger.info(f"Starting kernel: {self.kernel_id}")
            
            # Register kernel
            await self._register_kernel()
            
            # Initialize watchers
            await self._initialize_watchers()
            
            # Load pending work
            await self._load_pending_work()
            
            # Start coordinator loop
            self._running = True
            self._coordinator_task = asyncio.create_task(self._coordinator_loop())
            
            self.status = KernelStatus.RUNNING
            await self._emit_event('kernel.started', {
                'kernel_id': self.kernel_id,
                'domain': self.domain,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Kernel {self.kernel_id} started successfully")
            return True
            
        except Exception as e:
            self.status = KernelStatus.ERROR
            logger.error(f"Failed to start kernel: {e}")
            await self._emit_event('kernel.error', {
                'kernel_id': self.kernel_id,
                'error': str(e)
            })
            return False
    
    async def stop(self) -> bool:
        """
        Stop the kernel and clean up all resources.
        
        Returns:
            bool: True if stopped successfully
        """
        if self.status == KernelStatus.STOPPED:
            return True
        
        try:
            self.status = KernelStatus.STOPPING
            logger.info(f"Stopping kernel: {self.kernel_id}")
            
            # Stop coordinator loop
            self._running = False
            if self._coordinator_task:
                self._coordinator_task.cancel()
                try:
                    await self._coordinator_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel all watchers
            for watcher in self._watchers:
                watcher.cancel()
            await asyncio.gather(*self._watchers, return_exceptions=True)
            self._watchers.clear()
            
            # Terminate all sub-agents
            await self._terminate_all_agents()
            
            # Cleanup
            await self._cleanup()
            
            self.status = KernelStatus.STOPPED
            await self._emit_event('kernel.stopped', {
                'kernel_id': self.kernel_id,
                'uptime_seconds': (datetime.utcnow() - self.started_at).total_seconds() if self.started_at else 0,
                'metrics': self.metrics
            })
            
            logger.info(f"Kernel {self.kernel_id} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping kernel: {e}")
            return False
    
    async def pause(self):
        """Pause kernel operations without stopping"""
        if self.status == KernelStatus.RUNNING:
            self.status = KernelStatus.PAUSED
            await self._emit_event('kernel.paused', {'kernel_id': self.kernel_id})
            logger.info(f"Kernel {self.kernel_id} paused")
    
    async def resume(self):
        """Resume paused kernel operations"""
        if self.status == KernelStatus.PAUSED:
            self.status = KernelStatus.RUNNING
            await self._emit_event('kernel.resumed', {'kernel_id': self.kernel_id})
            logger.info(f"Kernel {self.kernel_id} resumed")
    
    async def spawn_agent(
        self,
        agent_type: str,
        task_data: Dict[str, Any],
        priority: str = 'normal'
    ) -> str:
        """
        Spawn a sub-agent to handle specific task.
        
        Args:
            agent_type: Type of agent to spawn
            task_data: Data for the agent's task
            priority: Task priority (low, normal, high)
            
        Returns:
            agent_id: Unique identifier for the spawned agent
        """
        agent_id = f"{agent_type}_{datetime.utcnow().timestamp()}"
        
        try:
            agent = await self._create_agent(agent_type, agent_id, task_data)
            
            if agent:
                # Store agent metadata for tracking
                self._sub_agents[agent_id] = {
                    'instance': agent,
                    'type': agent_type,
                    'started_at': datetime.utcnow(),
                    'priority': priority,
                    'task_data': task_data,
                    'status': 'starting'
                }
                
                self.metrics['agents_spawned'] += 1
                
                # Log to memory_sub_agents table
                await self._log_agent_spawn(agent_id, agent_type, task_data, priority)
                
                await self._emit_event('agent.spawned', {
                    'agent_id': agent_id,
                    'agent_type': agent_type,
                    'kernel_id': self.kernel_id,
                    'priority': priority,
                    'task': task_data.get('type', 'unknown')
                })
                
                # Start agent task in background (fire and forget)
                asyncio.create_task(self._run_agent(agent_id, agent))
                
                return agent_id
            
        except Exception as e:
            logger.error(f"Failed to spawn agent: {e}")
            self.metrics['errors'] += 1
            
        return None
    
    async def terminate_agent(self, agent_id: str):
        """Terminate a specific sub-agent"""
        if agent_id in self._sub_agents:
            try:
                agent_meta = self._sub_agents[agent_id]
                agent = agent_meta['instance'] if isinstance(agent_meta, dict) else agent_meta
                await self._stop_agent(agent)
                
                # Log termination
                await self._log_agent_termination(agent_id, "manual")
                
                del self._sub_agents[agent_id]
                
                await self._emit_event('agent.terminated', {
                    'agent_id': agent_id,
                    'kernel_id': self.kernel_id
                })
                
            except Exception as e:
                logger.error(f"Error terminating agent {agent_id}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current kernel status and metrics"""
        return {
            'kernel_id': self.kernel_id,
            'domain': self.domain,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'active_agents': len(self._sub_agents),
            'metrics': self.metrics.copy()
        }
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    async def _initialize_watchers(self):
        """Set up filesystem, event, or API watchers"""
        pass
    
    @abstractmethod
    async def _load_pending_work(self):
        """Load any pending work from queues/tables"""
        pass
    
    @abstractmethod
    async def _coordinator_loop(self):
        """Main coordination loop"""
        pass
    
    @abstractmethod
    async def _create_agent(self, agent_type: str, agent_id: str, task_data: Dict) -> Any:
        """Create a sub-agent instance"""
        pass
    
    @abstractmethod
    async def _cleanup(self):
        """Cleanup resources on shutdown"""
        pass
    
    # Internal helper methods
    
    async def _register_kernel(self):
        """Register kernel in memory_sub_agents or similar table"""
        if self.registry:
            try:
                self.registry.insert_row('memory_sub_agents', {
                    'agent_id': self.kernel_id,
                    'agent_type': f'{self.domain}_kernel',
                    'status': 'starting',
                    'started_at': datetime.utcnow().isoformat(),
                    'metadata': {
                        'domain': self.domain,
                        'is_kernel': True
                    }
                })
            except Exception as e:
                logger.warning(f"Could not register kernel: {e}")
    
    async def _terminate_all_agents(self):
        """Terminate all active sub-agents"""
        agent_ids = list(self._sub_agents.keys())
        for agent_id in agent_ids:
            await self.terminate_agent(agent_id)
    
    async def _run_agent(self, agent_id: str, agent: Any):
        """Run an agent's task and handle completion (background task)"""
        start_time = datetime.utcnow()
        success = False
        result = None
        
        try:
            # Update status to running
            if agent_id in self._sub_agents:
                self._sub_agents[agent_id]['status'] = 'running'
            
            result = await agent.execute()
            success = True
            
            self.metrics['jobs_completed'] += 1
            
            # Log completion to memory_sub_agents
            await self._log_agent_completion(agent_id, True, result)
            
            await self._emit_event('agent.completed', {
                'agent_id': agent_id,
                'kernel_id': self.kernel_id,
                'success': True,
                'execution_time': (datetime.utcnow() - start_time).total_seconds(),
                'result': str(result)[:200] if result else None
            })
            
            # Auto-cleanup completed agent
            if agent_id in self._sub_agents:
                del self._sub_agents[agent_id]
                
        except Exception as e:
            logger.error(f"Agent {agent_id} failed: {e}")
            self.metrics['errors'] += 1
            
            # Log failure to memory_sub_agents
            await self._log_agent_completion(agent_id, False, str(e))
            
            await self._emit_event('agent.failed', {
                'agent_id': agent_id,
                'kernel_id': self.kernel_id,
                'error': str(e),
                'execution_time': (datetime.utcnow() - start_time).total_seconds()
            })
            
            # Cleanup failed agent
            if agent_id in self._sub_agents:
                del self._sub_agents[agent_id]
        
        finally:
            logger.debug(f"Agent {agent_id} complete (success={success})")
    
    async def _stop_agent(self, agent: Any):
        """Stop a specific agent"""
        if hasattr(agent, 'stop'):
            await agent.stop()
        elif hasattr(agent, 'cancel'):
            agent.cancel()
    
    async def _log_agent_spawn(self, agent_id: str, agent_type: str, task_data: Dict, priority: str):
        """Log agent spawn to memory_sub_agents table"""
        if not self.registry:
            return
        
        try:
            from backend.subsystems.sub_agents_integration import sub_agents_integration
            await sub_agents_integration.initialize()
            
            await sub_agents_integration.register_agent(
                agent_id=agent_id,
                agent_name=f"{agent_type}_{agent_id.split('_')[-1][:8]}",
                agent_type=agent_type,
                mission=f"Process {task_data.get('type', 'task')}",
                capabilities=[agent_type, task_data.get('type', 'unknown')],
                constraints={
                    'priority': priority,
                    'spawned_by': self.kernel_id,
                    'task_data': task_data
                }
            )
            
            await sub_agents_integration.update_agent_status(
                agent_id=agent_id,
                status='active',
                current_task=task_data.get('type', 'processing')
            )
            
        except Exception as e:
            logger.error(f"Failed to log agent spawn: {e}")
    
    async def _log_agent_completion(self, agent_id: str, success: bool, result: Any):
        """Log agent completion to memory_sub_agents table"""
        try:
            from backend.subsystems.sub_agents_integration import sub_agents_integration
            await sub_agents_integration.initialize()
            
            await sub_agents_integration.log_task_completion(
                agent_id=agent_id,
                task_name=f"Task for {agent_id}",
                success=success,
                execution_time_sec=1.0,
                result_summary=str(result)[:500] if result else "completed"
            )
            
            await sub_agents_integration.update_agent_status(
                agent_id=agent_id,
                status='idle' if success else 'error'
            )
            
        except Exception as e:
            logger.error(f"Failed to log agent completion: {e}")
    
    async def _log_agent_termination(self, agent_id: str, reason: str):
        """Log agent termination"""
        try:
            from backend.subsystems.sub_agents_integration import sub_agents_integration
            await sub_agents_integration.initialize()
            
            await sub_agents_integration.update_agent_status(
                agent_id=agent_id,
                status='terminated',
                current_task=f"Terminated: {reason}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log agent termination: {e}")
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to the event bus"""
        self.last_heartbeat = datetime.utcnow()
        self.metrics['events_processed'] += 1
        
        if self.event_bus:
            try:
                await self.event_bus.emit(event_type, data)
            except Exception as e:
                logger.error(f"Failed to emit event: {e}")
        else:
            # Fallback: log event
            logger.info(f"Event: {event_type} - {data}")
