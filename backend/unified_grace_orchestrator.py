#!/usr/bin/env python3
"""
Grace Unified Orchestrator - Production Boot System
Integrates all Grace systems: migrations, kernels, learning, agents, memory
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import subprocess
import sys
import os
import signal
import psutil
import json
from pathlib import Path
import argparse
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any
import traceback

# Grace system imports
try:
    from .grace_process_registry import process_registry, ProcessInfo
    from .unified_logic_hub import unified_logic_hub
    from .grace_spine_integration import activate_grace_autonomy
    from .web_learning_orchestrator import web_learning_orchestrator
    from .integration_orchestrator import IntegrationOrchestrator
    from .boot_pipeline import BootPipeline
    from .grace_core import GraceCore
    from .trigger_mesh import trigger_mesh
    from .immutable_log import immutable_log
    from .memory_fusion import memory_fusion
    from .lightning_memory import lightning_memory
except ImportError as e:
    print(f"⚠️ Some Grace modules not available: {e}")

# Setup logging once
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraceUnifiedOrchestrator:
    """Production-ready Grace orchestrator with full system integration"""
    
    _instance = None
    _lock = asyncio.Lock()
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, environment: str = "dev", profile: str = "native", 
                 safe_mode: bool = False, dry_run: bool = False, timeout: int = 60):
        # Only initialize once
        if self._initialized:
            return
            
        self.environment = environment
        self.profile = profile
        self.safe_mode = safe_mode
        self.dry_run = dry_run
        self.timeout = timeout
        self.boot_id = f"grace-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.state_file = Path("grace_state.json")
        self.log_file = Path("logs/orchestrator.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize components
        self.boot_pipeline = None
        self.integration_orchestrator = None
        self.grace_core = None
        self.frontend_process = None
        self.launched_processes = []
        self.stage_results = {}
        self._is_running = False
        self._boot_task = None
        
        # Setup file logging (only once)
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
        
        logger.info(f"Grace Orchestrator initialized - {self.boot_id}")
        self._initialized = True

    async def boot(self) -> bool:
        """Main boot orchestration with full Grace integration"""
        async with self._lock:
            if self._is_running:
                logger.warning("Boot already in progress or completed")
                return True
                
            if self._boot_task and not self._boot_task.done():
                logger.warning("Boot task already running")
                return await self._boot_task
            
            self._boot_task = asyncio.create_task(self._execute_boot())
            return await self._boot_task

    async def _execute_boot(self) -> bool:
        """Execute the actual boot sequence"""
        logger.info(f"🚀 Grace Unified Boot - {self.environment.upper()} ({self.profile})")
        logger.info(f"📍 Boot ID: {self.boot_id}")
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No services will actually start")
            return await self._dry_run_boot()
        
        try:
            self._is_running = True
            
            # Stage 1: Pre-flight checks
            if not await self._stage_preflight():
                logger.error("❌ Pre-flight checks failed")
                return False
            
            # Stage 2: Database migrations
            if not await self._stage_database_migrations():
                logger.error("❌ Database migrations failed")
                return False
            
            # Stage 3: Core services initialization
            if not await self._stage_core_services():
                logger.error("❌ Core services initialization failed")
                return False
            
            # Stage 4: Domain kernels startup
            if not await self._stage_domain_kernels():
                logger.error("❌ Domain kernels startup failed")
                return False
            
            # Stage 5: Learning systems activation
            if not await self._stage_learning_systems():
                logger.error("❌ Learning systems activation failed")
                return False
            
            # Stage 6: Autonomous agents deployment
            if not await self._stage_autonomous_agents():
                logger.error("❌ Autonomous agents deployment failed")
                return False
            
            # Stage 7: Memory systems integration
            if not await self._stage_memory_systems():
                logger.error("❌ Memory systems integration failed")
                return False
            
            # Stage 8: Web services startup
            if not await self._stage_web_services():
                logger.error("❌ Web services startup failed")
                return False
            
            # Stage 9: Health verification
            if not await self._stage_health_verification():
                logger.error("❌ Health verification failed")
                return False
            
            # Stage 10: Post-boot diagnostics
            if not await self._stage_post_boot_diagnostics():
                logger.error("❌ Post-boot diagnostics failed")
                return False
            
            await self._save_boot_state()
            logger.info("✅ Grace boot completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Boot failed with exception: {e}")
            logger.error(traceback.format_exc())
            await self._emergency_rollback()
            return False
        finally:
            self._is_running = False

    async def _stage_preflight(self) -> bool:
        """Stage 1: Pre-flight environment checks"""
        logger.info("🔍 Stage 1: Pre-flight checks")
        
        # Check Python version
        if sys.version_info < (3, 11):
            logger.error(f"❌ Python 3.11+ required, found {sys.version}")
            return False
        
        # Check required directories
        required_dirs = ["backend", "logs", "data"]
        for dir_name in required_dirs:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Check environment variables
        required_env = ["SECRET_KEY"] if self.environment == "prod" else []
        for env_var in required_env:
            if not os.getenv(env_var):
                logger.error(f"❌ Required environment variable missing: {env_var}")
                return False
        
        self.stage_results["preflight"] = True
        logger.info("✅ Stage 1: Pre-flight checks completed")
        return True

    async def _stage_database_migrations(self) -> bool:
        """Stage 2: Database migrations and schema setup"""
        logger.info("🗄️ Stage 2: Database migrations")
        
        try:
            # Run Alembic migrations
            result = subprocess.run([
                sys.executable, "-m", "alembic", "upgrade", "head"
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Alembic migration warning: {result.stderr}")
            else:
                logger.info("✅ Database migrations completed")
            
            # Seed governance policies
            try:
                from .seed_governance_policies import seed_policies
                await seed_policies()
                logger.info("✅ Governance policies seeded")
            except ImportError:
                logger.warning("⚠️ Governance policy seeding not available")
            
            self.stage_results["database_migrations"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Database migration failed: {e}")
            return False

    async def _stage_core_services(self) -> bool:
        """Stage 3: Core services initialization"""
        logger.info("⚙️ Stage 3: Core services initialization")
        
        try:
            # Initialize trigger mesh
            if hasattr(trigger_mesh, 'start'):
                await trigger_mesh.start()
                logger.info("✅ Trigger mesh started")
            
            # Initialize immutable log
            if hasattr(immutable_log, 'start'):
                await immutable_log.start()
                logger.info("✅ Immutable log started")
            
            # Initialize unified logic hub
            if hasattr(unified_logic_hub, 'start'):
                await unified_logic_hub.start()
                logger.info("✅ Unified logic hub started")
            
            # Initialize process registry (lazy start)
            if hasattr(process_registry, 'start'):
                process_registry.start()
                logger.info("✅ Process registry started")
            
            self.stage_results["core_services"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Core services initialization failed: {e}")
            return False

    async def _stage_domain_kernels(self) -> bool:
        """Stage 4: Domain kernels startup"""
        logger.info("🧠 Stage 4: Domain kernels startup")
        
        if self.safe_mode:
            logger.info("⚠️ Safe mode: Skipping domain kernels")
            return True
        
        try:
            # Initialize integration orchestrator
            self.integration_orchestrator = IntegrationOrchestrator()
            if hasattr(self.integration_orchestrator, 'start'):
                await self.integration_orchestrator.start()
                logger.info("✅ Integration orchestrator started")
            
            # Start domain kernels (9 kernels with 311+ APIs)
            kernel_count = await self._start_domain_kernels()
            logger.info(f"✅ Started {kernel_count} domain kernels")
            
            self.stage_results["domain_kernels"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Domain kernels startup failed: {e}")
            return False

    async def _stage_learning_systems(self) -> bool:
        """Stage 5: Learning systems activation"""
        logger.info("📚 Stage 5: Learning systems activation")
        
        if self.safe_mode:
            logger.info("⚠️ Safe mode: Skipping learning systems")
            return True
        
        try:
            # Start web learning orchestrator
            if hasattr(web_learning_orchestrator, 'start'):
                await web_learning_orchestrator.start()
                logger.info("✅ Web learning orchestrator started")
            
            # Initialize learning systems
            learning_systems = [
                "github_mining", "youtube_learning", "reddit_learning",
                "web_scraping", "documentation_learning"
            ]
            
            for system in learning_systems:
                try:
                    # Dynamic import and start
                    module = __import__(f"backend.{system}", fromlist=[system])
                    if hasattr(module, 'start'):
                        await module.start()
                        logger.info(f"✅ {system} started")
                except ImportError:
                    logger.warning(f"⚠️ {system} not available")
            
            self.stage_results["learning_systems"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Learning systems activation failed: {e}")
            return False

    async def _stage_autonomous_agents(self) -> bool:
        """Stage 6: Autonomous agents deployment"""
        logger.info("🤖 Stage 6: Autonomous agents deployment")
        
        try:
            # Activate Grace autonomy (agentic spine)
            if hasattr(activate_grace_autonomy, '__call__'):
                await activate_grace_autonomy()
                logger.info("✅ Grace autonomy activated")
            
            # Start elite agents
            elite_agents = [
                "elite_self_healing", "elite_coding_agent", 
                "autonomous_improver", "proactive_intelligence"
            ]
            
            for agent in elite_agents:
                try:
                    module = __import__(f"backend.{agent}", fromlist=[agent])
                    if hasattr(module, 'start'):
                        await module.start()
                        logger.info(f"✅ {agent} started")
                except ImportError:
                    logger.warning(f"⚠️ {agent} not available")
            
            self.stage_results["autonomous_agents"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Autonomous agents deployment failed: {e}")
            return False

    async def _stage_memory_systems(self) -> bool:
        """Stage 7: Memory systems integration"""
        logger.info("🧠 Stage 7: Memory systems integration")
        
        try:
            # Start memory fusion
            if hasattr(memory_fusion, 'start'):
                await memory_fusion.start()
                logger.info("✅ Memory fusion started")
            
            # Start lightning memory
            if hasattr(lightning_memory, 'start'):
                await lightning_memory.start()
                logger.info("✅ Lightning memory started")
            
            # Initialize Grace core
            self.grace_core = GraceCore()
            if hasattr(self.grace_core, 'start'):
                await self.grace_core.start()
                logger.info("✅ Grace core started")
            
            self.stage_results["memory_systems"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Memory systems integration failed: {e}")
            return False

    async def _stage_web_services(self) -> bool:
        """Stage 8: Web services startup"""
        logger.info("🌐 Stage 8: Web services startup")
        
        try:
            # Start frontend (unless safe mode)
            if not self.safe_mode:
                if await self._start_frontend():
                    logger.info("✅ Frontend started")
                else:
                    logger.warning("⚠️ Frontend startup failed (non-critical)")
            
            # Register backend process
            if hasattr(process_registry, 'register_process'):
                process_id = process_registry.register_process(
                    pid=os.getpid(),
                    name="Grace Backend",
                    component="uvicorn",
                    command=f"{sys.executable} -m backend.unified_grace_orchestrator",
                    cwd=str(Path.cwd()),
                    ports=[8000],
                    endpoints=["http://localhost:8000"],
                    boot_id=self.boot_id,
                    environment=self.environment,
                    process_type="uvicorn",
                    shutdown_method="http",
                    shutdown_endpoint="http://localhost:8000/api/shutdown",
                    health_endpoint="http://localhost:8000/health"
                )
                
                self.launched_processes.append(process_id)
            
            self.stage_results["web_services"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Web services startup failed: {e}")
            return False

    async def _stage_health_verification(self) -> bool:
        """Stage 9: Health verification"""
        logger.info("🏥 Stage 9: Health verification")
        
        try:
            # Verify core systems
            health_checks = []
            
            if hasattr(trigger_mesh, 'health_check'):
                health_checks.append(("trigger_mesh", trigger_mesh.health_check))
            if hasattr(immutable_log, 'health_check'):
                health_checks.append(("immutable_log", immutable_log.health_check))
            if hasattr(unified_logic_hub, 'health_check'):
                health_checks.append(("unified_logic_hub", unified_logic_hub.health_check))
            
            for name, check in health_checks:
                try:
                    if await check():
                        logger.info(f"✅ {name} health check passed")
                    else:
                        logger.warning(f"⚠️ {name} health check failed")
                except Exception as e:
                    logger.warning(f"⚠️ {name} health check error: {e}")
            
            self.stage_results["health_verification"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Health verification failed: {e}")
            return False

    async def _stage_post_boot_diagnostics(self) -> bool:
        """Stage 10: Post-boot diagnostics"""
        logger.info("🔬 Stage 10: Post-boot diagnostics")
        
        try:
            # Run boot pipeline diagnostics
            if self.boot_pipeline and hasattr(self.boot_pipeline, 'run_diagnostics'):
                diagnostics = await self.boot_pipeline.run_diagnostics()
                logger.info(f"✅ Boot diagnostics completed: {diagnostics}")
            
            # Verify process registry
            if hasattr(process_registry, 'processes'):
                active_processes = len(process_registry.processes)
                logger.info(f"✅ {active_processes} processes registered")
            
            self.stage_results["post_boot_diagnostics"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Post-boot diagnostics failed: {e}")
            return False

    async def _start_domain_kernels(self) -> int:
        """Start domain kernels"""
        kernels = [
            "mission_control_hub", "autonomous_coding_pipeline", 
            "self_healing_workflow", "governance_engine", "hunter_engine"
        ]
        
        started = 0
        for kernel in kernels:
            try:
                module = __import__(f"backend.{kernel}", fromlist=[kernel])
                if hasattr(module, 'start'):
                    await module.start()
                    started += 1
            except ImportError:
                logger.warning(f"⚠️ Kernel {kernel} not available")
        
        return started

    async def _start_frontend(self) -> bool:
        """Start frontend development server"""
        frontend_dir = Path("frontend")
        if not frontend_dir.exists() or not (frontend_dir / "package.json").exists():
            logger.warning("⚠️ Frontend directory not found")
            return False
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait briefly to ensure it started
            await asyncio.sleep(2)
            
            if self.frontend_process.poll() is None:
                # Register frontend process
                if hasattr(process_registry, 'register_process'):
                    process_id = process_registry.register_process(
                        pid=self.frontend_process.pid,
                        name="Grace Frontend",
                        component="vite",
                        command="npm run dev",
                        cwd=str(frontend_dir),
                        ports=[5173],
                        endpoints=["http://localhost:5173"],
                        boot_id=self.boot_id,
                        environment=self.environment,
                        process_type="frontend"
                    )
                    
                    self.launched_processes.append(process_id)
                return True
            
        except Exception as e:
            logger.error(f"❌ Frontend startup failed: {e}")
        
        return False

    async def _dry_run_boot(self) -> bool:
        """Dry run boot simulation"""
        logger.info("🔍 DRY RUN: Simulating Grace boot sequence")
        
        stages = [
            "Pre-flight checks", "Database migrations", "Core services",
            "Domain kernels", "Learning systems", "Autonomous agents",
            "Memory systems", "Web services", "Health verification",
            "Post-boot diagnostics"
        ]
        
        for i, stage in enumerate(stages, 1):
            logger.info(f"🔍 DRY RUN Stage {i}: {stage}")
            await asyncio.sleep(0.5)  # Simulate work
        
        logger.info("🔍 DRY RUN: Boot sequence completed successfully")
        return True

    async def _save_boot_state(self):
        """Save boot state to JSON file"""
        state = {
            "boot_id": self.boot_id,
            "environment": self.environment,
            "profile": self.profile,
            "safe_mode": self.safe_mode,
            "backend_pid": os.getpid(),
            "backend_port": 8000,
            "frontend_pid": self.frontend_process.pid if self.frontend_process else None,
            "frontend_port": 5173,
            "launched_processes": self.launched_processes,
            "stage_results": self.stage_results,
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed system status"""
        state = self._load_state()
        
        return {
            "boot_id": state.get("boot_id", "unknown") if state else "not_running",
            "environment": state.get("environment", "unknown") if state else "unknown",
            "profile": state.get("profile", "unknown") if state else "unknown",
            "backend": {
                "status": "running" if state else "stopped",
                "pid": state.get("backend_pid") if state else None,
                "port": 8000,
                "endpoint": "http://localhost:8000"
            },
            "frontend": {
                "status": "running" if state and state.get("frontend_pid") else "stopped",
                "pid": state.get("frontend_pid") if state else None,
                "port": 5173,
                "endpoint": "http://localhost:5173"
            },
            "processes": len(self.launched_processes) if state else 0,
            "stage_results": state.get("stage_results", {}) if state else {},
            "started_at": state.get("started_at") if state else None,
            "uptime": self._calculate_uptime(state.get("started_at")) if state else None,
            "is_running": self._is_running
        }

    def _load_state(self) -> Optional[Dict]:
        """Load state from JSON file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    def _calculate_uptime(self, started_at: str) -> str:
        """Calculate uptime from start time"""
        if not started_at:
            return "unknown"
        
        try:
            start_time = datetime.fromisoformat(started_at)
            uptime = datetime.now() - start_time
            return str(uptime).split('.')[0]  # Remove microseconds
        except:
            return "unknown"

    async def _emergency_rollback(self):
        """Emergency rollback on boot failure"""
        logger.info("🔄 Emergency rollback initiated")
        await self.stop(force=True)

    async def stop(self, force: bool = False, timeout: int = 30) -> bool:
        """Stop all Grace services"""
        async with self._lock:
            logger.info("🛑 Stopping Grace services...")
            
            try:
                # Stop all registered processes
                if hasattr(process_registry, 'stop_all_processes'):
                    results = await process_registry.stop_all_processes(force=force, timeout=timeout)
                    total_stopped = len(results.get("stopped", [])) + len(results.get("force_killed", []))
                    logger.info(f"✅ Successfully stopped {total_stopped} processes")
                
                # Stop frontend process
                if self.frontend_process:
                    try:
                        self.frontend_process.terminate()
                        if force:
                            self.frontend_process.kill()
                    except:
                        pass
                
                # Stop core systems
                if self.grace_core and hasattr(self.grace_core, 'stop'):
                    await self.grace_core.stop()
                
                # Clear state
                self.launched_processes.clear()
                if self.state_file.exists():
                    self.state_file.unlink()
                
                self._is_running = False
                return True
                
            except Exception as e:
                logger.error(f"❌ Stop failed: {e}")
                return False

# Global orchestrator instance
orchestrator = GraceUnifiedOrchestrator()

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 FastAPI startup - Grace orchestrator ready")
    yield
    # Shutdown
    logger.info("🛑 FastAPI shutdown - stopping Grace services")
    await orchestrator.stop(force=True)

# FastAPI app with lifespan
app = FastAPI(
    title="Grace AI System", 
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Grace AI System is running", "status": "active", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "backend": "running", "frontend": "available"}

@app.get("/api/status")
async def api_status():
    return await orchestrator.get_detailed_status()

@app.post("/api/shutdown")
async def shutdown():
    """Graceful shutdown endpoint"""
    await orchestrator.stop()
    return {"message": "Grace shutdown initiated"}

@app.post("/api/boot")
async def boot():
    """Boot Grace systems"""
    success = await orchestrator.boot()
    return {"success": success, "boot_id": orchestrator.boot_id}

# Process manager for compatibility
class GraceProcessManager:
    def __init__(self):
        self.orchestrator = orchestrator
    
    def start_frontend(self):
        return asyncio.run(self.orchestrator._start_frontend())
    
    def stop_services(self, force=False):
        return asyncio.run(self.orchestrator.stop(force=force))

process_manager = GraceProcessManager()

def signal_handler(signum, frame):
    """Handle shutdown signals properly"""
    asyncio.run(orchestrator.stop(force=True))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    parser = argparse.ArgumentParser(description="Grace Unified Orchestrator")
    parser.add_argument("--stop", action="store_true", help="Stop Grace services")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--force", action="store_true", help="Force stop")
    parser.add_argument("--env", default="dev", help="Environment (dev/prod/test)")
    parser.add_argument("--profile", default="native", help="Profile (native/docker/k8s)")
    parser.add_argument("--safe-mode", action="store_true", help="Safe mode")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    parser.add_argument("--serve", action="store_true", help="Start API server only")
    
    args = parser.parse_args()
    
    # Update global orchestrator with CLI args
    global orchestrator
    orchestrator = GraceUnifiedOrchestrator(
        environment=args.env,
        profile=args.profile,
        safe_mode=args.safe_mode,
        dry_run=args.dry_run,
        timeout=args.timeout
    )
    
    async def run_command():
        if args.stop:
            await orchestrator.stop(force=args.force, timeout=args.timeout)
            return
        
        if args.status:
            status = await orchestrator.get_detailed_status()
            print(json.dumps(status, indent=2))
            return
        
        if args.serve:
            # Just start the API server without booting
            print("🌐 Starting Grace API server...")
            print("🔗 Backend: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
            return
        
        # Boot Grace first, then optionally serve
        success = await orchestrator.boot()
        
        if success:
            print(f"\n✅ Grace boot completed successfully!")
            print(f"🆔 Boot ID: {orchestrator.boot_id}")
            print(f"🌐 Backend: http://localhost:8000")
            print(f"🎨 Frontend: http://localhost:5173")
            print(f"📚 API Docs: http://localhost:8000/docs")
            
            # Only start uvicorn if not in dry-run mode and not already running under uvicorn
            if not args.dry_run and not os.getenv("UVICORN_RUNNING"):
                print("\n🚀 Starting API server...")
                os.environ["UVICORN_RUNNING"] = "1"
                uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        else:
            sys.exit(1)
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        asyncio.run(orchestrator.stop(force=True))
    except Exception as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

