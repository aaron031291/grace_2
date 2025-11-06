"""
Knowledge Revision Flow Test
- Validates ingest -> revisions -> rename -> soft-delete -> list-excludes -> restore
- Ensures revision numbers increment and soft-deleted artifacts are excluded by default

Run: py -m pytest -q
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
        username = f"rev_user_{int(time.time())}"
        password = "RevFlow123!"
        r = await client.post("/api/auth/register", json={"username": username, "password": password})
        if r.status_code not in (200, 201):
            r = await client.post("/api/auth/login", json={"username": username, "password": password})
            assert r.status_code == 200, f"Auth failed: {r.status_code} {r.text}"
        token = r.json().get("access_token")
        assert token, "Missing access_token from auth response"
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_revision_flow_end_to_end():
    import backend.main as m
    import httpx

    app = m.app

    await _run_startup(app)
    try:
        headers = await _auth_headers(app)
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1) Ingest a unique artifact
            title = f"RevFlow Artifact {int(time.time())}"
            r = await client.post(
                "/api/ingest/text",
                json={
                    "content": "Revision flow content",
                    "title": title,
                    "artifact_type": "text",
                    "domain": "general",
                    "tags": ["rev", "flow"],
                    "metadata": {"trust_score": 75},
                },
                headers=headers,
            )
            assert r.status_code == 200, f"ingest failed: {r.status_code} {r.text}"
            artifact_id = r.json().get("artifact_id")
            assert artifact_id, "artifact_id missing"

            # 2) Revisions should contain initial_ingest
            r = await client.get(f"/api/knowledge/artifacts/{artifact_id}/revisions", headers=headers)
            assert r.status_code == 200, f"revisions failed: {r.status_code} {r.text}"
            revs = r.json().get("revisions", [])
            assert len(revs) >= 1, "expected at least 1 revision"
            assert revs[0]["change_summary"] == "initial_ingest"
            last_rev_num = revs[-1]["revision_number"]

            # 3) Rename should add a new revision
            r = await client.patch(
                f"/api/knowledge/artifacts/{artifact_id}/rename",
                json={"new_title": "Renamed Via Test", "change_summary": "rename test"},
                headers=headers,
            )
            assert r.status_code == 200, f"rename failed: {r.status_code} {r.text}"

            r = await client.get(f"/api/knowledge/artifacts/{artifact_id}/revisions", headers=headers)
            assert r.status_code == 200
            revs2 = r.json().get("revisions", [])
            assert revs2[-1]["revision_number"] == last_rev_num + 1, "revision number should increment after rename"
            last_rev_num = revs2[-1]["revision_number"]

            # 4) Soft delete should add another revision and exclude from default list
            r = await client.request(
                "DELETE",
                f"/api/knowledge/artifacts/{artifact_id}",
                json={"reason": "revflow test"},
                headers=headers,
            )
            assert r.status_code == 200, f"delete failed: {r.status_code} {r.text}"

            r = await client.get("/api/ingest/artifacts", headers=headers)
            assert r.status_code == 200
            items = r.json()
            assert all(a.get("id") != artifact_id for a in items), "deleted artifact should be excluded from default list"

            # 5) Restore should re-include and add revision
            r = await client.post(f"/api/knowledge/artifacts/{artifact_id}/restore", headers=headers)
            assert r.status_code == 200, f"restore failed: {r.status_code} {r.text}"

            r = await client.get(f"/api/knowledge/artifacts/{artifact_id}/revisions", headers=headers)
            assert r.status_code == 200
            revs3 = r.json().get("revisions", [])
            assert revs3[-1]["revision_number"] == last_rev_num + 1, "revision number should increment after restore"

    finally:
        await _run_shutdown(app)
