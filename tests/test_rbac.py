import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from backend.auth import get_current_user
from backend.models import Base, User, async_session, engine
from backend.security import require_roles


@pytest.fixture(scope="module", autouse=True)
async def setup_users():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        session.add_all(
            [
                User(username="rbac_admin", password_hash="x", role="admin"),
                User(username="rbac_viewer", password_hash="x", role="viewer"),
            ]
        )
        await session.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app = FastAPI()


@app.get("/secure")
async def secure_endpoint(username: str = Depends(require_roles("admin"))):
    return {"user": username}


def test_rbac_allows_authorised_user():
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: "rbac_admin"
    response = client.get("/secure")
    assert response.status_code == 200
    assert response.json()["user"] == "rbac_admin"
    app.dependency_overrides.clear()


def test_rbac_blocks_unauthorised_user():
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: "rbac_viewer"
    response = client.get("/secure")
    assert response.status_code == 403
    app.dependency_overrides.clear()
