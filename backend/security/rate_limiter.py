"""Rate limiting utilities for the Grace API."""

from __future__ import annotations

import logging
from typing import Sequence

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


logger = logging.getLogger("grace.security.rate_limit")


def rate_limit_key(request: Request) -> str:
    """Return a rate-limiting key based on token or client address."""

    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ")[-1]

    api_key = request.headers.get("x-api-key")
    if api_key:
        return api_key

    return get_remote_address(request)


limiter = Limiter(key_func=rate_limit_key, default_limits=[])


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(
        "Rate limit exceeded",
        extra={
            "path": str(request.url.path),
            "method": request.method,
            "limit": exc.limit,
        },
    )
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Try again soon."},
        headers={"Retry-After": str(exc.detail)} if exc.detail else None,
    )


def init_rate_limiter(app, default_limits: Sequence[str]) -> None:
    """Attach the limiter middleware and exception handlers to the app."""

    limiter.default_limits = list(default_limits)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware, limiter=limiter)
