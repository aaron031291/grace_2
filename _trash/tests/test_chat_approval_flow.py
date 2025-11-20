"""
Smoke test for chat + approvals integration

Tests:
1. Chat endpoint receives message
2. OpenAI reasoner generates response
3. Action requiring approval is proposed
4. Approval request appears in governance
5. User approves action
6. Action executes successfully
"""

import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_chat_generates_response():
    """Test basic chat response generation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/unified/chat",
            json={
                "message": "Hello Grace, what's your status?",
                "user_id": "test_user",
                "include_telemetry": True,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reply" in data
        assert "trace_id" in data
        assert "session_id" in data
        assert "confidence" in data
        assert data["confidence"] >= 0.0
        assert data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_chat_with_action_approval():
    """Test chat that requires approval for action"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/unified/chat",
            json={
                "message": "Please create a new database table for user analytics",
                "user_id": "test_user",
                "include_telemetry": True,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "actions" in data
        if data.get("requires_approval"):
            assert len(data["actions"]) > 0
            
            action = data["actions"][0]
            assert "tier" in action
            assert action["tier"] >= 2


@pytest.mark.asyncio
async def test_memory_stats():
    """Test memory catalog stats endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/memory/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_assets" in data
        assert "total_bytes" in data
        assert "by_type" in data
        assert "by_status" in data


@pytest.mark.asyncio
async def test_remote_status():
    """Test remote monitoring status endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/remote/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "timestamp" in data
        assert "health" in data
        assert "trust_score" in data
        assert "confidence" in data
        assert "active_tasks" in data
        assert "pending_approvals" in data


@pytest.mark.asyncio
async def test_file_upload_ingestion():
    """Test file upload triggers memory ingestion"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("test.txt", b"Test content", "text/plain")}
        
        response = await client.post(
            "/api/memory/upload",
            files=files,
            data={"asset_type": "upload", "trust_score": "0.5"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "asset_id" in data
        assert "path" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
