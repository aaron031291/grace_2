#!/usr/bin/env python3
"""
Grace Unified Boot System - Single Entry Point for All Platforms
Handles dev/staging/prod environments with comprehensive validation
"""
import asyncio
import platform
import sys
import os
import json
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class BootStage:
    """Boot stage definition"""
    name: str
    dependencies: List[str]
    handler: callable
    required_config: List[str]
    health_check: Optional[callable] = None
    rollback: Optional[callable] = None
    timeout: int = 60

@dataclass
class SystemInventory:
    """System component inventory"""
    services: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    health_endpoints: Dict[str, str]
    process_registry: Dict[str, int]

class UnifiedBootOrchestrator:
    """Cross-platform Grace boot orchestrator"""
    
    def __init__(self, env: str = "dev", config_path: Optional[str] = None, safe_mode: bool = False):
        self.env = env
        self.safe_mode = safe_mode
        self.grace_root = Path(__file__).parent.parent.absolute()
        self.config_path = Path(config_path) if config_path else self.grace_root / f".env.{env}"
        
        # Platform detection
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == "windows"
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        
        # Boot state
        self.boot_id = f"boot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.process_registry: Dict[str, int] = {}
        self.stage_results: Dict[str, bool] = {}
        self.inventory: Optional[SystemInventory] = None
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup cross-platform logging"""
        log_dir = self.grace_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(log_dir / f"boot_{self.boot_id}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("grace.boot")

    async def boot(self) -> bool:
        """Main boot orchestration"""
        self.logger.info(f"🚀 Grace Unified Boot System - {self.env.upper()} mode")
        self.logger.info(f"📍 Platform: {platform.system()} {platform.release()}")
        self.logger.info(f"📁 Grace Root: {self.grace_root}")
        
        try:
            # Stage 1: Environment Preparation
            if not await self._stage_environment_prep():
                return False
            
            # Stage 2: Deep Inventory
            if not await self._stage_deep_inventory():
                return False
            
            # Stage 3: Dependency Validation
            if not await self._stage_dependency_validation():
                return False
            
            # Stage 4: Directory Scaffolding
            if not await self._stage_directory_scaffolding():
                return False
            
            # Stage 5: Service Boot Pipeline
            if not await self._stage_service_boot():
                return False
            
            # Stage 6: Comprehensive Validation
            if not await self._stage_comprehensive_validation():
                return False
            
            # Stage 7: Post-Boot Diagnostics
            if not await self._stage_post_boot_diagnostics():
                return False
            
            self.logger.info("✅ Grace boot completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Boot failed: {e}")
            await self._emergency_rollback()
            return False

    async def _stage_environment_prep(self) -> bool:
        """Stage 1: Cross-OS Environment Preparation"""
        self.logger.info("🔧 Stage 1: Environment Preparation")
        
        # OS-specific setup
        if self.is_windows:
            await self._setup_windows_environment()
        elif self.is_macos:
            await self._setup_macos_environment()
        elif self.is_linux:
            await self._setup_linux_environment()
        
        # Python environment validation
        if sys.version_info < (3, 9):
            self.logger.error(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.9+ required.")
            return False
        
        # Virtual environment check
        if not self._check_virtual_environment():
            self.logger.error("❌ Virtual environment not detected")
            return False
        
        self.logger.info("✅ Environment preparation complete")
        return True

    async def _setup_windows_environment(self):
        """Windows-specific environment setup"""
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUNBUFFERED'] = '1'
        
        # Set console to UTF-8
        try:
            subprocess.run(['chcp', '65001'], capture_output=True, shell=True)
        except:
            pass

    async def _setup_macos_environment(self):
        """macOS-specific environment setup"""
        # Check for Homebrew dependencies
        homebrew_deps = ['node', 'python3']
        for dep in homebrew_deps:
            if not self._command_exists(dep):
                self.logger.warning(f"⚠️  {dep} not found. Consider: brew install {dep}")

    async def _setup_linux_environment(self):
        """Linux-specific environment setup"""
        # Check for system dependencies
        system_deps = ['python3', 'python3-pip', 'nodejs', 'npm']
        missing_deps = []
        
        for dep in system_deps:
            if not self._command_exists(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            self.logger.warning(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")

    def _command_exists(self, command: str) -> bool:
        """Check if command exists cross-platform"""
        try:
            subprocess.run([command, '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_virtual_environment(self) -> bool:
        """Check if we're in a virtual environment"""
        return (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV') is not None
        )

    async def _stage_deep_inventory(self) -> bool:
        """Stage 2: Deep system inventory"""
        self.logger.info("📋 Stage 2: Deep System Inventory")
        
        services = {}
        dependencies = {}
        health_endpoints = {}
        
        # Inventory backend services
        backend_dir = self.grace_root / "backend"
        if backend_dir.exists():
            services['backend'] = {
                'type': 'fastapi',
                'entry': 'backend.main:app',
                'port': 8000,
                'health': '/health'
            }
            health_endpoints['backend'] = 'http://localhost:8000/health'
        
        # Inventory frontend
        frontend_dir = self.grace_root / "frontend"
        if frontend_dir.exists():
            services['frontend'] = {
                'type': 'vite',
                'entry': 'npm run dev',
                'port': 5173,
                'health': '/'
            }
            health_endpoints['frontend'] = 'http://localhost:5173'
            dependencies['frontend'] = ['backend']
        
        # Inventory domain kernels
        kernels_dir = backend_dir / "domain_kernels"
        if kernels_dir.exists():
            for kernel_file in kernels_dir.glob("*_kernel.py"):
                kernel_name = kernel_file.stem
                services[kernel_name] = {
                    'type': 'kernel',
                    'entry': f'backend.domain_kernels.{kernel_name}',
                    'dependencies': ['backend']
                }
        
        self.inventory = SystemInventory(
            services=services,
            dependencies=dependencies,
            health_endpoints=health_endpoints,
            process_registry={}
        )
        
        self.logger.info(f"✅ Inventoried {len(services)} services")
        return True

    async def _stage_directory_scaffolding(self) -> bool:
        """Stage 4: Create all required directories"""
        self.logger.info("📁 Stage 4: Directory Scaffolding")
        
        required_dirs = [
            "logs",
            "storage",
            "grace_training",
            "frontend/dist",
            "backend/cache",
            "backend/ml_artifacts",
            "backend/databases",
            "backend/exports",
            "backend/imports",
            "backend/temp"
        ]
        
        for dir_path in required_dirs:
            full_path = self.grace_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"📂 Created: {full_path}")
        
        self.logger.info("✅ Directory scaffolding complete")
        return True

    async def _emergency_rollback(self):
        """Emergency rollback on boot failure"""
        self.logger.info("🔄 Emergency rollback initiated")
        
        # Stop all registered processes
        for service_name, pid in self.process_registry.items():
            try:
                process = psutil.Process(pid)
                process.terminate()
                self.logger.info(f"🛑 Stopped {service_name} (PID: {pid})")
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                self.logger.error(f"❌ Failed to stop {service_name}: {e}")

def main():
    """Main entry point for grace boot command"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Grace Unified Boot System")
    parser.add_argument("--env", default="dev", choices=["dev", "staging", "prod"],
                       help="Environment to boot")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--safe-mode", action="store_true",
                       help="Boot in safe mode (minimal services)")
    parser.add_argument("--status", action="store_true",
                       help="Show system status")
    parser.add_argument("--stop", action="store_true",
                       help="Stop all Grace services")
    
    args = parser.parse_args()
    
    if args.status:
        # Show status
        print("🔍 Grace System Status")
        return
    
    if args.stop:
        # Stop services
        print("🛑 Stopping Grace services")
        return
    
    # Boot Grace
    orchestrator = UnifiedBootOrchestrator(
        env=args.env,
        config_path=args.config,
        safe_mode=args.safe_mode
    )
    
    success = asyncio.run(orchestrator.boot())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()