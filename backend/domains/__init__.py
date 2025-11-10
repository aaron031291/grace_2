"""
Domain Adapters - Integration layer between domains and Agent Core

Each domain implements the DomainAdapter interface to integrate
with GRACE's autonomous capabilities.
"""

from .core_domain_adapter import core_domain_adapter

# Import other domain adapters as they're implemented
# from .transcendence_adapter import transcendence_adapter
# from .knowledge_adapter import knowledge_adapter
# from .security_adapter import security_adapter
# from .ml_adapter import ml_adapter
# from .temporal_adapter import temporal_adapter
# from .parliament_adapter import parliament_adapter
# from .federation_adapter import federation_adapter
# from .speech_adapter import speech_adapter
# from .cognition_adapter import cognition_adapter

__all__ = [
    "core_domain_adapter",
    # Add others as implemented
]
