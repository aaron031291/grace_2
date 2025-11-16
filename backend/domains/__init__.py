"""
Domain System - Synergistic Domain Architecture

Provides:
- Auto-discovery and registration
- Pub/Sub event bus
- Shared collective memory
- Multi-domain workflows
- Smart routing
- Health federation
- Cryptographic trust

Creates a living, learning organism from independent domains
"""

from .domain_registry import domain_registry, DomainRegistry, DomainInfo
from .domain_event_bus import domain_event_bus, DomainEventBus, DomainEvent
from .shared_domain_memory import shared_domain_memory, SharedDomainMemory, MemoryContribution
from .domain_orchestrator import domain_orchestrator, DomainOrchestrator, Workflow, WorkflowStep

__all__ = [
    # Registry
    'domain_registry',
    'DomainRegistry',
    'DomainInfo',
    
    # Event Bus
    'domain_event_bus',
    'DomainEventBus',
    'DomainEvent',
    
    # Shared Memory
    'shared_domain_memory',
    'SharedDomainMemory',
    'MemoryContribution',
    
    # Orchestrator
    'domain_orchestrator',
    'DomainOrchestrator',
    'Workflow',
    'WorkflowStep',
]


async def initialize_domain_system():
    """
    Initialize the complete domain system
    Call this on Grace startup
    """
    await domain_registry.initialize()
    # Event bus and shared memory don't need async init
    
    return {
        'domain_registry': 'initialized',
        'event_bus': 'ready',
        'shared_memory': 'ready',
        'orchestrator': 'ready'
    }
