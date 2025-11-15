"""
Grace's Control Plane
Minimal orchestrator that manages all kernels

Responsibilities:
- Boot all kernels in correct order
- Monitor health (heartbeats)
- Auto-restart crashed kernels
- Maintain system state (running/paused/stopped)
- Coordinate shutdown
"""

import asyncio
import logging
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .message_bus import message_bus, MessagePriority
from .schemas import MessageType, create_kernel_message, KernelStatusPayload, TrustLevel

logger = logging.getLogger(__name__)


class KernelState(Enum):
    """Kernel state"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    RESTARTING = "restarting"


class Kernel:
    """Represents a kernel in the system"""
    
    def __init__(self, name: str, boot_priority: int, critical: bool = True, tier: str = "core"):
        self.name = name
        self.boot_priority = boot_priority
        self.critical = critical  # System fails if critical kernel fails
        self.tier = tier
        self.state = KernelState.STOPPED
        self.started_at = None
        self.last_heartbeat = None
        self.restart_count = 0
        self.task: Optional[asyncio.Task] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'state': self.state.value,
            'critical': self.critical,
            'tier': self.tier,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'restart_count': self.restart_count
        }


class ControlPlane:
    """
    Grace's control plane orchestrator
    
    The core that keeps everything running
    Manages kernel lifecycle and system state
    """
    
    def __init__(self):
        self.system_state = "stopped"
        self.kernels = self._define_kernels()
        self.heartbeat_timeout = 30  # seconds
        self.max_restarts = 3
        self.running = False
        self._worker_pools = defaultdict(lambda: 1)
    
    def _define_kernels(self) -> Dict[str, Kernel]:
        """Define all Grace kernels - 20 total (with voice loop)"""
        
        return {
            # Core infrastructure (boot first)
            'message_bus': Kernel('message_bus', boot_priority=1, critical=True, tier='core_infra'),
            'immutable_log': Kernel('immutable_log', boot_priority=2, critical=True, tier='core_infra'),
            'clarity_framework': Kernel('clarity_framework', boot_priority=3, critical=True, tier='core_infra'),
            'verification_framework': Kernel('verification_framework', boot_priority=4, critical=True, tier='core_infra'),
            'secret_manager': Kernel('secret_manager', boot_priority=5, critical=True, tier='core_infra'),
            'governance': Kernel('governance', boot_priority=6, critical=True, tier='core_infra'),
            'infrastructure_manager': Kernel('infrastructure_manager', boot_priority=7, critical=True, tier='core_infra'),
            
            # Execution layer
            'memory_fusion': Kernel('memory_fusion', boot_priority=10, critical=False, tier='execution'),
            'librarian': Kernel('librarian', boot_priority=11, critical=False, tier='execution'),
            'self_healing': Kernel('self_healing', boot_priority=12, critical=False, tier='execution'),
            'coding_agent': Kernel('coding_agent', boot_priority=13, critical=False, tier='execution'),
            'sandbox': Kernel('sandbox', boot_priority=14, critical=False, tier='execution'),
            
            # Layer 3 - Agentic Systems
            'agentic_spine': Kernel('agentic_spine', boot_priority=15, critical=False, tier='agentic'),
            'voice_conversation': Kernel('voice_conversation', boot_priority=16, critical=False, tier='agentic'),
            'meta_loop': Kernel('meta_loop', boot_priority=17, critical=False, tier='agentic'),
            'learning_integration': Kernel('learning_integration', boot_priority=18, critical=False, tier='agentic'),
            
            # Services
            'health_monitor': Kernel('health_monitor', boot_priority=20, critical=True, tier='services'),
            'trigger_mesh': Kernel('trigger_mesh', boot_priority=21, critical=False, tier='services'),
            'scheduler': Kernel('scheduler', boot_priority=22, critical=False, tier='services'),
            
            # API layer (boots last)
            'api_server': Kernel('api_server', boot_priority=30, critical=False, tier='api')
        }
    
    async def start(self):
        """Start control plane and boot all kernels"""
        
        logger.info("[CONTROL-PLANE] Starting Grace's control plane...")
        
        self.running = True
        self.system_state = "booting"
        
        # Publish system event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'booting', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
        
        # Boot kernels in priority order
        sorted_kernels = sorted(
            self.kernels.values(),
            key=lambda k: k.boot_priority
        )
        
        for kernel in sorted_kernels:
            await self._boot_kernel(kernel)
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor_loop())
        
        # System is running
        self.system_state = "running"
        
        logger.info("[CONTROL-PLANE] All kernels booted, system RUNNING")
        
        # Publish running event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'running', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
    
    async def stop(self):
        """Stop control plane and all kernels"""
        
        logger.info("[CONTROL-PLANE] Stopping Grace's control plane...")
        
        self.running = False
        self.system_state = "stopping"
        
        # Publish stopping event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'stopping', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.CRITICAL
        )
        
        # Stop kernels in reverse priority order
        sorted_kernels = sorted(
            self.kernels.values(),
            key=lambda k: k.boot_priority,
            reverse=True
        )
        
        for kernel in sorted_kernels:
            await self._stop_kernel(kernel)
        
        self.system_state = "stopped"
        
        logger.info("[CONTROL-PLANE] All kernels stopped, system STOPPED")
    
    async def pause(self):
        """Pause system (kernels stay alive but don't process)"""
        
        logger.info("[CONTROL-PLANE] Pausing system...")
        
        self.system_state = "paused"
        
        # Publish pause event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'pause', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
        
        logger.info("[CONTROL-PLANE] System PAUSED")
    
    async def resume(self):
        """Resume system"""
        
        logger.info("[CONTROL-PLANE] Resuming system...")
        
        self.system_state = "running"
        
        # Publish resume event
        await message_bus.publish(
            source='control_plane',
            topic='system.control',
            payload={'action': 'resume', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
        
        logger.info("[CONTROL-PLANE] System RUNNING")
    
    async def _boot_kernel(self, kernel: Kernel):
        """Boot a single kernel"""
        
        logger.info(f"[CONTROL-PLANE] Booting kernel: {kernel.name}")
        
        kernel.state = KernelState.STARTING
        
        try:
            # In production, would start actual kernel process
            # For now, mark as running
            kernel.state = KernelState.RUNNING
            kernel.started_at = datetime.utcnow()
            kernel.last_heartbeat = datetime.utcnow()
            # Spawn simulated heartbeat task
            if kernel.task:
                kernel.task.cancel()
            kernel.task = asyncio.create_task(self._kernel_heartbeat_loop(kernel))
            
            # Publish kernel started event
            await message_bus.publish(
                source='control_plane',
                topic=f'kernel.{kernel.name}',
                payload={'action': 'started', 'timestamp': datetime.utcnow().isoformat()},
                priority=MessagePriority.HIGH
            )
            
            logger.info(f"[CONTROL-PLANE] ✓ {kernel.name} RUNNING")
        
        except Exception as e:
            kernel.state = KernelState.FAILED
            logger.error(f"[CONTROL-PLANE] ✗ {kernel.name} FAILED: {e}")
            
            if kernel.critical:
                raise Exception(f"Critical kernel {kernel.name} failed to start")
    
    async def _stop_kernel(self, kernel: Kernel):
        """Stop a single kernel"""
        
        logger.info(f"[CONTROL-PLANE] Stopping kernel: {kernel.name}")
        
        try:
            if kernel.task:
                kernel.task.cancel()
                try:
                    await kernel.task
                except asyncio.CancelledError:
                    pass
                kernel.task = None
            
            kernel.state = KernelState.STOPPED
            kernel.last_heartbeat = None
            
            # Publish kernel stopped event
            await message_bus.publish(
                source='control_plane',
                topic=f'kernel.{kernel.name}',
                payload={'action': 'stopped', 'timestamp': datetime.utcnow().isoformat()},
                priority=MessagePriority.HIGH
            )
            
            logger.info(f"[CONTROL-PLANE] ✓ {kernel.name} STOPPED")
        
        except Exception as e:
            logger.error(f"[CONTROL-PLANE] Error stopping {kernel.name}: {e}")

    async def _kernel_heartbeat_loop(self, kernel: Kernel):
        """Simulated heartbeat loop for kernels without dedicated processes."""
        try:
            while self.running and kernel.state == KernelState.RUNNING:
                kernel.last_heartbeat = datetime.utcnow()
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass
    
    async def _health_monitor_loop(self):
        """
        TRIGGER LOOP: Health monitoring
        Runs continuously, checks kernel heartbeats, restarts failures
        """
        
        while self.running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                now = datetime.utcnow()
                
                for kernel in self.kernels.values():
                    if kernel.state == KernelState.RUNNING:
                        # Check heartbeat
                        if kernel.last_heartbeat:
                            time_since_heartbeat = now - kernel.last_heartbeat
                            
                            if time_since_heartbeat.total_seconds() > self.heartbeat_timeout:
                                logger.warning(f"[CONTROL-PLANE] {kernel.name} missed heartbeat")
                                
                                # Auto-restart if not exceeded max
                                if kernel.restart_count < self.max_restarts:
                                    await self._restart_kernel(kernel)
                                else:
                                    logger.error(f"[CONTROL-PLANE] {kernel.name} exceeded max restarts")
                                    kernel.state = KernelState.FAILED
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CONTROL-PLANE] Health monitor error: {e}")
    
    async def _restart_kernel(self, kernel: Kernel):
        """Restart a kernel"""
        
        logger.warning(f"[CONTROL-PLANE] Restarting kernel: {kernel.name}")
        
        kernel.state = KernelState.RESTARTING
        kernel.restart_count += 1
        
        # Stop
        await self._stop_kernel(kernel)
        
        # Wait
        await asyncio.sleep(2)
        
        # Start
        await self._boot_kernel(kernel)
        
        # Publish restart event
        await message_bus.publish(
            source='control_plane',
            topic='system.health',
            payload={
                'action': 'kernel_restarted',
                'kernel': kernel.name,
                'restart_count': kernel.restart_count,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.HIGH
        )
    
    async def pause_kernel(self, kernel_name: str):
        """Pause a non-critical kernel to shed load."""
        kernel = self.kernels.get(kernel_name)
        if not kernel or kernel.state != KernelState.RUNNING:
            return
        
        logger.info("[CONTROL-PLANE] Pausing kernel: %s", kernel.name)
        if kernel.task:
            kernel.task.cancel()
            try:
                await kernel.task
            except asyncio.CancelledError:
                pass
            kernel.task = None
        
        kernel.state = KernelState.PAUSED
        await message_bus.publish(
            source='control_plane',
            topic=f'kernel.{kernel.name}',
            payload={'action': 'paused', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
    
    async def resume_kernel(self, kernel_name: str):
        """Resume a paused kernel."""
        kernel = self.kernels.get(kernel_name)
        if not kernel or kernel.state != KernelState.PAUSED:
            return
        
        logger.info("[CONTROL-PLANE] Resuming kernel: %s", kernel.name)
        kernel.state = KernelState.RUNNING
        kernel.last_heartbeat = datetime.utcnow()
        kernel.task = asyncio.create_task(self._kernel_heartbeat_loop(kernel))
        await message_bus.publish(
            source='control_plane',
            topic=f'kernel.{kernel.name}',
            payload={'action': 'resumed', 'timestamp': datetime.utcnow().isoformat()},
            priority=MessagePriority.HIGH
        )
    
    def _get_worker_count(self, queue_name: str) -> int:
        return self._worker_pools[queue_name]
    
    async def _set_worker_count(self, queue_name: str, count: int):
        self._worker_pools[queue_name] = count
        await message_bus.publish(
            source='control_plane',
            topic='system.scaling',
            payload={
                'action': 'worker_scale',
                'queue': queue_name,
                'workers': count,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority=MessagePriority.HIGH
        )
    
    async def apply_self_healing_action(self, action: str, issue: Dict[str, Any]):
        """Execute remediation actions requested by self-healing triggers."""
        if action == 'scale_workers':
            queue_name = issue.get('queue', 'default')
            current = self._get_worker_count(queue_name)
            increment = issue.get('increment', 2)
            max_workers = issue.get('max_workers', 10)
            new_workers = min(current + increment, max_workers)
            await self._set_worker_count(queue_name, new_workers)
            logger.info("[CONTROL-PLANE] ⚡ Scaled %s workers: %s → %s", queue_name, current, new_workers)
        
        elif action == 'shed_load':
            victim = self._select_non_critical_kernel()
            if victim:
                await self.pause_kernel(victim.name)
                logger.info("[CONTROL-PLANE] ⚡ Paused %s to shed load", victim.name)
            else:
                logger.warning("[CONTROL-PLANE] No non-critical kernels available to pause")
        
        elif action == 'restore_model_weights':
            model_file = issue.get('file')
            if not model_file:
                logger.warning("[CONTROL-PLANE] restore_model_weights missing 'file' in issue payload")
                return
            
            snapshot_dir = Path(__file__).resolve().parents[2] / '.grace_snapshots' / 'models'
            snapshot_file = snapshot_dir / Path(model_file).name
            if snapshot_file.exists():
                snapshot_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(snapshot_file, model_file)
                    logger.info("[CONTROL-PLANE] ⚡ Restored %s from snapshot", Path(model_file).name)
                except Exception as exc:
                    logger.error("[CONTROL-PLANE] Failed to restore %s: %s", model_file, exc)
            else:
                logger.warning("[CONTROL-PLANE] Snapshot not found for %s", model_file)
    
    def _select_non_critical_kernel(self) -> Optional[Kernel]:
        """Return a running non-critical kernel for load shedding."""
        for kernel in self.kernels.values():
            if not kernel.critical and kernel.state == KernelState.RUNNING:
                return kernel
        return None
    
    def _check_acl(self, kernel: str, topic: str, subscribe: bool = False) -> bool:
        """Check if kernel has access to topic"""
        
        allowed = self.topic_acls.get(topic, [])
        
        # If no ACL, allow
        if not allowed:
            return True
        
        # Check if kernel is allowed
        return kernel in allowed
    
    async def heartbeat(self, kernel_name: str):
        """Receive heartbeat from kernel"""
        
        kernel = self.kernels.get(kernel_name)
        
        if kernel:
            kernel.last_heartbeat = datetime.utcnow()
            logger.debug(f"[CONTROL-PLANE] Heartbeat: {kernel_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get control plane status"""
        
        return {
            'system_state': self.system_state,
            'running': self.running,
            'kernels': {name: k.to_dict() for name, k in self.kernels.items()},
            'total_kernels': len(self.kernels),
            'running_kernels': sum(1 for k in self.kernels.values() if k.state == KernelState.RUNNING),
            'failed_kernels': sum(1 for k in self.kernels.values() if k.state == KernelState.FAILED)
        }


# Global instance - Grace's brain stem
control_plane = ControlPlane()
