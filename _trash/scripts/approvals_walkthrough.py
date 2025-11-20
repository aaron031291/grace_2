"""
Approvals Walkthrough Script

Usage (Windows):
  set GRACE_BACKEND_URL=http://localhost:8000
  set GRACE_TOKEN=<your-jwt>
  py scripts\approvals_walkthrough.py

This script exercises the approval flow: create -> list -> get -> decide -> stats
"""
from __future__ import annotations

import asyncio
import os
import json
import httpx


BASE_URL = os.getenv("GRACE_BACKEND_URL", "http://localhost:8000")
TOKEN = os.getenv("GRACE_TOKEN")


def _headers() -> dict:
    hdrs = {"Content-Type": "application/json"}
    if TOKEN:
        hdrs["Authorization"] = f"Bearer {TOKEN}"
    return hdrs


async def main():
    if not TOKEN:
        print("ERROR: GRACE_TOKEN not set. Obtain a JWT via login and set GRACE_TOKEN.")
        return 1

    async with httpx.AsyncClient(base_url=BASE_URL, headers=_headers(), timeout=30) as client:
        # 0) Health
        try:
            health = await client.get("/health")
            print("Health:", health.status_code, health.text)
        except Exception as e:
            print(f"Health check failed: {e}")

        # 1) Create approval
        print("\n1) Creating approval request...")
        create_resp = await client.post(
            "/api/governance/approvals",
            json={"event_id": 101, "reason": "Walkthrough demo"},
        )
        print("Status:", create_resp.status_code)
        print("Body:", create_resp.text)
        create_data = create_resp.json()
        approval_id = create_data.get("id")
        verification_id = create_data.get("_verification_id")
        print(f"Created approval_id={approval_id}, verification_id={verification_id}")

        # 2) List approvals (pending)
        print("\n2) Listing pending approvals...")
        list_resp = await client.get("/api/governance/approvals", params={"status": "pending", "limit": 10})
        print("Status:", list_resp.status_code)
        items = list_resp.json()
        print("Found", len(items), "item(s)")

        # 3) Get one
        print("\n3) Getting created approval...")
        get_resp = await client.get(f"/api/governance/approvals/{approval_id}")
        print("Status:", get_resp.status_code)
        print("Body:", get_resp.text)

        # 4) Decide approve
        print("\n4) Approving the request...")
        decide_resp = await client.post(
            f"/api/governance/approvals/{approval_id}/decision",
            json={"decision": "approve", "reason": "Looks OK"},
        )
        print("Status:", decide_resp.status_code)
        print("Body:", decide_resp.text)
        decided = decide_resp.json()
        print("Decision verification_id:", decided.get("_verification_id"))

        # 5) Stats
        print("\n5) Fetching stats...")
        stats_resp = await client.get("/api/governance/approvals/stats")
        print("Status:", stats_resp.status_code)
        print("Body:", stats_resp.text)

    print("\nWalkthrough complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
