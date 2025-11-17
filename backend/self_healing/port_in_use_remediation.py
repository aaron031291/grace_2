"""
Self-Healing: Port In Use Remediation
Failure Mode #2 - MTTR Target: < 10 seconds
"""

import asyncio
import logging
import socket
import subprocess
import platform
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PortInUseRemediation:
    """
    Detects and remediates "port already in use" failures
    """
    
    def __init__(self):
        self.name = "Port In Use Remediation"
        self.failure_mode = "port_in_use"
        self.mttr_target_seconds = 10
    
    async def detect(self, port: int) -> bool:
        """
        Detect if port is already in use
        
        Returns True if port is in use (failure detected)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            # Result 0 means something is listening
            return result == 0
        
        except Exception as e:
            logger.error(f"[PORT-REMEDIATION] Detection failed: {e}")
            return False
    
    def identify_process_using_port(self, port: int) -> Optional[Dict[str, Any]]:
        """
        Identify which process is using the port
        
        Returns process info or None
        """
        try:
            if platform.system() == "Windows":
                # Windows: netstat -ano | findstr :PORT
                cmd = f'netstat -ano | findstr ":{port}"'
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout:
                    # Parse output to get PID
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        # Last column is PID
                        parts = lines[0].split()
                        pid = int(parts[-1])
                        
                        # Get process name
                        ps_cmd = f'tasklist /FI "PID eq {pid}"'
                        ps_result = subprocess.run(
                            ps_cmd,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        process_name = "unknown"
                        if ps_result.returncode == 0:
                            ps_lines = ps_result.stdout.strip().split('\n')
                            if len(ps_lines) > 2:
                                process_name = ps_lines[2].split()[0]
                        
                        return {
                            "pid": pid,
                            "name": process_name,
                            "port": port
                        }
            
            else:
                # Linux/Mac: lsof -i :PORT
                cmd = f'lsof -i :{port}'
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Parse lsof output
                        parts = lines[1].split()
                        return {
                            "pid": int(parts[1]),
                            "name": parts[0],
                            "port": port
                        }
            
            return None
        
        except Exception as e:
            logger.warning(f"[PORT-REMEDIATION] Failed to identify process: {e}")
            return None
    
    def is_stale_grace_process(self, process_info: Dict[str, Any]) -> bool:
        """
        Check if process is a stale Grace instance
        """
        try:
            from backend.core.port_manager import port_manager
            
            # Check port_manager registry
            allocations = port_manager.get_all_allocations()
            for alloc in allocations:
                if alloc['port'] == process_info['port']:
                    # Check if PID matches
                    if 'pid' in alloc and alloc['pid'] == process_info['pid']:
                        # Check health
                        return alloc.get('health_status') in ['dead', 'unreachable']
            
            # Check process name
            name = process_info.get('name', '').lower()
            return 'python' in name or 'uvicorn' in name or 'grace' in name
        
        except Exception as e:
            logger.debug(f"[PORT-REMEDIATION] Stale check failed: {e}")
            return False
    
    async def remediate(self, port: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        Remediate port-in-use failure
        
        Returns remediation result with MTTR
        """
        from backend.guardian.incident_log import incident_log
        
        # Create incident
        incident = incident_log.create_incident(
            failure_mode=self.failure_mode,
            severity="high",
            metadata={"port": port}
        )
        
        start_time = datetime.utcnow()
        actions_taken = []
        
        try:
            # Step 1: Identify process
            actions_taken.append(f"Identifying process using port {port}")
            process_info = self.identify_process_using_port(port)
            
            if not process_info:
                actions_taken.append("No process found using port")
                incident.mark_resolved(success=True)
                incident_log.update_incident(incident)
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "mttr_seconds": incident.mttr_seconds,
                    "message": f"Port {port} is available"
                }
            
            actions_taken.append(f"Found process: PID {process_info['pid']} ({process_info['name']})")
            
            # Step 2: Check if stale Grace process
            if self.is_stale_grace_process(process_info):
                actions_taken.append("Detected stale Grace process")
                
                if not dry_run:
                    # Kill stale process
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(
                                f'taskkill /F /PID {process_info["pid"]}',
                                shell=True,
                                timeout=5
                            )
                        else:
                            subprocess.run(
                                ['kill', '-9', str(process_info['pid'])],
                                timeout=5
                            )
                        
                        actions_taken.append(f"Killed stale process PID {process_info['pid']}")
                        
                        # Wait for port to be released
                        await asyncio.sleep(1)
                        
                        # Verify port is free
                        if not await self.detect(port):
                            incident.mark_resolved(success=True)
                            incident_log.update_incident(incident)
                            
                            return {
                                "success": True,
                                "actions_taken": actions_taken,
                                "mttr_seconds": incident.mttr_seconds,
                                "message": f"Port {port} freed successfully"
                            }
                    
                    except Exception as e:
                        actions_taken.append(f"Failed to kill process: {e}")
            
            # Step 3: Port still in use - try next port
            next_port = port + 1
            if next_port > 8100:
                next_port = 8000  # Wrap around
            
            actions_taken.append(f"Trying next port: {next_port}")
            
            if not dry_run:
                # Update port manager
                try:
                    from backend.core.port_manager import port_manager
                    port_manager.release_port(port)
                    allocation = port_manager.allocate_port(
                        service_name="grace_backend",
                        started_by="port_remediation",
                        purpose="Recovered from port conflict",
                        preferred_port=next_port
                    )
                    actions_taken.append(f"Allocated new port: {allocation['port']}")
                except Exception as e:
                    actions_taken.append(f"Port manager update failed: {e}")
            
            incident.mark_resolved(success=True)
            incident_log.update_incident(incident)
            
            return {
                "success": True,
                "actions_taken": actions_taken,
                "mttr_seconds": incident.mttr_seconds,
                "new_port": next_port,
                "message": f"Moved to port {next_port}"
            }
        
        except Exception as e:
            error_msg = f"Remediation failed: {str(e)}"
            actions_taken.append(error_msg)
            
            incident.mark_resolved(success=False, error=error_msg)
            incident_log.update_incident(incident)
            
            return {
                "success": False,
                "actions_taken": actions_taken,
                "mttr_seconds": incident.mttr_seconds,
                "error": error_msg
            }


# Global instance
port_remediation = PortInUseRemediation()
