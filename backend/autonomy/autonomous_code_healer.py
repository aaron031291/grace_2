"""
Autonomous Code Healer
Grace's self-coding capability to fix errors automatically with governance oversight
"""

import os
import re
import ast
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import logging

from .trigger_mesh import trigger_mesh, TriggerEvent
from .code_generator import CodeGenerator
from .code_understanding import code_understanding
from .governance import governance_engine
from .immutable_log import ImmutableLog
from .ml_healing import ml_healing
from .unified_logger import unified_logger
from .grace_training_storage import training_storage

logger = logging.getLogger(__name__)


class AutonomousCodeHealer:
    """
    Detects runtime errors and autonomously generates code fixes
    with governance approval and verification
    """
    
    def __init__(self):
        self.code_generator = CodeGenerator()
        self.immutable_log = ImmutableLog()
        self.fixes_applied = 0
        self.fixes_proposed = 0
        self.running = False
        
        # Pattern matchers for common errors
        self.error_patterns = {
            'missing_await': {
                'pattern': r"object (\w+) can't be used in 'await' expression",
                'fix_type': 'add_async_wrapper',
                'severity': 'high'
            },
            'missing_attribute': {
                'pattern': r"type object '(\w+)' has no attribute '(\w+)'",
                'fix_type': 'add_attribute',
                'severity': 'medium'
            },
            'import_error': {
                'pattern': r"No module named '(\w+)'",
                'fix_type': 'add_import',
                'severity': 'low'
            },
            'type_error': {
                'pattern': r"Object of type (\w+) is not JSON serializable",
                'fix_type': 'add_serializer',
                'severity': 'medium'
            }
        }
    
    async def start(self):
        """Start autonomous code healing listener"""
        if self.running:
            return
        
        self.running = True
        
        # Subscribe to error events (subscribe is not async)
        trigger_mesh.subscribe("error.detected", self._on_error_detected)
        trigger_mesh.subscribe("warning.raised", self._on_warning_detected)
        
        # Start proactive scanning loop
        asyncio.create_task(self._proactive_scan_loop())
        
        logger.info("[CODE_HEAL] Autonomous Code Healer started")
        print("[CODE_HEAL] Self-healing active: monitoring errors + proactive scanning")
    
    async def stop(self):
        """Stop autonomous code healing"""
        self.running = False
        logger.info("[CODE_HEAL] Autonomous Code Healer stopped")
    
    async def _on_error_detected(self, event: TriggerEvent):
        """Handle detected error - analyze and propose fix"""
        try:
            error_data = event.payload
            error_type = error_data.get('error_type', '')
            error_msg = error_data.get('error_message', '')
            stack_trace = error_data.get('stack_trace', '')
            
            # Check if this is a code-level error we can fix
            fix_proposal = await self._analyze_error(error_type, error_msg, stack_trace)
            
            if fix_proposal:
                self.fixes_proposed += 1
                logger.info(f"[CODE_HEAL] 💡 Proposed fix for {error_type}: {fix_proposal['description']}")
                print(f"[CODE_HEAL] 🔧 SELF-REPAIR: {error_type} detected in {fix_proposal['file_path']}:{fix_proposal['line_number']}")
                print(f"[CODE_HEAL] 💡 Fix proposed: {fix_proposal['description']}")
                
                # Log to unified logger
                await unified_logger.log_healing_attempt(
                    attempt_id=fix_proposal['fix_id'],
                    error_type=error_type,
                    error_message=error_msg,
                    detected_by='code_healer',
                    severity=fix_proposal['severity'],
                    error_file=fix_proposal['file_path'],
                    error_line=fix_proposal['line_number'],
                    stack_trace=stack_trace,
                    fix_type=fix_proposal['fix_type'],
                    fix_description=fix_proposal['description'],
                    fix_code=fix_proposal['fix_code'],
                    original_code=fix_proposal['original_code'],
                    confidence=0.8,
                    ml_recommendation=None,  # Will be added if available
                    requires_approval=fix_proposal['requires_approval'],
                    status='proposed'
                )
                
                # Save to training folder
                await training_storage.save_knowledge(
                    category="errors_fixed",
                    item_id=fix_proposal['fix_id'],
                    content={
                        "error_type": error_type,
                        "error_message": error_msg,
                        "file_path": fix_proposal['file_path'],
                        "line_number": fix_proposal['line_number'],
                        "original_code": fix_proposal['original_code'],
                        "fixed_code": fix_proposal['fix_code'],
                        "fix_description": fix_proposal['description'],
                        "confidence": 0.8,
                        "requires_approval": fix_proposal['requires_approval']
                    },
                    source=fix_proposal['file_path'],
                    tags=["self_heal", error_type, fix_proposal['fix_type']]
                )
                
                # Request governance approval
                await self._request_fix_approval(fix_proposal, error_data)
        
        except Exception as e:
            logger.error(f"[CODE_HEAL] Error in healing pipeline: {e}", exc_info=True)
    
    async def _on_warning_detected(self, event: TriggerEvent):
        """Handle warnings - lighter analysis"""
        # For now, log warnings but don't auto-fix
        # Could extend to fix warnings in future
        pass
    
    async def _analyze_error(
        self,
        error_type: str,
        error_msg: str,
        stack_trace: str
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze error and determine if we can fix it
        
        Returns fix proposal or None
        """
        
        # Extract file and line info from stack trace
        file_info = self._extract_file_info(stack_trace)
        if not file_info:
            return None
        
        # Match against known error patterns
        for pattern_name, pattern_config in self.error_patterns.items():
            match = re.search(pattern_config['pattern'], error_msg)
            if match:
                return await self._generate_fix_proposal(
                    pattern_name=pattern_name,
                    pattern_config=pattern_config,
                    match_groups=match.groups(),
                    file_info=file_info,
                    error_type=error_type,
                    error_msg=error_msg
                )
        
        # No known pattern matched
        logger.debug(f"[CODE_HEAL] No fix pattern for: {error_type}")
        return None
    
    def _extract_file_info(self, stack_trace: str) -> Optional[Dict[str, Any]]:
        """Extract file path and line number from stack trace"""
        # Look for pattern: File "path/to/file.py", line 123
        pattern = r'File "([^"]+)", line (\d+)'
        matches = re.findall(pattern, stack_trace)
        
        if not matches:
            return None
        
        # Get the last (most recent) file in trace
        file_path, line_num = matches[-1]
        
        # Only fix files in backend directory
        if 'backend' not in file_path:
            return None
        
        return {
            'file_path': file_path,
            'line_number': int(line_num),
            'stack_trace': stack_trace
        }
    
    async def _generate_fix_proposal(
        self,
        pattern_name: str,
        pattern_config: Dict[str, Any],
        match_groups: tuple,
        file_info: Dict[str, Any],
        error_type: str,
        error_msg: str
    ) -> Dict[str, Any]:
        """Generate concrete fix proposal for the error"""
        
        fix_type = pattern_config['fix_type']
        file_path = file_info['file_path']
        line_num = file_info['line_number']
        
        # Get ML recommendation for best fix strategy
        ml_recommendation = await ml_healing.recommend_fix_strategy(pattern_name)
        if ml_recommendation:
            logger.info(f"[CODE_HEAL] 🧠 ML recommends: {ml_recommendation['strategy']} "
                       f"(success rate: {ml_recommendation['success_rate']:.2%})")
        
        # Read the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                lines = file_content.split('\n')
        except Exception as e:
            logger.error(f"[CODE_HEAL] Cannot read file {file_path}: {e}")
            return None
        
        # Generate fix based on type
        fix_code = None
        description = ""
        
        if fix_type == 'add_async_wrapper':
            # Example: get_grace_llm() needs to not be awaited
            function_name = match_groups[0] if match_groups else 'unknown'
            description = f"Remove 'await' from non-async function {function_name}"
            fix_code = await self._fix_missing_await(lines, line_num, function_name)
        
        elif fix_type == 'add_attribute':
            # Example: VerificationEvent.passed doesn't exist
            class_name, attr_name = match_groups if len(match_groups) >= 2 else ('Unknown', 'unknown')
            description = f"Add missing attribute '{attr_name}' to {class_name}"
            fix_code = await self._fix_missing_attribute(file_path, class_name, attr_name)
        
        elif fix_type == 'add_serializer':
            # Example: datetime object not JSON serializable
            type_name = match_groups[0] if match_groups else 'unknown'
            description = f"Add JSON serializer for {type_name}"
            fix_code = await self._fix_json_serialization(lines, line_num, type_name)
        
        if not fix_code:
            return None
        
        return {
            'fix_id': f"fix_{datetime.utcnow().timestamp()}",
            'pattern_name': pattern_name,
            'fix_type': fix_type,
            'description': description,
            'severity': pattern_config['severity'],
            'file_path': file_path,
            'line_number': line_num,
            'original_code': lines[line_num - 1] if line_num <= len(lines) else "",
            'fix_code': fix_code,
            'error_type': error_type,
            'error_msg': error_msg,
            'requires_approval': pattern_config['severity'] in ['medium', 'high']
        }
    
    async def _fix_missing_await(
        self,
        lines: List[str],
        line_num: int,
        function_name: str
    ) -> Optional[str]:
        """Fix 'await' on non-async function"""
        if line_num > len(lines):
            return None
        
        original_line = lines[line_num - 1]
        
        # Remove 'await' keyword
        fixed_line = re.sub(r'\bawait\s+' + re.escape(function_name), function_name, original_line)
        
        if fixed_line == original_line:
            return None
        
        return fixed_line
    
    async def _fix_missing_attribute(
        self,
        file_path: str,
        class_name: str,
        attr_name: str
    ) -> Optional[str]:
        """Generate code to add missing attribute to class"""
        # This is more complex - need to find the class definition
        # For now, return a suggestion
        return f"# Add to {class_name} class:\n{attr_name} = None  # TODO: Set proper default"
    
    async def _fix_json_serialization(
        self,
        lines: List[str],
        line_num: int,
        type_name: str
    ) -> Optional[str]:
        """Fix JSON serialization issue"""
        if line_num > len(lines):
            return None
        
        original_line = lines[line_num - 1]
        
        # If it's datetime, convert to isoformat
        if type_name == 'datetime':
            # Look for pattern where datetime object is used
            # Add .isoformat() conversion
            suggestion = "# Convert datetime to string: datetime_obj.isoformat()"
            return suggestion
        
        return None
    
    async def _request_fix_approval(
        self,
        fix_proposal: Dict[str, Any],
        error_data: Dict[str, Any]
    ):
        """Request governance approval for fix"""
        
        # Check if auto-approval is allowed
        auto_approve = not fix_proposal['requires_approval']
        
        if auto_approve:
            logger.info(f"[CODE_HEAL] ✅ Auto-approving low-severity fix")
            await self._apply_fix(fix_proposal)
            return
        
        # Request human approval via governance
        approval_request = {
            'action': 'code_fix',
            'fix_id': fix_proposal['fix_id'],
            'description': fix_proposal['description'],
            'severity': fix_proposal['severity'],
            'file_path': fix_proposal['file_path'],
            'line_number': fix_proposal['line_number'],
            'original_code': fix_proposal['original_code'],
            'fix_code': fix_proposal['fix_code'],
            'error_context': {
                'error_type': error_data.get('error_type'),
                'error_message': error_data.get('error_message')
            }
        }
        
        # Publish approval request event
        await trigger_mesh.publish(TriggerEvent(
            event_type="approval.requested",
            source="autonomous_code_healer",
            actor="grace",
            resource=fix_proposal['file_path'],
            payload=approval_request,
            timestamp=datetime.now(timezone.utc)
        ))
        
        logger.info(f"[CODE_HEAL] 🙋 Requesting approval for: {fix_proposal['description']}")
        
        # TODO: Wait for approval and then apply
        # For now, just log the proposal
    
    async def _apply_fix(self, fix_proposal: Dict[str, Any]):
        """Apply the approved fix to the code"""
        try:
            file_path = fix_proposal['file_path']
            line_num = fix_proposal['line_number']
            fix_code = fix_proposal['fix_code']
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply fix
            if line_num <= len(lines):
                lines[line_num - 1] = fix_code + '\n'
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.fixes_applied += 1
                
                logger.info(f"[CODE_HEAL] ✅ Applied fix to {file_path}:{line_num}")
                
                # Auto-commit the fix
                from .auto_commit import auto_commit
                commit_result = await auto_commit.commit_fix(
                    file_path=file_path,
                    fix_description=fix_proposal['description'],
                    actor="grace_autonomous",
                    auto_approve=True  # Auto-approve low severity fixes
                )
                
                # Log to immutable log
                await self.immutable_log.append(
                    actor="grace_autonomous",
                    action="code_fix_applied",
                    resource=file_path,
                    subsystem="autonomous_code_healer",
                    payload={
                        'fix_id': fix_proposal['fix_id'],
                        'line_number': line_num,
                        'description': fix_proposal['description'],
                        'committed': commit_result.get('committed', False)
                    },
                    result="success"
                )
                
                # Publish success event
                await trigger_mesh.publish(TriggerEvent(
                    event_type="code.fixed",
                    source="autonomous_code_healer",
                    actor="grace",
                    resource=file_path,
                    payload={
                        'fix_id': fix_proposal['fix_id'],
                        'description': fix_proposal['description'],
                        'file_path': file_path,
                        'line_number': line_num
                    },
                    timestamp=datetime.now(timezone.utc)
                ))
            
        except Exception as e:
            logger.error(f"[CODE_HEAL] Failed to apply fix: {e}", exc_info=True)
    
    async def _proactive_scan_loop(self):
        """Proactive scanning loop - periodically scan for potential issues"""
        logger.info("[CODE_HEAL] Starting proactive scan loop")
        
        while self.running:
            try:
                # Wait 5 minutes between scans
                await asyncio.sleep(300)
                
                if not self.running:
                    break
                
                logger.debug("[CODE_HEAL] Running proactive code scan...")
                
                # Could scan for common patterns, outdated dependencies, etc.
                # For now, just log that we're scanning
                # Future: integrate with code_understanding for deeper analysis
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CODE_HEAL] Error in proactive scan: {e}")
                await asyncio.sleep(60)  # Back off on error
    
    async def get_status(self) -> Dict[str, Any]:
        """Get healing system status"""
        return {
            'running': self.running,
            'fixes_proposed': self.fixes_proposed,
            'fixes_applied': self.fixes_applied,
            'patterns_supported': len(self.error_patterns)
        }


# Global instance
code_healer = AutonomousCodeHealer()
 
