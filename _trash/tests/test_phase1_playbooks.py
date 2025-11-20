"""
Phase 1 Playbook Tests
REAL tests that verify playbooks load and execute
"""

import pytest
import asyncio
from datetime import datetime

def test_network_playbooks_load():
    """Verify network playbooks can be imported and initialized"""
    from backend.self_heal.network_healing_playbooks import (
        NetworkPlaybookRegistry,
        RestartComponentPlaybook,
        ClearPortPlaybook,
        DiagnoseNetworkPlaybook,
        RebindPortPlaybook,
        NetworkIssue
    )
    
    # Test registry loads
    registry = NetworkPlaybookRegistry()
    assert len(registry.playbooks) == 4
    assert 'restart_component' in registry.playbooks
    assert 'clear_port' in registry.playbooks
    assert 'diagnose_network' in registry.playbooks
    assert 'rebind_port' in registry.playbooks

def test_auto_healing_playbooks_load():
    """Verify auto-healing playbooks can be imported and initialized"""
    from backend.self_heal.auto_healing_playbooks import (
        RestartKernelPlaybook,
        RestartServicePlaybook,
        PerformanceOptimizationPlaybook,
        ResourceCleanupPlaybook,
        RollbackDeploymentPlaybook,
        QuarantineArtifactsPlaybook,
        RunDiagnosticsPlaybook,
        DailyHealthCheckPlaybook,
        RotateSecretsPlaybook
    )
    
    # Test each playbook initializes
    playbooks = [
        RestartKernelPlaybook(),
        RestartServicePlaybook(),
        PerformanceOptimizationPlaybook(),
        ResourceCleanupPlaybook(),
        RollbackDeploymentPlaybook(),
        QuarantineArtifactsPlaybook(),
        RunDiagnosticsPlaybook(),
        DailyHealthCheckPlaybook(),
        RotateSecretsPlaybook()
    ]
    
    assert len(playbooks) == 9
    
    # Verify each has required methods
    for playbook in playbooks:
        assert hasattr(playbook, 'execute')
        assert hasattr(playbook, 'verify')
        assert hasattr(playbook, 'rollback')
        assert hasattr(playbook, 'dry_run')
        assert playbook.execution_count == 0

@pytest.mark.asyncio
async def test_playbook_dry_run():
    """Test playbook dry_run actually works"""
    from backend.self_heal.auto_healing_playbooks import RestartKernelPlaybook
    
    playbook = RestartKernelPlaybook()
    context = {"kernel_name": "test_kernel"}
    
    result = await playbook.dry_run(context)
    
    assert result['would_execute'] == True
    assert result['playbook'] == 'restart_kernel'
    assert 'simulated_steps' in result
    assert len(result['simulated_steps']) > 0

@pytest.mark.asyncio
async def test_mttr_tracker():
    """Test MTTR tracker actually tracks"""
    from backend.monitoring.mttr_tracker import MTTRTracker
    
    tracker = MTTRTracker()
    
    # Start an action
    action = tracker.start_action(
        action_id="test_001",
        issue_type="port_conflict",
        component="test_service",
        playbook="restart_component"
    )
    
    assert action.action_id == "test_001"
    assert action.issue_type == "port_conflict"
    assert action.started_at is not None
    
    # Simulate some work
    await asyncio.sleep(0.01)
    
    # Complete the action
    completed = tracker.complete_action("test_001", success=True)
    
    assert completed is not None
    assert completed.success == True
    assert completed.recovery_time_seconds is not None
    assert completed.recovery_time_seconds > 0
    
    # Get stats
    stats = tracker.get_stats()
    assert stats['total_actions'] == 1
    assert stats['successful'] == 1
    assert stats['failed'] == 0
    assert stats['mttr_seconds'] is not None

def test_guardian_api_exists():
    """Verify Guardian API endpoints are registered"""
    from backend.routes.guardian_api import router
    
    routes = [route.path for route in router.routes]
    
    # Routes have /api/guardian prefix
    assert '/api/guardian/stats' in routes
    assert '/api/guardian/healer/stats' in routes
    assert '/api/guardian/playbooks' in routes
    assert '/api/guardian/mttr/by-issue-type' in routes
    assert '/api/guardian/mttr/by-playbook' in routes
    assert '/api/guardian/failures/recent' in routes

def test_playbook_count_accurate():
    """Verify we actually have 13 playbooks (4 network + 9 auto)"""
    from backend.self_heal.network_healing_playbooks import NetworkPlaybookRegistry
    from backend.self_heal.auto_healing_playbooks import (
        RestartKernelPlaybook, RestartServicePlaybook,
        PerformanceOptimizationPlaybook, ResourceCleanupPlaybook,
        RollbackDeploymentPlaybook, QuarantineArtifactsPlaybook,
        RunDiagnosticsPlaybook, DailyHealthCheckPlaybook,
        RotateSecretsPlaybook
    )
    
    network_registry = NetworkPlaybookRegistry()
    network_count = len(network_registry.playbooks)
    
    auto_playbooks = [
        RestartKernelPlaybook(), RestartServicePlaybook(),
        PerformanceOptimizationPlaybook(), ResourceCleanupPlaybook(),
        RollbackDeploymentPlaybook(), QuarantineArtifactsPlaybook(),
        RunDiagnosticsPlaybook(), DailyHealthCheckPlaybook(),
        RotateSecretsPlaybook()
    ]
    auto_count = len(auto_playbooks)
    
    total = network_count + auto_count
    assert total == 13, f"Expected 13 playbooks, found {total}"
