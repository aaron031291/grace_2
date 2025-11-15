"""
Models module for agents_core
Re-exports Base and async_session from main models
"""

from backend.models.base_models import Base, engine, async_session

__all__ = ['Base', 'engine', 'async_session']
