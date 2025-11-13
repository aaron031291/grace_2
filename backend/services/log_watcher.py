"""
Log Watcher Service
Monitors log files and error directories for real-time event detection
Uses Watchdog to tail logs and trigger self-healing
"""

import asyncio
import os
from pathlib import Path
from typing import Callable, Dict, Any, List
from datetime import datetime
import re


class LogWatcher:
    """
    Watches log files and directories for changes
    Emits events when errors or patterns are detected
    """
    
    def __init__(self):
        self.watchers: List[Any] = []
        self.event_handlers: List[Callable] = []
        self.patterns: Dict[str, str] = {
            'error': r'ERROR|Exception|Traceback|Failed',
            'warning': r'WARN|Warning',
            'critical': r'CRITICAL|FATAL|Crash',
            'ingestion_failure': r'ingestion.*failed|Failed to ingest',
            'connection_lost': r'Connection.*lost|timeout|refused',
            'memory_pressure': r'MemoryError|Out of memory|OOM',
        }
        self.running = False
    
    async def start(self, watch_paths: List[str] = None):
        """Start watching log files"""
        if watch_paths is None:
            watch_paths = [
                'logs/',
                'grace_training/internal/errors/',
                'backend_startup.log',
                'serve.log',
            ]
        
        self.running = True
        print(f"[LogWatcher] Started watching {len(watch_paths)} paths")
        
        # In production, use actual Watchdog here
        # For now, we'll simulate with periodic checks
        asyncio.create_task(self._poll_logs(watch_paths))
    
    async def _poll_logs(self, paths: List[str]):
        """Poll log files for changes (simplified for now)"""
        while self.running:
            try:
                for path in paths:
                    if os.path.exists(path):
                        await self._check_file(path)
            except Exception as e:
                print(f"[LogWatcher] Error polling: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def _check_file(self, file_path: str):
        """Check a file for error patterns"""
        try:
            if os.path.isfile(file_path):
                # Read last 50 lines
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-50:]
                    
                for line in lines:
                    await self._analyze_line(line, file_path)
        except Exception as e:
            pass  # Silently ignore file read errors
    
    async def _analyze_line(self, line: str, source: str):
        """Analyze a log line for patterns"""
        for pattern_name, pattern in self.patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                event = {
                    'type': 'log_pattern_detected',
                    'pattern': pattern_name,
                    'source': source,
                    'line': line.strip(),
                    'timestamp': datetime.now().isoformat(),
                }
                
                # Emit event to handlers
                await self._emit_event(event)
    
    async def _emit_event(self, event: Dict[str, Any]):
        """Emit event to all registered handlers"""
        for handler in self.event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"[LogWatcher] Handler error: {e}")
    
    def register_handler(self, handler: Callable):
        """Register an event handler"""
        self.event_handlers.append(handler)
        print(f"[LogWatcher] Registered handler: {handler.__name__}")
    
    async def stop(self):
        """Stop watching"""
        self.running = False
        print("[LogWatcher] Stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get watcher status"""
        return {
            'running': self.running,
            'handlers_registered': len(self.event_handlers),
            'patterns_monitored': len(self.patterns),
        }


# Global instance
log_watcher = LogWatcher()


# Example self-healing integration
async def trigger_self_healing_on_error(event: Dict[str, Any]):
    """
    Handler that triggers self-healing when critical errors detected
    """
    pattern = event.get('pattern')
    
    if pattern in ['error', 'critical', 'ingestion_failure', 'connection_lost']:
        print(f"[Self-Healing] Triggered by log pattern: {pattern}")
        print(f"[Self-Healing] Source: {event.get('source')}")
        print(f"[Self-Healing] Line: {event.get('line')[:100]}")
        
        # TODO: Integrate with actual self-healing kernel
        # from backend.self_healing import trigger_playbook
        # await trigger_playbook(get_playbook_for_pattern(pattern))
