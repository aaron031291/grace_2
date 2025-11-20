"""
Log Watcher Service
Monitors log files and error directories for real-time event detection
Uses Clarity Framework BaseComponent pattern
"""

import asyncio
import os
from typing import Callable, Dict, Any, List
from datetime import datetime
import re

try:
    from backend.clarity import BaseComponent, ComponentStatus, get_event_bus
    HAS_CLARITY = True
except ImportError:
    HAS_CLARITY = False
    BaseComponent = object


class LogWatcher(BaseComponent if HAS_CLARITY else object):
    """
    Watches log files and directories for changes
    Emits events when errors or patterns are detected
    """
    
    def __init__(self):
        if HAS_CLARITY:
            super().__init__()
            self.component_type = "log_watcher"
        
        self.watchers: List[Any] = []
        self.event_handlers: List[Callable] = []
        self.patterns: Dict[str, str] = {
            'error': r'ERROR|Exception|Traceback|Failed',
            'warning': r'WARN|Warning',
            'critical': r'CRITICAL|FATAL|Crash',
            'ingestion_failure': r'ingestion.*failed|Failed to ingest',
            'connection_lost': r'Connection.*lost|timeout|refused',
            'memory_pressure': r'MemoryError|Out of memory|OOM',
            'unicode_console_error': r'UnicodeEncodeError|charmap codec can\'t encode character',
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
        """Emit event to all registered handlers and Clarity event bus"""
        # Emit to local handlers
        for handler in self.event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"[LogWatcher] Handler error: {e}")
        
        # Also emit to Clarity event bus if available
        if HAS_CLARITY:
            try:
                bus = get_event_bus()
                from backend.clarity.event_bus import Event
                await bus.publish(Event(
                    event_type=f"log_pattern.{event['pattern']}",
                    source="log_watcher",
                    payload=event
                ))
            except Exception:
                pass  # Clarity bus not available
    
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


# Consolidated healing trigger - routes to unified trigger mesh
async def trigger_self_healing_on_error(event: Dict[str, Any]):
    """
    Handler that triggers self-healing when critical errors detected.
    Routes through unified trigger mesh for consistency.
    """
    pattern = event.get('pattern')
    
    if pattern in ['error', 'critical', 'ingestion_failure', 'connection_lost']:
        from backend.self_heal.trigger_playbook_integration import trigger_playbook_integration
        
        context = {
            "error_type": f"log_pattern_{pattern}",
            "pattern": pattern,
            "source": event.get('source'),
            "line": event.get('line', '')[:200],
            "triggered_by": "log_watcher"
        }
        
        await trigger_playbook_integration.trigger_healing(
            trigger_type=pattern,
            context=context
        )


async def trigger_error_recognition_on_error(event: Dict[str, Any]):
    """
    Unified handler that routes serious log errors to the ErrorRecognitionSystem/coding agent.
    This is the bridge from raw logs → error recognition → self-healing/coding agent.
    """
    pattern = event.get('pattern')
    line = event.get('line') or ''
    source = event.get('source') or 'unknown'

    # Only escalate serious patterns
    if pattern not in ['error', 'critical', 'ingestion_failure', 'connection_lost', 'unicode_console_error']:
        return

    try:
        # Lazy import to avoid circular dependencies
        from backend.core.error_recognition_system import error_recognition_system

        # Derive a synthetic "kernel" name from the source so signatures group logically
        lower_source = source.lower()
        if 'serve' in lower_source:
            kernel_name = 'backend_boot'
        elif 'startup' in lower_source:
            kernel_name = 'backend_startup'
        else:
            kernel_name = 'log_watcher'

        # Wrap the log line as an exception so diagnostics have a message to work with
        error = RuntimeError(f"[{pattern}] {line}")

        await error_recognition_system.handle_kernel_failure(kernel_name=kernel_name, error=error)
    except Exception as e:
        # Never let the watcher crash on dispatch failures
        print(f"[LogWatcher] ErrorRecognition dispatch failed: {e}")


# Auto-register default handlers so any caller that starts log_watcher
# automatically gets self-healing + error-recognition wiring.
try:
    log_watcher.register_handler(trigger_self_healing_on_error)
    log_watcher.register_handler(trigger_error_recognition_on_error)
except Exception as _e:
    # Safe to ignore; watcher can still be used manually
    pass
