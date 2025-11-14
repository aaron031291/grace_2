"""Memory Research Whitelist - Re-export from memory_services module"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'ResearchWhitelist':
        from .memory_services.memory_research_whitelist import ResearchWhitelist
        return ResearchWhitelist
    elif name == 'initialize_default_whitelist':
        from .memory_services.memory_research_whitelist import initialize_default_whitelist
        return initialize_default_whitelist
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'ResearchWhitelist',
    'initialize_default_whitelist'
]
