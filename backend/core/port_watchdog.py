"""
Port Watchdog
Monitors all ports 8000-8010, tracks usage, detects issues
INTEGRATED with Guardian for auto-remediation
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import requests

from .port_manager import port_manager

logger = logging.getLogger(__name__)


class PortWatchdog:
    """
    Watchdog that monitors all allocated ports
    - Health checks every 30 seconds
    - Detects crashed services
    - Cleans up stale allocations
    - Tracks metadata (requests, errors, uptime)
    - Logs everything
    """
    
    def __init__(self, check_interval: int = 30, initial_delay: int = 60):
        self.check_interval = check_interval
        self.initial_delay = initial_delay  # Wait before first check (server startup time)
        self.running = False
        self.watchdog_task: Optional[asyncio.Task] = None
        self.checks_performed = 0
        self.issues_detected = 0
        self.stale_cleaned = 0
    
    async def start(self):
        """Start the watchdog with initial delay for server startup"""
        if self.running:
            return
        
        self.running = True
        self.watchdog_task = asyncio.create_task(self._watch_loop())
        
        logger.info(f"[PORT-WATCHDOG] Started (first check in {self.initial_delay}s, then every {self.check_interval}s)")
        logger.info(f"[PORT-WATCHDOG] Monitoring ports {port_manager.start_port}-{port_manager.end_port}")
    
    async def stop(self):
        """Stop the watchdog"""
        if not self.running:
            return
        
        self.running = False
        if self.watchdog_task:
            self.watchdog_task.cancel()
            try:
                await self.watchdog_task
            except asyncio.CancelledError:
                pass
        
        logger.info("[PORT-WATCHDOG] Stopped")
    
    async def _watch_loop(self):
        """Main watchdog loop with initial delay"""
        # Wait for server to fully start before first check
        logger.info(f"[PORT-WATCHDOG] Waiting {self.initial_delay}s for server startup...")
        await asyncio.sleep(self.initial_delay)
        
        while self.running:
            try:
                await self._perform_health_checks()
                self.checks_performed += 1
                
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[PORT-WATCHDOG] Error in watch loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on ONLY allocated ports (not entire range)"""
        
        # Only check ports that are actually allocated
        if not port_manager.allocations:
            logger.debug("[PORT-WATCHDOG] No allocated ports to check")
            return
        
        health_reports = port_manager.health_check_all()
        
        if not health_reports:
            return
        
        # Count issues
        active = sum(1 for h in health_reports if h['status'] == 'active')
        dead = sum(1 for h in health_reports if h['status'] == 'dead')
        issues = sum(1 for h in health_reports if h['status'] not in ['active', 'dead'])
        
        # Only log if there are actual issues with allocated ports
        if dead > 0:
            logger.warning(f"[PORT-WATCHDOG] Health check: {active} active, {dead} dead")
            self.issues_detected += dead
        elif issues > 0:
            logger.debug(f"[PORT-WATCHDOG] Health check: {active} active, {issues} issues (non-critical)")
        else:
            logger.debug(f"[PORT-WATCHDOG] Health check: {active} active ports, all healthy")
        
        # Log details ONLY for dead ports (not just "not_listening")
        for health in health_reports:
            if health['status'] == 'dead':
                logger.warning(f"[PORT-WATCHDOG] Port {health['port']} ({health['service_name']}): {health['status']}")
                
                # Try to ping the port
                await self._try_ping_port(health['port'])
    
    async def _try_ping_port(self, port: int):
        """Try to ping a port's health endpoint"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                logger.info(f"[PORT-WATCHDOG] Port {port} health endpoint OK")
                
                # Update allocation
                if port in port_manager.allocations:
                    port_manager.allocations[port].health_status = 'active'
            else:
                logger.warning(f"[PORT-WATCHDOG] Port {port} returned {response.status_code}")
                
                # Forward to Guardian
                await self._forward_to_guardian(
                    port=port,
                    failure_type="port_unhealthy",
                    description=f"Port {port} returned status {response.status_code}",
                    severity="warning"
                )
        except Exception as e:
            logger.warning(f"[PORT-WATCHDOG] Port {port} not responding: {e}")
            
            # Forward to Guardian for auto-remediation
            await self._forward_to_guardian(
                port=port,
                failure_type="port_not_responding",
                description=f"Port {port} not responding: {str(e)}",
                severity="error"
            )
    
    async def _forward_to_guardian(
        self,
        port: int,
        failure_type: str,
        description: str,
        severity: str
    ):
        """Forward alert to Guardian for auto-remediation"""
        
        try:
            from backend.core.watchdog_guardian_integration import watchdog_guardian_bridge, WatchdogAlert
            
            # Get service info
            allocation = port_manager.allocations.get(port)
            service_name = allocation.service_name if allocation else "unknown"
            
            # Create structured alert
            alert = WatchdogAlert(
                alert_id=f"watchdog_{port}_{datetime.utcnow().timestamp()}",
                timestamp=datetime.utcnow().isoformat(),
                subsystem="port_watchdog",
                component=f"port_{port}",
                failure_type=failure_type,
                severity=severity,
                description=description,
                last_successful_check=allocation.last_health_check if allocation else None,
                context={
                    'port': port,
                    'service_name': service_name,
                    'pid': allocation.pid if allocation else None
                },
                recommended_action="restart_service",
                priority=8 if severity == "error" else 5
            )
            
            # Submit to Guardian
            await watchdog_guardian_bridge.submit_alert(alert)
            
        except Exception as e:
            logger.debug(f"[PORT-WATCHDOG] Could not forward to Guardian: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get watchdog status"""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'checks_performed': self.checks_performed,
            'issues_detected': self.issues_detected,
            'stale_cleaned': self.stale_cleaned,
            'monitored_ports': len(port_manager.allocations)
        }


# Global instance
port_watchdog = PortWatchdog()
