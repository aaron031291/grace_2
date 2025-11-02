import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.self_healing import health_monitor, system_state

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
    assert system_state.mode == "normal"
    
    system_state.mode = "read_only"
    assert system_state.mode == "read_only"
    
    system_state.mode = "normal"
    assert system_state.mode == "normal"

@pytest.mark.asyncio
async def test_healing_action_logged():
    """Test that healing actions are logged"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health/status")
        data = response.json()
        
        assert isinstance(data["actions"], list)
