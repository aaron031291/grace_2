"""CLI scaffolding for interacting with Grace cognition metrics."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx


API_BASE = "http://localhost:8000"


async def cognition_status() -> None:
    """Fetch and display cognition status."""

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/cognition/status")
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))


async def cognition_readiness() -> None:
    """Fetch readiness report."""

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/api/cognition/report/latest")
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))


def run_sync(coro: Any) -> None:
    asyncio.run(coro)


__all__ = ["cognition_status", "cognition_readiness", "run_sync"]
