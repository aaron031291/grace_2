"""
Trigger Mesh - Declarative Event Routing System
Replaces ad-hoc pub/sub with YAML-driven signal network
"""

from .trigger_mesh import TriggerMesh, trigger_mesh
from .route_loader import RouteLoader
from .event_dispatcher import EventDispatcher

__all__ = [
    'TriggerMesh',
    'trigger_mesh',
    'RouteLoader',
    'EventDispatcher'
]</code></edit_file>
