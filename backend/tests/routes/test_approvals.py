import os
import pytest
import pytest_asyncio
import httpx


TEST_DB_PATH = os.path.join(".", "databases", "test_grace_approvals.db")


@pytest_asyncio.fixture(scope="module")
async def test_client():
    # Ensure env is set BEFORE importing the app/auth modules
    os.environ["SECRET_KEY"] = os.environ.get("SECRET_KEY", "test-secret-approvals")
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

    # Import here so startup events create tables against the test DB
    from backend.main import app

    transport = httpx.ASGITransport(app=app)

    # Manually trigger FastAPI startup/shutdown to ensure DB tables exist
    await app.router.startup()
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await app.router.shutdown()

    # Teardown: remove the test DB file to keep workspace clean
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception:
        # Best-effort cleanup; ignore on Windows file locks
        pass


def auth_headers():
    # Create a valid JWT using the app's auth helper
    from backend.auth import create_access_token
    token = create_access_token({"sub": "tester"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_approvals_happy_path(test_client: httpx.AsyncClient):
    headers = auth_headers()

    # 1) Create approval
    create_resp = await test_client.post(
        "/api/governance/approvals",
        json={"event_id": 123, "reason": "Sensitive operation"},
        headers=headers,
    )
    assert create_resp.status_code == 200, create_resp.text
    created = create_resp.json()
    assert "id" in created and created["id"] > 0
    assert created["status"] == "pending"
    # verify_action adds an envelope id to dict responses
    assert "_verification_id" in created

    approval_id = created["id"]

    # 2) List approvals (filter pending)
    list_resp = await test_client.get(
        "/api/governance/approvals?status=pending&limit=50", headers=headers
    )
    assert list_resp.status_code == 200, list_resp.text
    items = list_resp.json()
    assert any(item["id"] == approval_id for item in items)

    # 3) Get one
    get_resp = await test_client.get(f"/api/governance/approvals/{approval_id}", headers=headers)
    assert get_resp.status_code == 200, get_resp.text
    got = get_resp.json()
    assert got["id"] == approval_id
    assert got["status"] == "pending"

    # 4) Decide approve
    decide_resp = await test_client.post(
        f"/api/governance/approvals/{approval_id}/decision",
        json={"decision": "approve", "reason": "Looks safe"},
        headers=headers,
    )
    assert decide_resp.status_code == 200, decide_resp.text
    decided = decide_resp.json()
    assert decided["status"] == "approved"
    assert decided["decision_by"] == "tester"
    # verify_action adds an envelope id to dict responses
    assert "_verification_id" in decided

    # 5) Stats
    stats_resp = await test_client.get("/api/governance/approvals/stats", headers=headers)
    assert stats_resp.status_code == 200, stats_resp.text
    stats = stats_resp.json()
    for key in ("pending", "approved", "rejected"):
        assert key in stats


@pytest.mark.asyncio
async def test_approvals_invalid_and_double_decision(test_client: httpx.AsyncClient):
    headers = auth_headers()

    # Create a fresh approval
    create_resp = await test_client.post(
        "/api/governance/approvals",
        json={"event_id": 999, "reason": "Check invalid/duplicate"},
        headers=headers,
    )
    assert create_resp.status_code == 200, create_resp.text
    approval_id = create_resp.json()["id"]

    # Invalid decision value
    bad_resp = await test_client.post(
        f"/api/governance/approvals/{approval_id}/decision",
        json={"decision": "maybe", "reason": "?"},
        headers=headers,
    )
    assert bad_resp.status_code == 400
    assert "Invalid decision" in bad_resp.text

    # Valid first decision
    ok_resp = await test_client.post(
        f"/api/governance/approvals/{approval_id}/decision",
        json={"decision": "reject", "reason": "Not safe"},
        headers=headers,
    )
    assert ok_resp.status_code == 200, ok_resp.text
    assert ok_resp.json()["status"] == "rejected"

    # Duplicate decision should fail with 400
    dup_resp = await test_client.post(
        f"/api/governance/approvals/{approval_id}/decision",
        json={"decision": "approve", "reason": "changed mind"},
        headers=headers,
    )
    assert dup_resp.status_code == 400
    assert "Already decided" in dup_resp.text


@pytest.mark.asyncio
async def test_approvals_not_found(test_client: httpx.AsyncClient):
    headers = auth_headers()

    # Non-existent approval id
    nf_resp = await test_client.get("/api/governance/approvals/999999", headers=headers)
    assert nf_resp.status_code == 404

    nf_decide = await test_client.post(
        "/api/governance/approvals/999999/decision",
        json={"decision": "approve"},
        headers=headers,
    )
    assert nf_decide.status_code == 404



@pytest.mark.asyncio
async def test_approval_decision_rate_limit_overflow(test_client: httpx.AsyncClient):
    # Configure strict rate limit for the test and ensure no bypass
    os.environ.pop("RATE_LIMIT_BYPASS", None)
    os.environ["APPROVAL_DECISION_RATE_PER_MIN"] = "3"

    headers = auth_headers()

    # Use a non-existent request id to avoid changing state; limiter counts before handler runs
    target_id = 424242

    statuses = []
    for _ in range(5):
        resp = await test_client.post(
            f"/api/governance/approvals/{target_id}/decision",
            json={"decision": "approve", "reason": "limit test"},
            headers=headers,
        )
        statuses.append(resp.status_code)
        # First few within capacity should be non-429 (likely 404 for not found)
        # After capacity exceeded, expect 429 with Retry-After header

    assert statuses.count(429) >= 1, f"Expected at least one 429, got {statuses}"

    # Verify Retry-After header is present on at least one 429 response
    has_retry_after = False
    for _ in range(3):
        resp = await test_client.post(
            f"/api/governance/approvals/{target_id}/decision",
            json={"decision": "approve", "reason": "limit test"},
            headers=headers,
        )
        if resp.status_code == 429 and resp.headers.get("Retry-After"):
            has_retry_after = True
            break
    assert has_retry_after, "Missing Retry-After header on 429 response"
