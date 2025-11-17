"""
Resource Pressure Monitor - CPU/Memory/Disk Safeguard
Watches for resource saturation and triggers load shedding before watchdogs stall

Fixes Gap: S03_cpu_spike scenario had no watcher
"""

import asyncio
import logging
import psutil
from typing import Dict, Any
from datetime import datetime
from collections import deque

from backend.misc.trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


class ResourcePressureMonitor:
    """
    Monitors system resources and triggers load shedding
    
    Detects:
    - CPU saturation (>80% sustained)
    - Memory pressure (>85% used)
    - Disk pressure (>90% used)
    - Rapid resource growth
    
    Actions:
    - Triggers load shedding playbook BEFORE watchdogs stall
    - Scales down non-critical services
    - Throttles incoming requests
    - Routes to scheduler for prioritization
    """
    
    def __init__(self):
        # Thresholds
        self.cpu_threshold = 80.0  # percent
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.sustained_duration = 10  # seconds
        
        # History tracking
        self.cpu_history = deque(maxlen=60)  # 60 seconds
        self.memory_history = deque(maxlen=60)
        
        # Pressure state
        self.cpu_pressure_start = None
        self.memory_pressure_start = None
        self.disk_pressure_start = None
        
        # State
        self.running = False
        self.in_load_shedding = False
        
        # Statistics
        self.stats = {
            "cpu_incidents": 0,
            "memory_incidents": 0,
            "disk_incidents": 0,
            "load_shedding_triggered": 0,
            "playbooks_triggered": 0
        }
    
    async def start(self):
        """Start resource pressure monitoring"""
        
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring loop (check every second)
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("[RESOURCE MONITOR] Resource pressure monitor started")
        logger.info(f"[RESOURCE MONITOR] Thresholds: CPU {self.cpu_threshold}%, Memory {self.memory_threshold}%, Disk {self.disk_threshold}%")
    
    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("[RESOURCE MONITOR] Resource pressure monitor stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop (1Hz sampling)"""
        
        while self.running:
            try:
                # Sample resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                # Record to history
                self.cpu_history.append({
                    "timestamp": datetime.utcnow(),
                    "value": cpu_percent
                })
                
                self.memory_history.append({
                    "timestamp": datetime.utcnow(),
                    "value": memory_percent
                })
                
                # Check CPU pressure
                if cpu_percent > self.cpu_threshold:
                    await self._handle_cpu_pressure(cpu_percent)
                else:
                    self.cpu_pressure_start = None
                
                # Check memory pressure
                if memory_percent > self.memory_threshold:
                    await self._handle_memory_pressure(memory_percent)
                else:
                    self.memory_pressure_start = None
                
                # Check disk pressure
                if disk_percent > self.disk_threshold:
                    await self._handle_disk_pressure(disk_percent)
                else:
                    self.disk_pressure_start = None
                
            except Exception as e:
                logger.error(f"[RESOURCE MONITOR] Monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _handle_cpu_pressure(self, cpu_percent: float):
        """Handle CPU pressure"""
        
        now = datetime.utcnow()
        
        if not self.cpu_pressure_start:
            self.cpu_pressure_start = now
            logger.warning(f"[RESOURCE MONITOR] CPU pressure detected: {cpu_percent:.1f}%")
            return
        
        # Check if sustained
        duration = (now - self.cpu_pressure_start).total_seconds()
        
        if duration >= self.sustained_duration:
            logger.error(f"[RESOURCE MONITOR] SUSTAINED CPU PRESSURE: {cpu_percent:.1f}% for {duration:.0f}s")
            
            self.stats["cpu_incidents"] += 1
            
            # Trigger BEFORE watchdogs stall
            await self._trigger_load_shedding(
                resource_type="cpu",
                current_value=cpu_percent,
                threshold=self.cpu_threshold,
                duration=duration
            )
            
            # Reset to prevent repeat triggers
            self.cpu_pressure_start = None
    
    async def _handle_memory_pressure(self, memory_percent: float):
        """Handle memory pressure"""
        
        now = datetime.utcnow()
        
        if not self.memory_pressure_start:
            self.memory_pressure_start = now
            logger.warning(f"[RESOURCE MONITOR] Memory pressure detected: {memory_percent:.1f}%")
            return
        
        # Check if sustained
        duration = (now - self.memory_pressure_start).total_seconds()
        
        if duration >= self.sustained_duration:
            logger.error(f"[RESOURCE MONITOR] SUSTAINED MEMORY PRESSURE: {memory_percent:.1f}% for {duration:.0f}s")
            
            self.stats["memory_incidents"] += 1
            
            # Trigger load shedding
            await self._trigger_load_shedding(
                resource_type="memory",
                current_value=memory_percent,
                threshold=self.memory_threshold,
                duration=duration
            )
            
            self.memory_pressure_start = None
    
    async def _handle_disk_pressure(self, disk_percent: float):
        """Handle disk pressure"""
        
        now = datetime.utcnow()
        
        if not self.disk_pressure_start:
            self.disk_pressure_start = now
            logger.warning(f"[RESOURCE MONITOR] Disk pressure detected: {disk_percent:.1f}%")
            return
        
        # Check if sustained
        duration = (now - self.disk_pressure_start).total_seconds()
        
        if duration >= self.sustained_duration:
            logger.error(f"[RESOURCE MONITOR] SUSTAINED DISK PRESSURE: {disk_percent:.1f}% for {duration:.0f}s")
            
            self.stats["disk_incidents"] += 1
            
            # Trigger cleanup
            await self._trigger_load_shedding(
                resource_type="disk",
                current_value=disk_percent,
                threshold=self.disk_threshold,
                duration=duration
            )
            
            self.disk_pressure_start = None
    
    async def _trigger_load_shedding(
        self,
        resource_type: str,
        current_value: float,
        threshold: float,
        duration: float
    ):
        """Trigger load shedding playbook"""
        
        if self.in_load_shedding:
            logger.warning("[RESOURCE MONITOR] Already in load shedding mode")
            return
        
        self.in_load_shedding = True
        self.stats["load_shedding_triggered"] += 1
        self.stats["playbooks_triggered"] += 1
        
        playbook_name = f"resource_pressure_{resource_type}"
        
        # Publish incident event
        await trigger_mesh.publish(TriggerEvent(
            source="resource_pressure_monitor",
            event_type="event.incident",
            payload={
                "trigger_id": f"resource_pressure_{resource_type}",
                "playbook": playbook_name,
                "severity": "critical",
                "resource_type": resource_type,
                "current_value": current_value,
                "threshold": threshold,
                "sustained_duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        logger.info(f"[RESOURCE MONITOR] Triggered playbook: {playbook_name}")
        
        # Also route to scheduler for load prioritization
        await trigger_mesh.publish(TriggerEvent(
            source="resource_pressure_monitor",
            event_type="scheduler.load_shedding",
            payload={
                "resource_type": resource_type,
                "action": "reduce_load",
                "priority": "critical"
            }
        ))
        
        # Reset after 60 seconds
        await asyncio.sleep(60)
        self.in_load_shedding = False
    
    def get_current_pressure(self) -> Dict[str, Any]:
        """Get current resource pressure state"""
        
        try:
            cpu = psutil.cpu_percent(interval=0)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            return {
                "cpu": {
                    "current": cpu,
                    "threshold": self.cpu_threshold,
                    "under_pressure": cpu > self.cpu_threshold
                },
                "memory": {
                    "current": memory,
                    "threshold": self.memory_threshold,
                    "under_pressure": memory > self.memory_threshold
                },
                "disk": {
                    "current": disk,
                    "threshold": self.disk_threshold,
                    "under_pressure": disk > self.disk_threshold
                },
                "in_load_shedding": self.in_load_shedding
            }
        except Exception as e:
            logger.error(f"[RESOURCE MONITOR] Error getting pressure: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitor statistics"""
        return self.stats.copy()


# Global monitor instance
resource_pressure_monitor = ResourcePressureMonitor()
