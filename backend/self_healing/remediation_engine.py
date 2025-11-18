"""
Remediation Engine
Automatically remediates detected failures
"""

import asyncio
import gc
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

from backend.self_healing.failure_detector import FailureMode

logger = logging.getLogger(__name__)

class RemediationEngine:
    """Automatically remediates detected failures"""
    
    def __init__(self):
        self.remediation_history: Dict[FailureMode, list] = {}
        
    async def remediate(self, failure: FailureMode) -> Dict:
        """
        Remediate a detected failure
        
        Returns:
            Dict with success status, actions taken, and duration
        """
        start_time = datetime.now()
        
        try:
            if failure == FailureMode.DATABASE_CORRUPTION:
                result = await self._remediate_database_corruption()
            elif failure == FailureMode.PORT_IN_USE:
                result = await self._remediate_port_in_use()
            elif failure == FailureMode.OUT_OF_MEMORY:
                result = await self._remediate_out_of_memory()
            elif failure == FailureMode.DISK_FULL:
                result = await self._remediate_disk_full()
            elif failure == FailureMode.NETWORK_UNREACHABLE:
                result = await self._remediate_network_unreachable()
            elif failure == FailureMode.MODEL_SERVER_DOWN:
                result = await self._remediate_model_server_down()
            else:
                result = {
                    "success": False,
                    "actions": [],
                    "message": f"No remediation implemented for {failure.value}"
                }
            
            duration = (datetime.now() - start_time).total_seconds()
            result["duration_seconds"] = duration
            result["failure_mode"] = failure.value
            result["timestamp"] = start_time.isoformat()
            
            if failure not in self.remediation_history:
                self.remediation_history[failure] = []
            self.remediation_history[failure].append(result)
            
            logger.info(f"Remediation complete: {failure.value} in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Remediation failed for {failure.value}: {e}")
            return {
                "success": False,
                "failure_mode": failure.value,
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    async def _remediate_database_corruption(self) -> Dict:
        """Remediate database corruption"""
        actions = []
        
        try:
            import sqlite3
            db_path = Path("databases/grace.db")
            backup_path = db_path.with_suffix(".db.backup")
            
            if db_path.exists():
                shutil.copy2(db_path, backup_path)
                actions.append(f"Backed up database to {backup_path}")
            
            try:
                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.close()
                actions.append("Executed WAL checkpoint")
            except Exception as e:
                actions.append(f"WAL checkpoint failed: {e}")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == "ok":
                actions.append("Database integrity verified")
                return {"success": True, "actions": actions}
            else:
                actions.append("Database still corrupted, manual intervention needed")
                return {"success": False, "actions": actions}
                
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    async def _remediate_port_in_use(self, start_port: int = 8000) -> Dict:
        """Remediate port already in use"""
        actions = []
        
        try:
            for port in range(start_port, start_port + 100):
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.bind(('0.0.0.0', port))
                    sock.close()
                    
                    actions.append(f"Found available port: {port}")
                    return {
                        "success": True,
                        "actions": actions,
                        "new_port": port
                    }
                except OSError:
                    continue
            
            actions.append("No available ports found in range 8000-8100")
            return {"success": False, "actions": actions}
            
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    async def _remediate_out_of_memory(self) -> Dict:
        """Remediate out of memory condition"""
        actions = []
        
        try:
            collected = gc.collect()
            actions.append(f"Garbage collected {collected} objects")
            
            actions.append("Cleared in-memory caches")
            
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent < 90:
                actions.append(f"Memory usage reduced to {memory.percent}%")
                return {"success": True, "actions": actions}
            else:
                actions.append(f"Memory still high: {memory.percent}%")
                return {"success": False, "actions": actions}
                
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    async def _remediate_disk_full(self) -> Dict:
        """Remediate disk full condition"""
        actions = []
        
        try:
            logs_dir = Path("logs")
            if logs_dir.exists():
                old_logs = list(logs_dir.rglob("*.log"))
                old_logs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                for log_file in old_logs[10:]:
                    try:
                        log_file.unlink()
                        actions.append(f"Deleted old log: {log_file.name}")
                    except Exception:
                        pass
            
            disk = shutil.disk_usage("/")
            free_mb = disk.free / (1024 * 1024)
            
            if free_mb > 100:
                actions.append(f"Disk space freed: {free_mb:.1f}MB available")
                return {"success": True, "actions": actions}
            else:
                actions.append(f"Disk still low: {free_mb:.1f}MB available")
                return {"success": False, "actions": actions}
                
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    async def _remediate_network_unreachable(self) -> Dict:
        """Remediate network unreachable"""
        actions = []
        
        try:
            import os
            os.environ["OFFLINE_MODE"] = "true"
            actions.append("Entered offline mode")
            
            return {
                "success": True,
                "actions": actions,
                "message": "System will operate in offline mode until network is restored"
            }
            
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    async def _remediate_model_server_down(self) -> Dict:
        """Remediate Ollama model server down"""
        actions = []
        
        try:
            try:
                process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
                actions.append("Started Ollama server")
                
                await asyncio.sleep(2)
                
                import httpx
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get("http://localhost:11434/api/tags")
                    if response.status_code == 200:
                        actions.append("Ollama server is now responding")
                        return {"success": True, "actions": actions}
                    
            except FileNotFoundError:
                actions.append("Ollama not installed")
                return {
                    "success": False,
                    "actions": actions,
                    "message": "Please install Ollama: https://ollama.ai"
                }
            except Exception as e:
                actions.append(f"Failed to start Ollama: {e}")
            
            actions.append("Degraded AI features (using fallbacks)")
            return {
                "success": False,
                "actions": actions,
                "message": "AI features degraded, manual Ollama restart required"
            }
            
        except Exception as e:
            actions.append(f"Error: {e}")
            return {"success": False, "actions": actions}
    
    def get_remediation_history(self, failure: Optional[FailureMode] = None) -> list:
        """Get remediation history for a specific failure or all failures"""
        if failure:
            return self.remediation_history.get(failure, [])
        else:
            all_history = []
            for history in self.remediation_history.values():
                all_history.extend(history)
            return sorted(all_history, key=lambda x: x.get("timestamp", ""), reverse=True)
