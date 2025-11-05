"""
Export filters tests for Knowledge dataset export
- Verifies that tags_csv applies AND semantics
- Verifies that min_trust filters by metadata.trust_score
- Uses in-process ASGI client against backend.main.app
"""

import asyncio
import time
import pytest

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
        username = f"exp_user_{int(time.time())}"
        password = "Export123!"
        r = await client.post("/api/auth/register", json={"username": username, "password": password})
        if r.status_code not in (200, 201):
            r = await client.post("/api/auth/login", json={"username": username, "password": password})
            assert r.status_code == 200, f"Auth failed: {r.status_code} {r.text}"
        token = r.json().get("access_token")
        assert token, "Missing access_token from auth response"
        return {"Authorization": f"Bearer {token}"}


async def test_export_filters_tags_and_min_trust():
    import backend.main as m
    import httpx

    app = m.app

    await _run_startup(app)
    try:
        headers = await _auth_headers(app)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Ingest two artifacts with different tags and trust scores
            # Artifact A: tags [tag1, tag2], trust 80 (should match stricter export)
            r = await client.post(
                "/api/ingest/text",
                json={
                    "content": "Artifact A content",
                    "title": f"Artifact A {int(time.time())}",
                    "artifact_type": "text",
                    "domain": "general",
                    "tags": ["tag1", "tag2"],
                    "metadata": {"trust_score": 80}
                },
                headers=headers,
            )
            assert r.status_code == 200, f"ingest A failed: {r.status_code} {r.text}"

            # Artifact B: tags [tag1], trust 50 (should be filtered out by tags AND and min_trust)
            r = await client.post(
                "/api/ingest/text",
                json={
                    "content": "Artifact B content",
                    "title": f"Artifact B {int(time.time())}",
                    "artifact_type": "text",
                    "domain": "general",
                    "tags": ["tag1"],
                    "metadata": {"trust_score": 50}
                },
                headers=headers,
            )
            assert r.status_code == 200, f"ingest B failed: {r.status_code} {r.text}"

            # Export requiring both tag1 AND tag2, and min_trust 70
            r = await client.get(
                "/api/knowledge/export",
                params={
                    "domain": "general",
                    "tags_csv": "tag1,tag2",
                    "min_trust": 70,
                    "include_content": False,
                },
                headers=headers,
            )
            assert r.status_code == 200, f"export failed: {r.status_code} {r.text}"
            data = r.json()
            assert isinstance(data.get("items"), list)
            # Only Artifact A should satisfy both tags and min_trust
            assert data.get("count", 0) >= 1
            items = data["items"]
            assert all("tag1" in i.get("tags", []) and "tag2" in i.get("tags", []) for i in items)
            # Trust should be >= 70 in metadata; when present
            for i in items:
                meta = i.get("metadata", {})
                ts = meta.get("trust_score")
                if ts is not None:
                    assert float(ts) >= 70.0

            # Export with only tag2 should include Artifact A, but not B
            r2 = await client.get(
                "/api/knowledge/export",
                params={
                    "domain": "general",
                    "tags_csv": "tag2",
                    "include_content": False,
                },
                headers=headers,
            )
            assert r2.status_code == 200, f"export tag2 failed: {r2.status_code} {r2.text}"
            data2 = r2.json()
            assert all("tag2" in i.get("tags", []) for i in data2.get("items", []))
    finally:
        await _run_shutdown(app)
