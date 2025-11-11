#!/usr/bin/env python3
"""
Grace Process Registry - Track and manage all Grace processes across sessions
"""
import json
import psutil
import asyncio
import aiohttp
import signal
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import logging
import platform
import subprocess

@dataclass
class ProcessInfo:
    """Information about a tracked process"""
    pid: int
    name: str
    component: str
    command: List[str]
    cwd: str
    ports: List[int]
    endpoints: List[str]
    started_at: str
    boot_id: str
    environment: str
    process_type: str  # 'uvicorn', 'npm', 'docker', 'python', 'service'
    shutdown_method: str  # 'http', 'signal', 'api', 'docker'
    shutdown_endpoint: Optional[str] = None
    health_endpoint: Optional[str] = None
    temp_dirs: List[str] = None
    log_files: List[str] = None

    def __post_init__(self):
        if self.temp_dirs is None:
            self.temp_dirs = []
        if self.log_files is None:
            self.log_files = []

class GraceProcessRegistry:
    """Centralized registry for all Grace processes"""
    
    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path.home() / ".grace" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.state_dir / "process_registry.json"
        self.lock_file = self.state_dir / "registry.lock"
        
        self.processes: Dict[str, ProcessInfo] = {}
        self.logger = logging.getLogger("grace.process_registry")
        
        # Load existing registry
        self._load_registry()
        
        # Clean up stale entries on startup
        asyncio.create_task(self._cleanup_stale_processes())
    
    def _load_registry(self):
        """Load process registry from disk"""
        if not self.registry_file.exists():
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
            
            for process_id, process_data in data.get('processes', {}).items():
                self.processes[process_id] = ProcessInfo(**process_data)
            
            self.logger.info(f"📋 Loaded {len(self.processes)} processes from registry")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load registry: {e}")
            # Backup corrupted file
            if self.registry_file.exists():
                backup_file = self.registry_file.with_suffix('.json.backup')
                shutil.copy2(self.registry_file, backup_file)
                self.logger.info(f"💾 Backed up corrupted registry to {backup_file}")
    
    def _save_registry(self):
        """Save process registry to disk"""
        try:
            # Use atomic write with temp file
            temp_file = self.registry_file.with_suffix('.json.tmp')
            
            registry_data = {
                'version': '1.0',
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'processes': {
                    pid: asdict(process_info) 
                    for pid, process_info in self.processes.items()
                }
            }
            
            with open(temp_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
            # Atomic move
            temp_file.replace(self.registry_file)
            
            self.logger.debug(f"💾 Saved registry with {len(self.processes)} processes")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save registry: {e}")
    
    async def _cleanup_stale_processes(self):
        """Remove stale processes from registry"""
        stale_processes = []
        
        for process_id, process_info in self.processes.items():
            try:
                # Check if process still exists
                if not psutil.pid_exists(process_info.pid):
                    stale_processes.append(process_id)
                    continue
                
                # Check if it's actually our process
                try:
                    process = psutil.Process(process_info.pid)
                    cmdline = process.cmdline()
                    
                    # Verify command matches (basic check)
                    if not any(cmd_part in ' '.join(cmdline) for cmd_part in process_info.command[:2]):
                        stale_processes.append(process_id)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    stale_processes.append(process_id)
                    
            except Exception as e:
                self.logger.warning(f"⚠️  Error checking process {process_id}: {e}")
                stale_processes.append(process_id)
        
        # Remove stale processes
        for process_id in stale_processes:
            self.logger.info(f"🧹 Removing stale process: {self.processes[process_id].name}")
            del self.processes[process_id]
        
        if stale_processes:
            self._save_registry()
            self.logger.info(f"🧹 Cleaned up {len(stale_processes)} stale processes")
    
    def register_process(
        self,
        pid: int,
        name: str,
        component: str,
        command: List[str],
        cwd: str,
        ports: List[int] = None,
        endpoints: List[str] = None,
        boot_id: str = "unknown",
        environment: str = "dev",
        process_type: str = "python",
        shutdown_method: str = "signal",
        shutdown_endpoint: str = None,
        health_endpoint: str = None,
        temp_dirs: List[str] = None,
        log_files: List[str] = None
    ) -> str:
        """Register a new process"""
        
        process_id = f"{component}_{pid}"
        
        process_info = ProcessInfo(
            pid=pid,
            name=name,
            component=component,
            command=command,
            cwd=cwd,
            ports=ports or [],
            endpoints=endpoints or [],
            started_at=datetime.now(timezone.utc).isoformat(),
            boot_id=boot_id,
            environment=environment,
            process_type=process_type,
            shutdown_method=shutdown_method,
            shutdown_endpoint=shutdown_endpoint,
            health_endpoint=health_endpoint,
            temp_dirs=temp_dirs or [],
            log_files=log_files or []
        )
        
        self.processes[process_id] = process_info
        self._save_registry()
        
        self.logger.info(f"📝 Registered process: {name} (PID: {pid}, Ports: {ports})")
        return process_id
    
    def unregister_process(self, process_id: str):
        """Unregister a process"""
        if process_id in self.processes:
            process_info = self.processes[process_id]
            del self.processes[process_id]
            self._save_registry()
            self.logger.info(f"📝 Unregistered process: {process_info.name}")
    
    async def stop_all_processes(self, force: bool = False, timeout: int = 30) -> Dict[str, Any]:
        """Stop all registered processes"""
        if not self.processes:
            self.logger.info("📋 No processes to stop")
            return {"stopped": [], "failed": [], "not_found": []}
        
        self.logger.info(f"🛑 Stopping {len(self.processes)} registered processes...")
        
        results = {
            "stopped": [],
            "failed": [],
            "not_found": [],
            "force_killed": []
        }
        
        # Group processes by shutdown method for efficient handling
        shutdown_groups = {
            "http": [],
            "signal": [],
            "docker": [],
            "api": []
        }
        
        for process_id, process_info in self.processes.items():
            shutdown_groups[process_info.shutdown_method].append((process_id, process_info))
        
        # 1. HTTP shutdowns first (graceful)
        if shutdown_groups["http"]:
            await self._shutdown_http_processes(shutdown_groups["http"], results, timeout)
        
        # 2. API shutdowns
        if shutdown_groups["api"]:
            await self._shutdown_api_processes(shutdown_groups["api"], results, timeout)
        
        # 3. Docker shutdowns
        if shutdown_groups["docker"]:
            await self._shutdown_docker_processes(shutdown_groups["docker"], results, timeout)
        
        # 4. Signal-based shutdowns
        if shutdown_groups["signal"]:
            await self._shutdown_signal_processes(shutdown_groups["signal"], results, timeout)
        
        # 5. Force kill remaining processes if requested
        if force:
            await self._force_kill_remaining(results, timeout)
        
        # 6. Cleanup resources
        await self._cleanup_resources(results)
        
        # 7. Update registry
        for process_id in results["stopped"] + results["force_killed"]:
            if process_id in self.processes:
                del self.processes[process_id]
        
        self._save_registry()
        
        # 8. Verify ports are free
        await self._verify_ports_free(results)
        
        total_stopped = len(results["stopped"]) + len(results["force_killed"])
        total_failed = len(results["failed"])
        
        self.logger.info(f"🏁 Shutdown complete: {total_stopped} stopped, {total_failed} failed")
        
        return results
    
    async def _shutdown_http_processes(self, processes: List, results: Dict, timeout: int):
        """Shutdown processes via HTTP endpoints"""
        self.logger.info(f"🌐 Shutting down {len(processes)} HTTP processes...")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            for process_id, process_info in processes:
                try:
                    if not process_info.shutdown_endpoint:
                        # Try common shutdown endpoints
                        endpoints = [
                            f"http://localhost:{port}/shutdown" for port in process_info.ports
                        ] + [
                            f"http://localhost:{port}/api/shutdown" for port in process_info.ports
                        ]
                    else:
                        endpoints = [process_info.shutdown_endpoint]
                    
                    shutdown_success = False
                    for endpoint in endpoints:
                        try:
                            async with session.post(endpoint) as response:
                                if response.status in [200, 202]:
                                    self.logger.info(f"✅ HTTP shutdown: {process_info.name}")
                                    results["stopped"].append(process_id)
                                    shutdown_success = True
                                    break
                        except Exception:
                            continue
                    
                    if not shutdown_success:
                        # Fall back to signal
                        await self._signal_process(process_id, process_info, results)
                        
                except Exception as e:
                    self.logger.error(f"❌ HTTP shutdown failed for {process_info.name}: {e}")
                    results["failed"].append(process_id)
    
    async def _shutdown_signal_processes(self, processes: List, results: Dict, timeout: int):
        """Shutdown processes via signals"""
        self.logger.info(f"📡 Shutting down {len(processes)} signal processes...")
        
        for process_id, process_info in processes:
            await self._signal_process(process_id, process_info, results, timeout)
    
    async def _signal_process(self, process_id: str, process_info: ProcessInfo, results: Dict, timeout: int = 10):
        """Send signal to a process"""
        try:
            if not psutil.pid_exists(process_info.pid):
                results["not_found"].append(process_id)
                return
            
            process = psutil.Process(process_info.pid)
            
            # Send SIGTERM (graceful shutdown)
            if platform.system() == "Windows":
                process.terminate()
            else:
                process.send_signal(signal.SIGTERM)
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=timeout)
                self.logger.info(f"✅ Graceful shutdown: {process_info.name}")
                results["stopped"].append(process_id)
            except psutil.TimeoutExpired:
                # Process didn't shut down gracefully
                self.logger.warning(f"⚠️  {process_info.name} didn't shutdown gracefully")
                results["failed"].append(process_id)
                
        except psutil.NoSuchProcess:
            results["not_found"].append(process_id)
        except Exception as e:
            self.logger.error(f"❌ Signal shutdown failed for {process_info.name}: {e}")
            results["failed"].append(process_id)
    
    async def _shutdown_docker_processes(self, processes: List, results: Dict, timeout: int):
        """Shutdown Docker containers"""
        self.logger.info(f"🐳 Shutting down {len(processes)} Docker processes...")
        
        for process_id, process_info in processes:
            try:
                # Extract container name/ID from command
                container_id = None
                if "docker" in process_info.command:
                    # Find container name in command
                    cmd_str = " ".join(process_info.command)
                    if "--name" in cmd_str:
                        idx = process_info.command.index("--name")
                        if idx + 1 < len(process_info.command):
                            container_id = process_info.command[idx + 1]
                
                if container_id:
                    # Use docker stop
                    result = await asyncio.create_subprocess_exec(
                        "docker", "stop", container_id,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await result.communicate()
                    
                    if result.returncode == 0:
                        self.logger.info(f"✅ Docker stop: {process_info.name}")
                        results["stopped"].append(process_id)
                    else:
                        self.logger.error(f"❌ Docker stop failed: {stderr.decode()}")
                        results["failed"].append(process_id)
                else:
                    # Fall back to signal
                    await self._signal_process(process_id, process_info, results)
                    
            except Exception as e:
                self.logger.error(f"❌ Docker shutdown failed for {process_info.name}: {e}")
                results["failed"].append(process_id)
    
    async def _shutdown_api_processes(self, processes: List, results: Dict, timeout: int):
        """Shutdown processes via custom APIs"""
        self.logger.info(f"🔌 Shutting down {len(processes)} API processes...")
        
        # Implement custom API shutdowns here
        # For now, fall back to signal
        for process_id, process_info in processes:
            await self._signal_process(process_id, process_info, results)
    
    async def _force_kill_remaining(self, results: Dict, timeout: int):
        """Force kill any remaining processes"""
        remaining_processes = []
        
        for process_id in results["failed"]:
            if process_id in self.processes:
                remaining_processes.append((process_id, self.processes[process_id]))
        
        if not remaining_processes:
            return
        
        self.logger.warning(f"🔨 Force killing {len(remaining_processes)} stubborn processes...")
        
        for process_id, process_info in remaining_processes:
            try:
                if psutil.pid_exists(process_info.pid):
                    process = psutil.Process(process_info.pid)
                    process.kill()
                    
                    # Wait briefly for kill to take effect
                    try:
                        process.wait(timeout=5)
                        self.logger.info(f"🔨 Force killed: {process_info.name}")
                        results["force_killed"].append(process_id)
                        results["failed"].remove(process_id)
                    except psutil.TimeoutExpired:
                        self.logger.error(f"❌ Could not kill: {process_info.name}")
                        
            except psutil.NoSuchProcess:
                # Process already gone
                results["force_killed"].append(process_id)
                results["failed"].remove(process_id)
            except Exception as e:
                self.logger.error(f"❌ Force kill failed for {process_info.name}: {e}")
    
    async def _cleanup_resources(self, results: Dict):
        """Clean up temp directories and resources"""
        self.logger.info("🧹 Cleaning up resources...")
        
        cleaned_dirs = []
        cleaned_files = []
        
        for process_id in results["stopped"] + results["force_killed"]:
            if process_id not in self.processes:
                continue
                
            process_info = self.processes[process_id]
            
            # Clean temp directories
            for temp_dir in process_info.temp_dirs:
                try:
                    temp_path = Path(temp_dir)
                    if temp_path.exists() and temp_path.is_dir():
                        shutil.rmtree(temp_path)
                        cleaned_dirs.append(temp_dir)
                        self.logger.debug(f"🧹 Cleaned temp dir: {temp_dir}")
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not clean {temp_dir}: {e}")
            
            # Clean log files (optional)
            for log_file in process_info.log_files:
                try:
                    log_path = Path(log_file)
                    if log_path.exists() and log_path.stat().st_size > 100 * 1024 * 1024:  # > 100MB
                        log_path.unlink()
                        cleaned_files.append(log_file)
                        self.logger.debug(f"🧹 Cleaned large log: {log_file}")
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not clean {log_file}: {e}")
        
        if cleaned_dirs or cleaned_files:
            self.logger.info(f"🧹 Cleaned {len(cleaned_dirs)} dirs, {len(cleaned_files)} files")
    
    async def _verify_ports_free(self, results: Dict):
        """Verify that ports are now free"""
        self.logger.info("🔍 Verifying ports are free...")
        
        all_ports = set()
        for process_id in results["stopped"] + results["force_killed"]:
            if process_id in self.processes:
                all_ports.update(self.processes[process_id].ports)
        
        if not all_ports:
            return
        
        # Wait a moment for ports to be released
        await asyncio.sleep(2)
        
        still_in_use = []
        for port in all_ports:
            if self._is_port_in_use(port):
                still_in_use.append(port)
        
        if still_in_use:
            self.logger.warning(f"⚠️  Ports still in use: {still_in_use}")
        else:
            self.logger.info(f"✅ All {len(all_ports)} ports are now free")
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get registry status"""
        running_processes = []
        stopped_processes = []
        
        for process_id, process_info in self.processes.items():
            if psutil.pid_exists(process_info.pid):
                try:
                    process = psutil.Process(process_info.pid)
                    if process.is_running():
                        running_processes.append({
                            "id": process_id,
                            "name": process_info.name,
                            "component": process_info.component,
                            "pid": process_info.pid,
                            "ports": process_info.ports,
                            "uptime": (datetime.now(timezone.utc) - datetime.fromisoformat(process_info.started_at.replace('Z', '+00:00'))).total_seconds(),
                            "cpu_percent": process.cpu_percent(),
                            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 1)
                        })
                    else:
                        stopped_processes.append(process_id)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    stopped_processes.append(process_id)
            else:
                stopped_processes.append(process_id)
        
        return {
            "total_registered": len(self.processes),
            "running": len(running_processes),
            "stopped": len(stopped_processes),
            "processes": running_processes,
            "registry_file": str(self.registry_file),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def print_status(self):
        """Print formatted status"""
        status = self.get_status()
        
        print(f"\n📋 GRACE PROCESS REGISTRY")
        print(f"Registry File: {status['registry_file']}")
        print(f"Total Registered: {status['total_registered']}")
        print(f"Currently Running: {status['running']}")
        print(f"Stopped/Stale: {status['stopped']}")
        
        if status['processes']:
            print(f"\n🔧 RUNNING PROCESSES:")
            for proc in status['processes']:
                uptime_str = f"{proc['uptime']:.0f}s"
                ports_str = f":{','.join(map(str, proc['ports']))}" if proc['ports'] else ""
                print(f"  ✅ {proc['name']:<20} PID {proc['pid']:<6} {uptime_str:<8} CPU {proc['cpu_percent']:.1f}% RAM {proc['memory_mb']}MB{ports_str}")
        
        print()

# Global registry instance
process_registry = GraceProcessRegistry()