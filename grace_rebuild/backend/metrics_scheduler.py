"""Background tasks for maintaining Grace telemetry rollups."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Optional

from .metrics_service import metrics_service


logger = logging.getLogger(__name__)


class MetricsScheduler:
    """Periodic scheduler that maintains metric rollups and benchmarks."""

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self, interval_seconds: int = 3600) -> None:
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run(interval_seconds))
        logger.info("Metrics scheduler started (interval=%ss)", interval_seconds)

    async def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            logger.info("Metrics scheduler stopped")

    async def _run(self, interval_seconds: int) -> None:
        while self._running:
            try:
                await metrics_service.rollup_metrics()
                await metrics_service.evaluate_benchmarks()
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.exception("Metrics scheduler error: %s", exc)

            await asyncio.sleep(interval_seconds)


metrics_scheduler = MetricsScheduler()


__all__ = ["metrics_scheduler", "MetricsScheduler"]
