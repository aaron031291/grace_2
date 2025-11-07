"""
Compatibility layer for legacy imports expecting `ImmutableEntry`.

The ORM model now lives in `backend.base_models.ImmutableLogEntry`, but several
subsystems (immutable log analyzer, self-healing meta loop, etc.) still import
`ImmutableEntry` from this module.  Re-export the updated model so those imports
keep working without replicating the class definition or creating circular
dependencies.
"""

from .base_models import ImmutableLogEntry as ImmutableEntry  # noqa: F401

