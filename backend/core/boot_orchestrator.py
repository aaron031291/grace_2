"""
Boot Orchestrator
=================

Coordinates pre-boot warming, readiness validation, tier watchdogs, and
heartbeat telemetry for Grace's core kernels.
"""

from __future__ import annotations

import asyncio
import compileall
import logging
import os
import sqlite3
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Deque, List, Optional

from .control_plane import control_plane, Kernel, KernelState

logger = logging.getLogger(__name__)


class BootOrchestrator:
    """Production-grade boot orchestration helpers."""

    def __init__(self) -> None:
        self.pre_warmed_resources: Dict[str, object] = {}
        self.heartbeat_streams: Dict[str, Deque[datetime]] = defaultdict(lambda: deque(maxlen=120))
        self._watchdog_tasks: Dict[str, asyncio.Task] = {}
        self._monitor_tasks: Dict[str, asyncio.Task] = {}
        self._watchdogs_running: bool = False

    # ------------------------------------------------------------------
    # PRE-BOOT PHASE
    # ------------------------------------------------------------------
    async def pre_boot_warmup(self) -> None:
        """
        Perform practical warming steps that materially reduce boot time:
        - Warm DB connections
        - Prefetch secrets
        - Ensure bytecode compiled for backend package
        """

        print("🔧 Pre-boot warmup starting...")
        loop = asyncio.get_running_loop()

        # Database warmup
        print("  ⚡ Warming DB connections...", end=" ")
        db_conn = await loop.run_in_executor(None, self._warm_db_connection)
        self.pre_warmed_resources["db_connection"] = db_conn
        print("✅")

        # Secret prefetch
        print("  ⚡ Pre-fetching secrets...", end=" ")
        secrets = await loop.run_in_executor(None, self._prefetch_secrets)
        self.pre_warmed_resources["secrets"] = secrets
        print("✅")

        # Bytecode compilation
        print("  ⚡ Checking compiled bytecode...", end=" ")
        await loop.run_in_executor(None, self._compile_backend_bytecode)
        print("✅")
        print("🔧 Pre-boot warmup complete\n")

    def _warm_db_connection(self) -> sqlite3.Connection:
        db_path = Path(__file__).resolve().parents[2] / "databases" / "grace.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("SELECT 1")
        return conn

    def _prefetch_secrets(self) -> Dict[str, Optional[str]]:
        return {
            "openai_key": os.getenv("OPENAI_API_KEY"),
            "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
            "azure_key": os.getenv("AZURE_OPENAI_KEY"),
        }

    def _compile_backend_bytecode(self) -> None:
        backend_path = Path(__file__).resolve().parents[1]
        compileall.compile_dir(
            str(backend_path),
            quiet=1,
            workers=min(4, os.cpu_count() or 1),
            force=False,
        )

    async def release_warmup_resources(self) -> None:
        """Clean up any handles created during warmup."""
        db_conn = self.pre_warmed_resources.pop("db_connection", None)
        if db_conn:
            await asyncio.get_running_loop().run_in_executor(None, db_conn.close)

    # ------------------------------------------------------------------
    # READINESS + WATCHDOGS
    # ------------------------------------------------------------------
    async def wait_for_readiness(self, kernel_name: str, timeout: int = 5) -> bool:
        """
        Observe the control plane for a kernel reaching RUNNING state with a
        recent heartbeat. Returns True if the kernel becomes ready.
        """
        start = datetime.utcnow()

        while (datetime.utcnow() - start).total_seconds() < timeout:
            kernel = self._get_kernel(kernel_name)
            if not kernel:
                return False

            if kernel.state == KernelState.RUNNING:
                last = kernel.last_heartbeat
                if last and (datetime.utcnow() - last).total_seconds() < 5:
                    return True

            await asyncio.sleep(0.5)

        logger.warning("[BOOT-ORCH] Kernel %s failed readiness check", kernel_name)
        return False

    async def start_watchdogs(self) -> None:
        """Launch tier-level watchdog tasks."""
        if self._watchdogs_running:
            return

        self._watchdogs_running = True
        tiers = {kernel.tier for kernel in control_plane.kernels.values()}
        for tier in tiers:
            self._watchdog_tasks[tier] = asyncio.create_task(self._tier_watchdog(tier))

    async def stop_watchdogs(self) -> None:
        """Stop watchdog tasks gracefully."""
        self._watchdogs_running = False
        for task in self._watchdog_tasks.values():
            task.cancel()
        await asyncio.gather(*self._watchdog_tasks.values(), return_exceptions=True)
        self._watchdog_tasks.clear()

    async def _tier_watchdog(self, tier: str) -> None:
        """Monitor all kernels assigned to a tier."""
        logger.debug("[WATCHDOG-%s] started", tier)
        while self._watchdogs_running:
            try:
                await asyncio.sleep(10)
                tier_kernels = [
                    kernel for kernel in control_plane.kernels.values()
                    if kernel.tier == tier
                ]

                for kernel in tier_kernels:
                    if kernel.state != KernelState.RUNNING:
                        continue

                    last = kernel.last_heartbeat
                    if not last:
                        continue

                    elapsed = (datetime.utcnow() - last).total_seconds()
                    if elapsed > 30:
                        logger.warning("[WATCHDOG-%s] %s unresponsive (%.1fs)", tier, kernel.name, elapsed)
                        await self._handle_unresponsive_kernel(kernel)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("[WATCHDOG-%s] error: %s", tier, exc)
        logger.debug("[WATCHDOG-%s] stopped", tier)

    async def _handle_unresponsive_kernel(self, kernel: Kernel) -> None:
        """Attempt basic remediation for an unresponsive kernel."""
        try:
            await control_plane._restart_kernel(kernel)  # noqa: SLF001 (controlled internal call)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("[BOOT-ORCH] Restart attempt failed for %s: %s", kernel.name, exc)

    # ------------------------------------------------------------------
    # HEARTBEAT STREAMING
    # ------------------------------------------------------------------
    async def monitor_kernel(self, kernel_name: str, max_duration: int = 60) -> None:
        """
        Record heartbeat telemetry for a kernel for a limited duration.
        Useful for chaos drills and forensic replay.
        """
        start = datetime.utcnow()
        try:
            while (datetime.utcnow() - start) < timedelta(seconds=max_duration):
                await asyncio.sleep(1)
                timestamp = datetime.utcnow()
                self.heartbeat_streams[kernel_name].append(timestamp)
                self._log_event(
                    "kernel_heartbeat",
                    {
                        "kernel": kernel_name,
                        "timestamp": timestamp.isoformat(),
                    },
                )
        except asyncio.CancelledError:
            logger.debug("Heartbeat stream for %s cancelled", kernel_name)
            raise

    def start_kernel_monitor(self, kernel_name: str, duration: int = 60) -> None:
        """Begin monitoring a kernel heartbeat stream."""
        if kernel_name in self._monitor_tasks:
            return
        self._monitor_tasks[kernel_name] = asyncio.create_task(
            self.monitor_kernel(kernel_name, duration)
        )

    async def stop_kernel_monitor(self, kernel_name: str) -> None:
        """Stop an active kernel monitor."""
        task = self._monitor_tasks.pop(kernel_name, None)
        if not task:
            return
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    def _log_event(self, event_type: str, payload: Dict[str, str]) -> None:
        logger.debug("[BOOT-ORCH] %s %s", event_type, payload)

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _get_kernel(self, kernel_name: str) -> Optional[Kernel]:
        return control_plane.kernels.get(kernel_name)


boot_orchestrator = BootOrchestrator()
