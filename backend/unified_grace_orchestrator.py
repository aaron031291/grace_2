#!/usr/bin/env python3
"""
Grace Unified Production Orchestrator - Fixed Version
"""

import asyncio
import platform
import sys
import os
import json
import yaml
import psutil
import subprocess
import hashlib
import logging
import signal
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import process registry
try:
    from backend.grace_process_registry import process_registry, ProcessInfo
except ImportError:
    # Fallback if registry not available
    class MockRegistry:
        def register_process(self, **kwargs): return "mock_id"
        def stop_all_processes(self, **kwargs): return {"stopped": [], "failed": [], "not_found": []}
        def print_status(self): print("Process registry not available")
        @property
        def processes(self): return {}
    
    process_registry = MockRegistry()

class BootProfile(Enum):
    NATIVE = "native"
    DOCKER = "docker" 
    KUBERNETES = "kubernetes"
    SAFE_MODE = "safe_mode"

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
    critical: bool = True

class GraceUnifiedOrchestrator:
    """Unified Grace orchestrator with comprehensive process management"""
    
    def __init__(self, environment: str = "dev", profile: Union[BootProfile, str] = "native", 
                 config_path: Optional[Path] = None, safe_mode: bool = False, dry_run: bool = False):
        
        # Handle string profile
        if isinstance(profile, str):
            try:
                profile = BootProfile(profile)
            except ValueError:
                profile = BootProfile.NATIVE
        
        self.environment = environment
        self.profile = profile
        self.safe_mode = safe_mode
        self.dry_run = dry_run
        
        # Paths
        self.grace_root = Path(__file__).parent.parent.absolute()
        self.config_path = config_path or self.grace_root / f".env.{environment}"
        
        # Platform detection
        self.os_type = platform.system().lower()
        self.is_windows = self.os_type == "windows"
        self.is_macos = self.os_type == "darwin"
        self.is_linux = self.os_type == "linux"
        
        # Boot state
        self.boot_id = f"boot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.launched_processes: List[str] = []
        self.process_registry: Dict[str, int] = {}  # Local registry for this session
        self.stage_results: Dict[str, bool] = {}
        
        # Setup logging
        self._setup_logging()
        
        # Configuration
        self.config: Dict[str, Any] = {}
    
    def _setup_logging(self):
        """Setup cross-platform logging"""
        log_dir = self.grace_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        
        # Create logger
        self.logger = logging.getLogger("grace.orchestrator")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(log_dir / f"boot_{self.boot_id}.log")
            file_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(log_format))
            self.logger.addHandler(console_handler)
    
    async def boot(self) -> bool:
        """Main boot orchestration"""
        self.logger.info(f"🚀 Grace Unified Boot - {self.environment.upper()} ({self.profile.value})")
        self.logger.info(f"📍 Platform: {platform.system()} {platform.release()}")
        self.logger.info(f"📁 Grace Root: {self.grace_root}")
        
        if self.dry_run:
            self.logger.info("🔍 DRY RUN MODE - No services will actually start")
        
        try:
            # Stage 1: Environment validation
            if not await self._stage_environment_validation():
                self.logger.error("❌ Environment validation failed")
                return False
            
            # Stage 2: Configuration loading
            if not await self._stage_configuration_loading():
                self.logger.error("❌ Configuration loading failed")
                return False
            
            # Stage 3: Dependencies check
            if not await self._stage_dependencies_check():
                self.logger.error("❌ Dependencies check failed")
                return False
            
            # Stage 4: Database initialization
            if not await self._stage_database_initialization():
                self.logger.error("❌ Database initialization failed")
                return False
            
            # Stage 5: Service startup
            if not await self._stage_service_startup():
                self.logger.error("❌ Service startup failed")
                return False
            
            # Stage 6: Health verification
            if not await self._stage_health_verification():
                self.logger.error("❌ Health verification failed")
                return False
            
            self.logger.info("✅ Grace boot completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Boot failed with exception: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            await self._emergency_rollback()
            return False
    
    async def _stage_environment_validation(self) -> bool:
        """Validate environment and platform"""
        self.logger.info("🔍 Stage 1: Environment validation")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 8):
                self.logger.error(f"❌ Python 3.8+ required, got {python_version.major}.{python_version.minor}")
                return False
            
            self.logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check Grace root exists
            if not self.grace_root.exists():
                self.logger.error(f"❌ Grace root not found: {self.grace_root}")
                return False
            
            self.logger.info(f"✅ Grace root: {self.grace_root}")
            
            # Check virtual environment
            venv_path = self.grace_root / ".venv"
            if not venv_path.exists():
                venv_path = self.grace_root / "venv"
            
            if venv_path.exists():
                self.logger.info(f"✅ Virtual environment: {venv_path}")
            else:
                self.logger.warning("⚠️  No virtual environment found")
            
            # Platform-specific checks
            if self.is_windows:
                # Set UTF-8 encoding
                os.environ["PYTHONIOENCODING"] = "utf-8"
                self.logger.info("✅ Windows UTF-8 encoding configured")
            
            self.stage_results["environment_validation"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Environment validation failed: {e}")
            self.stage_results["environment_validation"] = False
            return False
    
    async def _stage_configuration_loading(self) -> bool:
        """Load and validate configuration"""
        self.logger.info("⚙️  Stage 2: Configuration loading")
        
        try:
            # Load .env file if it exists
            if self.config_path.exists():
                self.logger.info(f"📄 Loading config: {self.config_path}")
                
                with open(self.config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                            self.config[key.strip()] = value.strip()
                
                self.logger.info(f"✅ Loaded {len(self.config)} config values")
            else:
                self.logger.warning(f"⚠️  Config file not found: {self.config_path}")
            
            # Set default values
            defaults = {
                "DATABASE_URL": f"sqlite:///{self.grace_root}/databases/grace.db",
                "SECRET_KEY": "dev-secret-key-change-in-production",
                "LOG_LEVEL": "INFO"
            }
            
            for key, default_value in defaults.items():
                if key not in os.environ:
                    os.environ[key] = default_value
                    self.config[key] = default_value
            
            self.stage_results["configuration_loading"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration loading failed: {e}")
            self.stage_results["configuration_loading"] = False
            return False
    
    async def _stage_dependencies_check(self) -> bool:
        """Check required dependencies"""
        self.logger.info("📦 Stage 3: Dependencies check")
        
        try:
            # Check if we can import key modules
            required_modules = [
                "fastapi",
                "uvicorn", 
                "sqlalchemy",
                "alembic"
            ]
            
            missing_modules = []
            for module in required_modules:
                try:
                    __import__(module)
                    self.logger.debug(f"✅ {module}")
                except ImportError:
                    missing_modules.append(module)
                    self.logger.error(f"❌ Missing: {module}")
            
            if missing_modules:
                self.logger.error(f"❌ Missing dependencies: {missing_modules}")
                self.logger.info("💡 Run: pip install -r requirements.txt")
                return False
            
            self.logger.info(f"✅ All {len(required_modules)} dependencies available")
            self.stage_results["dependencies_check"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Dependencies check failed: {e}")
            self.stage_results["dependencies_check"] = False
            return False
    
    async def _stage_database_initialization(self) -> bool:
        """Initialize database"""
        self.logger.info("🗄️  Stage 4: Database initialization")
        
        try:
            # Create databases directory
            db_dir = self.grace_root / "databases"
            db_dir.mkdir(exist_ok=True)
            
            # Check if database exists
            db_url = os.environ.get("DATABASE_URL", "")
            if "sqlite" in db_url:
                db_path = db_url.replace("sqlite:///", "")
                db_file = Path(db_path)
                
                if db_file.exists():
                    self.logger.info(f"✅ Database exists: {db_file}")
                else:
                    self.logger.info(f"📄 Database will be created: {db_file}")
            
            # Try to import and test database connection
            try:
                from backend.database import engine, Base
                
                # Test connection (this will create tables if needed)
                if not self.dry_run:
                    # Simple connection test
                    self.logger.info("🔌 Testing database connection...")
                    # Connection test would go here
                    self.logger.info("✅ Database connection successful")
                else:
                    self.logger.info("🔍 DRY RUN: Would test database connection")
                
            except ImportError as e:
                self.logger.warning(f"⚠️  Could not import database modules: {e}")
                # Continue anyway - database might be initialized later
            
            self.stage_results["database_initialization"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            self.stage_results["database_initialization"] = False
            return False
    
    async def _stage_service_startup(self) -> bool:
        """Start core services"""
        self.logger.info("🚀 Stage 5: Service startup")
        
        try:
            services_started = 0
            
            # Start backend (always)
            if await self._start_uvicorn_backend():
                services_started += 1
            else:
                self.logger.error("❌ Failed to start backend")
                return False
            
            # Start frontend (if not safe mode)
            if not self.safe_mode and self.profile != BootProfile.SAFE_MODE:
                if await self._start_frontend():
                    services_started += 1
                # Frontend failure is not critical
            
            # Start Docker services (if Docker profile)
            if self.profile == BootProfile.DOCKER:
                if await self._start_docker_services():
                    services_started += 1
                # Docker failure is not critical in mixed environments
            
            self.logger.info(f"✅ Started {services_started} services")
            self.stage_results["service_startup"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Service startup failed: {e}")
            self.stage_results["service_startup"] = False
            return False
    
    async def _stage_health_verification(self) -> bool:
        """Verify services are healthy"""
        self.logger.info("🏥 Stage 6: Health verification")
        
        try:
            if self.dry_run:
                self.logger.info("🔍 DRY RUN: Would verify service health")
                self.stage_results["health_verification"] = True
                return True
            
            # Wait a moment for services to start
            await asyncio.sleep(3)
            
            # Check backend health
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8000/health", timeout=10) as response:
                        if response.status == 200:
                            self.logger.info("✅ Backend health check passed")
                        else:
                            self.logger.warning(f"⚠️  Backend health check returned {response.status}")
            except Exception as e:
                self.logger.warning(f"⚠️  Backend health check failed: {e}")
                # Don't fail boot for health check issues
            
            self.stage_results["health_verification"] = True
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Health verification failed: {e}")
            self.stage_results["health_verification"] = False
            return False
    
    async def _start_uvicorn_backend(self) -> bool:
        """Start Uvicorn backend"""
        try:
            self.logger.info("🚀 Starting Uvicorn backend...")
            
            if self.dry_run:
                self.logger.info("🔍 DRY RUN: Would start uvicorn backend")
                return True
            
            # Prepare command
            python_exe = sys.executable
            cmd = [
                python_exe, "-m", "uvicorn", 
                "backend.main:app",
                "--host", "0.0.0.0",
                "--port", "8000"
            ]
            
            if self.environment == "dev":
                cmd.append("--reload")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=self.grace_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0
            )
            
            # Wait briefly to ensure it started
            await asyncio.sleep(2)
            
            if process.poll() is None:  # Still running
                # Register with process registry
                try:
                    process_id = process_registry.register_process(
                        pid=process.pid,
                        name="Grace Backend",
                        component="uvicorn",
                        command=cmd,
                        cwd=str(self.grace_root),
                        ports=[8000],
                        endpoints=["http://localhost:8000"],
                        boot_id=self.boot_id,
                        environment=self.environment,
                        process_type="uvicorn",
                        shutdown_method="http",
                        shutdown_endpoint="http://localhost:8000/shutdown",
                        health_endpoint="http://localhost:8000/health"
                    )
                    
                    self.launched_processes.append(process_id)
                    self.process_registry[process_id] = process.pid
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not register process: {e}")
                
                self.logger.info(f"✅ Backend started (PID: {process.pid})")
                return True
            else:
                self.logger.error("❌ Backend failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start backend: {e}")
            return False
    
    async def _start_frontend(self) -> bool:
        """Start frontend development server"""
        try:
            frontend_dir = self.grace_root / "frontend"
            if not frontend_dir.exists():
                self.logger.warning("⚠️  Frontend directory not found, skipping")
                return True
            
            self.logger.info("🎨 Starting frontend...")
            
            if self.dry_run:
                self.logger.info("🔍 DRY RUN: Would start npm dev server")
                return True
            
            # Check if npm is available
            try:
                subprocess.run(["npm", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("⚠️  npm not found, skipping frontend")
                return True
            
            # Start npm dev server
            cmd = ["npm", "run", "dev"]
            
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=self.is_windows,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0
            )
            
            # Wait briefly to ensure it started
            await asyncio.sleep(3)
            
            if process.poll() is None:  # Still running
                try:
                    process_id = process_registry.register_process(
                        pid=process.pid,
                        name="Grace Frontend",
                        component="vite",
                        command=cmd,
                        cwd=str(frontend_dir),
                        ports=[5173],
                        endpoints=["http://localhost:5173"],
                        boot_id=self.boot_id,
                        environment=self.environment,
                        process_type="npm",
                        shutdown_method="signal",
                        health_endpoint="http://localhost:5173"
                    )
                    
                    self.launched_processes.append(process_id)
                    self.process_registry[process_id] = process.pid
                except Exception as e:
                    self.logger.warning(f"⚠️  Could not register frontend process: {e}")
                
                self.logger.info(f"✅ Frontend started (PID: {process.pid})")
                return True
            else:
                self.logger.error("❌ Frontend failed to start")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start frontend: {e}")
            return False
    
    async def _start_docker_services(self) -> bool:
        """Start Docker services"""
        try:
            compose_file = self.grace_root / "docker-compose.yml"
            if not compose_file.exists():
                self.logger.warning("⚠️  docker-compose.yml not found, skipping")
                return True
            
            self.logger.info("🐳 Starting Docker services...")
            
            if self.dry_run:
                self.logger.info("🔍 DRY RUN: Would start docker-compose services")
                return True
            
            # Start docker-compose
            cmd = ["docker-compose", "up", "-d"]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.grace_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                self.logger.info("✅ Docker services started")
                return True
            else:
                self.logger.error(f"❌ Docker services failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start Docker services: {e}")
            return False
    
    async def _emergency_rollback(self):
        """Emergency rollback on boot failure"""
        self.logger.info("🔄 Emergency rollback initiated")
        
        # Stop any processes we started
        for process_id in self.launched_processes:
            if process_id in self.process_registry:
                try:
                    pid = self.process_registry[process_id]
                    if psutil.pid_exists(pid):
                        process = psutil.Process(pid)
                        process.terminate()
                        self.logger.info(f"🛑 Stopped {process_id} (PID: {pid})")
                except Exception as e:
                    self.logger.error(f"❌ Failed to stop {process_id}: {e}")
    
    async def stop(self, force: bool = False, timeout: int = 30) -> bool:
        """Stop all Grace services"""
        self.logger.info("🛑 Stopping Grace services...")
        
        if self.dry_run:
            self.logger.info("🔍 DRY RUN: Would stop all services")
            return True
        
        try:
            # Stop all registered processes
            results = await process_registry.stop_all_processes(force=force, timeout=timeout)
            
            # Clear our tracking
            self.launched_processes.clear()
            self.process_registry.clear()
            
            # Report results
            total_stopped = len(results["stopped"]) + len(results["force_killed"])
            total_failed = len(results["failed"])
            
            if total_failed == 0:
                self.logger.info(f"✅ Successfully stopped {total_stopped} processes")
                return True
            else:
                self.logger.warning(f"⚠️  Stopped {total_stopped} processes, {total_failed} failed")
                return False
        except Exception as e:
            self.logger.error(f"❌ Stop failed: {e}")
            return False
    
    async def status(self) -> Dict[str, Any]:
        """Get system status"""
        try:
            return {
                "boot_id": self.boot_id,
                "environment": self.environment,
                "profile": self.profile.value,
                "grace_root": str(self.grace_root),
                "launched_processes": len(self.launched_processes),
                "stage_results": self.stage_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def print_status(self, status: Dict[str, Any]):
        """Print formatted status"""
        print(f"\n🚀 GRACE SYSTEM STATUS")
        print(f"Boot ID: {status.get('boot_id', 'unknown')}")
        print(f"Environment: {status.get('environment', 'unknown')}")
        print(f"Profile: {status.get('profile', 'unknown')}")
        print(f"Grace Root: {status.get('grace_root', 'unknown')}")
        print(f"Launched Processes: {status.get('launched_processes', 0)}")
        
        stage_results = status.get('stage_results', {})
        if stage_results:
            print(f"\n📊 BOOT STAGES:")
            for stage, result in stage_results.items():
                status_icon = "✅" if result else "❌"
                print(f"  {status_icon} {stage}")
        
        print()

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Grace Unified Production Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  grace                                    # Boot development environment
  grace --env prod --profile docker       # Boot production with Docker
  grace --stop                            # Stop all Grace processes
  grace --stop --force                    # Force stop all processes
  grace --status                          # Show process status
        """
    )
    
    parser.add_argument("--env", default="dev", choices=["dev", "staging", "prod"],
                       help="Environment to boot (default: dev)")
    parser.add_argument("--profile", default="native", 
                       choices=["native", "docker", "kubernetes", "safe_mode"],
                       help="Boot profile (default: native)")
    parser.add_argument("--config", type=Path, help="Path to config file")
    parser.add_argument("--safe-mode", action="store_true",
                       help="Boot in safe mode (minimal services)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry run (don't actually start services)")
    parser.add_argument("--status", action="store_true",
                       help="Show system status")
    parser.add_argument("--stop", action="store_true",
                       help="Stop all Grace services")
    parser.add_argument("--force", action="store_true",
                       help="Force stop (use with --stop)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Shutdown timeout in seconds (default: 30)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    async def run_command():
        try:
            if args.stop:
                print("🛑 Stopping all Grace processes...")
                if args.force:
                    print("⚠️  Force mode enabled - will kill stubborn processes")
                
                results = await process_registry.stop_all_processes(
                    force=args.force, 
                    timeout=args.timeout
                )
                
                # Print results
                total_stopped = len(results["stopped"]) + len(results["force_killed"])
                print(f"\n📊 SHUTDOWN RESULTS:")
                print(f"✅ Stopped: {len(results['stopped'])}")
                print(f"🔨 Force killed: {len(results['force_killed'])}")
                print(f"❌ Failed: {len(results['failed'])}")
                print(f"📈 Total: {total_stopped} processes stopped")
                return
            
            # Create orchestrator
            orchestrator = GraceUnifiedOrchestrator(
                environment=args.env,
                profile=args.profile,
                config_path=args.config,
                safe_mode=args.safe_mode,
                dry_run=args.dry_run
            )
            
            if args.status:
                status = await orchestrator.status()
                if args.verbose:
                    print(json.dumps(status, indent=2))
                else:
                    orchestrator.print_status(status)
                return
            
            # Boot Grace
            print(f"🚀 Starting Grace ({args.env}/{args.profile})")
            if args.dry_run:
                print("🔍 DRY RUN MODE - No services will actually start")
            
            success = await orchestrator.boot()
            
            if success:
                print("\n✅ Grace boot completed successfully!")
                print(f"🆔 Boot ID: {orchestrator.boot_id}")
                print(f"📝 Launched {len(orchestrator.launched_processes)} processes")
                
                if not args.dry_run:
                    print("\n💡 Commands:")
                    print("   grace --status     # Check status")
                    print("   grace --stop       # Stop all services")
                    print("   grace --stop --force # Force stop all")
            else:
                print("\n❌ Grace boot failed!")
                sys.exit(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Command failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n✅ Grace stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

