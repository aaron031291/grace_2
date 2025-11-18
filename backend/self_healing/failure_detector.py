"""
Failure Detection System
Monitors for the top 10 failure modes and triggers remediation
"""

import asyncio
import psutil
import shutil
import socket
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class FailureMode(Enum):
    """Top 10 failure modes"""
    DATABASE_CORRUPTION = "database_corruption"
    PORT_IN_USE = "port_in_use"
    SLOW_BOOT = "slow_boot"
    OUT_OF_MEMORY = "out_of_memory"
    DISK_FULL = "disk_full"
    NETWORK_UNREACHABLE = "network_unreachable"
    API_TIMEOUT = "api_timeout"
    MISSING_CONFIG = "missing_config"
    INVALID_CREDENTIALS = "invalid_credentials"
    MODEL_SERVER_DOWN = "model_server_down"

class FailureDetector:
    """Detects common failure modes"""
    
    def __init__(self):
        self.detection_history: List[Tuple[FailureMode, datetime]] = []
        self.memory_threshold_percent = 95
        self.disk_threshold_mb = 100
        self.boot_timeout_seconds = 30
        
    async def detect_all(self) -> List[FailureMode]:
        """Run all failure detectors and return detected failures"""
        failures = []
        
        results = await asyncio.gather(
            self.detect_database_corruption(),
            self.detect_port_in_use(),
            self.detect_out_of_memory(),
            self.detect_disk_full(),
            self.detect_network_unreachable(),
            self.detect_model_server_down(),
            return_exceptions=True
        )
        
        for result in results:
            if isinstance(result, FailureMode):
                failures.append(result)
                self.detection_history.append((result, datetime.now()))
        
        return failures
    
    async def detect_database_corruption(self) -> Optional[FailureMode]:
        """Detect database corruption or unavailability"""
        try:
            import sqlite3
            db_path = Path("databases/grace.db")
            
            if not db_path.exists():
                return None
            
            conn = sqlite3.connect(str(db_path), timeout=5)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] != "ok":
                logger.error(f"Database integrity check failed: {result}")
                return FailureMode.DATABASE_CORRUPTION
                
        except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
            logger.error(f"Database error detected: {e}")
            return FailureMode.DATABASE_CORRUPTION
        except Exception as e:
            logger.warning(f"Database check error: {e}")
            
        return None
    
    async def detect_port_in_use(self, port: int = 8000) -> Optional[FailureMode]:
        """Detect if configured port is already in use"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                logger.warning(f"Port {port} is already in use")
                return FailureMode.PORT_IN_USE
                
        except Exception as e:
            logger.warning(f"Port check error: {e}")
            
        return None
    
    async def detect_out_of_memory(self) -> Optional[FailureMode]:
        """Detect high memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > self.memory_threshold_percent:
                logger.error(f"High memory usage detected: {memory.percent}%")
                return FailureMode.OUT_OF_MEMORY
                
        except Exception as e:
            logger.warning(f"Memory check error: {e}")
            
        return None
    
    async def detect_disk_full(self) -> Optional[FailureMode]:
        """Detect low disk space"""
        try:
            disk = shutil.disk_usage("/")
            free_mb = disk.free / (1024 * 1024)
            
            if free_mb < self.disk_threshold_mb:
                logger.error(f"Low disk space detected: {free_mb:.1f}MB free")
                return FailureMode.DISK_FULL
                
        except Exception as e:
            logger.warning(f"Disk check error: {e}")
            
        return None
    
    async def detect_network_unreachable(self) -> Optional[FailureMode]:
        """Detect network connectivity issues"""
        try:
            import socket
            socket.gethostbyname("google.com")
            
        except socket.gaierror:
            logger.error("Network unreachable: DNS resolution failed")
            return FailureMode.NETWORK_UNREACHABLE
        except Exception as e:
            logger.warning(f"Network check error: {e}")
            
        return None
    
    async def detect_model_server_down(self) -> Optional[FailureMode]:
        """Detect if Ollama model server is down"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code != 200:
                    logger.error("Ollama server returned non-200 status")
                    return FailureMode.MODEL_SERVER_DOWN
                    
        except (httpx.ConnectError, httpx.TimeoutException):
            logger.warning("Ollama server not reachable")
            return FailureMode.MODEL_SERVER_DOWN
        except Exception as e:
            logger.warning(f"Ollama check error: {e}")
            
        return None
    
    def get_detection_history(self, limit: int = 100) -> List[Tuple[FailureMode, datetime]]:
        """Get recent detection history"""
        return self.detection_history[-limit:]
