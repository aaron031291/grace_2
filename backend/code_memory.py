"""
Compatibility wrapper for backend.code_memory
Re-exports from backend.misc.code_memory
"""

from backend.misc.code_memory import (
    CodePattern,
    CodeContext,
    CodeSymbol,
    CodeMemoryEngine,
    code_memory,
)

__all__ = [
    'CodePattern',
    'CodeContext',
    'CodeSymbol',
    'CodeMemoryEngine',
    'code_memory',
]
