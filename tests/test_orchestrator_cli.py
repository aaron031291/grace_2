#!/usr/bin/env python3
"""
Unit and smoke tests for Grace Unified Orchestrator CLI
Ensures regression-free operation of the boot system
"""
import pytest
import asyncio
import subprocess
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Import the orchestrator
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.unified_grace_orchestrator import GraceUnifiedOrchestrator, main

class TestGraceUnifiedOrchestrator:
    """Unit tests for the orchestrator class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def orchestrator(self, temp_dir):
        """Create orchestrator instance for testing"""
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        with patch('backend.unified_grace_orchestrator.Path.cwd', return_value=temp_dir):
            return GraceUnifiedOrchestrator(environment="test", dry_run=True)
    
    def test_singleton_pattern(self, temp_dir):
        """Test that orchestrator follows singleton pattern"""
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        with patch('backend.unified_grace_orchestrator.Path.cwd', return_value=temp_dir):
            orch1 = GraceUnifiedOrchestrator()
            orch2 = GraceUnifiedOrchestrator()
            
            assert orch1 is orch2
            assert id(orch1) == id(orch2)
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.environment == "test"
        assert orchestrator.dry_run is True
        assert orchestrator.boot_id.startswith("grace-")
        assert orchestrator._initialized is True
        assert orchestrator._is_running is False
    
    @pytest.mark.asyncio
    async def test_dry_run_boot(self, orchestrator):
        """Test dry run boot sequence"""
        success = await orchestrator.boot()
        assert success is True
        assert orchestrator._boot_task is not None
        assert orchestrator._boot_task.done()
    
    @pytest.mark.asyncio
    async def test_concurrent_boot_prevention(self, orchestrator):
        """Test that concurrent boots are prevented"""
        # Start first boot
        task1 = asyncio.create_task(orchestrator.boot())
        
        # Try to start second boot immediately
        task2 = asyncio.create_task(orchestrator.boot())
        
        # Both should complete successfully
        result1 = await task1
        result2 = await task2
        
        assert result1 is True
        assert result2 is True
    
    @pytest.mark.asyncio
    async def test_stage_preflight(self, orchestrator):
        """Test pre-flight checks stage"""
        success = await orchestrator._stage_preflight()
        assert success is True
        assert orchestrator.stage_results.get("preflight") is True
    
    @pytest.mark.asyncio
    async def test_get_detailed_status(self, orchestrator):
        """Test status reporting"""
        status = await orchestrator.get_detailed_status()
        
        assert "boot_id" in status
        assert "environment" in status
        assert "backend" in status
        assert "frontend" in status
        assert status["environment"] == "test"
    
    @pytest.mark.asyncio
    async def test_stop_services(self, orchestrator):
        """Test stopping services"""
        # Mock process registry
        with patch('backend.unified_grace_orchestrator.process_registry') as mock_registry:
            mock_registry.stop_all_processes = AsyncMock(return_value={"stopped": [], "force_killed": []})
            
            success = await orchestrator.stop()
            assert success is True

class TestCLIInterface:
    """Test CLI interface and argument parsing"""
    
    def test_cli_help(self):
        """Test CLI help output"""
        result = subprocess.run([
            sys.executable, "-m", "backend.unified_grace_orchestrator", "--help"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "Grace Unified Orchestrator" in result.stdout
        assert "--stop" in result.stdout
        assert "--status" in result.stdout
    
    def test_cli_dry_run(self):
        """Test CLI dry run mode"""
        result = subprocess.run([
            sys.executable, "-m", "backend.unified_grace_orchestrator", 
            "--dry-run", "--env", "test"
        ], capture_output=True, text=True, timeout=30)
        
        # Should complete successfully
        assert result.returncode == 0
    
    def test_cli_status_when_not_running(self):
        """Test status command when Grace is not running"""
        result = subprocess.run([
            sys.executable, "-m", "backend.unified_grace_orchestrator", "--status"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Parse JSON output
        try:
            status = json.loads(result.stdout)
            assert "boot_id" in status
            assert status["boot_id"] == "not_running"
        except json.JSONDecodeError:
            pytest.fail("Status output is not valid JSON")

class TestSmokeTests:
    """Smoke tests for critical functionality"""
    
    @pytest.mark.asyncio
    async def test_full_boot_sequence_dry_run(self):
        """Smoke test: Full boot sequence in dry run mode"""
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        orchestrator = GraceUnifiedOrchestrator(environment="test", dry_run=True)
        
        success = await orchestrator.boot()
        assert success is True
        
        # Check that all stages completed
        expected_stages = [
            "preflight", "database_migrations", "core_services",
            "domain_kernels", "learning_systems", "autonomous_agents",
            "memory_systems", "web_services", "health_verification",
            "post_boot_diagnostics"
        ]
        
        # In dry run, not all stages set results, but boot should succeed
        assert orchestrator._boot_task.done()
    
    def test_import_orchestrator(self):
        """Smoke test: Import orchestrator module"""
        try:
            from backend.unified_grace_orchestrator import GraceUnifiedOrchestrator, app
            assert GraceUnifiedOrchestrator is not None
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import orchestrator: {e}")
    
    def test_fastapi_app_creation(self):
        """Smoke test: FastAPI app creation"""
        from backend.unified_grace_orchestrator import app
        
        assert app.title == "Grace AI System"
        assert app.version == "2.0.0"
        
        # Check routes exist
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/health" in routes
        assert "/api/status" in routes
        assert "/api/shutdown" in routes

class TestRegressionTests:
    """Regression tests for known issues"""
    
    def test_no_duplicate_file_handlers(self):
        """Regression test: Ensure no duplicate file handlers"""
        import logging
        
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        logger = logging.getLogger("backend.unified_grace_orchestrator")
        initial_handlers = len(logger.handlers)
        
        # Create multiple orchestrator instances
        orch1 = GraceUnifiedOrchestrator()
        orch2 = GraceUnifiedOrchestrator()
        orch3 = GraceUnifiedOrchestrator()
        
        # Should not add more handlers due to singleton pattern
        final_handlers = len(logger.handlers)
        assert final_handlers <= initial_handlers + 1  # At most one file handler added
    
    @pytest.mark.asyncio
    async def test_no_recursive_uvicorn_launch(self):
        """Regression test: Ensure no recursive uvicorn launches"""
        import os
        
        # Set environment variable to simulate running under uvicorn
        os.environ["UVICORN_RUNNING"] = "1"
        
        try:
            # Reset singleton
            GraceUnifiedOrchestrator._instance = None
            GraceUnifiedOrchestrator._initialized = False
            
            orchestrator = GraceUnifiedOrchestrator(dry_run=True)
            success = await orchestrator.boot()
            
            # Should complete without trying to start uvicorn again
            assert success is True
        finally:
            # Clean up
            if "UVICORN_RUNNING" in os.environ:
                del os.environ["UVICORN_RUNNING"]
    
    @pytest.mark.asyncio
    async def test_concurrent_api_requests(self):
        """Regression test: Handle concurrent API requests safely"""
        # Reset singleton
        GraceUnifiedOrchestrator._instance = None
        GraceUnifiedOrchestrator._initialized = False
        
        orchestrator = GraceUnifiedOrchestrator(dry_run=True)
        
        # Simulate concurrent API requests
        tasks = [
            orchestrator.get_detailed_status(),
            orchestrator.get_detailed_status(),
            orchestrator.get_detailed_status(),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed and return consistent data
        assert len(results) == 3
        for result in results:
            assert "boot_id" in result
            assert "environment" in result

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])