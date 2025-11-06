"""
Knowledge Discovery Scheduler

Periodically identifies knowledge coverage gaps and queues discovery requests
via Trigger Mesh events, respecting governance policies, trusted sources, and
Hunter security checks. Publishes KPIs to the cognition metrics system.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List, Optional, Tuple

from .models import async_session
from sqlalchemy import select, func

from .knowledge_models import KnowledgeArtifact
from .trusted_sources import trust_manager, TrustedSource
from .trigger_mesh import trigger_mesh, TriggerEvent

# Best-effort imports for governance/hunter/metrics (swallow failures gracefully)
try:  # pragma: no cover - optional wiring
    from .governance import governance_engine  # type: ignore
except Exception:  # pragma: no cover
    governance_engine = None  # type: ignore

try:  # pragma: no cover - optional wiring
    from .hunter import hunter  # type: ignore
except Exception:  # pragma: no cover
    hunter = None  # type: ignore

try:  # pragma: no cover - optional wiring
    from .metrics_service import publish_metric  # type: ignore
except Exception:  # pragma: no cover
    async def publish_metric(*args, **kwargs):  # type: ignore
        return None


class KnowledgeDiscoveryScheduler:
    """Periodic scheduler for proactive, governed knowledge discovery.

    Strategy (baseline):
    - If external knowledge coverage is low, queue discovery for whitelisted domains.
    - Use TrustedSource entries; for each, construct a seed URL like https://{domain}/.
    - Only publish a discovery request if:
      * Domain is explicitly listed in TrustedSource (whitelisted), and
      * trust_manager.should_auto_approve(seed_url) is True, and
      * Governance does not block, and
      * Hunter does not raise critical alerts (best-effort).
    - Publish KPIs for scheduled and skipped items.
    """

    def __init__(self, interval_seconds: int = 1800, seeds_per_cycle: int = 3) -> None:
        self.interval_seconds = max(60, interval_seconds)
        self.seeds_per_cycle = max(1, seeds_per_cycle)
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        print(f"✓ Knowledge discovery scheduler started (interval: {self.interval_seconds}s)")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        print("✓ Knowledge discovery scheduler stopped")

    async def _loop(self) -> None:
        try:
            while self._running:
                try:
                    await self._run_cycle()
                except Exception as e:  # pragma: no cover - resilience
                    print(f"⚠ Discovery scheduler cycle error: {e}")
                await asyncio.sleep(self.interval_seconds)
        except asyncio.CancelledError:
            pass

    async def _run_cycle(self) -> None:
        # Determine if we should schedule discovery based on current coverage
        coverage = await self._get_external_coverage()
        total_external = coverage.get("external", 0)
        should_discover = total_external < 50  # heuristic baseline

        # Always inspect trusted sources, but limit published seeds per cycle
        trusted = await self._list_trusted_sources()
        published = 0
        skipped = 0

        for src in trusted:
            if published >= self.seeds_per_cycle:
                break

            seed_url = self._build_seed_url(src.domain)
            auto, score = await trust_manager.should_auto_approve(seed_url)

            if not auto:
                skipped += 1
                continue

            if not should_discover and score < 90:
                # If coverage looks fine, only take very high trust seeds
                skipped += 1
                continue

            if not await self._passes_governance(seed_url):
                skipped += 1
                continue

            if not await self._passes_hunter(seed_url):
                skipped += 1
                continue

            await self._publish_discovery(topic=src.domain, url=seed_url)
            published += 1

        # KPIs
        try:
            await publish_metric("knowledge", "discovery_scheduled", float(published))
            await publish_metric("knowledge", "discovery_skipped", float(skipped))
        except Exception:
            pass

        if published:
            print(f"🔎 Knowledge discovery scheduled: {published} seed(s), {skipped} skipped")
        else:
            print(f"ℹ Knowledge discovery: nothing scheduled (skipped={skipped})")

    async def _get_external_coverage(self) -> dict:
        """Count artifacts by domain."""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(KnowledgeArtifact.domain, func.count())
                    .group_by(KnowledgeArtifact.domain)
                )
                rows = result.all()
                return {d or "unknown": int(c) for d, c in rows}
        except Exception:
            return {"unknown": 0}

    async def _list_trusted_sources(self) -> List[TrustedSource]:
        try:
            async with async_session() as session:
                result = await session.execute(select(TrustedSource))
                return list(result.scalars().all())
        except Exception:
            return []

    def _build_seed_url(self, domain: str) -> str:
        scheme = "https" if domain != "localhost" else "http"
        return f"{scheme}://{domain}/"

    async def _passes_governance(self, url: str) -> bool:
        if governance_engine is None:
            return True
        try:
            decision = await governance_engine.check(
                actor="system",
                action="knowledge_discover",
                resource=url,
                payload={"reason": "proactive_scheduler"},
            )
            return decision.get("decision") != "block"
        except Exception:
            return True

    async def _passes_hunter(self, url: str) -> bool:
        if hunter is None:
            return True
        try:
            alerts = await hunter.inspect(
                actor="system",
                action="discover",
                resource=url,
                payload={"source": "scheduler"},
            )
            # Allow if no alerts or only informational ones; baseline: allow if no alerts
            return not alerts
        except Exception:
            return True

    async def _publish_discovery(self, topic: str, url: str) -> None:
        event = TriggerEvent(
            event_type="knowledge.discovery.requested",
            source="knowledge_scheduler",
            actor="system",
            resource=topic,
            payload={"topic": topic, "url": url},
            timestamp=datetime.utcnow(),
        )
        await trigger_mesh.publish(event)


# Global scheduler instance and helpers
_discovery_scheduler = KnowledgeDiscoveryScheduler()


async def start_discovery_scheduler(interval_seconds: Optional[int] = None, seeds_per_cycle: Optional[int] = None) -> None:
    if interval_seconds is not None:
        _discovery_scheduler.interval_seconds = max(60, int(interval_seconds))
    if seeds_per_cycle is not None:
        _discovery_scheduler.seeds_per_cycle = max(1, int(seeds_per_cycle))
    await _discovery_scheduler.start()


async def stop_discovery_scheduler() -> None:
    await _discovery_scheduler.stop()
