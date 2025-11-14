"""
Resilient Startup System
Grace catches startup errors, fixes them, and restarts automatically
"""

import asyncio
import sys
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging

from .autonomous_code_healer import code_healer
from .trigger_mesh import trigger_mesh, TriggerEvent
from .immutable_log import ImmutableLog

logger = logging.getLogger(__name__)


class ResilientStartup:
    """
    Wraps startup sequence with error handling and auto-recovery
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.max_retries = 3
        self.retry_count = 0
        self.startup_errors = []
        self.fixed_errors = []
    
    async def execute_with_recovery(
        self,
        startup_func: Callable,
        component_name: str,
        critical: bool = True
    ) -> bool:
        """
        Execute startup function with automatic recovery
        
        Args:
            startup_func: Async function to execute
            component_name: Name of component for logging
            critical: If True, retry on failure. If False, continue without
        
        Returns:
            True if successful, False if failed
        """
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                logger.info(f"[RESILIENT] Starting {component_name} (attempt {attempt + 1}/{self.max_retries})")
                
                # Execute startup function
                await startup_func()
                
                logger.info(f"[RESILIENT] ✅ {component_name} started successfully")
                return True
            
            except Exception as e:
                attempt += 1
                error_info = {
                    'component': component_name,
                    'attempt': attempt,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'stack_trace': traceback.format_exc(),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.startup_errors.append(error_info)
                
                logger.error(f"[RESILIENT] ❌ {component_name} failed (attempt {attempt}): {e}")
                
                # Publish error event
                asyncio.create_task(trigger_mesh.publish(TriggerEvent(
                    event_type="startup.error",
                    source="resilient_startup",
                    actor="grace_startup",
                    resource=component_name,
                    payload=error_info,
                    timestamp=datetime.utcnow()
                )))
                
                # Try to fix if not last attempt
                if attempt < self.max_retries:
                    logger.info(f"[RESILIENT] 🔧 Attempting auto-fix for {component_name}...")
                    
                    fix_applied = await self._attempt_fix(error_info)
                    
                    if fix_applied:
                        logger.info(f"[RESILIENT] ✅ Auto-fix applied, retrying {component_name}...")
                        self.fixed_errors.append(error_info)
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    else:
                        logger.warning(f"[RESILIENT] ⚠️  No auto-fix available")
                
                # If critical component, fail fast on last attempt
                if critical and attempt >= self.max_retries:
                    logger.critical(f"[RESILIENT] 🚨 Critical component {component_name} failed after {attempt} attempts")
                    return False
                
                # Non-critical: log and continue
                if not critical:
                    logger.warning(f"[RESILIENT] ⏭️  Skipping non-critical component {component_name}")
                    return False
        
        return False
    
    async def _attempt_fix(self, error_info: Dict[str, Any]) -> bool:
        """
        Attempt to auto-fix the error
        
        Returns True if fix was applied
        """
        
        error_type = error_info['error_type']
        error_msg = error_info['error_message']
        stack_trace = error_info['stack_trace']
        
        # Pattern 1: Incorrect await usage
        if "can't be used in 'await' expression" in error_msg:
            logger.info("[RESILIENT] 🔧 Detected incorrect await - attempting fix...")
            return await self._fix_incorrect_await(error_msg, stack_trace)
        
        # Pattern 2: Missing attribute
        if "has no attribute" in error_msg:
            logger.info("[RESILIENT] 🔧 Detected missing attribute - attempting fix...")
            return await self._fix_missing_attribute(error_msg, stack_trace)
        
        # Pattern 3: Import error
        if "No module named" in error_msg or "cannot import" in error_msg:
            logger.info("[RESILIENT] 🔧 Detected import error - logging for manual fix...")
            # Can't auto-fix missing dependencies
            return False
        
        return False
    
    async def _fix_incorrect_await(self, error_msg: str, stack_trace: str) -> bool:
        """Fix incorrect await usage"""
        try:
            # Extract file and line from stack trace
            file_pattern = r'File "([^"]+)", line (\d+)'
            matches = list(re.finditer(file_pattern, stack_trace))
            
            if not matches:
                return False
            
            # Get last file in trace
            file_path, line_num = matches[-1].groups()
            line_num = int(line_num)
            
            # Only fix backend files
            if 'backend' not in file_path:
                return False
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_num > len(lines):
                return False
            
            # Remove await from the line
            original_line = lines[line_num - 1]
            fixed_line = re.sub(r'\bawait\s+', '', original_line, count=1)
            
            if fixed_line == original_line:
                return False
            
            # Apply fix
            lines[line_num - 1] = fixed_line
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logger.info(f"[RESILIENT] ✅ Fixed incorrect await in {file_path}:{line_num}")
            
            # Log to immutable log
            await self.immutable_log.append(
                actor="grace_resilient_startup",
                action="auto_fix_applied",
                resource=file_path,
                subsystem="resilient_startup",
                payload={
                    'fix_type': 'remove_incorrect_await',
                    'line': line_num,
                    'original': original_line.strip(),
                    'fixed': fixed_line.strip()
                },
                result="success"
            )
            
            return True
        
        except Exception as e:
            logger.error(f"[RESILIENT] Error applying fix: {e}")
            return False
    
    async def _fix_missing_attribute(self, error_msg: str, stack_trace: str) -> bool:
        """Fix missing attribute - log suggestion"""
        # This is more complex - would need to modify class definitions
        # For now, just log for manual review
        logger.info("[RESILIENT] Missing attribute detected - requires manual fix")
        return False
    
    async def get_startup_report(self) -> Dict[str, Any]:
        """Get report of startup process"""
        return {
            'retry_count': self.retry_count,
            'errors_encountered': len(self.startup_errors),
            'errors_fixed': len(self.fixed_errors),
            'startup_errors': self.startup_errors,
            'fixed_errors': self.fixed_errors
        }


# Global instance
resilient_startup = ResilientStartup()
