"""
Remote Computer Access
Grace can access this computer remotely for learning and development
Fully governed with complete audit trail
"""

import asyncio
import subprocess
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging
import platform

from .governance_framework import governance_framework
from .constitutional_engine import constitutional_engine
from .unified_logger import unified_logger
from .immutable_log import immutable_log

logger = logging.getLogger(__name__)


class RemoteComputerAccess:
    """
    Allows Grace to access this computer remotely
    All actions governed, logged, and traceable
    """
    
    def __init__(self):
        self.computer_name = platform.node()
        self.os_type = platform.system()
        self.access_enabled = False
        self.actions_performed = 0
        
        # Allowed actions
        self.allowed_actions = [
            'read_file',
            'list_directory',
            'run_command',
            'check_disk_space',
            'check_memory',
            'check_processes',
            'get_system_info',
            'create_file',
            'install_package',
            'run_tests'
        ]
    
    async def start(self):
        """Enable remote access"""
        self.access_enabled = True
        logger.info(f"[REMOTE-ACCESS] ✅ Remote access enabled")
        logger.info(f"[REMOTE-ACCESS] Computer: {self.computer_name}")
        logger.info(f"[REMOTE-ACCESS] OS: {self.os_type}")
    
    async def stop(self):
        """Disable remote access"""
        self.access_enabled = False
        logger.info(f"[REMOTE-ACCESS] Remote access disabled")
    
    async def execute_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        purpose: str
    ) -> Dict[str, Any]:
        """
        Execute an action on this computer
        
        Args:
            action: Action to perform
            parameters: Action parameters
            purpose: Why Grace needs to do this
        
        Returns:
            Action result with complete audit trail
        """
        
        if not self.access_enabled:
            return {'error': 'Remote access not enabled'}
        
        if action not in self.allowed_actions:
            return {'error': f'Action not allowed: {action}'}
        
        logger.info(f"[REMOTE-ACCESS] 🖥️ Grace wants to: {action}")
        logger.info(f"[REMOTE-ACCESS] Purpose: {purpose}")
        logger.info(f"[REMOTE-ACCESS] Parameters: {parameters}")
        
        # Governance check
        approval = await governance_framework.check_action(
            actor='grace_remote_access',
            action=action,
            resource=self.computer_name,
            context={'action': action, 'parameters': parameters, 'purpose': purpose},
            confidence=0.8
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[REMOTE-ACCESS] 🚫 Governance blocked")
            await self._log_action(action, parameters, 'blocked', approval.get('reason'))
            return {'error': 'governance_blocked', 'reason': approval.get('reason')}
        
        # Constitutional check
        constitutional_check = await constitutional_engine.verify_action(
            action_type='remote_computer_access',
            context={'action': action, 'computer': self.computer_name, 'purpose': purpose}
        )
        
        if not constitutional_check.get('approved', False):
            logger.warning(f"[REMOTE-ACCESS] ⚖️ Constitutional check failed")
            return {'error': 'constitutional_blocked'}
        
        logger.info(f"[REMOTE-ACCESS] ✅ Governance and constitutional checks passed")
        
        # Execute action
        try:
            result = await self._perform_action(action, parameters)
            
            # Log success
            await self._log_action(action, parameters, 'success', result)
            
            self.actions_performed += 1
            
            logger.info(f"[REMOTE-ACCESS] ✅ Action completed successfully")
            
            return {
                'success': True,
                'action': action,
                'result': result,
                'computer': self.computer_name,
                'timestamp': datetime.utcnow().isoformat(),
                'fully_traceable': True
            }
            
        except Exception as e:
            logger.error(f"[REMOTE-ACCESS] ❌ Error: {e}", exc_info=True)
            await self._log_action(action, parameters, 'failed', str(e))
            return {'error': str(e)}
    
    async def _perform_action(self, action: str, parameters: Dict[str, Any]) -> Any:
        """Perform the actual action"""
        
        if action == 'read_file':
            return await self._read_file(parameters.get('path'))
        
        elif action == 'list_directory':
            return await self._list_directory(parameters.get('path', '.'))
        
        elif action == 'run_command':
            return await self._run_command(parameters.get('command'))
        
        elif action == 'check_disk_space':
            return await self._check_disk_space()
        
        elif action == 'check_memory':
            return await self._check_memory()
        
        elif action == 'check_processes':
            return await self._check_processes()
        
        elif action == 'get_system_info':
            return await self._get_system_info()
        
        elif action == 'create_file':
            return await self._create_file(parameters.get('path'), parameters.get('content'))
        
        elif action == 'install_package':
            return await self._install_package(parameters.get('package'))
        
        elif action == 'run_tests':
            return await self._run_tests(parameters.get('test_path'))
        
        else:
            return {'error': 'Unknown action'}
    
    async def _read_file(self, path: str) -> str:
        """Read a file"""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        return file_path.read_text()
    
    async def _list_directory(self, path: str) -> List[str]:
        """List directory contents"""
        dir_path = Path(path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        return [str(item) for item in dir_path.iterdir()]
    
    async def _run_command(self, command: str) -> str:
        """Run a shell command"""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            'stdout': stdout.decode('utf-8'),
            'stderr': stderr.decode('utf-8'),
            'returncode': proc.returncode
        }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        return {
            'total_gb': total // (2**30),
            'used_gb': used // (2**30),
            'free_gb': free // (2**30),
            'percent_used': (used / total) * 100
        }
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total_gb': mem.total // (2**30),
                'available_gb': mem.available // (2**30),
                'percent_used': mem.percent
            }
        except ImportError:
            return {'error': 'psutil not installed'}
    
    async def _check_processes(self) -> List[Dict[str, Any]]:
        """Check running processes"""
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes[:20]  # Top 20
        except ImportError:
            return [{'error': 'psutil not installed'}]
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'computer_name': self.computer_name,
            'os': self.os_type,
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'machine': platform.machine()
        }
    
    async def _create_file(self, path: str, content: str) -> str:
        """Create a file"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"File created: {path}"
    
    async def _install_package(self, package: str) -> str:
        """Install a Python package"""
        proc = await asyncio.create_subprocess_exec(
            'pip', 'install', package,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            'package': package,
            'stdout': stdout.decode('utf-8'),
            'stderr': stderr.decode('utf-8'),
            'success': proc.returncode == 0
        }
    
    async def _run_tests(self, test_path: str) -> Dict[str, Any]:
        """Run tests"""
        proc = await asyncio.create_subprocess_exec(
            'pytest', test_path, '-v',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            'test_path': test_path,
            'stdout': stdout.decode('utf-8'),
            'stderr': stderr.decode('utf-8'),
            'passed': proc.returncode == 0
        }
    
    async def _log_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        status: str,
        result: Any
    ):
        """Log action to immutable log"""
        
        # Log to immutable log
        await immutable_log.append(
            actor='grace_remote_access',
            action=action,
            resource=self.computer_name,
            subsystem='remote_access',
            payload={
                'action': action,
                'parameters': parameters,
                'computer': self.computer_name,
                'os': self.os_type,
                'status': status
            },
            result=status
        )
        
        # Log to unified logger
        await unified_logger.log_agentic_spine_decision(
            decision_type='remote_access_action',
            decision_context={'action': action, 'computer': self.computer_name},
            chosen_action=action,
            rationale=f"Remote access: {action}",
            actor='grace_remote_access',
            confidence=0.85,
            risk_score=0.15,
            status=status,
            resource=self.computer_name
        )
    
    async def get_status(self) -> Dict[str, Any]:
        """Get remote access status"""
        return {
            'access_enabled': self.access_enabled,
            'computer_name': self.computer_name,
            'os': self.os_type,
            'actions_performed': self.actions_performed,
            'allowed_actions': self.allowed_actions
        }


# Global instance
remote_access = RemoteComputerAccess()
