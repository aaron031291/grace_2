"""
Infrastructure Manager Kernel - Simplified Working Version
"""

import asyncio
import platform
import psutil
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from backend.core.kernel_sdk import KernelSDK
from backend.core.message_bus import message_bus, MessagePriority

# Simple no-op logger
def log_event(*args, **kwargs):
    pass


class HostOS(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


class Host:
    def __init__(self, host_id, hostname, os_type, ip_address):
        self.host_id = host_id
        self.hostname = hostname
        self.os_type = os_type
        self.ip_address = ip_address
        self.status = "healthy"
        self.last_seen = datetime.utcnow()
        self.metrics = {}
    
    def to_dict(self):
        return {
            "host_id": self.host_id,
            "hostname": self.hostname,
            "os_type": self.os_type.value if hasattr(self.os_type, 'value') else self.os_type,
            "status": self.status,
            "last_seen": self.last_seen.isoformat(),
            "metrics": self.metrics
        }


class InfrastructureManagerKernel(KernelSDK):
    """Multi-OS Fabric Manager - Simplified"""
    
    def __init__(self):
        super().__init__(kernel_name="infrastructure_manager")
        self.hosts: Dict[str, Host] = {}
        self._monitor_task = None
        self._heartbeat_task = None
    
    async def initialize(self):
        """Initialize and register local host"""
        await self.register_component(
            capabilities=['host_management', 'dependency_tracking'],
            contracts={'health_check_interval_sec': 30}
        )
        
        # Register local host
        await self.register_local_host()
        
        # Start monitoring
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        print("[INFRA] Infrastructure Manager initialized")
    
    async def register_local_host(self):
        """Register the local machine"""
        system = platform.system().lower()
        if system == "windows":
            os_type = HostOS.WINDOWS
        elif system == "linux":
            os_type = HostOS.LINUX
        elif system == "darwin":
            os_type = HostOS.MACOS
        else:
            os_type = "unknown"
        
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "127.0.0.1"
        
        host_id = f"{hostname}_{system}"
        
        host = Host(host_id, hostname, os_type, ip_address)
        host.metrics = self._collect_metrics()
        host.status = "healthy"
        
        self.hosts[host_id] = host
        
        # Publish registration
        await message_bus.publish(
            source="infrastructure_manager",
            topic="infrastructure.host.registered",
            payload=host.to_dict(),
            priority=MessagePriority.HIGH
        )
        
        print(f"[INFRA] Registered host: {hostname} ({os_type})")
        
        return host_id
    
    def _collect_metrics(self):
        """Collect basic metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        except:
            return {}
    
    async def _monitor_loop(self):
        """Monitor hosts"""
        while True:
            try:
                await asyncio.sleep(30)
                
                # Update local host metrics
                hostname = socket.gethostname()
                for host_id, host in self.hosts.items():
                    if host.hostname == hostname:
                        host.metrics = self._collect_metrics()
                        host.last_seen = datetime.utcnow()
                        
            except Exception as e:
                print(f"[INFRA] Monitor error: {e}")
    
    async def _heartbeat_loop(self):
        """Send heartbeats"""
        while True:
            try:
                await asyncio.sleep(10)
                await self.heartbeat()
                
                await self.report_status(
                    health="healthy",
                    metrics={
                        "total_hosts": len(self.hosts),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                print(f"[INFRA] Heartbeat error: {e}")
    
    async def get_all_hosts(self):
        """Get all registered hosts"""
        return [host.to_dict() for host in self.hosts.values()]
    
    async def shutdown(self):
        """Cleanup"""
        if self._monitor_task:
            self._monitor_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()


# Global instance
infrastructure_manager = InfrastructureManagerKernel()
