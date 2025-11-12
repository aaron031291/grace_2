"""
Tests for Grace Unified Orchestrator
"""

import sys
from pathlib import Path

# Add backend to path BEFORE imports
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import asyncio
from unittest.mock import Mock, patch

# Import the orchestrator
from backend.unified_grace_orchestrator import GraceUnifiedOrchestrator

class TestGraceUnifiedOrchestrator:
    """Test suite for Grace Unified Orchestrator"""
    
    @pytest.fixture
    def clean_orchestrator(self):
        """Create a fresh orchestrator instance for testing"""
        # Reset singleton for testing
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        return GraceUnifiedOrchestrator(environment="test", dry_run=True)
    
    def test_singleton_pattern(self):
        """Test that orchestrator follows singleton pattern"""
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        orch1 = GraceUnifiedOrchestrator()
        orch2 = GraceUnifiedOrchestrator()
        assert orch1 is orch2
    
    def test_initialization(self, clean_orchestrator):
        """Test orchestrator initialization"""
        assert clean_orchestrator.environment == "test"
        assert clean_orchestrator.dry_run is True
        assert clean_orchestrator.boot_id.startswith("grace-")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
