"""
Grace module - Backwards compatibility layer
Re-exports GraceAutonomous from backend.grace_agent
"""

from backend.grace_agent import GraceAutonomous, grace_autonomous

# Re-export for compatibility
__all__ = ["GraceAutonomous", "grace_autonomous"]
