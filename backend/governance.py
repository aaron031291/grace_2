"""
Governance Engine Module
Exports the main GovernanceEngine for service configuration
"""

from .governance_system.governance import GovernanceEngine, governance_engine

__all__ = ['GovernanceEngine', 'governance_engine']
