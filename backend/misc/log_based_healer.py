"""
Log-Based Healing System
Grace reads backend logs, detects error patterns, and fixes them autonomously
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging

from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class LogBasedHealer:
    """
    Periodically scans logs for errors and triggers autonomous healing
    """
    
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or self._find_log_file()
        self.scan_interval = 60  # Scan every 60 seconds
        self.last_position = 0
        self.running = False
        self.scanner_task = None
        self.immutable_log = ImmutableLog()
        
        # Error patterns to detect
        self.error_detectors = [
            {
                'pattern': r"TypeError: object (\w+) can't be used in 'await' expression",
                'name': 'incorrect_await',
                'severity': 'high',
                'auto_fix': True
            },
            {
                'pattern': r"AttributeError: (?:type object )?'?(\w+)'? (?:object )?has no attribute '(\w+)'",
                'name': 'missing_attribute',
                'severity': 'medium',
                'auto_fix': True
            },
            {
                'pattern': r"TypeError: Object of type (\w+) is not JSON serializable",
                'name': 'json_serialization',
                'severity': 'medium',
                'auto_fix': True
            },
            {
                'pattern': r"ModuleNotFoundError: No module named '(\w+)'",
                'name': 'missing_module',
                'severity': 'low',
                'auto_fix': False  # Can't auto-install packages
            },
            {
                'pattern': r"File \"([^\"]+)\", line (\d+)",
                'name': 'error_location',
                'severity': 'info',
                'auto_fix': False  # Just for context
            }
        ]
    
    def _find_log_file(self) -> str:
        """Find backend log file"""
        possible_paths = [
            Path(__file__).parent.parent / "logs" / "backend.log",
            Path(__file__).parent.parent / "backend.log",
            Path(__file__).parent / "backend.log"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        # Default path
        return str(Path(__file__).parent.parent / "logs" / "backend.log")
    
    async def start(self):
        """Start log scanning"""
        if self.running:
            return
        
        self.running = True
        self.scanner_task = asyncio.create_task(self._scan_logs_loop())
        logger.info(f"[LOG_HEAL] 📖 Log-based healer started (scanning {self.log_path})")
    
    async def stop(self):
        """Stop log scanning"""
        self.running = False
        if self.scanner_task:
            self.scanner_task.cancel()
        logger.info("[LOG_HEAL] Log-based healer stopped")
    
    async def _scan_logs_loop(self):
        """Continuous log scanning loop"""
        while self.running:
            try:
                await self._scan_logs()
                await asyncio.sleep(self.scan_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[LOG_HEAL] Error in scan loop: {e}", exc_info=True)
                await asyncio.sleep(self.scan_interval)
    
    async def _scan_logs(self):
        """Scan log file for new errors"""
        try:
            log_file = Path(self.log_path)
            if not log_file.exists():
                return
            
            # Read from last position
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.last_position)
                new_content = f.read()
                self.last_position = f.tell()
            
            if not new_content:
                return
            
            # Detect errors in new content
            errors_found = await self._detect_errors(new_content)
            
            if errors_found:
                logger.info(f"[LOG_HEAL] Detected {len(errors_found)} error pattern(s) in logs")
                
                for error_info in errors_found:
                    await self._handle_detected_error(error_info, new_content)
        
        except Exception as e:
            logger.error(f"[LOG_HEAL] Error scanning logs: {e}")
    
    async def _detect_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect error patterns in log content"""
        detected = []
        
        for detector in self.error_detectors:
            matches = re.finditer(detector['pattern'], content, re.MULTILINE)
            
            for match in matches:
                error_info = {
                    'pattern_name': detector['name'],
                    'severity': detector['severity'],
                    'auto_fix': detector['auto_fix'],
                    'match_groups': match.groups(),
                    'matched_text': match.group(0),
                    'position': match.start()
                }
                detected.append(error_info)
        
        return detected
    
    async def _handle_detected_error(self, error_info: Dict[str, Any], log_context: str):
        """Handle detected error - trigger healing if appropriate"""
        
        # Extract file location from surrounding context
        file_info = self._extract_file_location(log_context, error_info['position'])
        
        if not file_info:
            logger.debug(f"[LOG_HEAL] No file location for {error_info['pattern_name']}")
            return
        
        # Build error event
        error_event = {
            'error_type': error_info['pattern_name'],
            'error_message': error_info['matched_text'],
            'severity': error_info['severity'],
            'file_path': file_info.get('file_path'),
            'line_number': file_info.get('line_number'),
            'stack_trace': log_context[max(0, error_info['position']-500):error_info['position']+500],
            'detected_from': 'log_scan',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Publish error event to trigger mesh for code_healer to handle
        await trigger_mesh.publish(TriggerEvent(
            event_type="error.detected",
            source="log_based_healer",
            actor="grace_log_scanner",
            resource=file_info.get('file_path', 'unknown'),
            payload=error_event,
            timestamp=datetime.utcnow()
        ))
        
        logger.info(f"[LOG_HEAL] 🚨 Published error event: {error_info['pattern_name']} in {file_info.get('file_path')}")
        
        # Log to immutable log
        await self.immutable_log.append(
            actor="grace_log_scanner",
            action="error_detected_from_logs",
            resource=file_info.get('file_path', 'unknown'),
            subsystem="log_based_healer",
            payload=error_event,
            result="detected"
        )
    
    def _extract_file_location(self, log_content: str, error_position: int) -> Optional[Dict[str, str]]:
        """Extract file path and line number from log context around error"""
        
        # Look backwards from error position for File "..." line
        context_before = log_content[max(0, error_position-2000):error_position]
        
        # Find all file references
        file_pattern = r'File "([^"]+)", line (\d+)'
        matches = list(re.finditer(file_pattern, context_before))
        
        if not matches:
            return None
        
        # Get the last (most recent) file reference
        last_match = matches[-1]
        file_path = last_match.group(1)
        line_number = int(last_match.group(2))
        
        # Only process backend files
        if 'backend' not in file_path:
            return None
        
        return {
            'file_path': file_path,
            'line_number': line_number
        }


# Global instance
log_based_healer = LogBasedHealer()
