"""
Unified Event Publisher

Single entrypoint for publishing structured events through the Grace event bus.
Provides a synchronous-friendly wrapper so legacy callsites can publish without
managing their own asyncio loop.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from backend.event_bus import event_bus, Event, EventType

DEFAULT_EVENT_TYPE = EventType.AGENT_ACTION


def _coerce_event_type(event_type: str | EventType | None) -> EventType:
    """Map string values to EventType enum with a safe fallback."""
    if isinstance(event_type, EventType):
        return event_type
    if isinstance(event_type, str):
        return EventType.__members__.get(event_type.upper(), DEFAULT_EVENT_TYPE)
    return DEFAULT_EVENT_TYPE


async def publish_event_async(
    event_type: str | EventType,
    source: str,
    payload: Dict[str, Any],
    trace_id: Optional[str] = None,
) -> None:
    """Async helper that publishes directly to the event bus."""
    evt_type = _coerce_event_type(event_type)
    event = Event(
        event_type=evt_type,
        source=source,
        data=payload or {},
        trace_id=trace_id,
    )
    await event_bus.publish(event)


def publish_event(
    event_type: str | EventType,
    source: str,
    payload: Dict[str, Any],
    trace_id: Optional[str] = None,
) -> None:
    """
    Synchronous-friendly publisher.

    If an event loop is running, schedule the publish as a task.
    Otherwise, create a temporary loop to deliver the event immediately.
    """

    coro = publish_event_async(event_type, source, payload, trace_id=trace_id)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Fire-and-forget inside existing loop
        loop.create_task(coro)
    else:
        asyncio.run(coro)
