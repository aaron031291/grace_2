"""Input sanitization helpers and middleware."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_400_BAD_REQUEST


logger = logging.getLogger("grace.security.sanitizer")


class SuspiciousInputError(ValueError):
    """Raised when potentially malicious content is detected."""

    def __init__(self, message: str, value: str, field: Optional[str] = None) -> None:
        super().__init__(message)
        self.value = value
        self.field = field or "value"


_HTML_TAG_RE = re.compile(r"<\s*/?\s*\w+[^>]*>")
_SQL_KEYWORDS = re.compile(r"\b(select|insert|update|delete|drop|union|alter|create|grant|revoke)\b", re.IGNORECASE)


def sanitize_text_value(
    value: str,
    *,
    field: str = "value",
    allow_html: bool = False,
    allow_sql_keywords: bool = False,
) -> str:
    """Strip dangerous content from a string or raise if suspicious."""

    trimmed = value.strip()

    if not allow_html and _HTML_TAG_RE.search(trimmed):
        raise SuspiciousInputError(f"HTML tags are not allowed in {field}", trimmed, field)

    if not allow_sql_keywords and _SQL_KEYWORDS.search(trimmed):
        raise SuspiciousInputError(f"SQL keywords are not permitted in {field}", trimmed, field)

    return trimmed


class SanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces basic sanitization on query parameters."""

    def __init__(self, app, *, block_html: bool = True, block_sql: bool = True) -> None:
        super().__init__(app)
        self.block_html = block_html
        self.block_sql = block_sql

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        for key, value in request.query_params.multi_items():
            try:
                sanitize_text_value(
                    value,
                    field=key,
                    allow_html=not self.block_html,
                    allow_sql_keywords=not self.block_sql,
                )
            except SuspiciousInputError as exc:
                hashed = hashlib.sha256(exc.value.encode("utf-8")).hexdigest()
                logger.warning(
                    "Blocked suspicious query parameter",
                    extra={
                        "path": str(request.url.path),
                        "field": exc.field,
                        "hash": hashed,
                    },
                )
                return JSONResponse(
                    status_code=HTTP_400_BAD_REQUEST,
                    content={"detail": "Request rejected: suspected malicious content."},
                )

        response = await call_next(request)
        return response
