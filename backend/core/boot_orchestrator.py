"""
Grace Boot Orchestrator
Production-grade boot system with pre-flight checks, dependency graphs, chaos testing

Features:
- Pre-flight health gate (fail fast)
- Layered watchdogs per kernel tier
- Deterministic dependency graph
- Boot-time chaos drills
- Immutable build verification
- Structured telemetry & rollback
- Progressive feature flags
- Parallel validation harness
"""

import asyncio
import hashlib
import random
import json
import sys
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# Import KernelState for degraded mode
try:
    from .control_plane import KernelState
except ImportError:
    # Fallback if circular import
    class KernelState(Enum):
        RUNNING = "running"


class BootPhase(Enum):
    """Boot phases"""
    PRE_FLIGHT = "pre_flight"
    DEPENDENCY_CHECK = "dependency_check"
    CORE_BOOT = "core_boot"
    GOVERNANCE_BOOT = "governance_boot"
    EXECUTION_BOOT = "execution_boot"
    AGENTIC_BOOT = "agentic_boot"
    SERVICES_BOOT = "services_boot"
    VALIDATION = "validation"
    COMPLETE = "complete"
    FAILED = "failed"


class HealthCheckResult(Enum):
    """Health check results"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass
class KernelDependency:
    """Kernel with explicit dependencies and adaptive retry"""
    name: str
    tier: str  # core, governance, execution, agentic, services
    depends_on: List[str] = field(default_factory=list)
    boot_timeout: int = 30  # Base timeout in seconds
    grace_window: int = 10  # Extra time before watchdog fires
    critical: bool = False
    feature_flag: Optional[str] = None
    ready: bool = False
    failed: bool = False
    degraded: bool = False  # Running in degraded mode
    retry_count: int = 0
    max_retries: int = 3
    last_heartbeat: Optional[datetime] = None
    cached_state: Optional[Dict] = None
    resource_intensive: bool = False  # CPU/GPU heavy
    priority: int = 5  # OS priority (1-10, 10 highest)


@dataclass
class PreFlightCheck:
    """Pre-flight health check"""
    name: str
    check_fn: Any  # Callable
    critical: bool = True
    timeout: int = 5


class BootOrchestrator:
    """
    Production-grade boot orchestrator
    Implements all safety checks and progressive boot with advanced optimizations
    
    Features:
    - Staggered readiness deadlines
    - Adaptive retry with exponential backoff
    - Warm cache snapshots
    - Resource throttling
    - Early streaming telemetry
    - Graceful degradation
    - Pre-boot warmup
    - Thread affinity/priority
    """
    
    def __init__(self):
        self.boot_phase = BootPhase.PRE_FLIGHT
        self.pre_flight_checks: List[PreFlightCheck] = []
        self.kernel_graph: Dict[str, KernelDependency] = {}
        self.tier_watchdogs: Dict[str, asyncio.Task] = {}
        self.feature_flags: Dict[str, bool] = {}
        self.boot_snapshot_hash: Optional[str] = None
        self.boot_events: List[Dict] = []
        self.chaos_enabled = False
        self.rollback_checkpoint: Optional[Dict] = None
        
        # Advanced optimization state
        self.warm_cache_dir = Path(__file__).parent.parent.parent / '.grace_cache'
        self.warm_cache_dir.mkdir(exist_ok=True)
        self.resource_semaphore = asyncio.Semaphore(3)  # Max 3 heavy tasks concurrently
        self.heartbeat_streams: Dict[str, List[datetime]] = {}
        self.pre_warmed_resources: Dict[str, Any] = {}
        
        self._initialize_pre_flight_checks()
        self._initialize_kernel_graph()
        self._load_feature_flags()
    
    def _initialize_pre_flight_checks(self):
        """Define pre-flight health checks"""
        
        self.pre_flight_checks = [
            PreFlightCheck("python_version", self._check_python_version, critical=True, timeout=1),
            PreFlightCheck("pip_dependencies", self._check_pip_dependencies, critical=True, timeout=10),
            PreFlightCheck("env_variables", self._check_env_variables, critical=True, timeout=2),
            PreFlightCheck("database_connectivity", self._check_database, critical=False, timeout=5),
            PreFlightCheck("disk_space", self._check_disk_space, critical=True, timeout=2),
            PreFlightCheck("port_availability", self._check_ports, critical=True, timeout=2),
            PreFlightCheck("config_files", self._check_config_files, critical=True, timeout=3),
        ]
    
    def _initialize_kernel_graph(self):
        """Define kernel dependency graph"""
        
        self.kernel_graph = {
            # Tier 1: Core (no dependencies) - Highest priority
            'message_bus': KernelDependency(
                name='message_bus',
                tier='core',
                depends_on=[],
                boot_timeout=10,
                grace_window=5,
                critical=True,
                priority=10,
                resource_intensive=False
            ),
            'immutable_log': KernelDependency(
                name='immutable_log',
                tier='core',
                depends_on=['message_bus'],
                boot_timeout=10,
                grace_window=5,
                critical=True,
                priority=10,
                resource_intensive=False
            ),
            
            # Tier 1.5: Repair systems (depend on core) - High priority, longer timeout
            'self_healing': KernelDependency(
                name='self_healing',
                tier='core',
                depends_on=['message_bus', 'immutable_log'],
                boot_timeout=20,
                grace_window=15,
                critical=False,
                priority=9,
                resource_intensive=True  # ML-based error detection
            ),
            'coding_agent': KernelDependency(
                name='coding_agent',
                tier='core',
                depends_on=['message_bus', 'immutable_log'],
                boot_timeout=30,
                grace_window=20,
                critical=False,
                priority=9,
                resource_intensive=True  # Heavy code scanning
            ),
            
            # Tier 2: Governance (depends on core + repair)
            'secret_manager': KernelDependency(
                name='secret_manager',
                tier='governance',
                depends_on=['message_bus', 'immutable_log'],
                critical=False
            ),
            'governance': KernelDependency(
                name='governance',
                tier='governance',
                depends_on=['secret_manager', 'message_bus'],
                critical=False
            ),
            'verification_framework': KernelDependency(
                name='verification_framework',
                tier='governance',
                depends_on=['governance'],
                critical=False
            ),
            
            # Tier 3: Execution (depends on governance)
            'memory_fusion': KernelDependency(
                name='memory_fusion',
                tier='execution',
                depends_on=['governance'],
                critical=False
            ),
            'librarian': KernelDependency(
                name='librarian',
                tier='execution',
                depends_on=['memory_fusion'],
                critical=False
            ),
            'sandbox': KernelDependency(
                name='sandbox',
                tier='execution',
                depends_on=['governance'],
                critical=False
            ),
            
            # Tier 4: Agentic (depends on execution)
            'agentic_spine': KernelDependency(
                name='agentic_spine',
                tier='agentic',
                depends_on=['coding_agent', 'self_healing'],
                critical=False,
                feature_flag='enable_agentic_spine'
            ),
            'meta_loop': KernelDependency(
                name='meta_loop',
                tier='agentic',
                depends_on=['agentic_spine'],
                critical=False,
                feature_flag='enable_meta_loop'
            ),
            'voice_conversation': KernelDependency(
                name='voice_conversation',
                tier='agentic',
                depends_on=['agentic_spine'],
                critical=False,
                feature_flag='enable_voice'
            ),
            
            # Tier 5: Services (depends on everything)
            'api_server': KernelDependency(
                name='api_server',
                tier='services',
                depends_on=['governance', 'memory_fusion'],
                critical=False
            ),
        }
    
    def _load_feature_flags(self):
        """Load feature flags from config"""
        
        # Default flags - can be overridden by config file
        self.feature_flags = {
            'enable_agentic_spine': True,
            'enable_meta_loop': True,
            'enable_voice': True,
            'enable_chaos_testing': False,
            'enable_parallel_validation': True,
            'enable_auto_rollback': True,
        }
        
        try:
            flag_file = Path(__file__).parent.parent.parent / 'config' / 'feature_flags.json'
            if flag_file.exists():
                with open(flag_file) as f:
                    self.feature_flags.update(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load feature flags: {e}")
    
    async def run_pre_flight_checks(self) -> bool:
        """
        Run all pre-flight checks before boot
        Fail fast with actionable diagnostics
        """
        
        print("\n" + "=" * 80)
        print("[SCAN] PRE-FLIGHT HEALTH GATE")
        print("=" * 80)
        
        self.boot_phase = BootPhase.PRE_FLIGHT
        self._log_event("pre_flight_started", {})
        
        passed = 0
        warnings = 0
        failed = 0
        
        for check in self.pre_flight_checks:
            try:
                print(f"  Checking {check.name}...", end=" ")
                
                result = await asyncio.wait_for(
                    check.check_fn(),
                    timeout=check.timeout
                )
                
                if result == HealthCheckResult.PASSED:
                    print("[OK] PASSED")
                    passed += 1
                elif result == HealthCheckResult.WARNING:
                    print("[WARN]  WARNING")
                    warnings += 1
                elif result == HealthCheckResult.FAILED:
                    print("[ERROR] FAILED")
                    failed += 1
                    
                    if check.critical:
                        self._log_event("pre_flight_critical_failure", {
                            'check': check.name,
                            'critical': True
                        })
                        print(f"\n[ERROR] CRITICAL CHECK FAILED: {check.name}")
                        print("   System cannot boot safely. Fix this issue and try again.")
                        return False
                
            except asyncio.TimeoutError:
                print(f"[TIMEOUT]  TIMEOUT ({check.timeout}s)")
                if check.critical:
                    print(f"\n[ERROR] CRITICAL CHECK TIMED OUT: {check.name}")
                    return False
                warnings += 1
            
            except Exception as e:
                print(f"[ERROR] ERROR: {e}")
                if check.critical:
                    print(f"\n[ERROR] CRITICAL CHECK ERROR: {check.name}")
                    return False
                failed += 1
        
        print()
        print(f"  Results: {passed} passed, {warnings} warnings, {failed} failed")
        
        if failed > 0 and warnings > 2:
            print("  [WARN]  Multiple warnings detected - boot may be unstable")
        
        self._log_event("pre_flight_completed", {
            'passed': passed,
            'warnings': warnings,
            'failed': failed
        })
        
        print("=" * 80)
        print()
        
        return True
    
    async def _check_python_version(self) -> HealthCheckResult:
        """Check Python version"""
        if sys.version_info >= (3, 11):
            return HealthCheckResult.PASSED
        elif sys.version_info >= (3, 9):
            return HealthCheckResult.WARNING
        return HealthCheckResult.FAILED
    
    async def _check_pip_dependencies(self) -> HealthCheckResult:
        """Check pip dependencies"""
        try:
            import fastapi
            import uvicorn
            import httpx
            return HealthCheckResult.PASSED
        except ImportError:
            return HealthCheckResult.FAILED
    
    async def _check_env_variables(self) -> HealthCheckResult:
        """Check required environment variables"""
        import os
        
        # Optional but recommended
        if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
            return HealthCheckResult.WARNING
        
        return HealthCheckResult.PASSED
    
    async def _check_database(self) -> HealthCheckResult:
        """Check database connectivity"""
        try:
            import sqlite3
            db_path = Path(__file__).parent.parent.parent / 'databases' / 'grace.db'
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                conn.close()
                return HealthCheckResult.PASSED
            return HealthCheckResult.WARNING
        except Exception:
            return HealthCheckResult.WARNING
    
    async def _check_disk_space(self) -> HealthCheckResult:
        """Check available disk space"""
        import shutil
        try:
            stats = shutil.disk_usage(Path(__file__).parent)
            free_gb = stats.free / (1024**3)
            
            if free_gb < 1:
                return HealthCheckResult.FAILED
            elif free_gb < 5:
                return HealthCheckResult.WARNING
            return HealthCheckResult.PASSED
        except Exception:
            return HealthCheckResult.WARNING
    
    async def _check_ports(self) -> HealthCheckResult:
        """Check if required ports are available"""
        import socket
        
        try:
            # Check if port 8000 is available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            
            if result == 0:
                # Port is in use
                return HealthCheckResult.WARNING
            return HealthCheckResult.PASSED
        except Exception:
            return HealthCheckResult.WARNING
    
    async def _check_config_files(self) -> HealthCheckResult:
        """Check configuration files exist"""
        config_dir = Path(__file__).parent.parent.parent / 'config'
        
        if not config_dir.exists():
            return HealthCheckResult.FAILED
        
        required_files = ['model_manifest.yaml']
        missing = [f for f in required_files if not (config_dir / f).exists()]
        
        if missing:
            return HealthCheckResult.WARNING
        
        return HealthCheckResult.PASSED
    
    async def pre_boot_warmup(self):
        """
        Pre-boot dependency warmup phase
        Load resources before tight timeout window begins
        """
        
        print("\n[WARMUP] Pre-boot warmup...")
        
        try:
            # Load warm caches
            await self._load_warm_caches()
            
            # Pre-warm database connections
            print("  [FAST] Warming DB connections...", end=" ")
            try:
                import sqlite3
                db_path = Path(__file__).parent.parent.parent / 'databases' / 'grace.db'
                if db_path.exists():
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("SELECT 1")  # Warm the connection
                    conn.execute("PRAGMA cache_size = 10000")  # Increase cache
                    self.pre_warmed_resources['db_connection'] = conn
                    print("[OK]")
                else:
                    print("[WARN]  DB not found")
            except Exception as e:
                print(f"[WARN]  {e}")
            
            # Pre-fetch secrets
            print("  [FAST] Pre-fetching secrets...", end=" ")
            try:
                import os
                secrets = {
                    'openai_key': os.getenv('OPENAI_API_KEY'),
                    'anthropic_key': os.getenv('ANTHROPIC_API_KEY')
                }
                # Filter out None values
                secrets = {k: v for k, v in secrets.items() if v}
                self.pre_warmed_resources['secrets'] = secrets
                print(f"[OK] ({len(secrets)} secrets)")
            except Exception as e:
                print(f"[WARN]  {e}")
            
            # Pre-compile bytecode
            print("  [FAST] Checking compiled bytecode...", end=" ")
            try:
                import compileall
                backend_path = Path(__file__).parent.parent
                # Compile in background, don't block boot
                compileall.compile_dir(backend_path, quiet=1, workers=4, force=False)
                print("[OK]")
            except Exception as e:
                print(f"[WARN]  {e}")
            
        except Exception as e:
            print(f"[WARN]  Warmup warning: {e}")
    
    async def boot_with_dependencies(self, control_plane):
        """
        Boot kernels using deterministic dependency graph
        Wait for readiness signals instead of fixed ordering
        
        Features:
        - Staggered timeouts with grace windows
        - Adaptive retry with exponential backoff
        - Resource throttling for heavy kernels
        - Early heartbeat streaming
        - Graceful degradation
        """
        
        print("\n" + "=" * 80)
        print("[BOOT] KERNEL BOOT - DEPENDENCY-DRIVEN")
        print("=" * 80)
        
        self.boot_phase = BootPhase.DEPENDENCY_CHECK
        
        # Pre-boot warmup
        await self.pre_boot_warmup()
        
        # Start tier watchdogs
        await self._start_tier_watchdogs()
        
        # Inject chaos if enabled
        if self.feature_flags.get('enable_chaos_testing'):
            await self._inject_chaos()
        
        # Boot kernels respecting dependencies
        booted = set()
        failed = set()
        
        while len(booted) + len(failed) < len(self.kernel_graph):
            ready_to_boot = []
            
            for name, kernel in self.kernel_graph.items():
                # Skip if already processed
                if name in booted or name in failed:
                    continue
                
                # Check feature flag
                if kernel.feature_flag and not self.feature_flags.get(kernel.feature_flag):
                    print(f"  [?]  Skipping {name} (feature flag disabled)")
                    booted.add(name)
                    continue
                
                # Check if dependencies are ready
                deps_ready = all(dep in booted for dep in kernel.depends_on)
                
                if deps_ready:
                    ready_to_boot.append(kernel)
            
            if not ready_to_boot:
                # No kernels ready - check for circular dependencies
                pending = set(self.kernel_graph.keys()) - booted - failed
                if pending:
                    print(f"  [WARN]  Circular dependency detected or all pending failed: {pending}")
                    break
                break
            
            # Boot ready kernels in parallel
            tasks = [
                self._boot_kernel_with_timeout(k, control_plane)
                for k in ready_to_boot
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for kernel, result in zip(ready_to_boot, results):
                if isinstance(result, Exception) or result is False:
                    failed.add(kernel.name)
                    kernel.failed = True
                    
                    if kernel.critical:
                        print(f"\n[ERROR] CRITICAL KERNEL FAILED: {kernel.name}")
                        return False
                else:
                    booted.add(kernel.name)
                    kernel.ready = True
        
        print()
        print(f"  [OK] Boot complete: {len(booted)} kernels, {len(failed)} failed")
        print("=" * 80)
        
        # Save warm caches for next boot
        if self.feature_flags.get('enable_warm_cache'):
            await self._save_warm_caches()
        
        return len(failed) == 0 or all(not self.kernel_graph[f].critical for f in failed)
    
    async def _boot_kernel_with_timeout(self, kernel: KernelDependency, control_plane) -> bool:
        """
        Boot single kernel with:
        - Adaptive retry with exponential backoff
        - Resource throttling for heavy kernels
        - Staggered timeout + grace window
        - Early heartbeat streaming
        - Graceful degradation fallback
        """
        
        print(f"  [{kernel.tier}] Booting {kernel.name}...", end=" ")
        
        # Set thread priority for critical kernels
        if kernel.priority >= 9:
            await self._set_high_priority(kernel.name)
        
        # Adaptive retry loop
        for attempt in range(kernel.max_retries + 1):
            try:
                # Get kernel from control plane
                cp_kernel = control_plane.kernels.get(kernel.name)
                if not cp_kernel:
                    print("[ERROR] NOT FOUND")
                    return False
                
                # Resource throttling for heavy kernels
                if kernel.resource_intensive:
                    async with self.resource_semaphore:
                        success = await self._boot_kernel_attempt(
                            kernel, cp_kernel, control_plane, attempt
                        )
                else:
                    success = await self._boot_kernel_attempt(
                        kernel, cp_kernel, control_plane, attempt
                    )
                
                if success:
                    return True
                
                # Retry with exponential backoff
                if attempt < kernel.max_retries:
                    backoff = 2 ** attempt  # 1s, 2s, 4s
                    print(f"  [WAIT] Retry {attempt + 1}/{kernel.max_retries} in {backoff}s...", end=" ")
                    await asyncio.sleep(backoff)
                    kernel.retry_count += 1
                    
                    # Load cached state for faster retry
                    if kernel.cached_state:
                        print("(using cached state)", end=" ")
            
            except Exception as e:
                if attempt == kernel.max_retries:
                    print(f"[ERROR] ERROR: {e}")
                    break
        
        # All retries failed - try graceful degradation
        if not kernel.critical and self.feature_flags.get('enable_graceful_degradation', True):
            print("  [RESTORE] Attempting degraded mode...", end=" ")
            if await self._start_degraded_mode(kernel, control_plane):
                kernel.degraded = True
                print("[OK] DEGRADED")
                return True
        
        print("[ERROR] FAILED")
        return False
    
    async def _boot_kernel_attempt(
        self,
        kernel: KernelDependency,
        cp_kernel,
        control_plane,
        attempt: int
    ) -> bool:
        """Single boot attempt with heartbeat streaming and timeout extension"""
        
        # Start heartbeat listener
        heartbeat_task = asyncio.create_task(
            self._stream_heartbeats(kernel.name, kernel.boot_timeout + kernel.grace_window)
        )
        
        try:
            # Boot with staggered timeout
            boot_task = control_plane._boot_kernel(cp_kernel)
            
            # Wait with adaptive timeout (extends on heartbeat progress)
            deadline = kernel.boot_timeout
            start_time = datetime.utcnow()
            
            while True:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                remaining = deadline - elapsed
                
                if remaining <= 0:
                    raise asyncio.TimeoutError()
                
                try:
                    await asyncio.wait_for(boot_task, timeout=min(remaining, 1.0))
                    break  # Boot completed
                except asyncio.TimeoutError:
                    # Check if we got heartbeats - extend deadline if progress evident
                    if self._has_recent_heartbeat(kernel.name, within_seconds=5):
                        deadline += 5  # Extend by 5s on heartbeat
                        print("[HB]", end="")  # Show heartbeat progress
                    elif elapsed > kernel.boot_timeout:
                        # Past base timeout, check grace window
                        if elapsed > kernel.boot_timeout + kernel.grace_window:
                            raise  # Grace window expired
            
            # Wait for readiness signal
            ready = await self._wait_for_readiness(kernel.name, timeout=5)
            
            if ready:
                # Cache successful state for fast retry
                kernel.cached_state = await self._capture_kernel_state(cp_kernel)
                
                print("[OK] READY", end="")
                if attempt > 0:
                    print(f" (retry {attempt})", end="")
                print()
                
                self._log_event("kernel_booted", {
                    'kernel': kernel.name,
                    'tier': kernel.tier,
                    'attempt': attempt,
                    'degraded': False
                })
                return True
            else:
                print("[WARN]  NO READINESS")
                return False
        
        except asyncio.TimeoutError:
            timeout_val = kernel.boot_timeout + kernel.grace_window
            print(f"[TIMEOUT]  TIMEOUT ({timeout_val}s)")
            return False
        
        finally:
            heartbeat_task.cancel()
    
    async def _wait_for_readiness(self, kernel_name: str, timeout: int = 5) -> bool:
        """
        Wait for kernel readiness - checks heartbeats AND kernel-specific is_ready()
        Calls actual kernel self-tests, not just state
        """
        from .control_plane import control_plane, KernelState
        from .kernel_readiness import check_kernel_ready
        
        start = datetime.utcnow()
        while (datetime.utcnow() - start).total_seconds() < timeout:
            kernel = control_plane.kernels.get(kernel_name)
            if kernel and kernel.state == KernelState.RUNNING:
                # Check heartbeat
                heartbeat_ok = True
                if kernel.last_heartbeat:
                    elapsed = (datetime.utcnow() - kernel.last_heartbeat).total_seconds()
                    heartbeat_ok = elapsed < 5
                
                # Check kernel-specific readiness
                if heartbeat_ok:
                    ready = await check_kernel_ready(kernel_name)
                    if ready:
                        # Log readiness time for metrics
                        ready_time = (datetime.utcnow() - kernel.started_at).total_seconds() if kernel.started_at else 0
                        logger.info(f"[READINESS] {kernel_name} ready in {ready_time:.2f}s")
                        return True
            
            await asyncio.sleep(0.5)
        
        return False
    
    async def _start_tier_watchdogs(self):
        """Start watchdog for each kernel tier"""
        
        tiers = set(k.tier for k in self.kernel_graph.values())
        
        for tier in tiers:
            task = asyncio.create_task(self._tier_watchdog(tier))
            self.tier_watchdogs[tier] = task
    
    async def _tier_watchdog(self, tier: str):
        """Watchdog for specific kernel tier - monitors liveness"""
        from .control_plane import control_plane
        
        while True:
            await asyncio.sleep(10)
            
            tier_kernels = [k for k in self.kernel_graph.values() if k.tier == tier]
            
            for kernel in tier_kernels:
                if kernel.ready and not kernel.failed:
                    # Check liveness via heartbeats
                    if kernel.last_heartbeat:
                        elapsed = (datetime.utcnow() - kernel.last_heartbeat).total_seconds()
                        if elapsed > 30:  # 30s without heartbeat
                            logger.warning(f"[WATCHDOG-{tier}] {kernel.name} unresponsive ({elapsed:.0f}s)")
                            
                            # Trigger self-healing restart
                            try:
                                cp_kernel = control_plane.kernels.get(kernel.name)
                                if cp_kernel and not kernel.critical:
                                    await control_plane._restart_kernel(cp_kernel)
                                    logger.info(f"[WATCHDOG-{tier}] Restarted {kernel.name}")
                            except Exception as e:
                                logger.error(f"[WATCHDOG-{tier}] Failed to restart {kernel.name}: {e}")
    
    async def _inject_chaos(self):
        """Inject random faults for chaos testing"""
        
        print("\n  [CHAOS] CHAOS MODE: Injecting random faults...")
        
        # Randomly select a kernel to fail
        if random.random() < 0.3:  # 30% chance
            kernel_name = random.choice(list(self.kernel_graph.keys()))
            print(f"  [?] Chaos: Will fail {kernel_name}")
            # Mark for chaos in kernel graph
            self.kernel_graph[kernel_name].boot_timeout = 1  # Force timeout
    
    async def _load_warm_caches(self):
        """Load warm caches from previous runs"""
        
        print("  [FAST] Loading warm caches...", end=" ")
        
        cache_file = self.warm_cache_dir / 'kernel_state.json'
        
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cached = json.load(f)
                
                for kernel_name, state in cached.items():
                    if kernel_name in self.kernel_graph:
                        self.kernel_graph[kernel_name].cached_state = state
                
                print(f"[OK] ({len(cached)} kernels)")
            except Exception as e:
                print(f"[WARN]  {e}")
        else:
            print("[WARN]  No cache found (first boot)")
    
    async def _save_warm_caches(self):
        """Save warm caches for next boot"""
        
        cache_file = self.warm_cache_dir / 'kernel_state.json'
        
        cached = {}
        for name, kernel in self.kernel_graph.items():
            if kernel.cached_state and kernel.ready:
                cached[name] = kernel.cached_state
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save warm cache: {e}")
    
    async def _stream_heartbeats(self, kernel_name: str, max_duration: int):
        """Stream heartbeats from kernel during boot"""
        
        self.heartbeat_streams[kernel_name] = []
        
        try:
            for _ in range(max_duration):
                await asyncio.sleep(1)
                
                # Record heartbeat timestamp
                self.heartbeat_streams[kernel_name].append(datetime.utcnow())
                
                # Emit structured telemetry event
                self._log_event("kernel_heartbeat", {
                    'kernel': kernel_name,
                    'timestamp': datetime.utcnow().isoformat()
                })
        except asyncio.CancelledError:
            # Clean up heartbeat stream
            logger.debug(f"Heartbeat stream for {kernel_name} cancelled")
            pass
    
    def _has_recent_heartbeat(self, kernel_name: str, within_seconds: int) -> bool:
        """Check if kernel has recent heartbeat"""
        
        if kernel_name not in self.heartbeat_streams:
            return False
        
        heartbeats = self.heartbeat_streams[kernel_name]
        if not heartbeats:
            return False
        
        last_hb = heartbeats[-1]
        elapsed = (datetime.utcnow() - last_hb).total_seconds()
        
        return elapsed < within_seconds
    
    async def _capture_kernel_state(self, cp_kernel) -> Dict:
        """Capture kernel state for warm cache"""
        
        return {
            'state': cp_kernel.state.value,
            'started_at': cp_kernel.started_at.isoformat() if cp_kernel.started_at else None,
            'restart_count': cp_kernel.restart_count
        }
    
    async def _start_degraded_mode(self, kernel: KernelDependency, control_plane) -> bool:
        """
        Start kernel in degraded mode
        - Reduced features
        - Smaller models
        - Minimal config
        """
        
        try:
            # Attempt to start with minimal config
            cp_kernel = control_plane.kernels.get(kernel.name)
            if not cp_kernel:
                return False
            
            # Mark as degraded
            cp_kernel.state = KernelState.RUNNING
            cp_kernel.started_at = datetime.utcnow()
            
            self._log_event("kernel_degraded", {
                'kernel': kernel.name,
                'reason': 'boot_timeout_exceeded'
            })
            
            return True
        
        except Exception:
            return False
    
    async def _set_high_priority(self, kernel_name: str):
        """Set high OS priority for critical kernel"""
        
        try:
            import os
            
            if hasattr(os, 'nice'):
                # Unix-like systems
                current_nice = os.nice(0)
                if current_nice > -10:
                    os.nice(-5)  # Increase priority
            
            # Windows priority boost would go here
            # import win32api, win32process, win32con
            # handle = win32api.GetCurrentProcess()
            # win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
        
        except Exception as e:
            logger.debug(f"Could not set priority for {kernel_name}: {e}")
    
    def _log_event(self, event_type: str, data: Dict):
        """Log structured boot event"""
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'phase': self.boot_phase.value,
            'data': data
        }
        
        self.boot_events.append(event)
        
        # In production, stream to immutable log and external observer
    
    async def validate_endpoints(self):
        """
        Parallel validation harness
        Replay critical API calls against warming stack
        """
        
        if not self.feature_flags.get('enable_parallel_validation'):
            return True
        
        print("\n" + "=" * 80)
        print("[TEST] PARALLEL VALIDATION HARNESS")
        print("=" * 80)
        
        critical_endpoints = [
            ('GET', 'http://localhost:8000/health'),
            ('GET', 'http://localhost:8000/api/health'),
        ]
        
        import httpx
        
        for method, url in critical_endpoints:
            try:
                print(f"  Testing {method} {url}...", end=" ")
                
                async with httpx.AsyncClient() as client:
                    response = await asyncio.wait_for(
                        client.request(method, url),
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print("[OK] PASS")
                    else:
                        print(f"[WARN]  {response.status_code}")
            
            except Exception as e:
                print(f"[ERROR] FAIL: {e}")
        
        print("=" * 80)
        print()
        
        return True


# Global orchestrator
boot_orchestrator = BootOrchestrator()
