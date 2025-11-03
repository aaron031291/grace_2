"""Agentic orchestration package for Grace's coding assistant."""

from .orchestrator import CodingOrchestrator

# Shared orchestrator instance used by API layer
coding_orchestrator = CodingOrchestrator()

__all__ = ["CodingOrchestrator", "coding_orchestrator"]
