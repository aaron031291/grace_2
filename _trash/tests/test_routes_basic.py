import asyncio
import sys
from pathlib import Path
import pytest

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.mark.anyio
async def test_health_endpoint_ok():
    import backend.main as m
    app = m.app

    import httpx
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") == "ok"


@pytest.mark.anyio
async def test_core_heartbeat_200():
    import backend.main as m
    app = m.app

    import httpx
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/core/heartbeat")
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") == "alive"
        assert "uptime" in body
