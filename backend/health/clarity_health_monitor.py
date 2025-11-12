# -*- coding: utf-8 -*-
"""
Clarity Health Monitor - Example of BaseComponent integration
Monitors system health and publishes events via clarity framework
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from backend.clarity import (
    BaseComponent,
    ComponentStatus,
    get_event_bus,
    Event,
    get_manifest,
    TrustLevel,
    GraceLoopOutput
)


class ClarityHealthMonitor(BaseComponent):
    """
    Health monitoring component using Clarity Framework.
    Demonstrates proper integration of BaseComponent, EventBus, and GraceLoopOutput.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.component_type = "health_monitor"
        if config:
            self.config.update(config)
        
        # Component state
        self.event_bus = get_event_bus()
        self.monitoring_task = None
        self.health_checks = []
        self.last_check_time = None
        self.check_interval = self.config.get("check_interval", 60)  # seconds
    
    async def activate(self) -> bool:
        """Activate the health monitor"""
        try:
            self.set_status(ComponentStatus.ACTIVATING)
            
            # Register with manifest
            manifest = get_manifest()
            manifest.register(
                self,
                trust_level=TrustLevel.VERIFIED,  # Health monitor is trusted
                role_tags=["health", "monitoring", "core"]
            )
            
            # Start monitoring loop
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self.set_status(ComponentStatus.ACTIVE)
            self.activated_at = datetime.utcnow()
            
            # Publish activation event
            await self.event_bus.publish(Event(
                event_type="component.activated",
                source=self.component_id,
                payload={
                    "component_type": self.component_type,
                    "check_interval": self.check_interval
                }
            ))
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    async def deactivate(self) -> bool:
        """Deactivate the health monitor"""
        try:
            self.set_status(ComponentStatus.DEACTIVATING)
            
            # Stop monitoring loop
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Unregister from manifest
            manifest = get_manifest()
            manifest.unregister(self.component_id)
            
            self.set_status(ComponentStatus.STOPPED)
            
            # Publish deactivation event
            await self.event_bus.publish(Event(
                event_type="component.deactivated",
                source=self.component_id,
                payload={"component_type": self.component_type}
            ))
            
            return True
            
        except Exception as e:
            self.set_status(ComponentStatus.ERROR, str(e))
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "status": self.status.value,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "check_interval": self.check_interval,
            "health_checks_count": len(self.health_checks),
            "config": self.config,
            "metadata": self.metadata
        }
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Publish error event
                await self.event_bus.publish(Event(
                    event_type="component.error",
                    source=self.component_id,
                    payload={"error": str(e)}
                ))
    
    async def _perform_health_check(self):
        """Perform a health check cycle"""
        # Create loop output for traceability
        loop_output = GraceLoopOutput(
            loop_type="health_check",
            component_id=self.component_id
        )
        
        try:
            self.last_check_time = datetime.utcnow()
            
            # Perform checks (simplified example)
            manifest = get_manifest()
            active_components = manifest.get_active_components()
            
            health_status = {
                "timestamp": self.last_check_time.isoformat(),
                "active_components": len(active_components),
                "system_healthy": len(active_components) > 0
            }
            
            # Mark loop as completed
            loop_output.mark_completed(
                results=health_status,
                confidence=1.0
            )
            
            # Publish health status
            event_type = "health.healthy" if health_status["system_healthy"] else "health.degraded"
            await self.event_bus.publish(Event(
                event_type=event_type,
                source=self.component_id,
                payload={
                    "loop_output": loop_output.to_dict(),
                    "health_status": health_status
                }
            ))
            
            # Store check result
            self.health_checks.append(loop_output)
            # Keep only last 100 checks
            if len(self.health_checks) > 100:
                self.health_checks.pop(0)
            
        except Exception as e:
            loop_output.mark_failed(str(e))
            await self.event_bus.publish(Event(
                event_type="loop.failed",
                source=self.component_id,
                payload={
                    "loop_output": loop_output.to_dict(),
                    "error": str(e)
                }
            ))
    
    def get_recent_checks(self, limit: int = 10) -> list:
        """Get recent health check results"""
        return [check.to_dict() for check in self.health_checks[-limit:]]


# Example usage
async def demo():
    """Demonstrate the clarity health monitor"""
    
    # Create and activate monitor
    monitor = ClarityHealthMonitor(config={"check_interval": 5})
    success = await monitor.activate()
    
    if success:
        print(f"Health monitor activated: {monitor.component_id}")
        
        # Let it run for a bit
        await asyncio.sleep(12)
        
        # Check status
        status = monitor.get_status()
        print(f"Monitor status: {status}")
        
        # Get recent checks
        checks = monitor.get_recent_checks()
        print(f"Recent checks: {len(checks)}")
        
        # Deactivate
        await monitor.deactivate()
        print("Monitor deactivated")


if __name__ == "__main__":
    asyncio.run(demo())
