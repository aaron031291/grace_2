"""Research Sweeper - Re-export from knowledge module"""

from typing import Any as _Any

research_sweeper: _Any
ResearchSweeper: _Any


# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'research_sweeper':
        from .knowledge.research_sweeper import research_sweeper
        return research_sweeper
    elif name == 'ResearchSweeper':
        from .knowledge.research_sweeper import ResearchSweeper
        return ResearchSweeper
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ['research_sweeper', 'ResearchSweeper']
