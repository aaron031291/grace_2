"""
Tests for Grace Unified Orchestrator
Moved from main orchestrator file to avoid import conflicts
"""

import sys
from pathlib import Path

# Add backend to path BEFORE imports
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

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
        assert clean_orchestrator._is_running is False
    
    @pytest.mark.asyncio
    async def test_start_system(self, clean_orchestrator):
        """Test system startup using real start() method"""
        success = await clean_orchestrator.start()
        assert success is True
        assert clean_orchestrator._is_running is True
    
    @pytest.mark.asyncio
    async def test_stop_system(self, clean_orchestrator):
        """Test system shutdown"""
        # Start first
        await clean_orchestrator.start()
        
        # Then stop
        success = await clean_orchestrator.stop()
        assert success is True
        assert clean_orchestrator._is_running is False
    
    @pytest.mark.asyncio
    async def test_get_status(self, clean_orchestrator):
        """Test status reporting"""
        status = await clean_orchestrator.get_detailed_status()
        
        assert "boot_id" in status
        assert "environment" in status
        assert "platform" in status
        assert "imports_successful" in status
        assert "components" in status
        assert status["environment"] == "test"
    
    def test_state_management(self, clean_orchestrator):
        """Test state save/load functionality"""
        test_state = {
            "boot_id": "test-boot-123",
            "environment": "test",
            "started_at": "2024-01-01T00:00:00"
        }
        
        # Save state using real method
        clean_orchestrator._save_state(test_state)
        
        # Load state using real method
        loaded_state = clean_orchestrator._load_state()
        assert loaded_state is not None
        assert loaded_state["boot_id"] == "test-boot-123"
        assert loaded_state["environment"] == "test"
        
        # Cleanup
        if clean_orchestrator.state_file.exists():
            clean_orchestrator.state_file.unlink()
    
    def test_config_update(self, clean_orchestrator):
        """Test configuration updates"""
        clean_orchestrator.update_config("prod", "docker", True, False, 120)
        
        assert clean_orchestrator.environment == "prod"
        assert clean_orchestrator.profile == "docker"
        assert clean_orchestrator.safe_mode is True
        assert clean_orchestrator.dry_run is False
        assert clean_orchestrator.timeout == 120
    
    @pytest.mark.asyncio
    async def test_core_systems_startup(self, clean_orchestrator):
        """Test core systems startup with mocking"""
        # Mock the actual method that exists
        with patch.object(clean_orchestrator, '_start_core_systems', return_value={"core": 1, "memory": 2}) as mock_start:
            success = await clean_orchestrator.start()
            assert success is True
            mock_start.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
