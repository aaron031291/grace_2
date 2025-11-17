"""Request ID middleware

Adds/propagates X-Request-ID header for each request and exposes it via request.state.request_id
so handlers can include it in structured logs.
"""
from __future__ import annotations

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get(self.header_name)
        if not req_id:
            req_id = f"req_{uuid.uuid4().hex[:12]}"
        # attach to request state
        request.state.request_id = req_id
        response: Response = await call_next(request)
        # echo back header for correlation
        response.headers.setdefault(self.header_name, req_id)
        return response
