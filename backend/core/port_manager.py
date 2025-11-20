"""
Port Manager & Watchdog
Manages ports 8000-8500 with full tracking, logging, and metadata
Integrated with network hardening for comprehensive issue detection
"""

import socket
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import psutil

from .network_hardening import network_hardening

logger = logging.getLogger(__name__)


class PortAllocation:
    """Metadata for an allocated port"""
    def __init__(
        self,
        port: int,
        service_name: str,
        started_by: str,
        purpose: str,
        pid: Optional[int] = None
    ):
        self.port = port
        self.service_name = service_name
        self.started_by = started_by
        self.purpose = purpose
        self.pid = pid
        self.allocated_at = datetime.utcnow().isoformat()
        self.last_health_check = datetime.utcnow().isoformat()
        self.health_status = "active"
        self.request_count = 0
        self.error_count = 0


class PortManager:
    """
    Manages port range 8000-8500
    - Allocates ports automatically
    - Tracks who/what/when/why for each port
    - Watchdog monitors health
    - Full audit trail
    - Automatic cleanup
    """
    
    def __init__(self, start_port=8000, end_port=8010):
        """
        Initialize port manager
        
        UPDATED: Only monitor actually used ports (8000-8010)
        - 8000: Grace backend
        - 5173: Frontend (handled separately)
        - 8000-8010: Small buffer for any additional services
        
        Old range (8000-8500) caused watchdog to check hundreds of dead ports
        """
        self.start_port = start_port
        self.end_port = end_port
        self.allocations: Dict[int, PortAllocation] = {}
        
        # Storage
        self.storage_path = Path("databases/port_registry")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Logs
        self.log_path = Path("logs/port_manager")
        self.log_path.mkdir(parents=True, exist_ok=True)
        
        # Clean up stale allocations on init
        self._clean_stale_state()
        
        self._load_allocations()
        
        logger.info(f"[PORT-MANAGER] Initialized: Managing ports {start_port}-{end_port}")
        logger.info(f"[PORT-MANAGER] Active allocations: {len(self.allocations)}")
    
    def allocate_port(
        self,
        service_name: str,
        started_by: str = "system",
        purpose: str = "api_server",
        preferred_port: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Allocate a port from the managed range
        WITH comprehensive network checks and hardening
        
        Args:
            service_name: Name of service (e.g., "grace_backend", "grace_learning")
            started_by: Who/what started this service
            purpose: Why this port is needed
            preferred_port: Try this port first (optional)
        
        Returns:
            Port allocation info with metadata + network health check
        """
        
        # Try preferred port first
        if preferred_port and self._is_port_available(preferred_port):
            port = preferred_port
        else:
            # Find next available port
            port = self._find_next_available_port()
        
        if not port:
            logger.error("[PORT-MANAGER] No available ports in range!")
            return {
                'error': 'no_available_ports',
                'range': f'{self.start_port}-{self.end_port}'
            }
        
        # Run comprehensive network checks
        network_check = network_hardening.check_all_networking_issues(port)
        
        if network_check['status'] == 'critical':
            logger.error(f"[PORT-MANAGER] Critical network issues detected for port {port}")
            logger.error(f"[PORT-MANAGER] Issues: {network_check['critical_issues']}")
            return {
                'error': 'critical_network_issues',
                'port': port,
                'issues': network_check['critical_issues'],
                'details': network_check
            }
        
        if network_check['warnings']:
            logger.warning(f"[PORT-MANAGER] Network warnings for port {port}: {network_check['warnings']}")
        
        # Create allocation
        allocation = PortAllocation(
            port=port,
            service_name=service_name,
            started_by=started_by,
            purpose=purpose,
            pid=None  # Will be set when service starts
        )
        
        self.allocations[port] = allocation
        self._save_allocations()
        self._log_allocation(allocation)
        
        logger.info(f"[PORT-MANAGER] ✅ Allocated port {port} for {service_name}")
        logger.info(f"[PORT-MANAGER] Purpose: {purpose}, Started by: {started_by}")
        logger.info(f"[PORT-MANAGER] Network health: {network_check['status']}")
        
        return {
            'port': port,
            'service_name': service_name,
            'purpose': purpose,
            'started_by': started_by,
            'allocated_at': allocation.allocated_at,
            'network_health': network_check
        }
    
    def register_pid(self, port: int, pid: int):
        """Register process ID for a port"""
        if port in self.allocations:
            self.allocations[port].pid = pid
            self._save_allocations()
            logger.info(f"[PORT-MANAGER] Registered PID {pid} for port {port}")
    
    def release_port(self, port: int) -> bool:
        """Release a port"""
        if port not in self.allocations:
            return False
        
        allocation = self.allocations[port]
        
        logger.info(f"[PORT-MANAGER] Releasing port {port} ({allocation.service_name})")
        
        # Log release
        self._log_release(allocation)
        
        del self.allocations[port]
        self._save_allocations()
        
        return True
    
    def health_check_all(self) -> List[Dict[str, Any]]:
        """
        Watchdog: Check health of all allocated ports
        Detects stale allocations, crashes, port hijacking
        Auto-cleans dead/stale allocations
        """
        
        health_report = []
        stale_ports = []
        
        for port, allocation in list(self.allocations.items()):
            health = self._check_port_health(port, allocation)
            
            # Update allocation
            allocation.last_health_check = datetime.utcnow().isoformat()
            allocation.health_status = health['status']
            
            # Determine if port is stale
            is_stale = False
            
            # Dead process
            if health['status'] == 'dead':
                is_stale = True
            
            # Not listening for extended period (auto-cleanup after 2 minutes)
            elif health['status'] in ['not_listening', 'unreachable']:
                allocated_at = datetime.fromisoformat(allocation.allocated_at)
                age_minutes = (datetime.utcnow() - allocated_at).total_seconds() / 60
                
                if age_minutes > 2:
                    logger.warning(
                        f"[PORT-MANAGER] Port {port} ({allocation.service_name}) "
                        f"not responding for {age_minutes:.1f} min - marking stale"
                    )
                    is_stale = True
            
            # Add to stale list
            if is_stale:
                stale_ports.append(port)
            
            # Only report active or dead (skip noise from not_listening)
            if health['status'] in ['active', 'dead']:
                health_report.append(health)
        
        # Cleanup stale ports
        if stale_ports:
            logger.info(f"[PORT-MANAGER] Cleaning up {len(stale_ports)} stale ports")
            for port in stale_ports:
                self.release_port(port)
        
        self._save_allocations()
        
        return health_report
    
    def _check_port_health(self, port: int, allocation: PortAllocation) -> Dict[str, Any]:
        """Check if a port is still active and healthy"""
        
        health = {
            'port': port,
            'service_name': allocation.service_name,
            'status': 'unknown',
            'responding': False,
            'process_alive': False
        }
        
        # Check if port is listening
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                health['responding'] = True
                health['status'] = 'active'
            else:
                health['status'] = 'not_listening'
        except:
            health['status'] = 'unreachable'
        
        # Check if process is still alive
        if allocation.pid:
            try:
                process = psutil.Process(allocation.pid)
                if process.is_running():
                    health['process_alive'] = True
                    health['process_status'] = process.status()
                else:
                    health['status'] = 'dead'
            except psutil.NoSuchProcess:
                health['status'] = 'dead'
        
        return health
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        if port in self.allocations:
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return True
        except OSError:
            return False
    
    def _find_next_available_port(self) -> Optional[int]:
        """Find next available port in range"""
        for port in range(self.start_port, self.end_port + 1):
            if self._is_port_available(port):
                return port
        return None
    
    def get_all_allocations(self) -> List[Dict[str, Any]]:
        """Get all port allocations"""
        return [
            {
                'port': alloc.port,
                'service_name': alloc.service_name,
                'started_by': alloc.started_by,
                'purpose': alloc.purpose,
                'pid': alloc.pid,
                'allocated_at': alloc.allocated_at,
                'health_status': alloc.health_status,
                'request_count': alloc.request_count,
                'error_count': alloc.error_count
            }
            for alloc in self.allocations.values()
        ]
    
    def get_allocation(self, port: int) -> Optional[Dict[str, Any]]:
        """Get allocation info for specific port"""
        if port not in self.allocations:
            return None
        
        alloc = self.allocations[port]
        return {
            'port': alloc.port,
            'service_name': alloc.service_name,
            'started_by': alloc.started_by,
            'purpose': alloc.purpose,
            'pid': alloc.pid,
            'allocated_at': alloc.allocated_at,
            'last_health_check': alloc.last_health_check,
            'health_status': alloc.health_status
        }
    
    def _save_allocations(self):
        """Save allocations to disk"""
        allocations_data = {
            'allocations': {
                str(port): {
                    'port': alloc.port,
                    'service_name': alloc.service_name,
                    'started_by': alloc.started_by,
                    'purpose': alloc.purpose,
                    'pid': alloc.pid,
                    'allocated_at': alloc.allocated_at,
                    'last_health_check': alloc.last_health_check,
                    'health_status': alloc.health_status,
                    'request_count': alloc.request_count,
                    'error_count': alloc.error_count
                }
                for port, alloc in self.allocations.items()
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
        registry_file = self.storage_path / "port_registry.json"
        registry_file.write_text(json.dumps(allocations_data, indent=2))
    
    def _clean_stale_state(self):
        """Clean up stale allocations file - fresh start each boot"""
        registry_file = self.storage_path / "port_registry.json"
        
        if registry_file.exists():
            try:
                # Backup old state
                backup_file = self.storage_path / f"port_registry_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                import shutil
                shutil.copy(registry_file, backup_file)
                
                # Delete stale state
                registry_file.unlink()
                logger.info(f"[PORT-MANAGER] Cleaned stale port registry (backed up to {backup_file.name})")
            except Exception as e:
                logger.warning(f"[PORT-MANAGER] Could not clean stale state: {e}")
    
    def _load_allocations(self):
        """Load allocations from disk"""
        registry_file = self.storage_path / "port_registry.json"
        if not registry_file.exists():
            logger.info("[PORT-MANAGER] No existing allocations (fresh start)")
            return
        
        try:
            data = json.loads(registry_file.read_text())
            
            loaded_count = 0
            skipped_count = 0
            
            for port_str, alloc_data in data.get('allocations', {}).items():
                port = int(port_str)
                
                # Skip ports outside our range
                if port < self.start_port or port > self.end_port:
                    skipped_count += 1
                    continue
                
                # Recreate allocation
                allocation = PortAllocation(
                    port=alloc_data['port'],
                    service_name=alloc_data['service_name'],
                    started_by=alloc_data['started_by'],
                    purpose=alloc_data['purpose'],
                    pid=alloc_data.get('pid')
                )
                allocation.allocated_at = alloc_data['allocated_at']
                allocation.last_health_check = alloc_data.get('last_health_check', allocation.allocated_at)
                allocation.health_status = alloc_data.get('health_status', 'unknown')
                allocation.request_count = alloc_data.get('request_count', 0)
                allocation.error_count = alloc_data.get('error_count', 0)
                
                self.allocations[port] = allocation
                loaded_count += 1
            
            logger.info(f"[PORT-MANAGER] Loaded {loaded_count} allocations in range (skipped {skipped_count} old ports)")
        except Exception as e:
            logger.error(f"[PORT-MANAGER] Failed to load allocations: {e}")
    
    def _log_allocation(self, allocation: PortAllocation):
        """Log port allocation to audit file"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'allocate',
            'port': allocation.port,
            'service_name': allocation.service_name,
            'started_by': allocation.started_by,
            'purpose': allocation.purpose
        }
        
        log_file = self.log_path / f"allocations_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _log_release(self, allocation: PortAllocation):
        """Log port release to audit file"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'release',
            'port': allocation.port,
            'service_name': allocation.service_name,
            'duration_seconds': self._calculate_duration(allocation.allocated_at),
            'request_count': allocation.request_count,
            'error_count': allocation.error_count
        }
        
        log_file = self.log_path / f"allocations_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _calculate_duration(self, allocated_at: str) -> float:
        """Calculate how long port was allocated"""
        try:
            start = datetime.fromisoformat(allocated_at)
            duration = (datetime.utcnow() - start).total_seconds()
            return duration
        except:
            return 0.0
    
    def cleanup_all_allocations(self):
        """Cleanup all allocations - use for manual reset"""
        count = len(self.allocations)
        self.allocations.clear()
        self._save_allocations()
        logger.info(f"[PORT-MANAGER] Cleaned up {count} allocations (manual reset)")
        return {'cleaned': count}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get port manager statistics"""
        return {
            'port_range': f'{self.start_port}-{self.end_port}',
            'total_ports': self.end_port - self.start_port + 1,
            'allocated_ports': len(self.allocations),
            'available_ports': (self.end_port - self.start_port + 1) - len(self.allocations),
            'allocations': self.get_all_allocations()
        }


# Global instance
port_manager = PortManager()
