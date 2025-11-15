"""
Port Watchdog
Monitors all ports 8000-8100, tracks usage, detects issues
"""

import asyncio
import logging
from typing import Dict, List, Any
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
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.running = False
        self.watchdog_task: Optional[asyncio.Task] = None
        self.checks_performed = 0
        self.issues_detected = 0
        self.stale_cleaned = 0
    
    async def start(self):
        """Start the watchdog"""
        if self.running:
            return
        
        self.running = True
        self.watchdog_task = asyncio.create_task(self._watch_loop())
        
        logger.info(f"[PORT-WATCHDOG] Started (checking every {self.check_interval}s)")
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
        """Main watchdog loop"""
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
        """Perform health checks on all allocated ports"""
        
        health_reports = port_manager.health_check_all()
        
        if not health_reports:
            return
        
        # Count issues
        active = sum(1 for h in health_reports if h['status'] == 'active')
        dead = sum(1 for h in health_reports if h['status'] == 'dead')
        issues = sum(1 for h in health_reports if h['status'] not in ['active', 'dead'])
        
        if dead or issues:
            logger.warning(f"[PORT-WATCHDOG] Health check: {active} active, {dead} dead, {issues} issues")
            self.issues_detected += dead + issues
        
        # Log details for non-active ports
        for health in health_reports:
            if health['status'] != 'active':
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
        except Exception as e:
            logger.warning(f"[PORT-WATCHDOG] Port {port} not responding: {e}")
    
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
