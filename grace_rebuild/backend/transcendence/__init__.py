"""Transcendence configuration namespace.

This package centralises parameters that drive Grace's agentic code
generation pipeline so that all subsystems (understanding, planning, and
generation) reference a single source of truth.
"""

from .config import (
    CODE_GENERATION_DEFAULTS,
    CODE_GENERATION_TEMPLATES,
    DEFAULT_CODE_LANGUAGE,
    LANGUAGE_CONTEXTS,
    SUPPORTED_TASK_TYPES,
)

__all__ = [
    "CODE_GENERATION_DEFAULTS",
    "CODE_GENERATION_TEMPLATES",
    "DEFAULT_CODE_LANGUAGE",
    "LANGUAGE_CONTEXTS",
    "SUPPORTED_TASK_TYPES",
]
