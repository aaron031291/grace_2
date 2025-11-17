"""
OS Shard Agent
Lightweight daemon that runs on each target OS (Ubuntu, WSL, Windows, Mac)
Reports health, dependencies, and environment status
"""

import sys
import platform
import subprocess
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class ShardAgent:
    """Environment monitoring agent for a specific OS shard"""
    
    def __init__(self, shard_id: str, os_type: str):
        self.shard_id = shard_id
        self.os_type = os_type  # ubuntu, wsl, windows, mac
        self.last_probe: Optional[datetime] = None
        self.health_status = "unknown"
    
    async def health_probe(self) -> Dict[str, Any]:
        """
        Complete health probe of this OS shard
        Returns comprehensive environment telemetry
        """
        probe_data = {
            'shard_id': self.shard_id,
            'os_type': self.os_type,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'checks': {}
        }
        
        # OS Info
        probe_data['checks']['os'] = await self._check_os_info()
        
        # Python Environment
        probe_data['checks']['python'] = await self._check_python_env()
        
        # Node Environment
        probe_data['checks']['node'] = await self._check_node_env()
        
        # Package Managers
        probe_data['checks']['pip'] = await self._check_pip_status()
        probe_data['checks']['npm'] = await self._check_npm_status()
        
        # Virtual Environment
        probe_data['checks']['virtualenv'] = await self._check_virtualenv()
        
        # GPU Drivers (if applicable)
        probe_data['checks']['gpu'] = await self._check_gpu_drivers()
        
        # Disk Space
        probe_data['checks']['disk'] = await self._check_disk_space()
        
        # Determine overall status
        critical_failures = [
            k for k, v in probe_data['checks'].items()
            if v.get('status') == 'critical'
        ]
        
        if critical_failures:
            probe_data['status'] = 'critical'
        elif any(v.get('status') == 'degraded' for v in probe_data['checks'].values()):
            probe_data['status'] = 'degraded'
        else:
            probe_data['status'] = 'healthy'
        
        self.health_status = probe_data['status']
        self.last_probe = datetime.utcnow()
        
        return probe_data
    
    async def _check_os_info(self) -> Dict[str, Any]:
        """Check OS kernel version, architecture"""
        return {
            'status': 'healthy',
            'platform': platform.platform(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'kernel': platform.release(),
        }
    
    async def _check_python_env(self) -> Dict[str, Any]:
        """Check Python version and installation"""
        return {
            'status': 'healthy',
            'version': sys.version.split()[0],
            'executable': sys.executable,
            'implementation': platform.python_implementation(),
        }
    
    async def _check_node_env(self) -> Dict[str, Any]:
        """Check Node.js version"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                
                # Check if version meets requirements (Node 20.x)
                major = int(version.lstrip('v').split('.')[0])
                status = 'healthy' if major >= 18 else 'degraded'
                
                return {
                    'status': status,
                    'version': version,
                    'available': True
                }
            else:
                return {
                    'status': 'critical',
                    'version': None,
                    'available': False,
                    'error': 'node command failed'
                }
        except Exception as e:
            return {
                'status': 'degraded',
                'version': None,
                'available': False,
                'error': str(e)
            }
    
    async def _check_pip_status(self) -> Dict[str, Any]:
        """Check pip and installed packages"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                
                # Check for critical packages
                critical_pkgs = {'fastapi', 'sqlalchemy', 'pydantic', 'uvicorn'}
                installed = {pkg['name'].lower() for pkg in packages}
                missing = critical_pkgs - installed
                
                return {
                    'status': 'critical' if missing else 'healthy',
                    'total_packages': len(packages),
                    'missing_critical': list(missing),
                    'available': True
                }
            else:
                return {
                    'status': 'critical',
                    'error': 'pip list failed',
                    'available': False
                }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'available': False
            }
    
    async def _check_npm_status(self) -> Dict[str, Any]:
        """Check npm and node_modules"""
        try:
            # Check if node_modules exists
            node_modules = Path('frontend/node_modules')
            
            if node_modules.exists():
                # Count packages
                package_count = len(list(node_modules.iterdir()))
                
                return {
                    'status': 'healthy',
                    'node_modules_exists': True,
                    'package_count': package_count
                }
            else:
                return {
                    'status': 'degraded',
                    'node_modules_exists': False,
                    'package_count': 0,
                    'warning': 'Run: npm install'
                }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e)
            }
    
    async def _check_virtualenv(self) -> Dict[str, Any]:
        """Check virtual environment status and checksum"""
        venv_path = Path('.venv') if Path('.venv').exists() else Path('venv')
        
        if not venv_path.exists():
            return {
                'status': 'degraded',
                'exists': False,
                'warning': 'No virtual environment found'
            }
        
        # Calculate checksum of venv
        try:
            # Get list of installed packages for checksum
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'freeze'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                packages = result.stdout
                checksum = hashlib.sha256(packages.encode()).hexdigest()[:16]
                
                return {
                    'status': 'healthy',
                    'exists': True,
                    'path': str(venv_path),
                    'checksum': checksum,
                    'package_count': len(packages.split('\n'))
                }
        except Exception as e:
            pass
        
        return {
            'status': 'healthy',
            'exists': True,
            'path': str(venv_path)
        }
    
    async def _check_gpu_drivers(self) -> Dict[str, Any]:
        """Check GPU availability and drivers"""
        try:
            # Try NVIDIA
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(',')
                return {
                    'status': 'healthy',
                    'available': True,
                    'type': 'nvidia',
                    'gpu_name': gpu_info[0].strip() if len(gpu_info) > 0 else 'unknown',
                    'driver': gpu_info[1].strip() if len(gpu_info) > 1 else 'unknown'
                }
        except:
            pass
        
        # No GPU or drivers not available
        return {
            'status': 'healthy',
            'available': False,
            'note': 'No GPU detected (not required)'
        }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            usage = shutil.disk_usage('.')
            
            free_gb = usage.free / (1024**3)
            total_gb = usage.total / (1024**3)
            percent_used = (usage.used / usage.total) * 100
            
            status = 'healthy'
            if free_gb < 5:
                status = 'critical'
            elif free_gb < 20:
                status = 'degraded'
            
            return {
                'status': status,
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'percent_used': round(percent_used, 2)
            }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e)
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize shard status"""
        return {
            'shard_id': self.shard_id,
            'os_type': self.os_type,
            'health_status': self.health_status,
            'last_probe': self.last_probe.isoformat() if self.last_probe else None
        }


# Create shard agents for common OS targets
SHARD_AGENTS: Dict[str, ShardAgent] = {
    'windows_host': ShardAgent('windows_host', 'windows'),
    'wsl_ubuntu': ShardAgent('wsl_ubuntu', 'wsl'),
    'ubuntu_server': ShardAgent('ubuntu_server', 'ubuntu'),
    'mac_remote': ShardAgent('mac_remote', 'mac'),
}
