"""
Event Publisher - Compatibility Wrapper

This module provides backward compatibility for code that imports from:
    from backend.event_publisher import publish_event

It wraps the real implementation in backend.core.unified_event_publisher.
"""

from backend.core.unified_event_publisher import (
    publish_event,
    publish_domain_event,
    publish_trigger,
    publish_message,
    publish_event_obj,
    publish_domain_event_obj,
    get_unified_publisher,
    UnifiedEventPublisher
)

__all__ = [
    'publish_event',
    'publish_domain_event',
    'publish_trigger',
    'publish_message',
    'publish_event_obj',
    'publish_domain_event_obj',
    'get_unified_publisher',
    'UnifiedEventPublisher'
]
