#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grace Unified Orchestrator - COMPLETE SYSTEM INTEGRATION
Manages ALL Grace subsystems across ALL platforms (Windows/macOS/Linux)
"""

import asyncio
import logging
import json
import os
import sys
import platform
import subprocess
import traceback
import signal
import psutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from contextlib import asynccontextmanager

# FastAPI and web framework
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Grace system imports - COMPLETE INTEGRATION (ALL SUBSYSTEMS)
IMPORTS_SUCCESSFUL = True
import_errors = []

# Defensive imports with detailed error tracking
def safe_import(module_name: str, from_module: str = None):
    """Safely import modules with error tracking"""
    global IMPORTS_SUCCESSFUL, import_errors
    try:
        if from_module:
            module = __import__(from_module, fromlist=[module_name])
            return getattr(module, module_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        import_errors.append(f"{from_module}.{module_name}" if from_module else module_name)
        IMPORTS_SUCCESSFUL = False
        return None

# Create stub for missing components
class StubComponent:
    def __init__(self, name: str):
        self.name = name
        self._started = False
    
    async def start(self):
        self._started = True
        return True
    
    async def initialize(self):
        self._started = True
        return True
    
    async def stop(self):
        self._started = False
        return True
    
    def is_running(self):
        return self._started

# Core Infrastructure - using absolute imports
process_registry = safe_import('process_registry', 'backend.grace_process_registry') or StubComponent('process_registry')
ProcessInfo = safe_import('ProcessInfo', 'backend.grace_process_registry') or dict
unified_logic_hub = safe_import('unified_logic_hub', 'backend.unified_logic_hub') or StubComponent('unified_logic_hub')
activate_grace_autonomy = safe_import('activate_grace_autonomy', 'backend.grace_spine_integration') or StubComponent('activate_grace_autonomy')
IntegrationOrchestrator = safe_import('IntegrationOrchestrator', 'backend.integration_orchestrator') or StubComponent
BootPipeline = safe_import('BootPipeline', 'backend.boot_pipeline') or StubComponent
GraceCore = safe_import('GraceCore', 'backend.grace_core') or StubComponent

# Memory Systems - check if files exist before importing
memory_fusion = None
if Path("backend/memory_fusion.py").exists():
    memory_fusion = safe_import('memory_fusion', 'backend.memory_fusion')
else:
    memory_fusion = StubComponent('memory_fusion')

lightning_memory = None
if Path("backend/lightning_memory.py").exists():
    lightning_memory = safe_import('lightning_memory', 'backend.lightning_memory')
else:
    lightning_memory = StubComponent('lightning_memory')

agentic_memory = safe_import('agentic_memory', 'backend.agentic_memory') or StubComponent('agentic_memory')
PersistentMemory = safe_import('PersistentMemory', 'backend.memory') or StubComponent
code_memory = safe_import('code_memory', 'backend.code_memory') or StubComponent('code_memory')

multi_modal_memory = None
if Path("backend/multi_modal_memory.py").exists():
    multi_modal_memory = safe_import('multi_modal_memory', 'backend.multi_modal_memory')
else:
    multi_modal_memory = StubComponent('multi_modal_memory')

# LLM & Cognition
get_grace_llm = safe_import('get_grace_llm', 'backend.grace_llm') or (lambda: StubComponent('grace_llm'))
GraceLLM = safe_import('GraceLLM', 'backend.grace_llm') or StubComponent
CognitionIntent = safe_import('CognitionIntent', 'backend.cognition_intent') or StubComponent('cognition_intent')
cognition_intent = None  # Will be initialized during boot

# Domain Kernels - check if kernel directory exists
kernel_path = Path("backend/kernels")
if kernel_path.exists():
    MemoryKernel = safe_import('MemoryKernel', 'backend.kernels.memory_kernel') or StubComponent
    CoreKernel = safe_import('CoreKernel', 'backend.kernels.core_kernel') or StubComponent
    CodeKernel = safe_import('CodeKernel', 'backend.kernels.code_kernel') or StubComponent
    GovernanceKernel = safe_import('GovernanceKernel', 'backend.kernels.governance_kernel') or StubComponent
    VerificationKernel = safe_import('VerificationKernel', 'backend.kernels.verification_kernel') or StubComponent
    IntelligenceKernel = safe_import('IntelligenceKernel', 'backend.kernels.intelligence_kernel') or StubComponent
    InfrastructureKernel = safe_import('InfrastructureKernel', 'backend.kernels.infrastructure_kernel') or StubComponent
    FederationKernel = safe_import('FederationKernel', 'backend.kernels.federation_kernel') or StubComponent
else:
    # Create stub kernels if directory doesn't exist
    MemoryKernel = CoreKernel = CodeKernel = GovernanceKernel = StubComponent
    VerificationKernel = IntelligenceKernel = InfrastructureKernel = FederationKernel = StubComponent

# API Routes - check if routes exist
routes_path = Path("backend/routes")
chat_router = None
if (routes_path / "chat.py").exists():
    chat_router = safe_import('router', 'backend.routes.chat')

multimodal_router = None
if (routes_path / "multimodal_api.py").exists():
    multimodal_router = safe_import('router', 'backend.routes.multimodal_api')

# CLI Systems - check if cli directory exists
cli_path = Path("cli")
EnhancedGraceCLI = StubComponent
if cli_path.exists() and (cli_path / "enhanced_grace_cli.py").exists():
    EnhancedGraceCLI = safe_import('EnhancedGraceCLI', 'cli.enhanced_grace_cli') or StubComponent

# Multi-OS Detection and Configuration
CURRENT_OS = platform.system().lower()
IS_WINDOWS = CURRENT_OS == "windows"
IS_MACOS = CURRENT_OS == "darwin"
IS_LINUX = CURRENT_OS == "linux"

# OS-specific configurations
OS_CONFIG = {
    "windows": {
        "shell": True,
        "python_cmd": "python",
        "npm_cmd": "npm.cmd",
        "encoding": "utf-8",
        "path_sep": "\\",
        "process_creation_flags": subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0
    },
    "darwin": {  # macOS
        "shell": False,
        "python_cmd": "python3",
        "npm_cmd": "npm",
        "encoding": "utf-8",
        "path_sep": "/",
        "process_creation_flags": 0
    },
    "linux": {
        "shell": False,
        "python_cmd": "python3",
        "npm_cmd": "npm",
        "encoding": "utf-8",
        "path_sep": "/",
        "process_creation_flags": 0
    }
}

current_config = OS_CONFIG.get(CURRENT_OS, OS_CONFIG["linux"])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GraceUnifiedOrchestrator:
    """
    Production-ready Grace orchestrator with COMPLETE system integration
    Singleton pattern with proper state management
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, environment: str = "dev", profile: str = "native", 
                 safe_mode: bool = False, dry_run: bool = False, timeout: int = 60):
        # Only initialize once, but allow configuration updates
        if not self._initialized:
            self._do_init(environment, profile, safe_mode, dry_run, timeout)
        else:
            # Update configuration on existing singleton
            self.update_config(environment, profile, safe_mode, dry_run, timeout)
    
    def _do_init(self, environment: str, profile: str, safe_mode: bool, dry_run: bool, timeout: int):
        """Initial setup - only called once"""
        self.environment = environment
        self.profile = profile
        self.safe_mode = safe_mode
        self.dry_run = dry_run
        self.timeout = timeout
        self.boot_id = f"grace-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Multi-OS support
        self.os_type = CURRENT_OS
        self.os_config = current_config
        self.is_windows = IS_WINDOWS
        self.is_macos = IS_MACOS
        self.is_linux = IS_LINUX
        
        # File paths (OS-agnostic)
        self.state_file = Path("grace_state.json")
        self.log_file = Path("logs/orchestrator.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Component tracking with proper assignment
        self.grace_llm = None
        self.cognition_system = None
        self.metrics_engine = None
        self.metrics_collector = None
        
        # System collections
        self.memory_systems = {}
        self.domain_kernels = {}
        self.agentic_systems = {}
        self.healing_systems = {}
        self.learning_systems = {}
        self.governance_systems = {}
        self.code_systems = {}
        self.performance_systems = {}
        self.ingestion_systems = {}
        self.transcendence_systems = {}
        self.task_systems = {}
        self.cli_systems = {}
        
        # Process management
        self.frontend_process = None
        self.launched_processes = []
        self.stage_results = {}
        self._is_running = False
        self._boot_task = None
        
        # Setup logging (only once)
        if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
            file_handler = logging.FileHandler(self.log_file, encoding=self.os_config["encoding"])
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(file_handler)
        
        logger.info(f"Grace Orchestrator initialized - {self.boot_id}")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Imports successful: {IMPORTS_SUCCESSFUL}")
        if import_errors:
            logger.debug(f"Optional components unavailable: {', '.join(import_errors[:5])}{'...' if len(import_errors) > 5 else ''}")
            import_errors.clear()
        
        self._initialized = True
    
    def update_config(self, environment: str, profile: str, safe_mode: bool, dry_run: bool, timeout: int):
        """Update configuration on existing singleton"""
        logger.info(f"Updating orchestrator config: env={environment}, profile={profile}")
        self.environment = environment
        self.profile = profile
        self.safe_mode = safe_mode
        self.dry_run = dry_run
        self.timeout = timeout

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save orchestrator state to file"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _load_state(self) -> Optional[Dict[str, Any]]:
        """Load orchestrator state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
        return None

    async def _start_core_systems(self) -> Dict[str, int]:
        """Start core Grace systems with proper status tracking"""
        logger.info("🚀 Starting core Grace systems...")
        
        counts = {"core": 0, "memory": 0, "kernels": 0, "cognition": 0}
        
        # Start LLM system
        try:
            if get_grace_llm:
                self.grace_llm = get_grace_llm()
                if hasattr(self.grace_llm, 'start'):
                    await self.grace_llm.start()
                counts["core"] += 1
                logger.info("✅ Grace LLM started")
        except Exception as e:
            logger.error(f"❌ Grace LLM failed: {e}")
        
        # Start cognition system
        try:
            if cognition_intent and not isinstance(cognition_intent, StubComponent):
                await cognition_intent.start()
                self.cognition_system = cognition_intent
                counts["cognition"] += 1
                logger.info("✅ Cognition system started")
        except Exception as e:
            logger.error(f"❌ Cognition system failed: {e}")
        
        # Start memory systems
        memory_classes = {
            'fusion': memory_fusion,
            'lightning': lightning_memory,
            'agentic': agentic_memory,
            'persistent': PersistentMemory,
            'code': code_memory,
            'multimodal': multi_modal_memory
        }
        
        for name, memory_class in memory_classes.items():
            try:
                if memory_class and not isinstance(memory_class, StubComponent):
                    if hasattr(memory_class, 'start'):
                        await memory_class.start()
                    elif hasattr(memory_class, 'initialize'):
                        await memory_class.initialize()
                    self.memory_systems[name] = memory_class
                    counts["memory"] += 1
                    logger.info(f"✅ Memory system: {name}")
            except Exception as e:
                logger.error(f"❌ Memory system {name}: {e}")
        
        # Start domain kernels
        kernel_classes = {
            'memory': MemoryKernel,
            'core': CoreKernel,
            'code': CodeKernel,
            'governance': GovernanceKernel,
            'verification': VerificationKernel,
            'intelligence': IntelligenceKernel,
            'infrastructure': InfrastructureKernel,
            'federation': FederationKernel
        }
        
        for name, kernel_class in kernel_classes.items():
            try:
                if kernel_class and not isinstance(kernel_class, StubComponent):
                    kernel_instance = kernel_class()
                    if hasattr(kernel_instance, 'start'):
                        await kernel_instance.start()
                    self.domain_kernels[name] = kernel_instance
                    counts["kernels"] += 1
                    logger.info(f"✅ Domain kernel: {name}")
            except Exception as e:
                logger.error(f"❌ Domain kernel {name}: {e}")
        
        return counts

    async def start(self) -> bool:
        """Start the complete Grace system"""
        logger.info("🚀 Starting Grace Unified Orchestrator")
        
        try:
            # Start core systems
            counts = await self._start_core_systems()
            
            # Save state
            state = {
                "boot_id": self.boot_id,
                "environment": self.environment,
                "started_at": datetime.now().isoformat(),
                "subsystem_counts": counts,
                "platform": self.os_type,
                "imports_successful": IMPORTS_SUCCESSFUL
            }
            self._save_state(state)
            
            self._is_running = True
            logger.info(f"✅ Grace system started - {sum(counts.values())} components")
            return True
            
        except Exception as e:
            logger.error(f"❌ Grace startup failed: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the Grace system"""
        logger.info("🛑 Stopping Grace system...")
        
        try:
            # Stop all processes
            for process in self.launched_processes:
                try:
                    if process.poll() is None:
                        process.terminate()
                        await asyncio.sleep(2)
                        if process.poll() is None:
                            process.kill()
                except Exception as e:
                    logger.error(f"Error stopping process: {e}")
            
            # Clear state
            if self.state_file.exists():
                self.state_file.unlink()
            
            self._is_running = False
            logger.info("✅ Grace system stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping Grace: {e}")
            return False

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        state = self._load_state()
        
        return {
            "boot_id": self.boot_id,
            "environment": self.environment,
            "platform": {
                "os": self.os_type.title(),
                "platform": platform.platform(),
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
            "imports_successful": IMPORTS_SUCCESSFUL,
            "import_errors": import_errors[:10] if import_errors else [],
            "components": {
                "grace_llm": "running" if self.grace_llm else "not_started",
                "cognition_system": "running" if self.cognition_system else "not_started",
                "memory_systems": len(self.memory_systems),
                "domain_kernels": len(self.domain_kernels),
            },
            "is_running": self._is_running,
            "started_at": state.get("started_at") if state else None,
        }

# Initialize singleton orchestrator
orchestrator = GraceUnifiedOrchestrator()

# FastAPI lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifespan with Grace boot/stop"""
    # Startup - boot Grace when uvicorn starts
    logger.info("🚀 FastAPI startup - booting Grace...")
    try:
        await orchestrator.start()
        logger.info("✅ Grace booted successfully")
    except Exception as e:
        logger.error(f"❌ Grace boot failed: {e}")
    
    yield
    
    # Shutdown - stop Grace when uvicorn stops
    logger.info("🛑 FastAPI shutdown - stopping Grace...")
    try:
        await orchestrator.stop()
        logger.info("✅ Grace stopped successfully")
    except Exception as e:
        logger.error(f"❌ Grace stop failed: {e}")

# FastAPI app with lifespan management
app = FastAPI(
    title="Grace AI System - Complete Multi-OS Architecture", 
    version="2.0.0",
    description=f"Grace AI System on {CURRENT_OS.title()}",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (only if they exist)
if chat_router:
    app.include_router(chat_router, prefix="/api")
    logger.info("✅ Chat router included")

if multimodal_router:
    app.include_router(multimodal_router, prefix="/api")
    logger.info("✅ Multimodal router included")

@app.get("/")
async def root():
    return {
        "message": "Grace AI System - Complete Multi-OS Architecture", 
        "status": "active", 
        "version": "2.0.0",
        "platform": CURRENT_OS.title(),
        "imports_successful": IMPORTS_SUCCESSFUL,
        "boot_id": orchestrator.boot_id
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return await orchestrator.get_detailed_status()

@app.post("/api/start")
async def start_system():
    """Start Grace system"""
    try:
        success = await orchestrator.start()
        return {"success": success, "message": "Grace system started" if success else "Failed to start"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop")
async def stop_system():
    """Stop Grace system"""
    try:
        success = await orchestrator.stop()
        return {"success": success, "message": "Grace system stopped" if success else "Failed to stop"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "platform": CURRENT_OS.title(),
        "imports_successful": IMPORTS_SUCCESSFUL,
        "version": "2.0.0"
    }

# CLI entry point - separate from uvicorn serving
def main():
    """CLI entry point - handles boot/status/stop commands"""
    parser = argparse.ArgumentParser(description="Grace Unified Orchestrator CLI")
    parser.add_argument("--stop", action="store_true", help="Stop Grace services")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--boot", action="store_true", help="Boot Grace systems")
    parser.add_argument("--serve", action="store_true", help="Start API server")
    parser.add_argument("--env", default="dev", help="Environment")
    parser.add_argument("--profile", default="native", help="Profile")
    parser.add_argument("--safe-mode", action="store_true", help="Safe mode")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout")
    
    args = parser.parse_args()
    
    # Update singleton configuration
    orchestrator.update_config(args.env, args.profile, args.safe_mode, args.dry_run, args.timeout)
    
    async def run_command():
        if args.stop:
            success = await orchestrator.stop()
            print("✅ Grace stopped" if success else "❌ Stop failed")
            return
        
        if args.status:
            status = await orchestrator.get_detailed_status()
            print(json.dumps(status, indent=2))
            return
        
        if args.boot:
            success = await orchestrator.start()
            print("✅ Grace booted" if success else "❌ Boot failed")
            return
        
        if args.serve:
            # Start uvicorn server (lifespan will handle boot/stop)
            import uvicorn
            print("🌐 Starting Grace API server...")
            print("🔗 Backend: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            
            uvicorn_config = {
                "app": "backend.unified_grace_orchestrator:app",
                "host": "0.0.0.0",
                "port": 8000,
                "log_level": "info"
            }
            
            if IS_WINDOWS:
                uvicorn_config["loop"] = "asyncio"
            
            uvicorn.run(**uvicorn_config)
            return
        
        # Default: show help
        parser.print_help()
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted")
        asyncio.run(orchestrator.stop())
    except Exception as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)

# Signal handlers
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    asyncio.run(orchestrator.stop())
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Only run uvicorn if this file is executed directly (not imported)
if __name__ == "__main__":
    main()

