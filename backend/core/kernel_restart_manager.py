"""
Kernel Restart Manager - Self-Healing Kernel Supervision
Part of Layer 1 Control Plane

Monitors kernel heartbeats and automatically restarts failed kernels.
Works with external watchdog for full resilience.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
from enum import Enum

from backend.core.message_bus import message_bus, MessagePriority
from backend.core.kernel_sdk import KernelSDK


class RestartReason(str, Enum):
    """Why a kernel was restarted"""
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    HEALTH_DEGRADED = "health_degraded"
    CRASH_DETECTED = "crash_detected"
    MANUAL_REQUEST = "manual_request"
    DEPENDENCY_DRIFT = "dependency_drift"


class KernelRestartManager:
    """
    Manages automatic kernel restarts
    
    Integration with Layer 1:
    - Control Plane: Calls this to monitor kernel health
    - Self-Healing: Receives restart events, applies playbooks
    - Governance: Approves restarts for critical kernels
    - Memory: Persists restart history
    - Immutable Log: Records all restart events
    """
    
    def __init__(self):
        self.kernels: Dict[str, Dict[str, Any]] = {}
        self.restart_history = []
        
        # Configuration
        self.heartbeat_timeout = 60  # seconds
        self.max_restart_attempts = 3
        self.restart_cooldown = 30  # seconds between restart attempts
        
        # Monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self.enabled = True
    
    async def start(self):
        """Start the restart manager"""
        self._monitor_task = asyncio.create_task(self._monitor_kernels())
        print("[RESTART-MGR] Kernel restart manager started")
    
    def register_kernel(
        self,
        kernel_name: str,
        restart_function: Callable,
        critical: bool = False
    ):
        """Register a kernel for monitoring"""
        
        self.kernels[kernel_name] = {
            "name": kernel_name,
            "restart_function": restart_function,
            "critical": critical,
            "last_heartbeat": datetime.utcnow(),
            "status": "healthy",
            "restart_count": 0,
            "last_restart": None
        }
        
        print(f"[RESTART-MGR] Registered kernel: {kernel_name} (critical={critical})")
    
    async def record_heartbeat(self, kernel_name: str):
        """Record a heartbeat from a kernel"""
        
        if kernel_name in self.kernels:
            self.kernels[kernel_name]["last_heartbeat"] = datetime.utcnow()
            self.kernels[kernel_name]["status"] = "healthy"
    
    async def _monitor_kernels(self):
        """Continuously monitor kernel heartbeats"""
        
        while self.enabled:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                
                now = datetime.utcnow()
                timeout_cutoff = now - timedelta(seconds=self.heartbeat_timeout)
                
                for kernel_name, kernel_info in self.kernels.items():
                    last_hb = kernel_info["last_heartbeat"]
                    
                    # Check if heartbeat is stale
                    if last_hb < timeout_cutoff and kernel_info["status"] != "restarting":
                        print(f"[RESTART-MGR] ⚠️ Kernel {kernel_name} heartbeat timeout!")
                        await self._restart_kernel(
                            kernel_name,
                            RestartReason.HEARTBEAT_TIMEOUT
                        )
            
            except Exception as e:
                print(f"[RESTART-MGR] Monitor error: {e}")
    
    async def _restart_kernel(
        self,
        kernel_name: str,
        reason: RestartReason
    ):
        """Restart a failed kernel"""
        
        kernel_info = self.kernels.get(kernel_name)
        if not kernel_info:
            return
        
        # Check restart attempts
        if kernel_info["restart_count"] >= self.max_restart_attempts:
            await self._handle_max_restarts(kernel_name)
            return
        
        # Check cooldown
        if kernel_info["last_restart"]:
            elapsed = (datetime.utcnow() - kernel_info["last_restart"]).total_seconds()
            if elapsed < self.restart_cooldown:
                print(f"[RESTART-MGR] {kernel_name} in restart cooldown ({elapsed:.0f}s)")
                return
        
        print(f"[RESTART-MGR] 🔄 Restarting kernel: {kernel_name} (reason: {reason.value})")
        
        kernel_info["status"] = "restarting"
        kernel_info["restart_count"] += 1
        kernel_info["last_restart"] = datetime.utcnow()
        
        # Record restart event
        restart_event = {
            "kernel_name": kernel_name,
            "reason": reason.value,
            "timestamp": datetime.utcnow().isoformat(),
            "attempt": kernel_info["restart_count"],
            "critical": kernel_info["critical"]
        }
        
        self.restart_history.append(restart_event)
        
        # Publish restart event
        await message_bus.publish(
            source="restart_manager",
            topic="kernel.restart.initiated",
            payload=restart_event,
            priority=MessagePriority.HIGH
        )
        
        try:
            # Call the kernel's restart function
            restart_fn = kernel_info["restart_function"]
            await restart_fn()
            
            kernel_info["status"] = "healthy"
            kernel_info["last_heartbeat"] = datetime.utcnow()
            
            # Publish success
            await message_bus.publish(
                source="restart_manager",
                topic="kernel.restart.success",
                payload={
                    **restart_event,
                    "success": True,
                    "completed_at": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.NORMAL
            )
            
            print(f"[RESTART-MGR] ✅ Kernel {kernel_name} restarted successfully")
            
        except Exception as e:
            kernel_info["status"] = "failed"
            
            # Publish failure
            await message_bus.publish(
                source="restart_manager",
                topic="kernel.restart.failed",
                payload={
                    **restart_event,
                    "success": False,
                    "error": str(e),
                    "completed_at": datetime.utcnow().isoformat()
                },
                priority=MessagePriority.HIGH
            )
            
            print(f"[RESTART-MGR] ❌ Failed to restart {kernel_name}: {e}")
    
    async def _handle_max_restarts(self, kernel_name: str):
        """Handle kernel that hit max restart attempts"""
        
        kernel_info = self.kernels[kernel_name]
        
        alert = {
            "kernel_name": kernel_name,
            "critical": kernel_info["critical"],
            "restart_attempts": kernel_info["restart_count"],
            "timestamp": datetime.utcnow().isoformat(),
            "action_needed": "manual_intervention"
        }
        
        # Publish critical alert
        await message_bus.publish(
            source="restart_manager",
            topic="kernel.restart.max_attempts",
            payload=alert,
            priority=MessagePriority.CRITICAL
        )
        
        print(f"[RESTART-MGR] 🚨 CRITICAL: {kernel_name} hit max restart attempts!")
        print(f"[RESTART-MGR] Manual intervention required")
        
        # If critical kernel, alert control plane
        if kernel_info["critical"]:
            await message_bus.publish(
                source="restart_manager",
                topic="system.critical_kernel_down",
                payload=alert,
                priority=MessagePriority.CRITICAL
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get restart manager status"""
        
        return {
            "enabled": self.enabled,
            "monitored_kernels": len(self.kernels),
            "total_restarts": len(self.restart_history),
            "recent_restarts": self.restart_history[-10:],
            "kernel_status": {
                name: {
                    "status": info["status"],
                    "restart_count": info["restart_count"],
                    "last_heartbeat": info["last_heartbeat"].isoformat()
                }
                for name, info in self.kernels.items()
            }
        }
    
    async def shutdown(self):
        """Stop the restart manager"""
        self.enabled = False
        if self._monitor_task:
            self._monitor_task.cancel()


# Global instance
kernel_restart_manager = KernelRestartManager()
