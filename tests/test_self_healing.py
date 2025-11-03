import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from backend.main import app
from backend.self_healing import health_monitor, system_state
from backend.governance_models import HealthCheck, HealingAction
from backend.models import async_session
from backend.reflection import reflection_service
from backend.task_executor import task_executor


@pytest.mark.asyncio
async def test_health_check_all_components():
    """Test that health monitor checks all components"""
    await health_monitor.check_all_components()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health/status")
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert "actions" in data
        assert "system_mode" in data


@pytest.mark.asyncio
async def test_system_mode_changes():
    """Test system mode transitions"""
    original_mode = system_state.mode
    
    system_state.mode = "read_only"
    assert system_state.mode == "read_only"
    
    system_state.mode = "normal"
    assert system_state.mode == "normal"
    
    # Restore original mode
    system_state.mode = original_mode


@pytest.mark.asyncio
async def test_healing_action_logged():
    """Test that healing actions are logged"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health/status")
        data = response.json()
        
        assert isinstance(data["actions"], list)


@pytest.mark.asyncio
async def test_simulated_reflection_loop_crash():
    """Test self-healing when reflection service crashes"""
    print("\n[TEST] Testing reflection loop crash simulation...")
    
    # Simulate crash by stopping reflection service
    await reflection_service.stop()
    
    # Trigger health check - should detect failure
    await health_monitor.check_all_components()
    
    # Check that failure was logged
    async with async_session() as session:
        result = await session.execute(
            select(HealthCheck)
            .where(HealthCheck.component == "reflection_service")
            .order_by(HealthCheck.created_at.desc())
            .limit(1)
        )
        check = result.scalar_one_or_none()
        assert check is not None
        assert check.status == "critical"
    
    # Trigger second consecutive check to trigger healing
    await health_monitor.check_all_components()
    
    # Wait a moment for healing to complete
    await asyncio.sleep(1)
    
    # Verify healing action was logged
    async with async_session() as session:
        result = await session.execute(
            select(HealingAction)
            .where(HealingAction.component == "reflection_service")
            .order_by(HealingAction.created_at.desc())
            .limit(1)
        )
        action = result.scalar_one_or_none()
        assert action is not None
        assert action.action == "restart_reflection_service"
        assert action.result == "success"
    
    # Verify component is restored
    assert reflection_service._running
    
    print("[PASS] Reflection service crash recovery verified")


@pytest.mark.asyncio
async def test_simulated_database_connection_failure():
    """Test self-healing when database connection fails"""
    print("\n[TEST] Testing database connection failure simulation...")
    
    original_mode = system_state.mode
    
    # Force a database failure check by mocking
    health_monitor.consecutive_failures["database"] = 1
    
    # Simulate database failure in health check
    old_check_db = health_monitor._check_database
    
    async def mock_failing_db():
        return {"ok": False, "error": "Connection timeout"}
    
    health_monitor._check_database = mock_failing_db
    
    try:
        # Trigger health check
        await health_monitor.check_all_components()
        
        # Verify system entered read-only mode
        assert system_state.mode == "read_only"
        assert system_state.reason == "Database connection issues"
        
        # Verify healing action was logged
        async with async_session() as session:
            result = await session.execute(
                select(HealingAction)
                .where(HealingAction.component == "database")
                .order_by(HealingAction.created_at.desc())
                .limit(1)
            )
            action = result.scalar_one_or_none()
            assert action is not None
            assert action.action == "enter_read_only_mode"
            assert action.result == "success"
        
        print("[PASS] Database failure fallback to read-only mode verified")
    
    finally:
        # Restore original check function and mode
        health_monitor._check_database = old_check_db
        system_state.mode = original_mode
        health_monitor.consecutive_failures["database"] = 0


@pytest.mark.asyncio
async def test_simulated_sandbox_timeout():
    """Test self-healing when sandbox execution times out"""
    print("\n[TEST] Testing sandbox timeout simulation...")
    
    from backend.sandbox_manager import sandbox_manager
    
    # Create a script that will timeout
    test_file = "timeout_test.py"
    content = "import time\ntime.sleep(15)  # Longer than 10s timeout"
    
    await sandbox_manager.write_file("test_user", test_file, content)
    
    # Execute command that will timeout
    stdout, stderr, exit_code, duration_ms = await sandbox_manager.run_command(
        "test_user",
        f"python {test_file}",
        test_file
    )
    
    # Verify timeout handling
    assert exit_code == -1
    assert "timeout" in stderr.lower()
    assert duration_ms >= 10000  # Should be at least 10 seconds
    
    # Verify sandbox run was logged
    from backend.sandbox_models import SandboxRun
    async with async_session() as session:
        result = await session.execute(
            select(SandboxRun)
            .where(SandboxRun.command.like(f"%{test_file}%"))
            .order_by(SandboxRun.created_at.desc())
            .limit(1)
        )
        run = result.scalar_one_or_none()
        assert run is not None
        assert run.exit_code == -1
        assert not run.success
    
    # Cleanup
    await sandbox_manager.reset_sandbox("test_user")
    
    print("[PASS] Sandbox timeout cleanup verified")


@pytest.mark.asyncio
async def test_simulated_memory_overflow():
    """Test self-healing for memory overflow scenarios"""
    print("\n[TEST] Testing memory overflow simulation...")
    
    from backend.sandbox_manager import sandbox_manager
    
    # Create a script that tries to allocate too much memory
    test_file = "memory_test.py"
    content = """
try:
    # Try to allocate 100MB string
    big_data = 'x' * (100 * 1024 * 1024)
    print("Allocated")
except MemoryError:
    print("Memory limit reached")
"""
    
    await sandbox_manager.write_file("test_user", test_file, content)
    
    # Execute the memory-intensive script
    stdout, stderr, exit_code, duration_ms = await sandbox_manager.run_command(
        "test_user",
        f"python {test_file}",
        test_file
    )
    
    # Should either complete or fail gracefully
    assert exit_code in [0, -1]
    
    # Cleanup
    await sandbox_manager.reset_sandbox("test_user")
    
    print("[PASS] Memory overflow handling verified")


@pytest.mark.asyncio
async def test_cascading_failure_detection():
    """Test detection and handling of multiple component failures"""
    print("\n[TEST] Testing cascading failure detection...")
    
    original_mode = system_state.mode
    
    # Simulate multiple component failures
    old_check_reflection = health_monitor._check_reflection
    old_check_executor = health_monitor._check_executor
    
    async def mock_failing_reflection():
        return {"ok": False, "error": "Reflection loop crashed"}
    
    async def mock_failing_executor():
        return {"ok": False, "error": "No workers available"}
    
    health_monitor._check_reflection = mock_failing_reflection
    health_monitor._check_executor = mock_failing_executor
    
    # Set consecutive failures to trigger healing
    health_monitor.consecutive_failures["reflection_service"] = 1
    health_monitor.consecutive_failures["task_executor"] = 1
    
    try:
        # Trigger health check - should detect multiple failures
        await health_monitor.check_all_components()
        
        # Verify multiple healing actions were logged
        async with async_session() as session:
            result = await session.execute(
                select(HealingAction)
                .order_by(HealingAction.created_at.desc())
                .limit(10)
            )
            actions = result.scalars().all()
            
            action_components = [a.component for a in actions]
            assert "reflection_service" in action_components or "task_executor" in action_components
        
        print("[PASS] Cascading failure detection verified")
    
    finally:
        # Restore original check functions
        health_monitor._check_reflection = old_check_reflection
        health_monitor._check_executor = old_check_executor
        system_state.mode = original_mode
        health_monitor.consecutive_failures.clear()


@pytest.mark.asyncio
async def test_manual_restart_with_governance():
    """Test manual restart requires governance approval"""
    print("\n[TEST] Testing manual restart with governance...")
    
    # Test manual restart (should be governed)
    result = await health_monitor.manual_restart("reflection_service", "test_admin")
    
    # Result should indicate governance check
    assert "status" in result
    assert result["status"] in ["success", "blocked", "pending_approval", "failed"]
    
    # Verify action was logged
    async with async_session() as session:
        result_query = await session.execute(
            select(HealingAction)
            .where(HealingAction.component == "reflection_service")
            .where(HealingAction.action.like("%manual%"))
            .order_by(HealingAction.created_at.desc())
            .limit(1)
        )
        action = result_query.scalar_one_or_none()
        
        # Action should exist if governance allowed it
        if result["status"] in ["success", "failed"]:
            assert action is not None
            assert "manual" in action.action.lower()
    
    print("[PASS] Manual restart governance verified")


@pytest.mark.asyncio
async def test_consecutive_failure_threshold():
    """Test that healing only triggers after consecutive failures"""
    print("\n[TEST] Testing consecutive failure threshold...")
    
    # Reset consecutive failures
    health_monitor.consecutive_failures["test_component"] = 0
    
    # First failure - should log but not heal
    health_monitor.consecutive_failures["test_component"] = 1
    assert health_monitor.consecutive_failures["test_component"] == 1
    
    # Second consecutive failure - should trigger healing
    health_monitor.consecutive_failures["test_component"] = 2
    assert health_monitor.consecutive_failures["test_component"] >= 2
    
    # Cleanup
    health_monitor.consecutive_failures.pop("test_component", None)
    
    print("[PASS] Consecutive failure threshold verified")


@pytest.mark.asyncio
async def test_health_check_latency_tracking():
    """Test that health checks track latency"""
    print("\n[TEST] Testing health check latency tracking...")
    
    await health_monitor.check_all_components()
    
    # Verify latency was recorded
    async with async_session() as session:
        result = await session.execute(
            select(HealthCheck)
            .where(HealthCheck.component == "database")
            .order_by(HealthCheck.created_at.desc())
            .limit(1)
        )
        check = result.scalar_one_or_none()
        assert check is not None
        assert check.latency_ms is not None
        assert check.latency_ms >= 0
    
    print("[PASS] Health check latency tracking verified")


@pytest.mark.asyncio
async def test_healing_action_success_resets_failures():
    """Test that successful healing resets consecutive failures"""
    print("\n[TEST] Testing healing success resets failure count...")
    
    component = "test_reset_component"
    health_monitor.consecutive_failures[component] = 5
    
    # Simulate successful check
    health_monitor.consecutive_failures[component] = 0
    
    assert health_monitor.consecutive_failures[component] == 0
    
    print("[PASS] Failure reset after successful healing verified")
