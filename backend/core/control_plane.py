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
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

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
    
    def __init__(self, name: str, boot_priority: int, critical: bool = True):
        self.name = name
        self.boot_priority = boot_priority
        self.critical = critical  # System fails if critical kernel fails
        self.state = KernelState.STOPPED
        self.started_at = None
        self.last_heartbeat = None
        self.restart_count = 0
        self.task = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'state': self.state.value,
            'critical': self.critical,
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
    
    def _define_kernels(self) -> Dict[str, Kernel]:
        """Define all Grace kernels"""
        
        return {
            # Core infrastructure (boot first)
            'message_bus': Kernel('message_bus', boot_priority=1, critical=True),
            'immutable_log': Kernel('immutable_log', boot_priority=2, critical=True),
            'clarity_framework': Kernel('clarity_framework', boot_priority=3, critical=True),
            'verification_framework': Kernel('verification_framework', boot_priority=4, critical=True),
            'secret_manager': Kernel('secret_manager', boot_priority=5, critical=True),
            'governance': Kernel('governance', boot_priority=6, critical=True),
            
            # Execution layer
            'memory_fusion': Kernel('memory_fusion', boot_priority=10, critical=False),
            'librarian': Kernel('librarian', boot_priority=11, critical=False),
            'self_healing': Kernel('self_healing', boot_priority=12, critical=False),
            'coding_agent': Kernel('coding_agent', boot_priority=13, critical=False),
            'sandbox': Kernel('sandbox', boot_priority=14, critical=False),
            
            # Services
            'health_monitor': Kernel('health_monitor', boot_priority=20, critical=True),
            'trigger_mesh': Kernel('trigger_mesh', boot_priority=21, critical=False),
            'scheduler': Kernel('scheduler', boot_priority=22, critical=False),
            
            # API layer (boots last)
            'api_server': Kernel('api_server', boot_priority=30, critical=False),
            'websocket': Kernel('websocket', boot_priority=31, critical=False)
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
            # In production, would stop actual kernel process
            kernel.state = KernelState.STOPPED
            
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
