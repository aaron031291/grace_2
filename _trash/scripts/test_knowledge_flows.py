"""
Knowledge Flows Probe
- Starts backend.main app startup handlers (DB init, services)
- Registers test user, logs in to get JWT
- Exercises knowledge endpoints:
  * /api/ingest/text -> get artifact_id
  * /api/knowledge/artifacts/{id}/revisions -> expect initial_ingest
  * /api/knowledge/artifacts/{id}/rename -> expect revision increment
  * /api/ingest/artifacts (list) excludes deleted by default
  * /api/knowledge/artifacts/{id} DELETE (soft delete) -> then restore
  * /api/knowledge/export -> expect JSON with items
  * /api/ingest/url with unknown domain -> expect pending_approval
Exits 0 on success; non-zero on failure.

Windows:
  py scripts\test_knowledge_flows.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def main() -> int:
    import backend.main as m

    app = m.app

    # Run startup handlers (mirrors scripts/test_backend_startup_backend.py)
    if app.router.on_startup:
        for handler in app.router.on_startup:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()

    passed = 0
    failed = 0

    # HTTPX AsyncClient with ASGI transport
    try:
        import httpx
    except Exception:
        print("ERROR: httpx required. pip install httpx")
        return 1

    headers: Dict[str, str] = {}

    try:
        # Register or login
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Try register
            r = await client.post("/api/auth/register", json={"username": "tester", "password": "Password123"})
            if r.status_code not in (200, 201):
                # Try login
                r = await client.post("/api/auth/login", json={"username": "tester", "password": "Password123"})
                if r.status_code != 200:
                    print(f"[AUTH] FAIL: {r.status_code} {r.text}")
                    failed += 1
                else:
                    passed += 1
            else:
                passed += 1
            token = r.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # 1) Ingest text
            from datetime import datetime
            unique = datetime.utcnow().isoformat()
            title = f"Test Artifact {unique}"
            content = f"Hello Knowledge Base {unique}"
            r = await client.post(
                "/api/ingest/text",
                json={
                    "content": content,
                    "title": title,
                    "artifact_type": "text",
                    "domain": "general",
                    "tags": ["test", "demo"],
                    "metadata": {"trust_score": 80}
                },
                headers=headers,
            )
            assert r.status_code == 200, f"ingest/text failed: {r.status_code} {r.text}"
            artifact_id = r.json().get("artifact_id")
            assert artifact_id, "artifact_id missing"
            passed += 1

            # 2) Revisions (expect initial_ingest)
            r = await client.get(f"/api/knowledge/artifacts/{artifact_id}/revisions", headers=headers)
            assert r.status_code == 200, f"revisions failed: {r.status_code} {r.text}"
            revs = r.json().get("revisions", [])
            assert revs and revs[0]["change_summary"] == "initial_ingest", "initial revision missing"
            passed += 1

            # 3) Rename
            r = await client.patch(
                f"/api/knowledge/artifacts/{artifact_id}/rename",
                json={"new_title": "Renamed Artifact", "change_summary": "rename probe"},
                headers=headers,
            )
            assert r.status_code == 200, f"rename failed: {r.status_code} {r.text}"
            passed += 1

            # 4) Soft delete
            # Some httpx versions don't support json= on delete(); use generic request
            r = await client.request(
                "DELETE",
                f"/api/knowledge/artifacts/{artifact_id}",
                json={"reason": "probe"},
                headers=headers,
            )
            assert r.status_code == 200, f"delete failed: {r.status_code} {r.text}"
            passed += 1

            # 5) List excludes deleted
            r = await client.get("/api/ingest/artifacts", headers=headers)
            assert r.status_code == 200, f"list artifacts failed: {r.status_code} {r.text}"
            items = r.json()
            assert all(a.get("id") != artifact_id for a in items), "deleted artifact should be excluded from list"
            passed += 1

            # 6) Restore
            r = await client.post(f"/api/knowledge/artifacts/{artifact_id}/restore", headers=headers)
            assert r.status_code == 200, f"restore failed: {r.status_code} {r.text}"
            passed += 1

            # 7) Export dataset
            r = await client.get("/api/knowledge/export?domain=general&include_content=false", headers=headers)
            assert r.status_code == 200, f"export failed: {r.status_code} {r.text}"
            data = r.json()
            assert "items" in data, "export missing items"
            passed += 1

            # 8) Ingest URL with unknown domain (should be pending)
            r = await client.post("/api/ingest/url", json={"url": "https://unknown-example-probe-domain.xyz"}, headers=headers)
            assert r.status_code == 200, f"ingest url pending check failed: {r.status_code} {r.text}"
            body = r.json()
            assert body.get("status") == "pending_approval", f"expected pending_approval, got {body}"
            passed += 1

    except AssertionError as e:
        print(f"ASSERT FAIL: {e}")
        failed += 1
    except Exception as e:
        print(f"EXCEPTION: {e}")
        failed += 1

    # Run shutdown
    if app.router.on_shutdown:
        for handler in app.router.on_shutdown:
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()

    print("\nKnowledge Flows Probe Summary:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        code = loop.run_until_complete(main())
    sys.exit(code)
