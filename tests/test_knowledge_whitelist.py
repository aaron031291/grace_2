"""
Knowledge whitelist and trust score tests
- Uses in-process ASGI client against backend.main.app
- Verifies unknown domains are not auto-approved and require pending approval
- Verifies trust score API returns expected structure and recommendation
"""

import asyncio
import time
import pytest

# Mark tests to run in any async environment
pytestmark = pytest.mark.anyio


async def _run_startup(app):
    if app.router.on_startup:
        for handler in app.router.on_startup:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()


async def _run_shutdown(app):
    if app.router.on_shutdown:
        for handler in app.router.on_shutdown:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()


async def _auth_headers(app):
    import httpx

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        username = f"wl_user_{int(time.time())}"
        password = "Whitelist123!"
        r = await client.post("/api/auth/register", json={"username": username, "password": password})
        if r.status_code not in (200, 201):
            r = await client.post("/api/auth/login", json={"username": username, "password": password})
            assert r.status_code == 200, f"Auth failed: {r.status_code} {r.text}"
        token = r.json().get("access_token")
        assert token, "Missing access_token from auth response"
        return {"Authorization": f"Bearer {token}"}


async def test_unknown_domain_requires_pending_approval():
    import backend.main as m
    app = m.app

    await _run_startup(app)
    try:
        import httpx
        headers = await _auth_headers(app)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Use an unknown domain that is not in default trusted list
            url = "https://unknown-example-probe-domain.xyz"

            # Trust score endpoint should work and indicate review/block
            r = await client.get("/api/trust/score", params={"url": url})
            assert r.status_code == 200, f"trust/score failed: {r.status_code} {r.text}"
            body = r.json()
            assert "trust_score" in body and "auto_approve" in body and "recommendation" in body
            assert body["auto_approve"] is False

            # Ingest URL should return pending_approval without attempting network fetch
            r = await client.post("/api/ingest/url", json={"url": url}, headers=headers)
            assert r.status_code == 200, f"ingest/url pending check failed: {r.status_code} {r.text}"
            data = r.json()
            assert data.get("status") == "pending_approval"
            assert "approval_id" in data
    finally:
        await _run_shutdown(app)
