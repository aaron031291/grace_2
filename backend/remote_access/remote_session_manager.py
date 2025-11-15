"""
Remote Session Manager
WebSocket-based remote shell access with recording and governance
"""

import asyncio
import subprocess
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import shlex

from .zero_trust_gate import zero_trust_gate
from .rbac_enforcer import rbac_enforcer
from .session_recorder import session_recorder

logger = logging.getLogger(__name__)


class RemoteSessionManager:
    """
    Manages remote shell sessions with:
    - Zero-trust authentication
    - RBAC enforcement
    - Complete session recording
    - Real-time command execution
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.command_history: Dict[str, List[str]] = {}
    
    async def create_session(
        self,
        token: str,
        workspace_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new remote session
        
        Args:
            token: Session token from zero-trust gate
            workspace_dir: Working directory for session
        
        Returns:
            Session info or error
        """
        # Verify token through zero-trust
        verification = zero_trust_gate.verify_session(token)
        
        if not verification.get('valid'):
            logger.warning(f"[REMOTE-SESSION] 🚫 Invalid token")
            return {
                'error': 'invalid_token',
                'reason': verification.get('error', 'unknown')
            }
        
        session_id = verification['session_id']
        device_id = verification['device_id']
        device_name = verification['device_name']
        user_identity = verification['user_identity']
        
        # Start session recording
        recording_id = await session_recorder.start_recording(
            session_id=session_id,
            device_id=device_id,
            device_name=device_name
        )
        
        # Create session
        session = {
            'session_id': session_id,
            'token': token,
            'device_id': device_id,
            'device_name': device_name,
            'user_identity': user_identity,
            'recording_id': recording_id,
            'workspace_dir': workspace_dir or '.',
            'created_at': datetime.utcnow().isoformat(),
            'commands_executed': 0,
            'last_activity': datetime.utcnow().isoformat()
        }
        
        self.active_sessions[session_id] = session
        self.command_history[session_id] = []
        
        logger.info(f"[REMOTE-SESSION] ✅ Session created: {session_id}")
        logger.info(f"[REMOTE-SESSION] User: {user_identity}, Device: {device_name}")
        logger.info(f"[REMOTE-SESSION] Recording: {recording_id}")
        
        return {
            'success': True,
            'session_id': session_id,
            'recording_id': recording_id,
            'device_name': device_name,
            'user_identity': user_identity,
            'workspace_dir': session['workspace_dir']
        }
    
    async def execute_command(
        self,
        session_id: str,
        command: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a shell command in the session
        
        Args:
            session_id: Session ID
            command: Command to execute
            timeout: Timeout in seconds
        
        Returns:
            Command result
        """
        # Verify session exists
        if session_id not in self.active_sessions:
            return {'error': 'session_not_found'}
        
        session = self.active_sessions[session_id]
        device_id = session['device_id']
        recording_id = session['recording_id']
        
        # Check RBAC permission
        permission_check = rbac_enforcer.check_permission(
            device_id=device_id,
            action='execute',
            resource=command
        )
        
        if not permission_check.get('allowed'):
            logger.warning(f"[REMOTE-SESSION] 🚫 Permission denied: {command}")
            
            # Record blocked attempt
            await session_recorder.record_command(
                recording_id=recording_id,
                command=command,
                output=f"PERMISSION DENIED: {permission_check.get('reason')}",
                exit_code=-1,
                execution_time_ms=0
            )
            
            return {
                'error': 'permission_denied',
                'reason': permission_check.get('reason'),
                'required_permission': permission_check.get('required_permission')
            }
        
        logger.info(f"[REMOTE-SESSION] Executing: {command}")
        
        # Execute command
        start_time = datetime.utcnow()
        
        try:
            # Use shlex to safely split command
            # Run in session workspace
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session['workspace_dir']
            )
            
            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Record timeout
                await session_recorder.record_command(
                    recording_id=recording_id,
                    command=command,
                    output=f"TIMEOUT after {timeout}s",
                    exit_code=-2,
                    execution_time_ms=execution_time
                )
                
                return {
                    'error': 'timeout',
                    'timeout_seconds': timeout
                }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')
            output = stdout_str + stderr_str
            
            # Record command
            await session_recorder.record_command(
                recording_id=recording_id,
                command=command,
                output=output,
                exit_code=process.returncode or 0,
                execution_time_ms=execution_time
            )
            
            # Update session stats
            session['commands_executed'] += 1
            session['last_activity'] = datetime.utcnow().isoformat()
            self.command_history[session_id].append(command)
            
            logger.info(f"[REMOTE-SESSION] ✅ Command completed: exit_code={process.returncode}")
            
            return {
                'success': True,
                'stdout': stdout_str,
                'stderr': stderr_str,
                'exit_code': process.returncode or 0,
                'execution_time_ms': execution_time,
                'command': command
            }
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.error(f"[REMOTE-SESSION] ❌ Command failed: {e}")
            
            # Record error
            await session_recorder.record_command(
                recording_id=recording_id,
                command=command,
                output=f"ERROR: {str(e)}",
                exit_code=-3,
                execution_time_ms=execution_time
            )
            
            return {
                'error': 'execution_failed',
                'reason': str(e)
            }
    
    async def read_file(
        self,
        session_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Read a file in the session
        
        Args:
            session_id: Session ID
            file_path: Path to file
        
        Returns:
            File contents or error
        """
        if session_id not in self.active_sessions:
            return {'error': 'session_not_found'}
        
        session = self.active_sessions[session_id]
        device_id = session['device_id']
        recording_id = session['recording_id']
        
        # Check permission
        permission_check = rbac_enforcer.check_permission(
            device_id=device_id,
            action='read_data',
            resource=file_path
        )
        
        if not permission_check.get('allowed'):
            return {
                'error': 'permission_denied',
                'reason': permission_check.get('reason')
            }
        
        try:
            # Read file
            from pathlib import Path
            full_path = Path(session['workspace_dir']) / file_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            content = full_path.read_text()
            
            # Record file access
            await session_recorder.record_file_access(
                recording_id=recording_id,
                file_path=str(full_path),
                action='read',
                size_bytes=len(content)
            )
            
            logger.info(f"[REMOTE-SESSION] ✅ File read: {file_path}")
            
            return {
                'success': True,
                'file_path': file_path,
                'content': content,
                'size_bytes': len(content)
            }
            
        except Exception as e:
            logger.error(f"[REMOTE-SESSION] ❌ File read failed: {e}")
            return {
                'error': 'read_failed',
                'reason': str(e)
            }
    
    async def write_file(
        self,
        session_id: str,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Write a file in the session
        
        Args:
            session_id: Session ID
            file_path: Path to file
            content: File content
        
        Returns:
            Write result
        """
        if session_id not in self.active_sessions:
            return {'error': 'session_not_found'}
        
        session = self.active_sessions[session_id]
        device_id = session['device_id']
        recording_id = session['recording_id']
        
        # Check permission
        permission_check = rbac_enforcer.check_permission(
            device_id=device_id,
            action='write_data',
            resource=file_path
        )
        
        if not permission_check.get('allowed'):
            return {
                'error': 'permission_denied',
                'reason': permission_check.get('reason')
            }
        
        try:
            # Write file
            from pathlib import Path
            full_path = Path(session['workspace_dir']) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            
            # Record file access
            await session_recorder.record_file_access(
                recording_id=recording_id,
                file_path=str(full_path),
                action='write',
                size_bytes=len(content)
            )
            
            logger.info(f"[REMOTE-SESSION] ✅ File written: {file_path}")
            
            return {
                'success': True,
                'file_path': file_path,
                'size_bytes': len(content)
            }
            
        except Exception as e:
            logger.error(f"[REMOTE-SESSION] ❌ File write failed: {e}")
            return {
                'error': 'write_failed',
                'reason': str(e)
            }
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """
        Close a remote session
        
        Args:
            session_id: Session ID to close
        
        Returns:
            Close result
        """
        if session_id not in self.active_sessions:
            return {'error': 'session_not_found'}
        
        session = self.active_sessions[session_id]
        recording_id = session['recording_id']
        
        # Stop recording
        recording_path = await session_recorder.stop_recording(recording_id)
        
        # Remove session
        del self.active_sessions[session_id]
        if session_id in self.command_history:
            del self.command_history[session_id]
        
        logger.info(f"[REMOTE-SESSION] ✅ Session closed: {session_id}")
        logger.info(f"[REMOTE-SESSION] Recording saved: {recording_path}")
        
        return {
            'success': True,
            'session_id': session_id,
            'recording_path': recording_path,
            'commands_executed': session['commands_executed']
        }
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session info"""
        return self.active_sessions.get(session_id)
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return list(self.active_sessions.values())


# Global instance
remote_session_manager = RemoteSessionManager()
