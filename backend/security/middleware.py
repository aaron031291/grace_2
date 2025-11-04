import asyncio
import json
import re
import time
from collections import defaultdict, deque
from typing import Any, Iterable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class SuspiciousInputError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class InMemoryRateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._events: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        now = time.monotonic()
        async with self._lock:
            events = self._events[key]
            while events and now - events[0] > self.window:
                events.popleft()
            if len(events) >= self.limit:
                return False
            events.append(now)
            return True


SUSPICIOUS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)<\s*script"),
    re.compile(r"(?i)javascript:"),
    re.compile(r"(?i)union\s+select"),
    re.compile(r"(?i)drop\s+table"),
    re.compile(r"(?i)or\s+1\s*=\s*1"),
)

MAX_JSON_BODY_BYTES = 2 * 1024 * 1024  # 2 MB


def _scan_strings(values: Iterable[str]) -> None:
    for value in values:
        if not value:
            continue
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.search(value):
                raise SuspiciousInputError(
                    detail="Request blocked by security filters."
                )


def _walk_payload(payload: Any) -> Iterable[str]:
    if isinstance(payload, str):
        yield payload
    elif isinstance(payload, dict):
        for value in payload.values():
            yield from _walk_payload(value)
    elif isinstance(payload, (list, tuple, set)):
        for item in payload:
            yield from _walk_payload(item)


def _client_identifier(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def setup_security_middleware(app, *, rate_limit: int = 120, window_seconds: int = 60):
    limiter = InMemoryRateLimiter(limit=rate_limit, window_seconds=window_seconds)

    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        if not await limiter.allow(_client_identifier(request)):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down.",
                },
            )

        try:
            _scan_strings(request.query_params.values())

            if request.method in {"POST", "PUT", "PATCH"}:
                body = await request.body()
                if len(body) > MAX_JSON_BODY_BYTES:
                    raise HTTPException(status_code=413, detail="Request entity too large")

                if body:
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        try:
                            payload = json.loads(body)
                        except json.JSONDecodeError:
                            payload = None
                        if payload is not None:
                            _scan_strings(_walk_payload(payload))

                async def receive() -> dict:
                    return {"type": "http.request", "body": body, "more_body": False}

                request._receive = receive  # type: ignore[attr-defined]

        except SuspiciousInputError as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

        return await call_next(request)

