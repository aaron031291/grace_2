"""
Placeholder Authentication Handler for Grace.

This provides a dummy `get_current_user` dependency to allow other
modules to load. In a real application, this would be replaced with a
proper authentication system (e.g., OAuth2 with JWTs).
"""

from fastapi import Depends

async def get_current_user() -> dict:
    """
    A placeholder dependency that returns a mock user.
    This allows endpoints protected by authentication to run during development
    without a full auth implementation.
    """
    return {
        "username": "grace_agent",
        "email": "grace@system.local",
        "roles": ["admin", "system", "agent"],
    }