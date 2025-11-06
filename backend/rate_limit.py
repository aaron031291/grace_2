"""Simple in-memory rate limiter decorators for per-user actions.

Designed for low-volume governance endpoints. Not suitable for multi-process deployments.
"""
from __future__ import annotations

import os
import time
import asyncio
from typing import Callable, Dict, Deque, Optional
from collections import deque
from fastapi import HTTPException


class _TokenBucket:
    def __init__(self, capacity: int, window_secs: int):
        self.capacity = capacity
        self.window = window_secs
        self.events: Deque[float] = deque()
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        now = time.monotonic()
        cutoff = now - self.window
        async with self._lock:
            while self.events and self.events[0] < cutoff:
                self.events.popleft()
            if len(self.events) < self.capacity:
                self.events.append(now)
                return True
            return False


action_buckets: Dict[str, Dict[str, _TokenBucket]] = {}
_action_locks: Dict[str, asyncio.Lock] = {}


def _get_bucket(action: str, key: str, capacity: int, window: int) -> _TokenBucket:
    # Per-action lock to avoid thundering herd on dict init
    lock = _action_locks.setdefault(action, asyncio.Lock())
    async def _create() -> _TokenBucket:
        async with lock:
            inner = action_buckets.setdefault(action, {})
            bucket = inner.get(key)
            if not bucket:
                bucket = _TokenBucket(capacity, window)
                inner[key] = bucket
            return bucket
    # Return a coroutine-aware accessor
    return _BucketProxy(_create)


class _BucketProxy:
    def __init__(self, factory_coro: Callable[[], asyncio.Future]):
        self._factory_coro = factory_coro
        self._bucket: Optional[_TokenBucket] = None

    async def ensure(self) -> _TokenBucket:
        if self._bucket is None:
            self._bucket = await self._factory_coro()
        return self._bucket


def rate_limited(
    action: str,
    *,
    per_minute_env: str = "APPROVAL_DECISION_RATE_PER_MIN",
    default_per_minute: int = 10,
    bypass_env: str = "RATE_LIMIT_BYPASS",
    user_extractor: Optional[Callable[[dict], str]] = None,
):
    """Decorator to limit calls per user for a given action.

    Reads capacity from env var; when bypass env is truthy, limiter is disabled.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Bypass in tests/dev when requested
            if os.getenv(bypass_env, "").lower() in {"1", "true", "yes", "on"}:
                return await func(*args, **kwargs)

            # Identify user from kwargs injected by dependency (get_current_user)
            user = None
            if user_extractor:
                try:
                    user = user_extractor(kwargs)
                except Exception:
                    user = None
            if not user:
                user = kwargs.get("current_user") or "anonymous"

            try:
                capacity = int(os.getenv(per_minute_env, str(default_per_minute)))
            except Exception:
                capacity = default_per_minute

            window_secs = 60
            key = f"{user}"
            proxy = _get_bucket(action, key, capacity, window_secs)
            bucket = await proxy.ensure()
            allowed = await bucket.allow()
            if not allowed:
                # Suggest retry after remaining window (approximate)
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
