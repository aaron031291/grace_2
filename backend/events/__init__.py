"""
Event compatibility package.

This makes ``backend.events`` a proper Python package so legacy imports like
``from backend.events.unified_publisher import publish_event`` resolve
correctly after the unified event publisher refactor.
"""

from backend.events.unified_publisher import publish_event, publish_event_async

__all__ = ["publish_event", "publish_event_async"]
