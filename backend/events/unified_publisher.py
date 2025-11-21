"""
Compatibility shim for legacy modules importing backend.events.unified_publisher.

The new unified event publisher lives at backend.unified_event_publisher; this
module simply re-exports its public API so existing imports continue to work.
"""

from backend.unified_event_publisher import (
    publish_event,
    publish_event_async,
)

__all__ = ["publish_event", "publish_event_async"]
