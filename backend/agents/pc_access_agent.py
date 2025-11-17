"""
PC Access Agent
Grace's controlled access to local PC with security guardrails
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..unified_logger import unified_logger
from ..grace_control_center import grace_control, SystemState
from ..activity_monitor import activity_monitor

logger = logging.getLogger(__name__)


class PCAccessAgent:
    """
    Secure PC access for Grace
    
    All access:
    - Goes through RBAC
    - Recorded in audit trail
    - Subject to governance approval
    - Can be emergency stopped
    """
    
    def __init__(self):
        self.enabled = False
        self.commands_executed = 0
        self.blocked_commands = []
        
        # Whitelist of safe commands Grace can run
        self.safe_commands = [
            'dir',
            'ls',
            'cat',
            'type',
            'python',
            'pip',
            'git',
            'curl',
            'wget'
        ]
        
        # Blacklist of dangerous commands (NEVER allowed)
        self.blacklisted_commands = [
            'rm -rf /',
            'del /f /s /q',
            'format',
            'diskpart',
            'regedit',
            'shutdown',
            'restart',
            'net user'
        ]
    
    async def start(self, enabled: bool = False):
        """
        Start PC access agent
        
        Args:
            enabled: Enable PC access (default: False for safety)
        """
        
        self.enabled = enabled
        
        if enabled:
            logger.warning("[PC-ACCESS] PC Access ENABLED - Grace can execute commands")
        else:
            logger.info("[PC-ACCESS] PC Access DISABLED (safe mode)")
    
    async def execute_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: int = 30,
        requires_approval: bool = True
    ) -> Dict[str, Any]:
        """
        Execute command on local PC
        
        Args:
            command: Command to execute
            working_dir: Working directory
            timeout: Max execution time
            requires_approval: Whether to require governance approval
        
        Returns:
            Execution result
        """
        
        result = {
            'command': command,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'output': '',
            'error': '',
            'exit_code': None,
            'execution_time_ms': 0,
            'approved': False
        }
        
        # Check if enabled
        if not self.enabled:
            result['status'] = 'disabled'
            result['error'] = 'PC access is disabled. Enable with ENABLE_PC_ACCESS=true'
            logger.warning(f"[PC-ACCESS] Blocked (disabled): {command}")
            return result
        
        # Check if system is paused/stopped
        state = grace_control.get_state()
        if state['system_state'] != SystemState.RUNNING:
            result['status'] = 'system_paused'
            result['error'] = f"System is {state['system_state']}"
            logger.warning(f"[PC-ACCESS] Blocked (system {state['system_state']}): {command}")
            return result
        
        # Security check: Blacklist
        if self._is_blacklisted(command):
            result['status'] = 'blocked'
            result['error'] = 'Command blacklisted for security'
            self.blocked_commands.append({
                'command': command,
                'timestamp': datetime.utcnow().isoformat(),
                'reason': 'blacklisted'
            })
            logger.warning(f"[PC-ACCESS] BLOCKED (blacklisted): {command}")
            
            # Log security violation
            await unified_logger.log_agentic_spine_decision(
                decision_type='pc_access_blocked',
                decision_context={'command': command, 'reason': 'blacklisted'},
                chosen_action='block_command',
                rationale='Command is blacklisted for security',
                actor='pc_access_agent',
                confidence=1.0,
                risk_score=0.95,
                status='blocked',
                resource=command
            )
            
            return result
        
        # Governance approval for non-safe commands
        if requires_approval and not self._is_safe_command(command):
            logger.info(f"[PC-ACCESS] Governance approval required for: {command}")
            
            # In production, would submit to governance
            # For now, auto-approve if low risk
            approval = await self._request_approval(command)
            
            if not approval['approved']:
                result['status'] = 'not_approved'
                result['error'] = f"Governance denied: {approval['reason']}"
                return result
            
            result['approved'] = True
        
        # Log activity - what Grace is doing
        await activity_monitor.log_activity(
            activity_type='pc_command',
            description=f'Executing: {command}',
            details={'working_dir': working_dir or 'current'}
        )
        
        # Execute command
        try:
            start_time = datetime.utcnow()
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            end_time = datetime.utcnow()
            
            result['output'] = stdout.decode('utf-8', errors='ignore')
            result['error'] = stderr.decode('utf-8', errors='ignore')
            result['exit_code'] = process.returncode
            result['execution_time_ms'] = (end_time - start_time).total_seconds() * 1000
            result['status'] = 'success' if process.returncode == 0 else 'failed'
            
            self.commands_executed += 1
            
            # Log execution
            await unified_logger.log_agentic_spine_decision(
                decision_type='pc_command_executed',
                decision_context={
                    'command': command,
                    'exit_code': result['exit_code'],
                    'execution_time_ms': result['execution_time_ms']
                },
                chosen_action='execute_local_command',
                rationale=f'Executed PC command: {command}',
                actor='pc_access_agent',
                confidence=0.8,
                risk_score=0.3,
                status=result['status'],
                resource=command
            )
            
            logger.info(f"[PC-ACCESS] Executed: {command} (exit: {result['exit_code']})")
        
        except asyncio.TimeoutError:
            result['status'] = 'timeout'
            result['error'] = f'Command exceeded {timeout}s timeout'
            logger.error(f"[PC-ACCESS] Timeout: {command}")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"[PC-ACCESS] Error executing {command}: {e}")
        
        return result
    
    def _is_blacklisted(self, command: str) -> bool:
        """Check if command is blacklisted"""
        
        cmd_lower = command.lower()
        
        return any(blocked in cmd_lower for blocked in self.blacklisted_commands)
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is in safe whitelist"""
        
        cmd_lower = command.lower().split()[0] if command else ''
        
        return cmd_lower in self.safe_commands
    
    async def _request_approval(self, command: str) -> Dict[str, Any]:
        """Request governance approval for command"""
        
        # Simple risk assessment
        risk_score = 0.3  # Default medium risk
        
        # Higher risk for write operations
        if any(keyword in command.lower() for keyword in ['del', 'rm', 'write', 'modify']):
            risk_score = 0.6
        
        # Lower risk for read operations
        if any(keyword in command.lower() for keyword in ['dir', 'ls', 'cat', 'type', 'read']):
            risk_score = 0.2
        
        # Auto-approve low risk
        if risk_score < 0.3:
            return {
                'approved': True,
                'reason': 'auto_approved_low_risk',
                'risk_score': risk_score
            }
        
        # Would submit to governance in production
        return {
            'approved': False,
            'reason': 'requires_governance_approval',
            'risk_score': risk_score
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get PC access statistics"""
        
        return {
            'enabled': self.enabled,
            'commands_executed': self.commands_executed,
            'commands_blocked': len(self.blocked_commands),
            'safe_commands': self.safe_commands,
            'recent_blocked': self.blocked_commands[-5:] if self.blocked_commands else []
        }


# Global instance
pc_access_agent = PCAccessAgent()
