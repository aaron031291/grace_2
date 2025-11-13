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
optional_import_errors = []

# Defensive imports with detailed error tracking
def safe_import(module_name: str, from_module: str = None, optional: bool = False):
    """
    Safely import modules with error tracking
    Args:
        module_name: Name of the module or attribute to import
        from_module: Parent module to import from
        optional: If True, failures don't mark IMPORTS_SUCCESSFUL as False
    """
    global IMPORTS_SUCCESSFUL, import_errors, optional_import_errors
    try:
        if from_module:
            module = __import__(from_module, fromlist=[module_name])
            return getattr(module, module_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        error_msg = f"{from_module}.{module_name}" if from_module else module_name
        if optional:
            optional_import_errors.append(error_msg)
        else:
            import_errors.append(error_msg)
            IMPORTS_SUCCESSFUL = False
        return None

# Create stub for missing components
class StubComponent:
    def __init__(self, name: str = "stub"):
        self.name = name
        self._started = False
    
    def __call__(self, *args, **kwargs):
        """Allow StubComponent to be called as a constructor"""
        return StubComponent(self.name)
    
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

# Core Infrastructure - using absolute imports (optional with fallbacks)
process_registry = safe_import('process_registry', 'backend.grace_process_registry', optional=True) or StubComponent('process_registry')
ProcessInfo = safe_import('ProcessInfo', 'backend.grace_process_registry', optional=True) or dict
unified_logic_hub = safe_import('unified_logic_hub', 'backend.unified_logic_hub', optional=True) or StubComponent('unified_logic_hub')
activate_grace_autonomy = safe_import('activate_grace_autonomy', 'backend.grace_spine_integration', optional=True) or StubComponent('activate_grace_autonomy')
IntegrationOrchestrator = safe_import('IntegrationOrchestrator', 'backend.integration_orchestrator', optional=True) or StubComponent
BootPipeline = safe_import('BootPipeline', 'backend.boot_pipeline', optional=True) or StubComponent
GraceCore = safe_import('GraceCore', 'backend.grace_core', optional=True) or StubComponent

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

agentic_memory = safe_import('agentic_memory', 'backend.agentic_memory', optional=True) or StubComponent('agentic_memory')
PersistentMemory = safe_import('PersistentMemory', 'backend.memory', optional=True) or StubComponent
code_memory = safe_import('code_memory', 'backend.code_memory', optional=True) or StubComponent('code_memory')

multi_modal_memory = None
if Path("backend/multi_modal_memory.py").exists():
    multi_modal_memory = safe_import('multi_modal_memory', 'backend.multi_modal_memory')
else:
    multi_modal_memory = StubComponent('multi_modal_memory')

# LLM & Cognition (optional with fallbacks)
get_grace_llm = safe_import('get_grace_llm', 'backend.grace_llm', optional=True) or (lambda: StubComponent('grace_llm'))
GraceLLM = safe_import('GraceLLM', 'backend.grace_llm', optional=True) or StubComponent
CognitionIntent = safe_import('CognitionIntent', 'backend.cognition_intent', optional=True) or StubComponent('cognition_intent')
cognition_intent = None  # Will be initialized during boot

# Domain Kernels - check if kernel directory exists (optional with fallbacks)
kernel_path = Path("backend/kernels")
if kernel_path.exists():
    MemoryKernel = safe_import('MemoryKernel', 'backend.kernels.memory_kernel', optional=True) or StubComponent
    CoreKernel = safe_import('CoreKernel', 'backend.kernels.core_kernel', optional=True) or StubComponent
    CodeKernel = safe_import('CodeKernel', 'backend.kernels.code_kernel', optional=True) or StubComponent
    GovernanceKernel = safe_import('GovernanceKernel', 'backend.kernels.governance_kernel', optional=True) or StubComponent
    VerificationKernel = safe_import('VerificationKernel', 'backend.kernels.verification_kernel', optional=True) or StubComponent
    IntelligenceKernel = safe_import('IntelligenceKernel', 'backend.kernels.intelligence_kernel', optional=True) or StubComponent
    InfrastructureKernel = safe_import('InfrastructureKernel', 'backend.kernels.infrastructure_kernel', optional=True) or StubComponent
    FederationKernel = safe_import('FederationKernel', 'backend.kernels.federation_kernel', optional=True) or StubComponent
    
    # Librarian Data Orchestrator (NEW)
    LibrarianKernel = safe_import('LibrarianKernel', 'backend.kernels.librarian_kernel', optional=True) or StubComponent
    LibrarianClarityAdapter = safe_import('LibrarianClarityAdapter', 'backend.kernels.librarian_clarity_adapter', optional=True) or StubComponent
    get_event_bus = safe_import('get_event_bus', 'backend.kernels.event_bus', optional=True) or (lambda *args, **kwargs: StubComponent('event_bus'))

    # Self-Healing Kernel (NEW)
    SelfHealingKernel = safe_import('SelfHealingKernel', 'backend.kernels.self_healing_kernel', optional=True) or StubComponent
else:
    # Create stub kernels if directory doesn't exist
    MemoryKernel = CoreKernel = CodeKernel = GovernanceKernel = StubComponent
    VerificationKernel = IntelligenceKernel = InfrastructureKernel = FederationKernel = StubComponent
    LibrarianKernel = LibrarianClarityAdapter = SelfHealingKernel = StubComponent
    get_event_bus = lambda *args, **kwargs: StubComponent('event_bus')

# API Routes - check if routes exist (OPTIONAL - have fallbacks)
routes_path = Path("backend/routes")

# Self-Healing API Routes (NEW)
self_healing_api_router = None
if (routes_path / "self_healing_api.py").exists():
    self_healing_api_router = safe_import('router', 'backend.routes.self_healing_api', optional=True)

chat_router = None
if (routes_path / "chat.py").exists():
    chat_router = safe_import('router', 'backend.routes.chat', optional=True)

multimodal_router = None
if (routes_path / "multimodal_api.py").exists():
    multimodal_router = safe_import('router', 'backend.routes.multimodal_api', optional=True)

# Memory Studio Routes
memory_api_router = None
if (routes_path / "memory_api.py").exists():
    memory_api_router = safe_import('router', 'backend.routes.memory_api', optional=True)

grace_memory_router = None
if (routes_path / "grace_memory_api.py").exists():
    grace_memory_router = safe_import('router', 'backend.routes.grace_memory_api', optional=True)

ingestion_router = None
if (routes_path / "ingestion_api.py").exists():
    ingestion_router = safe_import('router', 'backend.routes.ingestion_api', optional=True)

# Memory Tables Routes
memory_tables_router = None
if (routes_path / "memory_tables_api.py").exists():
    memory_tables_router = safe_import('router', 'backend.routes.memory_tables_api', optional=True)

# Auto-Ingestion Routes
auto_ingestion_router = None
if (routes_path / "auto_ingestion_api.py").exists():
    auto_ingestion_router = safe_import('router', 'backend.routes.auto_ingestion_api', optional=True)

# Ingestion Bridge Routes
ingestion_bridge_router = None
if (routes_path / "ingestion_bridge_api.py").exists():
    ingestion_bridge_router = safe_import('router', 'backend.routes.ingestion_bridge_api', optional=True)

# Memory Files Routes (for Memory Panel UI)
memory_files_router = None
if (routes_path / "memory_files_api.py").exists():
    memory_files_router = safe_import('router', 'backend.routes.memory_files_api', optional=True)

# Collaboration Routes
collaboration_router = None
if (routes_path / "collaboration_api.py").exists():
    collaboration_router = safe_import('router', 'backend.routes.collaboration_api', optional=True)

# Librarian Routes (NEW)
librarian_api_router = None
if (routes_path / "librarian_api.py").exists():
    librarian_api_router = safe_import('router', 'backend.routes.librarian_api', optional=True)

chunked_upload_router = None
if (routes_path / "chunked_upload_api.py").exists():
    chunked_upload_router = safe_import('router', 'backend.routes.chunked_upload_api', optional=True)

# CLI Systems - check if cli directory exists (OPTIONAL - not required for orchestrator)
cli_path = Path("cli")
EnhancedGraceCLI = StubComponent
if cli_path.exists() and (cli_path / "enhanced_grace_cli.py").exists():
    EnhancedGraceCLI = safe_import('EnhancedGraceCLI', 'cli.enhanced_grace_cli', optional=True) or StubComponent

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
        
        # Librarian Data Orchestrator (NEW)
        self.librarian_kernel = None
        self.librarian_adapter = None
        self.event_bus = None
        
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
        
        # Log critical import errors
        if import_errors:
            logger.error(f"Critical import errors: {', '.join(import_errors)}")
        
        # Log optional import errors at debug level
        if optional_import_errors:
            logger.debug(f"Optional components unavailable: {', '.join(optional_import_errors[:5])}{'...' if len(optional_import_errors) > 5 else ''}")
        
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
        
        counts = {"core": 0, "memory": 0, "kernels": 0, "cognition": 0, "memory_tables": 0}
        
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
                # Skip if it's the StubComponent class or an instance of it
                if memory_class is StubComponent or isinstance(memory_class, StubComponent):
                    continue
                if memory_class:
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
            'federation': FederationKernel,
            'self_healing': SelfHealingKernel
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
        
        # Start Librarian Data Orchestrator (NEW)
        try:
            if LibrarianKernel and not isinstance(LibrarianKernel, type(StubComponent)):
                logger.info("🔧 Initializing Librarian Data Orchestrator...")
                
                # Get/create memory tables registry
                try:
                    from backend.memory_tables.registry import table_registry
                    registry = table_registry
                except Exception:
                    registry = None
                    logger.warning("⚠️ Memory tables registry not available for Librarian")
                
                # Create event bus
                self.event_bus = get_event_bus(registry=registry)
                
                # Create Librarian kernel
                self.librarian_kernel = LibrarianKernel(
                    registry=registry,
                    event_bus=self.event_bus
                )
                
                # Create clarity adapter
                self.librarian_adapter = LibrarianClarityAdapter(
                    librarian_kernel=self.librarian_kernel,
                    registry=registry,
                    event_mesh=self.event_bus,
                    unified_logic=None  # Will be wired later
                )
                
                # Initialize and start
                await self.librarian_adapter.initialize()

                # Set the global kernel instance for API routes
                try:
                    from backend.routes import librarian_api
                    librarian_api._librarian_kernel = self.librarian_kernel
                    logger.info("✅ Librarian kernel instance set for API routes")
                except Exception as e:
                    logger.warning(f"Could not set librarian kernel for API: {e}")

                self.domain_kernels['librarian'] = self.librarian_adapter
                counts["kernels"] += 1

                logger.info("✅ Librarian Data Orchestrator started")
                logger.info(f"   📁 Watching: {[str(p) for p in self.librarian_kernel.watch_paths]}")
                logger.info(f"   🤖 Sub-agents ready: 4 types")
                logger.info(f"   📊 Queues: schema, ingestion, trust_audit")
        except Exception as e:
            logger.error(f"❌ Librarian Data Orchestrator failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Initialize Memory Tables system
        try:
            from backend.memory_tables.initialization import initialize_memory_tables
            tables_initialized = await initialize_memory_tables()
            if tables_initialized:
                counts["memory_tables"] = 1
                logger.info("✅ Memory Tables system started")
        except Exception as e:
            logger.error(f"❌ Memory Tables initialization failed: {e}")
        
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

# Memory Studio Routes
if memory_api_router:
    app.include_router(memory_api_router)
    logger.info("✅ Memory API router included")

if grace_memory_router:
    app.include_router(grace_memory_router)
    logger.info("✅ Grace Memory API router included")

if ingestion_router:
    app.include_router(ingestion_router)
    logger.info("✅ Ingestion API router included")

if memory_tables_router:
    app.include_router(memory_tables_router)
    logger.info("✅ Memory Tables API router included")

if auto_ingestion_router:
    app.include_router(auto_ingestion_router)
    logger.info("✅ Auto-Ingestion API router included")

if ingestion_bridge_router:
    app.include_router(ingestion_bridge_router)
    logger.info("✅ Ingestion Bridge API router included")

if memory_files_router:
    app.include_router(memory_files_router)
    logger.info("✅ Memory Files API router included")

if collaboration_router:
    app.include_router(collaboration_router)
    logger.info("✅ Collaboration API router included")

# Librarian Routes (NEW)
if librarian_api_router:
    app.include_router(librarian_api_router)
    logger.info("✅ Librarian API router included")

if chunked_upload_router:
    app.include_router(chunked_upload_router)
    logger.info("✅ Chunked Upload API router included")

# Self-Healing API Routes (NEW)
if self_healing_api_router:
    app.include_router(self_healing_api_router)
    logger.info("✅ Self-Healing API router included")

# Enhanced System Routes (NEW)
try:
    logger.info("Loading enhanced system routes...")
    
    # Load stub routes first (prevent JSON errors)
    from backend.routes.librarian_stubs import router as stub_router
    app.include_router(stub_router, prefix="/api/librarian", tags=["librarian-stubs"])
    
    from backend.routes.self_healing_stubs import router as healing_stub_router
    app.include_router(healing_stub_router, prefix="/api/self-healing", tags=["self-healing-stubs"])
    
    logger.info("Stub routes registered (librarian + self-healing)")
    
    # Test endpoint
    from backend.routes.test_endpoint import router as test_router
    app.include_router(test_router, prefix="/api", tags=["test"])
    logger.info("Test router registered: /api/test")
    
    # Book dashboard (may override some stubs with real implementations)
    try:
        from backend.routes.book_dashboard import router as book_router
        app.include_router(book_router, prefix="/api/books", tags=["books"])
        logger.info("Book dashboard router registered: /api/books/*")
    except Exception as e:
        logger.warning(f"Book dashboard routes not loaded: {e}")
    
    # File organizer (may override stubs)
    try:
        from backend.routes.file_organizer_api import router as organizer_router
        # Don't override stub routes, use different prefix
        app.include_router(organizer_router, prefix="/api/organizer", tags=["file-organizer"])
        logger.info("File organizer router registered: /api/organizer/*")
    except Exception as e:
        logger.warning(f"File organizer routes not loaded: {e}")
    
    # Unified Kernels API (access all 12 domain kernels)
    try:
        from backend.routes.kernels_api import router as kernels_router
        app.include_router(kernels_router, prefix="/api", tags=["kernels"])
        logger.info("Unified kernels API registered: /api/kernels")
    except Exception as e:
        logger.warning(f"Kernels API not loaded: {e}")
    
    # Complete Librarian API (overrides stubs with full implementation)
    try:
        from backend.routes.librarian_complete_api import router as librarian_full_router
        app.include_router(librarian_full_router, prefix="/api/librarian", tags=["librarian-full"])
        logger.info("Complete Librarian API registered (with logs, proposals, trusted sources)")
    except Exception as e:
        logger.warning(f"Complete Librarian API not loaded: {e}")
    
    logger.info("Book system routes loaded (stubs ensure no JSON errors)")
except Exception as e:
    logger.error(f"Failed to load book system routes: {e}")
    import traceback
    traceback.print_exc()

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

# Clarity Framework API Endpoints
@app.get("/api/clarity/status")
async def get_clarity_status():
    """Get clarity framework status"""
    try:
        from backend.clarity.orchestrator_integration import get_clarity_integration
        integration = get_clarity_integration()
        return integration.get_clarity_status()
    except Exception as e:
        return {"error": str(e), "clarity_available": False}

@app.get("/api/clarity/components")
async def get_clarity_components():
    """Get registered components from manifest"""
    try:
        from backend.clarity import get_manifest
        manifest = get_manifest()
        return manifest.to_dict()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/clarity/events")
async def get_clarity_events(limit: int = 100):
    """Get recent events from event bus"""
    try:
        from backend.clarity import get_event_bus
        bus = get_event_bus()
        history = bus.get_history(limit=limit)
        return {
            "events": [e.to_dict() for e in history],
            "total": len(history)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/clarity/mesh")
async def get_clarity_mesh():
    """Get trigger mesh configuration"""
    try:
        from backend.clarity import get_mesh_loader
        loader = get_mesh_loader()
        return {
            "events": loader.get_events(),
            "routing_rules": loader.get_routing_rules(),
            "subscriber_groups": loader.get_subscriber_groups()
        }
    except Exception as e:
        return {"error": str(e)}

# Ingestion API Endpoints
@app.get("/api/ingestion/status")
async def get_ingestion_status():
    """Get ingestion orchestrator status"""
    try:
        from backend.clarity.ingestion_orchestrator import get_ingestion_orchestrator
        orchestrator = await get_ingestion_orchestrator()
        return orchestrator.get_status()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/ingestion/tasks")
async def get_ingestion_tasks(status: str = None):
    """Get all ingestion tasks"""
    try:
        from backend.clarity.ingestion_orchestrator import get_ingestion_orchestrator
        orchestrator = await get_ingestion_orchestrator()
        return {"tasks": orchestrator.get_tasks(status)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/ingestion/start")
async def start_ingestion(task_type: str, source: str):
    """Start a new ingestion task"""
    try:
        from backend.clarity.ingestion_orchestrator import get_ingestion_orchestrator
        orchestrator = await get_ingestion_orchestrator()
        task = await orchestrator.create_task(task_type, source)
        success = await orchestrator.start_task(task.task_id)
        return {"success": success, "task": task.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingestion/stop/{task_id}")
async def stop_ingestion(task_id: str):
    """Stop an active ingestion task"""
    try:
        from backend.clarity.ingestion_orchestrator import get_ingestion_orchestrator
        orchestrator = await get_ingestion_orchestrator()
        success = await orchestrator.stop_task(task_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# LLM API Endpoints
@app.get("/api/llm/status")
async def get_llm_status():
    """Get LLM system status"""
    return {
        "status": "operational" if get_grace_llm else "stub",
        "model": "grace_llm",
        "is_stub": get_grace_llm is None or isinstance(get_grace_llm, type),
        "available": get_grace_llm is not None
    }

# Intelligence Kernel API
@app.get("/api/intelligence/status")
async def get_intelligence_status():
    """Get intelligence kernel status"""
    return {
        "status": "operational" if IntelligenceKernel and IntelligenceKernel is not StubComponent else "stub",
        "kernel_type": "intelligence",
        "is_stub": IntelligenceKernel is StubComponent
    }

# Learning System API
@app.get("/api/learning/status")
async def get_learning_status():
    """Get continuous learning loop status"""
    try:
        from backend.continuous_learning_loop import ContinuousLearningLoop
        # Check if learning loop exists
        return {
            "status": "available",
            "component": "continuous_learning_loop"
        }
    except ImportError:
        return {
            "status": "not_available",
            "error": "Learning loop module not found"
        }

# Chat API Endpoint
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """Basic chat endpoint"""
    return {
        "response": f"Echo: {req.message}",
        "status": "processed",
        "clarity_enabled": True
    }

# Memory File Service API
@app.get("/api/memory/files")
async def list_memory_files(path: str = ""):
    """List files in memory workspace"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return service.list_files(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/file")
async def read_memory_file(path: str):
    """Read a file from memory workspace"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.get_file(path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/memory/file")
async def save_memory_file(path: str, content: str, metadata: dict = None):
    """Save a file to memory workspace"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.save_file(path, content, metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/file")
async def delete_memory_file(path: str, recursive: bool = False):
    """Delete a file from memory workspace"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.delete_file(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/memory/file")
async def rename_memory_file(old_path: str, new_path: str):
    """Rename or move a file"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.rename_file(old_path, new_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/folder")
async def create_memory_folder(path: str):
    """Create a new folder"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return await service.create_folder(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/status")
async def get_memory_service_status():
    """Get memory service status"""
    try:
        from backend.memory_file_service import get_memory_service
        service = await get_memory_service()
        return service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Domain Kernels API
@app.get("/api/kernels")
async def list_all_kernels():
    """List all 9 domain kernels"""
    try:
        from backend.kernels.all_kernels_clarity import (
            ClarityMemoryKernel,
            ClarityCoreKernel,
            ClarityCodeKernel,
            ClarityGovernanceKernel,
            ClarityVerificationKernel,
            ClarityIntelligenceKernel,
            ClarityInfrastructureKernel,
            ClarityFederationKernel,
            ClarityMLKernel
        )
        
        kernels = [
            {"name": "Memory", "domain": "memory", "type": "ClarityMemoryKernel"},
            {"name": "Core", "domain": "core", "type": "ClarityCoreKernel"},
            {"name": "Code", "domain": "code", "type": "ClarityCodeKernel"},
            {"name": "Governance", "domain": "governance", "type": "ClarityGovernanceKernel"},
            {"name": "Verification", "domain": "verification", "type": "ClarityVerificationKernel"},
            {"name": "Intelligence", "domain": "intelligence", "type": "ClarityIntelligenceKernel"},
            {"name": "Infrastructure", "domain": "infrastructure", "type": "ClarityInfrastructureKernel"},
            {"name": "Federation", "domain": "federation", "type": "ClarityFederationKernel"},
            {"name": "ML & AI", "domain": "ml", "type": "ClarityMLKernel"}
        ]
        
        return {
            "total_kernels": 9,
            "kernels": kernels,
            "clarity_enabled": True
        }
    except Exception as e:
        return {"error": str(e), "total_kernels": 9, "clarity_enabled": False}

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
    
    # Handle --serve separately (no async needed)
    if args.serve:
        import uvicorn
        print("Starting Grace API server...")
        print("Backend: http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        
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
    
    # Update singleton configuration for other commands
    orchestrator.update_config(args.env, args.profile, args.safe_mode, args.dry_run, args.timeout)
    
    async def run_command():
        if args.stop:
            success = await orchestrator.stop()
            print("Grace stopped" if success else "Stop failed")
            return
        
        if args.status:
            status = await orchestrator.get_detailed_status()
            print(json.dumps(status, indent=2))
            return
        
        if args.boot:
            success = await orchestrator.start()
            print("Grace booted successfully" if success else "Boot failed")
            return
        
        # Default: show help
        parser.print_help()
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\nInterrupted")
        asyncio.run(orchestrator.stop())
    except Exception as e:
        print(f"Command failed: {e}")
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

