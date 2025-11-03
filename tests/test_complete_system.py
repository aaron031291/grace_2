import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_complete_workflow():
    """Test end-to-end Grace workflow"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 1. Register user
        reg_response = await ac.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "testpass"}
        )
        assert reg_response.status_code == 201
        token = reg_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Send chat message
        chat_response = await ac.post(
            "/api/chat/",
            json={"message": "hello"},
            headers=headers
        )
        assert chat_response.status_code == 200
        assert "response" in chat_response.json()
        
        # 3. Check metrics
        metrics_response = await ac.get("/api/metrics/summary")
        assert metrics_response.status_code == 200
        metrics = metrics_response.json()
        assert metrics["total_messages"] > 0
        
        # 4. Get reflections
        ref_response = await ac.get("/api/reflections/")
        assert ref_response.status_code == 200
        
        # 5. Create memory artifact
        mem_response = await ac.post(
            "/api/memory/items",
            json={
                "path": "test/example.md",
                "content": "# Test Knowledge",
                "domain": "test",
                "reason": "Integration test"
            },
            headers=headers
        )
        assert mem_response.status_code == 200
        
        # 6. Verify immutable log
        log_response = await ac.get("/api/log/entries?limit=10")
        assert log_response.status_code == 200
        log_data = log_response.json()
        assert len(log_data["entries"]) > 0
        
        # 7. Verify log integrity
        verify_response = await ac.get("/api/log/verify")
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] == True

@pytest.mark.asyncio
async def test_governance_flow():
    """Test governance and approval workflow"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # Get policies
        policies = await ac.get("/api/governance/policies")
        assert policies.status_code == 200
        
        # Check audit log
        audit = await ac.get("/api/governance/audit")
        assert audit.status_code == 200

@pytest.mark.asyncio
async def test_self_healing():
    """Test self-healing system"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # Check health status
        health = await ac.get("/api/health/status")
        assert health.status_code == 200
        data = health.json()
        assert "system_mode" in data
        assert "checks" in data

@pytest.mark.asyncio
async def test_meta_loops():
    """Test meta-loop system"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # Get meta analyses
        analyses = await ac.get("/api/meta/analyses")
        assert analyses.status_code == 200
        
        # Get evaluations
        evals = await ac.get("/api/meta/evaluations")
        assert evals.status_code == 200
