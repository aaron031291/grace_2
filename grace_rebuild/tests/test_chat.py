import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.models import async_session, Base, engine, User, ChatMessage
from backend.auth import hash_password

@pytest.fixture(autouse=True, scope="module")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        test_user = User(
            username="testuser",
            password_hash=hash_password("testpass")
        )
        session.add(test_user)
        await session.commit()
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_register():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={"username": "newuser", "password": "newpass"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

@pytest.mark.asyncio
async def test_chat_basic():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_response = await ac.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        token = login_response.json()["access_token"]
        
        response = await ac.post(
            "/api/chat/",
            json={"message": "hello"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Grace" in data["response"] or "Hello" in data["response"]

@pytest.mark.asyncio
async def test_chat_history():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_response = await ac.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )
        token = login_response.json()["access_token"]
        
        await ac.post(
            "/api/chat/",
            json={"message": "test message 1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = await ac.post(
            "/api/chat/",
            json={"message": "show me my history"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

@pytest.mark.asyncio
async def test_metrics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/metrics/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_messages" in data
        assert "active_users" in data
        assert "registered_users" in data
